# SPDX-License-Identifier: MIT
# Copyright (c) 2026 Marek Cingel

"""Example ownership, exact verification matches and rendered Material tabs."""

import json
from html import unescape
import os
import socket
import subprocess
import sys
import time
from types import SimpleNamespace
import unittest
from unittest.mock import patch
from urllib.error import URLError
from urllib.request import urlopen

from mkdocs.exceptions import PluginError

import test_portal as fixture
import test_sources

assembly = fixture.assembly
examples = assembly.examples
SLOT = "<!-- opentlv-examples: fixed.roundtrip -->\nFallback native links.\n<!-- /opentlv-examples -->\n"


class ExampleTests(unittest.TestCase):
    write = fixture.PortalTests.write
    git = fixture.PortalTests.git
    mkdocs = fixture.PortalTests.mkdocs
    component_git = test_sources.MultiRepositoryTests.component_git
    commit_component = test_sources.MultiRepositoryTests.commit_component
    save_manifest = test_sources.MultiRepositoryTests.save_manifest

    def setUp(self):
        test_sources.MultiRepositoryTests.setUp(self)
        self.write(self.core / "docs/index.md", "# Home\n\n" + SLOT)
        self.write(self.core / "examples/roundtrip.c", 'puts("Core source");\n')
        self.native = {"version": 1, "examples": [{"feature": "fixed.roundtrip", "language": "c",
                       "status": "supported", "path": "examples/roundtrip.c"}]}
        self.binding = {"version": 1, "component_version": "2.3.0", "examples": [
            {"feature": "fixed.roundtrip", "language": "python", "status": "supported",
             "path": "examples/roundtrip.py"}]}
        self.write(self.core / "docs-examples.json", json.dumps(self.native))
        self.write(self.component / "examples/roundtrip.py", 'print("Python source")\n')
        self.write(self.component / "manual/index.md", "# Python\n\n" + SLOT)
        self.write(self.component / "docs-examples.json", json.dumps(self.binding))
        self.commit_component()
        self.component_sha = self.component_git("rev-parse", "HEAD")
        self.git("add", ".")
        self.git("-c", "user.name=Fixture", "-c", "user.email=fixture@example.invalid",
                 "-c", "commit.gpgsign=false", "commit", "-m", "Example fixture")
        self.sha = self.git("rev-parse", "HEAD")
        self.manifest["sources"][0]["revision"] = self.sha
        self.manifest["sources"][1]["revision"] = self.component_sha
        self.manifest["sources"][1]["examples"] = {"languages": ["python"]}
        self.save_manifest()

    def result(self, **changes):
        record = {"feature": "fixed.roundtrip", "language": "python", "component_commit": self.component_sha,
                  "core_commit": self.sha, "core_version": "0.7.1", "result": "passed",
                  "platform": "linux-x86_64", "configuration": "default",
                  "evidence": "https://example.invalid/results/immutable-test-id"}
        record.update(changes)
        self.manifest["sources"][1]["examples"]["results"] = [record]
        self.save_manifest()

    def assemble(self):
        assembly.assemble(self.portal)
        return (self.portal / "build/assembled/docs/index.md").read_text(encoding="utf-8")

    def test_sources_render_as_tabs_with_owner_links_and_provenance(self):
        before = (self.core / "docs/index.md").read_bytes()
        self.result()
        result = self.mkdocs()
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        html = (self.portal / "site/index.html").read_text(encoding="utf-8")
        self.assertIn('class="tabbed-set', html)
        self.assertIn('>Python</label>', html)
        self.assertIn('>C</label>', html)
        self.assertIn('"content.tabs.link"', html)
        other_page = (self.portal / "site/bindings/python/index.html").read_text(encoding="utf-8")
        self.assertIn('>Python</label>', other_page)
        self.assertIn('"content.tabs.link"', other_page)
        self.assertIn("Component version: 2.3.0", html)
        self.assertIn("Verified Core: 0.7.1", html)
        self.assertIn(f"/blob/{self.component_sha}/examples/roundtrip.py", html)
        self.assertIn("linux-x86_64", unescape(html))
        self.assertNotIn("Fallback native links", html)
        self.assertEqual(before, (self.core / "docs/index.md").read_bytes())
        self.assertEqual(self.git("status", "--porcelain"), "")
        self.assertEqual(self.component_git("status", "--porcelain"), "")
        metadata = json.loads((self.portal / "site/source-revision.json").read_text())
        self.assertEqual(len(metadata["example_inputs"]), 4)
        self.assertTrue(all(len(item["sha256"]) == 64 for item in metadata["example_inputs"]))
        self.assertEqual(self.assemble().count("/// tab | Python"), 1)

    def test_live_preview_rebuilds_when_example_source_changes(self):
        result = self.mkdocs()
        self.assertEqual(result.returncode, 0, result.stderr)
        self.write(self.portal / "mkdocs.local.yml", (fixture.ROOT / "mkdocs.local.yml").read_text())
        with socket.socket() as sock:
            sock.bind(("127.0.0.1", 0))
            port = sock.getsockname()[1]
        url = f"http://127.0.0.1:{port}/"
        log_path = self.base / "example-serve.log"
        env = dict(os.environ, OPENTLV_DOCS_LOCAL="1", PYTHONIOENCODING="utf-8")
        with log_path.open("w", encoding="utf-8") as log:
            process = subprocess.Popen(
                [sys.executable, "-m", "mkdocs", "serve", "-f", "mkdocs.local.yml", "--dev-addr", f"127.0.0.1:{port}"],
                cwd=self.portal, env=env, stdout=log, stderr=subprocess.STDOUT,
                creationflags=subprocess.CREATE_NO_WINDOW if os.name == "nt" else 0,
            )
            try:
                def wait_for(text):
                    deadline = time.monotonic() + 30
                    while time.monotonic() < deadline:
                        self.assertIsNone(process.poll(), log_path.read_text(encoding="utf-8"))
                        try:
                            with urlopen(url, timeout=1) as response:
                                if text in response.read().decode("utf-8"):
                                    return
                        except (URLError, TimeoutError):
                            pass
                        time.sleep(0.2)
                    self.fail(log_path.read_text(encoding="utf-8"))

                wait_for("Python source")
                self.write(self.component / "examples/roundtrip.py", 'print("Updated external example")\n')
                wait_for("Updated external example")
                time.sleep(1)
                builds = log_path.read_text(encoding="utf-8").count("Documentation built in")
                time.sleep(2)
                self.assertEqual(log_path.read_text(encoding="utf-8").count("Documentation built in"), builds)
            finally:
                process.terminate()
                process.wait(timeout=10)

    def test_core_only_and_omitted_binding(self):
        self.manifest["sources"][1]["repository"] = "https://github.com/OpenTLV/absent"
        self.save_manifest()
        text = self.assemble()
        self.assertIn("Repository unavailable", text)
        self.assertIn('puts("Core source")', text)
        self.manifest["sources"].pop()
        self.save_manifest()
        text = self.assemble()
        self.assertNotIn("Python", text)
        self.assertIn('puts("Core source")', text)

    def test_missing_unsupported_and_unverified_are_distinct(self):
        text = self.assemble()
        self.assertIn("not established (no result supplied)", text)
        self.assertIn('print("Python source")', text)
        with patch.dict(os.environ, {"OPENTLV_DOCS_LOCAL": "1"}):
            self.binding["examples"] = []
            self.write(self.component / "docs-examples.json", json.dumps(self.binding))
            self.assertIn("No example supplied", self.assemble())
            self.binding["examples"] = [{"feature": "fixed.roundtrip", "language": "python",
                                          "status": "unsupported", "reason": "Feature is not implemented."}]
            self.write(self.component / "docs-examples.json", json.dumps(self.binding))
            text = self.assemble()
            self.assertIn("Unsupported:", text)
            self.assertNotIn('print("Python source")', text)

    def test_failed_and_untested_results_withhold_code(self):
        for status in ("failed", "untested"):
            with self.subTest(status=status):
                self.result(result=status)
                text = self.assemble()
                self.assertIn(f"Test result: {status}", text)
                self.assertIn("Example withheld", text)
                self.assertNotIn('print("Python source")', text)

    def test_stale_commits_and_local_preview_never_claim_verified(self):
        for field in ("component_commit", "core_commit"):
            with self.subTest(field=field):
                self.result(**{field: "f" * 40})
                self.assertNotIn("Verified Core: 0", self.assemble())
        self.result()
        with patch.dict(os.environ, {"OPENTLV_DOCS_LOCAL": "1"}):
            self.assertNotIn("Verified Core: 0", self.assemble())

    def test_invalid_catalog_preserves_previous_assembly(self):
        original = self.assemble()
        entries = self.binding["examples"]
        invalid = [dict(self.binding, examples=entries * 2), {"version": 99, "examples": []},
                   dict(self.binding, examples=[dict(entries[0], path="../outside.py")]),
                   dict(self.binding, examples=[dict(entries[0], path="missing.py")]),
                   dict(self.binding, examples=[dict(entries[0], language="unknown")]),
                   dict(self.binding, examples=[dict(entries[0], status="maybe")])]
        with patch.dict(os.environ, {"OPENTLV_DOCS_LOCAL": "1"}):
            for value in invalid:
                with self.subTest(value=value):
                    self.write(self.component / "docs-examples.json", json.dumps(value))
                    with self.assertRaises(PluginError):
                        self.assemble()
                    self.assertEqual(original, (self.portal / "build/assembled/docs/index.md").read_text())

    def test_ignored_example_is_not_imported(self):
        with patch.dict(os.environ, {"OPENTLV_DOCS_LOCAL": "1"}):
            self.write(self.component / ".gitignore", "ignored/\n")
            self.write(self.component / "ignored/private.py", "not an example\n")
            self.binding["examples"][0]["path"] = "ignored/private.py"
            self.write(self.component / "docs-examples.json", json.dumps(self.binding))
            with self.assertRaisesRegex(PluginError, "tracked regular"):
                self.assemble()

    def test_duplicate_provider_and_ambiguous_results_fail(self):
        self.manifest["sources"][0]["examples"] = {"languages": ["c", "python"]}
        self.save_manifest()
        with self.assertRaisesRegex(PluginError, "multiple repositories"):
            self.assemble()
        del self.manifest["sources"][0]["examples"]
        self.result()
        self.manifest["sources"][1]["examples"]["results"] *= 2
        self.save_manifest()
        with self.assertRaisesRegex(PluginError, "duplicate result"):
            self.assemble()

    def test_invalid_verification_is_rejected(self):
        for changes in ({"component_commit": "main"}, {"result": "success"},
                        {"core_version": ""}, {"platform": ""}, {"evidence": "javascript:alert(1)"},
                        {"feature": "missing.feature"}):
            with self.subTest(changes=changes):
                self.result(**changes)
                with self.assertRaises(PluginError):
                    self.assemble()

    def test_source_symlink_cannot_escape_repository(self):
        link = self.component / "examples/link.py"
        try:
            link.symlink_to(self.core / "examples/roundtrip.c")
        except OSError:
            self.skipTest("Creating symlinks requires Windows developer mode or privileges")
        self.binding["examples"][0]["path"] = "examples/link.py"
        self.write(self.component / "docs-examples.json", json.dumps(self.binding))
        with patch.dict(os.environ, {"OPENTLV_DOCS_LOCAL": "1"}), self.assertRaises(PluginError):
            self.assemble()

    def test_code_fences_and_literal_markers_preserve_source(self):
        code = '# [literal](../../absent)\nprint("````")\n///\n' + SLOT
        with patch.dict(os.environ, {"OPENTLV_DOCS_LOCAL": "1"}):
            self.write(self.component / "examples/roundtrip.py", code)
            text = self.assemble()
            self.assertIn("`````python\n" + code.rstrip("\n") + "\n`````", text)
            _, source = assembly.assemble(self.portal)
            config = SimpleNamespace(config_file_path=str(self.portal / "mkdocs.yml"),
                                     repo_url="https://github.com/OpenTLV/opentlv-docs",
                                     extra={"core_source": source, "core_checkout": str(self.core)})
            page = SimpleNamespace(file=SimpleNamespace(src_uri="index.md"))
            with self.assertNoLogs("mkdocs.hooks.opentlv", level="WARNING"):
                rewritten = fixture.hooks.on_page_markdown(text, page, config, [])
            self.assertIn(code.rstrip("\n"), rewritten)
            code_html = '<pre><code>href="https://github.com/OpenTLV/opentlv/blob/' + self.sha + '/docs/index.md"</code></pre>'
            self.assertEqual(fixture.hooks.on_page_content(code_html, page, config, []), code_html)
            catalog = examples.Catalog(assembly.selected_sources(self.portal), assembly.git)
            literal = "````markdown\n" + SLOT + "````\n"
            self.assertEqual(catalog.transform(literal), literal)
            # Exercise Material's block parser with delimiter-looking code too.
            result = self.mkdocs()
            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
            html = (self.portal / "site/index.html").read_text(encoding="utf-8")
            self.assertIn('class="tabbed-set', html)
            self.assertIn("../../absent", html)

    def test_invalid_slots_and_fallback_without_catalogs(self):
        catalog = examples.Catalog(assembly.selected_sources(self.portal), assembly.git)
        for text in (SLOT + examples.END, "<!-- opentlv-examples: broken -->\n",
                     "<!-- opentlv-examples: Bad ID -->\n", SLOT.replace("Fallback native links.", SLOT)):
            with self.subTest(text=text), self.assertRaises(PluginError):
                catalog.transform(text)
        catalog.providers.clear()
        self.assertIn("Fallback native links.", catalog.transform(SLOT))


if __name__ == "__main__":
    unittest.main()
