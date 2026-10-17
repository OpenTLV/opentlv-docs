# SPDX-License-Identifier: MIT
# Copyright (c) 2026 Marek Cingel

"""CLI extraction regression: Core has no CLI pages; the pinned CLI owns them."""

import json
import os
import subprocess
import unittest
from unittest.mock import patch

from mkdocs.exceptions import PluginError

import test_portal as fixture
from test_publication import ci


class CliSourceTests(unittest.TestCase):
    write = fixture.PortalTests.write
    git = fixture.PortalTests.git
    mkdocs = fixture.PortalTests.mkdocs

    def setUp(self):
        fixture.PortalTests.setUp(self)
        self.cli = self.base / "cli with spaces"
        self.write(self.cli / "docs/README.md", "# Command line\n\n## First inspection\n\n"
                   "[JSON](json-schema.md) | [Develop](development.md) | [Release](releases.md)\n")
        self.write(self.cli / "docs/json-schema.md", "# JSON schema\n\n[Commands](README.md#first-inspection)\n")
        self.write(self.cli / "docs/development.md", "# Development\n\n"
                   "[Repository](../README.md#cli-root) | [Tests](../tests/README.md#tests)\n")
        self.write(self.cli / "docs/releases.md", "# Releases\n")
        self.write(self.cli / "README.md", "# CLI root\n")
        self.write(self.cli / "tests/README.md", "# Tests\n")
        self.cli_git("init", "-b", "main")
        self.cli_git("add", ".")
        self.cli_git("-c", "user.name=Fixture", "-c", "user.email=fixture@example.invalid",
                     "-c", "commit.gpgsign=false", "commit", "-m", "CLI docs")
        self.cli_sha = self.cli_git("rev-parse", "HEAD")
        self.manifest = json.loads((self.portal / "docs-sources.json").read_text())
        actual = json.loads((fixture.ROOT / "docs-sources.json").read_text())
        cli = next(item for item in actual["sources"] if item["id"] == "cli")
        self.assertTrue(cli["required"])
        self.assertEqual(cli["mount"], "cli")
        self.manifest["sources"].append(dict(cli, revision=self.cli_sha))
        self.save_manifest()
        os.environ["OPENTLV_CLI_DIR"] = str(self.cli)
        self.assertFalse((self.core / "docs/cli").exists())

    def cli_git(self, *args):
        return subprocess.check_output(["git", "-C", str(self.cli), *args], stderr=subprocess.PIPE).decode().strip()

    def save_manifest(self):
        self.write(self.portal / "docs-sources.json", json.dumps(self.manifest))

    def home(self, content):
        self.write(self.core / "docs/index.md", "# Home\n\n" + content)
        self.git("add", ".")
        self.git("-c", "user.name=Fixture", "-c", "user.email=fixture@example.invalid",
                 "-c", "commit.gpgsign=false", "commit", "-m", "Core links")
        self.sha = self.git("rev-parse", "HEAD")
        self.manifest["sources"][0]["revision"] = self.sha
        self.save_manifest()

    def test_locked_strict_build_cli_navigation_links_and_provenance(self):
        base = "https://github.com/OpenTLV/opentlv-cli/blob"
        self.home(f"[Inspect]({base}/main/docs/README.md#first-inspection)\n\n"
                  f"[JSON][json]\n\n[json]: {base}/main/docs/json-schema.md#json-schema\n\n"
                  f'<a href="{base}/main/docs/development.md?view=portal#development">Develop</a>\n\n'
                  f"[Exact]({base}/{self.cli_sha}/docs/releases.md#releases)\n\n"
                  f"[Historical]({base}/{'b' * 40}/docs/README.md)\n\n"
                  f"[Other ref]({base}/next/docs/README.md)\n\n"
                  f"[Repository]({base}/main/README.md)\n\n"
                  "[Other repository](https://github.com/Elsewhere/cli/blob/main/docs/README.md)\n\n"
                  f"```markdown\n[Example]({base}/main/docs/missing.md)\n```\n")
        selected = fixture.assembly.selected_sources(self.portal)
        lock = {"manifest": self.manifest["sources"], "sources": [item for _, item in selected]}
        path = self.portal / "build/sources.lock.json"
        self.write(path, json.dumps(lock))
        with patch.dict(os.environ, {"OPENTLV_DOCS_LOCK": str(path), "OPENTLV_DOCS_PUBLISH": "1"}):
            result = self.mkdocs()
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        site = self.portal / "site"
        home = (site / "index.html").read_text(encoding="utf-8")
        for target in ("cli/#first-inspection", "cli/json-schema/#json-schema",
                       "cli/development/?view=portal#development", "cli/releases/#releases"):
            self.assertIn(f'href="{target}"', home)
        for target in (f"{base}/{'b' * 40}/docs/README.md", f"{base}/next/docs/README.md",
                       f"{base}/main/README.md", f"{base}/main/docs/missing.md",
                       "https://github.com/Elsewhere/cli/blob/main/docs/README.md"):
            self.assertIn(target, home)
        cli_html = (site / "cli/index.html").read_text(encoding="utf-8")
        self.assertIn(f"https://github.com/OpenTLV/opentlv-cli/edit/{self.cli_sha}/docs/README.md", cli_html)
        dev = (site / "cli/development/index.html").read_text(encoding="utf-8")
        self.assertIn(f"{base}/{self.cli_sha}/README.md#cli-root", dev)
        self.assertIn(f"{base}/{self.cli_sha}/tests/README.md#tests", dev)
        schema = (site / "cli/json-schema/index.html").read_text(encoding="utf-8")
        self.assertIn('href="../#first-inspection"', schema)
        metadata = json.loads((site / "source-revision.json").read_text())
        self.assertEqual(metadata["sources"], lock["sources"])
        self.assertEqual([item["commit"] for item in metadata["sources"]], [self.sha, self.cli_sha])
        self.assertEqual(metadata["sources"][1]["link_aliases"], ["main"])
        owners = json.loads((self.portal / "build/assembled/owners.json").read_text())
        self.assertEqual(owners["cli/README.md"]["id"], "cli")
        self.assertEqual(owners["cli/README.md"]["path"], "docs/README.md")
        ci.check_navigation(self.portal / "build/assembled/docs",
                            (self.portal / "build/assembled/navigation.json").read_text())
        self.assertEqual(self.git("status", "--porcelain"), "")
        self.assertEqual(self.cli_git("status", "--porcelain"), "")

    def test_alias_links_reject_missing_pages_and_anchors(self):
        for target in ("missing.md", "README.md#missing"):
            with self.subTest(target=target):
                self.home(f"[Broken](https://github.com/OpenTLV/opentlv-cli/blob/main/docs/{target})\n")
                result = self.mkdocs()
                self.assertNotEqual(result.returncode, 0, result.stdout + result.stderr)

    def test_required_cli_missing_and_legacy_core_collision_fail(self):
        with patch.dict(os.environ, {"OPENTLV_CLI_DIR": str(self.base / "absent")}):
            with self.assertRaisesRegex(PluginError, "explicitly selected"):
                fixture.assembly.assemble(self.portal)
        self.write(self.core / "docs/cli/README.md", "# Old Core CLI\n")
        with patch.dict(os.environ, {"OPENTLV_DOCS_LOCAL": "1"}):
            with self.assertRaisesRegex(PluginError, "collision"):
                fixture.assembly.assemble(self.portal)

    def test_alias_validation_and_lock_mismatch(self):
        for aliases in ("main", [], ["main", "main"], ["../outside"], ["a" * 40], [1], ["bad\nref"]):
            with self.subTest(aliases=aliases):
                self.manifest["sources"][1]["link_aliases"] = aliases
                self.save_manifest()
                with self.assertRaises(PluginError):
                    fixture.assembly.sources.manifest(self.portal)
        self.manifest["sources"][1]["link_aliases"] = ["main"]
        self.save_manifest()
        selected = fixture.assembly.selected_sources(self.portal)
        path = self.portal / "build/sources.lock.json"
        self.write(path, json.dumps({"manifest": self.manifest["sources"],
                                    "sources": [item for _, item in selected]}))
        self.manifest["sources"][1]["link_aliases"] = ["next"]
        self.save_manifest()
        with patch.dict(os.environ, {"OPENTLV_DOCS_LOCK": str(path)}):
            with self.assertRaisesRegex(PluginError, "lock does not match"):
                fixture.assembly.selected_sources(self.portal)


if __name__ == "__main__":
    unittest.main()
