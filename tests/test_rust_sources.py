# SPDX-License-Identifier: MIT
# Copyright (c) 2026 Marek Cingel

"""Standalone Rust navigation, links and ownership through locked assembly."""

import json
import os
import subprocess
import unittest
from unittest.mock import patch

from mkdocs.exceptions import PluginError

import test_portal as fixture
from test_publication import ci


class RustSourceTests(unittest.TestCase):
    write = fixture.PortalTests.write
    git = fixture.PortalTests.git
    mkdocs = fixture.PortalTests.mkdocs

    def setUp(self):
        fixture.PortalTests.setUp(self)
        self.rust = self.base / "rust with spaces"
        actual = json.loads((fixture.ROOT / "docs-sources.json").read_text())
        self.definition = next(item for item in actual["sources"] if item["id"] == "rust")
        self.assertTrue(self.definition["required"])
        self.assertEqual(self.definition["mount"], "rust")
        # Main notifications update the reviewed pin; no release receipt is trusted yet.
        self.assertEqual(self.definition["updates"],
                         {"mode": "documentation", "workflow": ".github/workflows/rust-main.yml"})
        self.assertNotIn("publication", self.definition)
        for path in ci.nav_paths(self.definition["navigation"]["items"]):
            self.write(self.rust / "docs" / path, "# Manual\n")
        self.write(self.rust / "docs/guides/rust.md", "# Rust API\n\n## Cargo setup\n\n"
                   "[Core](https://github.com/OpenTLV/opentlv/blob/main/docs/index.md#home)\n\n"
                   "[Build](../development/rust.md#manual) | "
                   "[Example](../../opentlv/examples/quick_start.rs)\n\n"
                   "[Issues](https://github.com/OpenTLV/opentlv-rust/issues)\n")
        self.write(self.rust / "opentlv/examples/quick_start.rs", "fn main() {}\n")
        self.rust_git("init", "-b", "main")
        self.rust_git("add", ".")
        self.rust_git("-c", "user.name=Fixture", "-c", "user.email=fixture@example.invalid",
                      "-c", "commit.gpgsign=false", "commit", "-m", "Rust docs")
        self.rust_sha = self.rust_git("rev-parse", "HEAD")
        self.write(self.core / "docs/index.md", "# Home\n\n"
                   "[Rust](https://github.com/OpenTLV/opentlv-rust/blob/main/docs/guides/rust.md#cargo-setup)\n")
        self.git("add", ".")
        self.git("-c", "user.name=Fixture", "-c", "user.email=fixture@example.invalid",
                 "-c", "commit.gpgsign=false", "commit", "-m", "External Rust guide")
        self.sha = self.git("rev-parse", "HEAD")
        self.manifest = json.loads((self.portal / "docs-sources.json").read_text())
        self.manifest["sources"][0].update(revision=self.sha, link_aliases=["main"])
        self.manifest["sources"].append(dict(self.definition, revision=self.rust_sha))
        self.write(self.portal / "docs-sources.json", json.dumps(self.manifest))
        os.environ["OPENTLV_RUST_DIR"] = str(self.rust)

    def rust_git(self, *args):
        return subprocess.check_output(["git", "-C", str(self.rust), *args],
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
        api = (site / "rust/guides/rust/index.html").read_text(encoding="utf-8")
        self.assertIn('href="rust/guides/rust/#cargo-setup"', home)
        self.assertIn('href="../../../#home"', api)
        self.assertIn('href="../../development/rust/#manual"', api)
        self.assertIn(f"https://github.com/OpenTLV/opentlv-rust/blob/{self.rust_sha}/"
                      "opentlv/examples/quick_start.rs", api)
        self.assertIn(f"https://github.com/OpenTLV/opentlv-rust/edit/{self.rust_sha}/docs/guides/rust.md", api)
        self.assertIn('href="https://github.com/OpenTLV/opentlv-rust/issues"', api)
        metadata = json.loads((site / "source-revision.json").read_text())
        self.assertEqual(metadata["commit"], self.sha)
        self.assertEqual(metadata["sources"], lock["sources"])
        owners = json.loads((self.portal / "build/assembled/owners.json").read_text())
        self.assertEqual(owners["rust/guides/rust.md"]["id"], "rust")
        ci.check_navigation(self.portal / "build/assembled/docs",
                            (self.portal / "build/assembled/navigation.json").read_text())
        self.assertEqual(self.git("status", "--porcelain"), "")
        self.assertEqual(self.rust_git("status", "--porcelain"), "")

    def test_missing_source_manual_and_anchor_fail(self):
        with patch.dict(os.environ, {"OPENTLV_RUST_DIR": str(self.base / "absent")}):
            with self.assertRaisesRegex(PluginError, "explicitly selected"):
                fixture.assembly.assemble(self.portal)
        self.write(self.rust / "docs/guides/rust.md", "# Rust API\n")
        with patch.dict(os.environ, {"OPENTLV_DOCS_LOCAL": "1"}):
            result = self.mkdocs()
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("cargo-setup", result.stdout + result.stderr)
        (self.rust / "docs/guides/rust.md").unlink()
        with patch.dict(os.environ, {"OPENTLV_DOCS_LOCAL": "1"}):
            result = self.mkdocs()
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("guides/rust.md", result.stdout + result.stderr)


if __name__ == "__main__":
    unittest.main()
