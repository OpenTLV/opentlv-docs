# SPDX-License-Identifier: MIT
# Copyright (c) 2026 Marek Cingel

"""Standalone JS navigation, links and ownership through locked assembly."""

import json
import os
import subprocess
import unittest
from unittest.mock import patch

from mkdocs.exceptions import PluginError

import test_portal as fixture
from test_publication import ci


class JSSourceTests(unittest.TestCase):
    write = fixture.PortalTests.write
    git = fixture.PortalTests.git
    mkdocs = fixture.PortalTests.mkdocs

    def setUp(self):
        fixture.PortalTests.setUp(self)
        self.js = self.base / "js with spaces"
        actual = json.loads((fixture.ROOT / "docs-sources.json").read_text())
        self.definition = next(item for item in actual["sources"] if item["id"] == "js")
        self.assertTrue(self.definition["required"])
        self.assertEqual(self.definition["mount"], "js")
        # Main notifications update the reviewed pin; no release receipt is trusted yet.
        self.assertEqual(self.definition["updates"],
                         {"mode": "documentation", "workflow": ".github/workflows/js-main.yml"})
        self.assertNotIn("publication", self.definition)
        for path in ci.nav_paths(self.definition["navigation"]["items"]):
            self.write(self.js / "docs" / path, "# Manual\n")
        self.write(self.js / "docs/webassembly.md", "# JS API\n\n## Build\n\n"
                   "[Core](https://github.com/OpenTLV/opentlv/blob/main/docs/index.md#home)\n\n"
                   "[Build](packaging.md#manual) | "
                   "[Example](../examples/parse.mjs)\n\n"
                   "[Issues](https://github.com/OpenTLV/opentlv-js/issues)\n")
        self.write(self.js / "examples/parse.mjs", 'console.log("parse fixture");\n')
        self.write(self.js / "smoke.mjs", "// smoke fixture\n")
        self.write(self.js / "docs-examples.json", json.dumps({
            "version": 1, "component_version": "0.1.0-dev.0", "examples": [{
                "feature": "ber.parse", "language": "js", "status": "supported",
                "path": "examples/parse.mjs"}]}))
        self.js_git("init", "-b", "main")
        self.js_git("add", ".")
        self.js_git("-c", "user.name=Fixture", "-c", "user.email=fixture@example.invalid",
                      "-c", "commit.gpgsign=false", "commit", "-m", "JS docs")
        self.js_sha = self.js_git("rev-parse", "HEAD")
        self.write(self.core / "docs/index.md", "# Home\n\n"
                   "[JS](https://github.com/OpenTLV/opentlv-js/blob/main/docs/webassembly.md#build)\n\n"
                   "<!-- opentlv-examples: ber.parse -->\n"
                   "<!-- /opentlv-examples -->\n")
        self.git("add", ".")
        self.git("-c", "user.name=Fixture", "-c", "user.email=fixture@example.invalid",
                 "-c", "commit.gpgsign=false", "commit", "-m", "External JS guide")
        self.sha = self.git("rev-parse", "HEAD")
        self.manifest = json.loads((self.portal / "docs-sources.json").read_text())
        self.manifest["sources"][0].update(revision=self.sha, link_aliases=["main"])
        self.manifest["sources"].append(dict(self.definition, revision=self.js_sha))
        self.write(self.portal / "docs-sources.json", json.dumps(self.manifest))
        os.environ["OPENTLV_JS_DIR"] = str(self.js)

    def js_git(self, *args):
        return subprocess.check_output(["git", "-C", str(self.js), *args],
                                       stderr=subprocess.PIPE).decode().strip()

    def test_locked_build_links_navigation_and_provenance(self):
        selected = fixture.assembly.selected_sources(self.portal)
        lock = {"manifest": self.manifest["sources"], "sources": [item for _, item in selected]}
        lock_path = self.portal / "build/sources.lock.json"
        self.write(lock_path, json.dumps(lock))
        with patch.dict(os.environ, {"OPENTLV_DOCS_LOCK": str(lock_path), "OPENTLV_DOCS_PUBLISH": "1"}):
            result = self.mkdocs()
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        site = self.portal / "site"
        home = (site / "index.html").read_text(encoding="utf-8")
        api = (site / "js/webassembly/index.html").read_text(encoding="utf-8")
        self.assertIn('href="js/webassembly/#build"', home)
        self.assertIn("Component version: 0.1.0-dev.0", home)
        self.assertIn("Verified Core: not established", home)
        self.assertIn(f"https://github.com/OpenTLV/opentlv-js/blob/{self.js_sha}/"
                      "examples/parse.mjs", home)
        self.assertIn('href="../../#home"', api)
        self.assertIn('href="../packaging/#manual"', api)
        self.assertIn(f"https://github.com/OpenTLV/opentlv-js/blob/{self.js_sha}/"
                      "examples/parse.mjs", api)
        self.assertIn(f"https://github.com/OpenTLV/opentlv-js/edit/{self.js_sha}/docs/webassembly.md", api)
        self.assertIn('href="https://github.com/OpenTLV/opentlv-js/issues"', api)
        metadata = json.loads((site / "source-revision.json").read_text())
        self.assertEqual(metadata["commit"], self.sha)
        self.assertEqual(metadata["sources"], lock["sources"])
        owners = json.loads((self.portal / "build/assembled/owners.json").read_text())
        self.assertEqual(owners["js/webassembly.md"]["id"], "js")
        ci.check_navigation(self.portal / "build/assembled/docs",
                            (self.portal / "build/assembled/navigation.json").read_text())
        self.assertEqual(self.git("status", "--porcelain"), "")
        self.assertEqual(self.js_git("status", "--porcelain"), "")

    def test_wrong_revision_dirty_source_and_missing_example_fail(self):
        self.manifest["sources"][-1]["revision"] = self.sha
        self.write(self.portal / "docs-sources.json", json.dumps(self.manifest))
        with self.assertRaises(PluginError):
            fixture.assembly.selected_sources(self.portal)
        self.manifest["sources"][-1]["revision"] = self.js_sha
        self.write(self.portal / "docs-sources.json", json.dumps(self.manifest))
        (self.js / "examples/parse.mjs").unlink()
        with self.assertRaisesRegex(PluginError, "dirty"):
            fixture.assembly.selected_sources(self.portal)
        with patch.dict(os.environ, {"OPENTLV_DOCS_LOCAL": "1"}):
            with self.assertRaisesRegex(PluginError, "tracked regular file"):
                fixture.assembly.assemble(self.portal)

    def test_current_core_links_follow_js_and_archival_links_remain_original(self):
        from types import SimpleNamespace
        page = SimpleNamespace(file=SimpleNamespace(src_uri="guides/examples.md"))
        original = ("[Example](../../bindings/wasm/examples/parse.mjs)\n"
                    "[Guide](../development/webassembly.md#build)\n")
        source = (self.js, dict(self.definition, commit=self.js_sha))
        rewritten = fixture.hooks.rewrite_source_links(
            original + "```md\n" + original + "```\n", page, self.core,
            {"id": "core"}, "https://github.com/OpenTLV/opentlv", self.sha, "docs", "guides", js_source=source)
        self.assertIn(f"opentlv-js/blob/{self.js_sha}/examples/parse.mjs", rewritten)
        self.assertIn("../js/webassembly.md#build", rewritten)
        self.assertIn("```md\n" + original, rewritten)
        with self.assertRaisesRegex(PluginError, "missing source"):
            fixture.hooks.rewrite_source_links(
                "[Missing](../../bindings/wasm/examples/missing.mjs)", page, self.core,
                {"id": "core"}, "", self.sha, "docs", "guides", js_source=source)
        immutable = f"[Old](https://github.com/OpenTLV/opentlv/blob/{self.sha}/bindings/wasm/examples/parse.mjs)"
        self.assertEqual(fixture.hooks.rewrite_source_links(
            immutable, page, self.core, {"id": "core"}, "", self.sha, "docs", "guides", js_source=source), immutable)
        archived = fixture.hooks.rewrite_source_links(
            original, page, self.core, {"id": "core"}, "https://github.com/OpenTLV/opentlv",
            self.sha, "docs", "guides")
        self.assertIn("/bindings/wasm/examples/parse.mjs", archived)
        self.assertIn("../development/webassembly.md#build", archived)

    def test_only_exact_clean_bootstrap_can_omit_new_manual(self):
        definition = dict(self.definition, commit=fixture.assembly.js.BOOTSTRAP_COMMIT,
                          included=True, local=False)
        core = (self.core, dict(self.manifest["sources"][0], commit=self.sha, included=True))
        def paths(item):
            return ci.nav_paths(fixture.assembly.navigation([], [core, (self.js, item)]))
        self.assertNotIn("js/webassembly.md", paths(definition))
        for change in ({"commit": "f" * 40}, {"local": True},
                       {"repository": "https://github.com/another/js"}):
            with self.subTest(change=change):
                self.assertIn("js/webassembly.md", paths(dict(definition, **change)))

    def test_missing_source_manual_and_anchor_fail(self):
        with patch.dict(os.environ, {"OPENTLV_JS_DIR": str(self.base / "absent")}):
            with self.assertRaisesRegex(PluginError, "explicitly selected"):
                fixture.assembly.assemble(self.portal)
        self.write(self.js / "docs/webassembly.md", "# JS API\n")
        with patch.dict(os.environ, {"OPENTLV_DOCS_LOCAL": "1"}):
            result = self.mkdocs()
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("build", result.stdout + result.stderr)
        (self.js / "docs/webassembly.md").unlink()
        with patch.dict(os.environ, {"OPENTLV_DOCS_LOCAL": "1"}):
            result = self.mkdocs()
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("webassembly.md", result.stdout + result.stderr)


if __name__ == "__main__":
    unittest.main()
