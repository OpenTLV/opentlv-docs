# SPDX-License-Identifier: MIT
# Copyright (c) 2026 Marek Cingel

"""Standalone Go navigation, links and ownership through locked assembly."""

import json
import os
import subprocess
import unittest
from unittest.mock import patch

from mkdocs.exceptions import PluginError

import test_portal as fixture
from test_publication import ci


class GoSourceTests(unittest.TestCase):
    write = fixture.PortalTests.write
    git = fixture.PortalTests.git
    mkdocs = fixture.PortalTests.mkdocs

    def setUp(self):
        fixture.PortalTests.setUp(self)
        self.go = self.base / "go with spaces"
        actual = json.loads((fixture.ROOT / "docs-sources.json").read_text())
        self.definition = next(item for item in actual["sources"] if item["id"] == "go")
        self.assertTrue(self.definition["required"])
        self.assertEqual(self.definition["mount"], "go")
        # Main notifications update the reviewed pin; no release receipt is trusted yet.
        self.assertEqual(self.definition["updates"],
                         {"mode": "documentation", "workflow": ".github/workflows/go-main.yml"})
        self.assertNotIn("publication", self.definition)
        for path in ci.nav_paths(self.definition["navigation"]["items"]):
            self.write(self.go / "docs" / path, "# Manual\n")
        self.write(self.go / "docs/guides/go.md", "# Go API\n\n## Install and integrate\n\n"
                   "[Core](https://github.com/OpenTLV/opentlv/blob/main/docs/index.md#home)\n\n"
                   "[Build](../development/go.md#manual) | "
                   "[Example](../../examples/quick_start/main.go)\n\n"
                   "[Issues](https://github.com/OpenTLV/opentlv-go/issues)\n")
        self.write(self.go / "examples/quick_start/main.go", "package main\nfunc main() {}\n")
        self.write(self.go / "reader_test.go", "package opentlv_test\n")
        self.write(self.go / "docs-examples.json", json.dumps({
            "version": 1, "component_version": "0.1.0-dev", "examples": [{
                "feature": "fixed.roundtrip", "language": "go", "status": "supported",
                "path": "examples/quick_start/main.go"}]}))
        self.go_git("init", "-b", "main")
        self.go_git("add", ".")
        self.go_git("-c", "user.name=Fixture", "-c", "user.email=fixture@example.invalid",
                      "-c", "commit.gpgsign=false", "commit", "-m", "Go docs")
        self.go_sha = self.go_git("rev-parse", "HEAD")
        self.write(self.core / "docs/index.md", "# Home\n\n"
                   "[Go](https://github.com/OpenTLV/opentlv-go/blob/main/docs/guides/go.md#install-and-integrate)\n\n"
                   "<!-- opentlv-examples: fixed.roundtrip -->\n"
                   "<!-- /opentlv-examples -->\n")
        self.git("add", ".")
        self.git("-c", "user.name=Fixture", "-c", "user.email=fixture@example.invalid",
                 "-c", "commit.gpgsign=false", "commit", "-m", "External Go guide")
        self.sha = self.git("rev-parse", "HEAD")
        self.manifest = json.loads((self.portal / "docs-sources.json").read_text())
        self.manifest["sources"][0].update(revision=self.sha, link_aliases=["main"])
        self.manifest["sources"].append(dict(self.definition, revision=self.go_sha))
        self.write(self.portal / "docs-sources.json", json.dumps(self.manifest))
        os.environ["OPENTLV_GO_DIR"] = str(self.go)

    def go_git(self, *args):
        return subprocess.check_output(["git", "-C", str(self.go), *args],
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
        api = (site / "go/guides/go/index.html").read_text(encoding="utf-8")
        self.assertIn('href="go/guides/go/#install-and-integrate"', home)
        self.assertIn("Component version: 0.1.0-dev", home)
        self.assertIn("Verified Core: not established", home)
        self.assertIn(f"https://github.com/OpenTLV/opentlv-go/blob/{self.go_sha}/"
                      "examples/quick_start/main.go", home)
        self.assertIn('href="../../../#home"', api)
        self.assertIn('href="../../development/go/#manual"', api)
        self.assertIn(f"https://github.com/OpenTLV/opentlv-go/blob/{self.go_sha}/"
                      "examples/quick_start/main.go", api)
        self.assertIn(f"https://github.com/OpenTLV/opentlv-go/edit/{self.go_sha}/docs/guides/go.md", api)
        self.assertIn('href="https://github.com/OpenTLV/opentlv-go/issues"', api)
        metadata = json.loads((site / "source-revision.json").read_text())
        self.assertEqual(metadata["commit"], self.sha)
        self.assertEqual(metadata["sources"], lock["sources"])
        owners = json.loads((self.portal / "build/assembled/owners.json").read_text())
        self.assertEqual(owners["go/guides/go.md"]["id"], "go")
        ci.check_navigation(self.portal / "build/assembled/docs",
                            (self.portal / "build/assembled/navigation.json").read_text())
        self.assertEqual(self.git("status", "--porcelain"), "")
        self.assertEqual(self.go_git("status", "--porcelain"), "")

    def test_wrong_revision_dirty_source_and_missing_example_fail(self):
        self.manifest["sources"][-1]["revision"] = self.sha
        self.write(self.portal / "docs-sources.json", json.dumps(self.manifest))
        with self.assertRaises(PluginError):
            fixture.assembly.selected_sources(self.portal)
        self.manifest["sources"][-1]["revision"] = self.go_sha
        self.write(self.portal / "docs-sources.json", json.dumps(self.manifest))
        (self.go / "examples/quick_start/main.go").unlink()
        with self.assertRaisesRegex(PluginError, "dirty"):
            fixture.assembly.selected_sources(self.portal)
        with patch.dict(os.environ, {"OPENTLV_DOCS_LOCAL": "1"}):
            with self.assertRaisesRegex(PluginError, "tracked regular file"):
                fixture.assembly.assemble(self.portal)

    def test_current_core_links_follow_go_and_archival_links_remain_original(self):
        from types import SimpleNamespace
        page = SimpleNamespace(file=SimpleNamespace(src_uri="guides/examples.md"))
        original = ("[Example](../../bindings/go/examples/quick_start/main.go)\n"
                    "[Test](../../bindings/go/tests/reader_test.go)\n"
                    "[Guide](go.md#install-and-integrate)\n"
                    "[Contract](../../bindings/go/README.md#document)\n")
        go = (self.go, dict(self.definition, commit=self.go_sha))
        rewritten = fixture.hooks.rewrite_source_links(
            original + "```md\n" + original + "```\n", page, self.core,
            {"id": "core"}, "https://github.com/OpenTLV/opentlv", self.sha, "docs", "guides", go=go)
        self.assertIn(f"opentlv-go/blob/{self.go_sha}/examples/quick_start/main.go", rewritten)
        self.assertIn(f"opentlv-go/blob/{self.go_sha}/reader_test.go", rewritten)
        self.assertIn("../go/guides/go.md#install-and-integrate", rewritten)
        self.assertIn("../go/implementation.md#document", rewritten)
        self.assertIn("```md\n" + original, rewritten)
        with self.assertRaisesRegex(PluginError, "missing source"):
            fixture.hooks.rewrite_source_links(
                "[Missing](../../bindings/go/examples/missing.go)", page, self.core,
                {"id": "core"}, "", self.sha, "docs", "guides", go=go)
        # Without the explicit current-page handoff, Core's relative links keep
        # their historical ownership. Absolute immutable links are never adapted.
        immutable = f"[Old](https://github.com/OpenTLV/opentlv/blob/{self.sha}/bindings/go/README.md)"
        self.assertEqual(fixture.hooks.rewrite_source_links(
            immutable, page, self.core, {"id": "core"}, "", self.sha, "docs", "guides", go=go), immutable)

    def test_missing_source_manual_and_anchor_fail(self):
        with patch.dict(os.environ, {"OPENTLV_GO_DIR": str(self.base / "absent")}):
            with self.assertRaisesRegex(PluginError, "explicitly selected"):
                fixture.assembly.assemble(self.portal)
        self.write(self.go / "docs/guides/go.md", "# Go API\n")
        with patch.dict(os.environ, {"OPENTLV_DOCS_LOCAL": "1"}):
            result = self.mkdocs()
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("install-and-integrate", result.stdout + result.stderr)
        (self.go / "docs/guides/go.md").unlink()
        with patch.dict(os.environ, {"OPENTLV_DOCS_LOCAL": "1"}):
            result = self.mkdocs()
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("guides/go.md", result.stdout + result.stderr)


if __name__ == "__main__":
    unittest.main()
