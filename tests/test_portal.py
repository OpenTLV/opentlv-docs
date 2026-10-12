# SPDX-License-Identifier: MIT
# Copyright (c) 2026 Marek Cingel

"""Behavioral checks using disposable Git repositories, never the user's Core."""

import importlib.util
import json
import os
from pathlib import Path
import socket
import subprocess
import sys
import tempfile
import time
from types import SimpleNamespace
import unittest
from unittest.mock import patch
from urllib.error import URLError
from urllib.request import urlopen

from mkdocs.exceptions import PluginError

ROOT = Path(__file__).resolve().parents[1]


def load_hook(name):
    spec = importlib.util.spec_from_file_location(name, ROOT / "tools" / "docs" / f"{name}.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


assembly = load_hook("assembly")
hooks = load_hook("hooks")


class PortalTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.base = Path(self.temp.name).resolve()
        self.core = self.base / "core with spaces"
        self.portal = self.base / "portal"
        self.write(self.core / "docs/index.md", "# Home\n\n[Source](../LICENSE)\n")
        self.write(self.core / "docs/README.md", "# GitHub index\n")
        self.write(self.core / "docs/assets/README.md", "# Old asset page\n")
        self.write(self.core / "LICENSE", "Core license\n")
        self.write(self.core / ".gitignore", "ignored/\n")
        self.git("init", "-b", "main")
        self.git("add", ".")
        self.git("-c", "user.name=Fixture", "-c", "user.email=fixture@example.invalid",
                 "-c", "commit.gpgsign=false", "commit", "-m", "Test fixture")
        self.sha = self.git("rev-parse", "HEAD")
        self.git("tag", "v1")
        self.git("-c", "user.name=Fixture", "-c", "user.email=fixture@example.invalid",
                 "-c", "tag.gpgsign=false", "tag", "-a", "v1-annotated", "-m", "Fixture release")
        self.write(self.portal / "core-source.json", json.dumps({
            "repository": "https://github.com/OpenTLV/opentlv", "revision": self.sha,
        }))
        self.write(self.portal / "docs/assets/README.md", "# Assets\n\n[License](../../LICENSE)\n")
        self.write(self.portal / "LICENSE", "Portal license\n")
        for tree in ("c-api", "cxx-api"):
            self.write(self.portal / f"build/api/docs/{tree}/html/index.html", "<html>Fixture</html>")
        clean_env = {key: value for key, value in os.environ.items() if not key.startswith("OPENTLV_")}
        clean_env["OPENTLV_CORE_DIR"] = str(self.core)
        self.env = patch.dict(os.environ, clean_env, clear=True)
        self.env.start()
        self.addCleanup(self.env.stop)

    def write(self, path, text):
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(text, encoding="utf-8")

    def git(self, *args):
        return subprocess.check_output(["git", "-C", str(self.core), *args], stderr=subprocess.PIPE).decode().strip()

    def config(self):
        root, source = assembly.assemble(self.portal)
        return SimpleNamespace(
            config_file_path=str(self.portal / "mkdocs.yml"),
            repo_url="https://github.com/OpenTLV/opentlv-docs",
            extra={"core_source": source, "core_checkout": str(root)},
        )

    def test_clean_assembly_preserves_core_and_overlays_portal_assets(self):
        before = self.git("status", "--porcelain")
        root, source = assembly.assemble(self.portal)
        self.assertEqual(root, self.core)
        self.assertEqual(source["commit"], self.sha)
        self.assertFalse(source["local"] or source["dirty"])
        docs = self.portal / "build/assembled/docs"
        self.assertEqual((docs / "index.md").read_bytes(), (self.core / "docs/index.md").read_bytes())
        self.assertIn("# Assets", (docs / "assets/README.md").read_text())
        self.assertIn("# Old asset page", (self.core / "docs/assets/README.md").read_text())
        self.assertEqual(self.git("status", "--porcelain"), before)
        self.write(docs / "stale.md", "stale")
        assembly.assemble(self.portal)
        self.assertFalse((docs / "stale.md").exists())

    def test_tag_and_annotated_tag_resolve_to_commit(self):
        for tag in ("v1", "v1-annotated"):
            with self.subTest(tag=tag), patch.dict(os.environ, {"OPENTLV_CORE_REF": tag}):
                self.assertEqual(assembly.selected_source(self.portal)[1]["commit"], self.sha)

    def test_branch_short_sha_and_unknown_revision_rejected(self):
        for ref in ("main", self.sha[:8], "missing-tag", "v1^", "v1~0"):
            with self.subTest(ref=ref), patch.dict(os.environ, {"OPENTLV_CORE_REF": ref}):
                with self.assertRaises(PluginError):
                    assembly.selected_source(self.portal)

    def test_wrong_checkout_revision_rejected_even_in_local_mode(self):
        self.write(self.core / "LICENSE", "changed")
        self.git("add", "LICENSE")
        self.git("-c", "user.name=Fixture", "-c", "user.email=fixture@example.invalid",
                 "-c", "commit.gpgsign=false", "commit", "-m", "New fixture revision")
        with patch.dict(os.environ, {"OPENTLV_DOCS_LOCAL": "1"}):
            with self.assertRaisesRegex(PluginError, "HEAD does not match"):
                assembly.selected_source(self.portal)

    def test_dirty_and_untracked_sources_rejected_by_default(self):
        self.write(self.core / "docs/new.md", "# New page")
        with self.assertRaisesRegex(PluginError, "dirty"):
            assembly.selected_source(self.portal)
        (self.core / "docs/new.md").unlink()
        self.write(self.core / "docs/index.md", "# Modified")
        with self.assertRaisesRegex(PluginError, "dirty"):
            assembly.selected_source(self.portal)

    def test_local_preview_includes_changes_additions_and_deletions(self):
        self.write(self.core / "docs/index.md", "# Modified")
        self.write(self.core / "docs/new.md", "# New")
        (self.core / "docs/README.md").unlink()
        self.write(self.core / "docs/ignored/debris.md", "not a source")
        with patch.dict(os.environ, {"OPENTLV_DOCS_LOCAL": "1"}):
            _, source = assembly.assemble(self.portal)
        self.assertTrue(source["local"] and source["dirty"])
        docs = self.portal / "build/assembled/docs"
        self.assertEqual((docs / "index.md").read_text(), "# Modified")
        self.assertTrue((docs / "new.md").exists())
        self.assertFalse((docs / "README.md").exists())
        self.assertFalse((docs / "ignored/debris.md").exists())

    def test_source_and_edit_links_use_owning_repository(self):
        config = self.config()
        page = SimpleNamespace(file=SimpleNamespace(src_uri="index.md"))
        result = hooks.on_page_markdown("[Source](../LICENSE?raw=1#license)", page, config, [])
        self.assertEqual(result, f"[Source](https://github.com/OpenTLV/opentlv/blob/{self.sha}/LICENSE?raw=1#license)")
        self.assertEqual(page.edit_url, f"https://github.com/OpenTLV/opentlv/edit/{self.sha}/docs/index.md")
        page.file.src_uri = "assets/README.md"
        result = hooks.on_page_markdown("[License](../../LICENSE)", page, config, [])
        self.assertEqual(result, "[License](https://github.com/OpenTLV/opentlv-docs/blob/main/LICENSE)")
        self.assertEqual(page.edit_url, "https://github.com/OpenTLV/opentlv-docs/edit/main/docs/assets/README.md")

    def test_index_rewrite_preserves_fragment_and_other_links(self):
        config = self.config()
        page = SimpleNamespace(file=SimpleNamespace(src_uri="guides/reader.md"))
        self.assertEqual(hooks.on_page_markdown("[Home](../README.md#home)", page, config, []),
                         "[Home](../index.md#home)")
        text = "[Other](writer.md) [Remote](https://example.com/) ![Image](../image.svg)"
        self.assertEqual(hooks.on_page_markdown(text, page, config, []), text)

    def test_missing_source_link_warns(self):
        config = self.config()
        page = SimpleNamespace(file=SimpleNamespace(src_uri="index.md"))
        with self.assertLogs("mkdocs.hooks.opentlv", level="WARNING"):
            hooks.on_page_markdown("[Missing](../missing.c)", page, config, [])

    def mkdocs(self):
        self.write(self.portal / "mkdocs.yml", f"""site_name: Fixture
docs_dir: docs
strict: true
repo_url: https://github.com/OpenTLV/opentlv-docs
theme:
  name: material
  custom_dir: '{(ROOT / 'tools/docs/overrides').as_posix()}'
  features:
    - content.action.edit
extra:
  docs_channel: development
exclude_docs: /README.md
validation:
  nav:
    omitted_files: warn
  links:
    anchors: warn
hooks:
  - '{(ROOT / 'tools/docs/assembly.py').as_posix()}'
  - '{(ROOT / 'tools/docs/hooks.py').as_posix()}'
nav:
  - Home: index.md
  - Assets: assets/README.md
""")
        return subprocess.run([sys.executable, "-m", "mkdocs", "build", "--strict"],
                              cwd=self.portal, capture_output=True, text=True, encoding="utf-8", errors="replace")

    def test_strict_build_and_published_provenance_without_optional_components(self):
        result = self.mkdocs()
        self.assertEqual(result.returncode, 0, result.stderr)
        site = self.portal / "site"
        source = json.loads((site / "source-revision.json").read_text())
        self.assertEqual(source["commit"], self.sha)
        self.assertNotIn(str(self.core), json.dumps(source))
        html = (site / "index.html").read_text(encoding="utf-8")
        self.assertIn(f"/edit/{self.sha}/docs/index.md", html)
        self.assertIn("development", html)
        self.assertTrue((site / "reference/api/cxx-api/html/index.html").exists())

    def test_local_preview_banner_overrides_release_channel(self):
        with patch.dict(os.environ, {"OPENTLV_DOCS_LOCAL": "1", "OPENTLV_DOCS_CHANNEL": "release"}):
            result = self.mkdocs()
        self.assertEqual(result.returncode, 0, result.stderr)
        html = (self.portal / "site/index.html").read_text(encoding="utf-8")
        self.assertIn("Local preview", html)

    def test_missing_api_reference_fails_build(self):
        (self.portal / "build/api/docs/cxx-api/html/index.html").unlink()
        result = self.mkdocs()
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("generated API reference not found", result.stdout + result.stderr)

    def test_explicitly_required_wasm_fails_when_missing(self):
        with patch.dict(os.environ, {"OPENTLV_DOCS_REQUIRE_WASM": "1"}):
            result = self.mkdocs()
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("WebAssembly module files", result.stdout + result.stderr)

    def test_strict_build_rejects_broken_links_and_missing_anchors(self):
        for text in ("[Missing](missing.md)", "[Source](../missing.c)", "[Anchor](#missing)"):
            with self.subTest(text=text):
                self.write(self.core / "docs/index.md", f"# Home\n\n{text}\n")
                with patch.dict(os.environ, {"OPENTLV_DOCS_LOCAL": "1"}):
                    result = self.mkdocs()
                self.assertNotEqual(result.returncode, 0, result.stderr)
                self.assertIn("WARNING", result.stderr)

    def test_live_preview_reassembles_inputs_without_rebuild_loop(self):
        result = self.mkdocs()  # Write config and verify the initial input.
        self.assertEqual(result.returncode, 0, result.stderr)
        with socket.socket() as sock:
            sock.bind(("127.0.0.1", 0))
            port = sock.getsockname()[1]
        url = f"http://127.0.0.1:{port}/"
        log_path = self.base / "serve.log"
        env = dict(os.environ, OPENTLV_DOCS_LOCAL="1", PYTHONIOENCODING="utf-8")
        with log_path.open("w", encoding="utf-8") as log:
            process = subprocess.Popen(
                [sys.executable, "-m", "mkdocs", "serve", "--dev-addr", f"127.0.0.1:{port}"],
                cwd=self.portal, env=env, stdout=log, stderr=subprocess.STDOUT,
                creationflags=subprocess.CREATE_NO_WINDOW if os.name == "nt" else 0,
            )
            try:
                def wait_for(text):
                    deadline = time.monotonic() + 20
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

                wait_for("Local preview")
                self.write(self.core / "docs/index.md", "# Updated live preview\n")
                wait_for("Updated live preview")
                time.sleep(1)
                built = log_path.read_text(encoding="utf-8").count("Documentation built in")
                time.sleep(2)
                self.assertEqual(log_path.read_text(encoding="utf-8").count("Documentation built in"), built)
            finally:
                process.terminate()
                process.wait(timeout=10)


if __name__ == "__main__":
    unittest.main()
