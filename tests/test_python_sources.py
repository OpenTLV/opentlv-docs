# SPDX-License-Identifier: MIT
# Copyright (c) 2026 Marek Cingel

"""Standalone Python navigation, links and ownership through locked assembly."""

import json
import os
import subprocess
import unittest
from unittest.mock import patch

from mkdocs.exceptions import PluginError

import test_portal as fixture
from test_publication import ci


class PythonSourceTests(unittest.TestCase):
    write = fixture.PortalTests.write
    git = fixture.PortalTests.git
    mkdocs = fixture.PortalTests.mkdocs

    def setUp(self):
        fixture.PortalTests.setUp(self)
        self.python = self.base / "python with spaces"
        actual = json.loads((fixture.ROOT / "docs-sources.json").read_text())
        self.definition = next(item for item in actual["sources"] if item["id"] == "python")
        self.assertTrue(self.definition["required"])
        self.assertEqual(self.definition["mount"], "python")
        for path in ci.nav_paths(self.definition["navigation"]["items"]):
            self.write(self.python / "docs" / path, "# Manual\n")
        self.write(self.python / "docs/guides/python.md", "# Python API\n\n## Setup\n\n"
                   "[Core](https://github.com/OpenTLV/opentlv/blob/main/docs/index.md#home)\n\n"
                   "[Build](../development/python.md#manual) | "
                   "[Example](../../bindings/python/opentlv/examples/quick_start.py)\n\n"
                   "[Issues](https://github.com/OpenTLV/opentlv-python/issues)\n")
        self.write(self.python / "bindings/python/opentlv/examples/quick_start.py", 'print("example")\n')
        self.python_git("init", "-b", "main")
        self.python_git("add", ".")
        self.python_git("-c", "user.name=Fixture", "-c", "user.email=fixture@example.invalid",
                        "-c", "commit.gpgsign=false", "commit", "-m", "Python docs")
        self.python_sha = self.python_git("rev-parse", "HEAD")
        self.write(self.core / "docs/index.md", "# Home\n\n"
                   "[Python](https://github.com/OpenTLV/opentlv-python/blob/main/docs/guides/python.md#setup)\n")
        self.git("add", ".")
        self.git("-c", "user.name=Fixture", "-c", "user.email=fixture@example.invalid",
                 "-c", "commit.gpgsign=false", "commit", "-m", "External Python guide")
        self.sha = self.git("rev-parse", "HEAD")
        self.manifest = json.loads((self.portal / "docs-sources.json").read_text())
        self.manifest["sources"][0].update(revision=self.sha, link_aliases=["main"])
        self.manifest["sources"].append(dict(self.definition, revision=self.python_sha))
        self.write(self.portal / "docs-sources.json", json.dumps(self.manifest))
        os.environ["OPENTLV_PYTHON_DIR"] = str(self.python)

    def python_git(self, *args):
        return subprocess.check_output(["git", "-C", str(self.python), *args],
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
        api = (site / "python/guides/python/index.html").read_text(encoding="utf-8")
        self.assertIn('href="python/guides/python/#setup"', home)
        self.assertIn('href="../../../#home"', api)
        self.assertIn('href="../../development/python/#manual"', api)
        self.assertIn(f"https://github.com/OpenTLV/opentlv-python/blob/{self.python_sha}/"
                      "bindings/python/opentlv/examples/quick_start.py", api)
        self.assertIn(f"https://github.com/OpenTLV/opentlv-python/edit/{self.python_sha}/docs/guides/python.md", api)
        self.assertIn('href="https://github.com/OpenTLV/opentlv-python/issues"', api)
        metadata = json.loads((site / "source-revision.json").read_text())
        self.assertEqual(metadata["commit"], self.sha)
        self.assertEqual(metadata["sources"], lock["sources"])
        owners = json.loads((self.portal / "build/assembled/owners.json").read_text())
        self.assertEqual(owners["python/guides/python.md"]["id"], "python")
        ci.check_navigation(self.portal / "build/assembled/docs",
                            (self.portal / "build/assembled/navigation.json").read_text())
        self.assertEqual(self.git("status", "--porcelain"), "")
        self.assertEqual(self.python_git("status", "--porcelain"), "")

    def test_missing_source_manual_and_anchor_fail(self):
        with patch.dict(os.environ, {"OPENTLV_PYTHON_DIR": str(self.base / "absent")}):
            with self.assertRaisesRegex(PluginError, "explicitly selected"):
                fixture.assembly.assemble(self.portal)
        self.write(self.python / "docs/guides/python.md", "# Python API\n")
        with patch.dict(os.environ, {"OPENTLV_DOCS_LOCAL": "1"}):
            result = self.mkdocs()
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("setup", result.stdout + result.stderr)
        (self.python / "docs/guides/python.md").unlink()
        with patch.dict(os.environ, {"OPENTLV_DOCS_LOCAL": "1"}):
            result = self.mkdocs()
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("guides/python.md", result.stdout + result.stderr)


if __name__ == "__main__":
    unittest.main()
