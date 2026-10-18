# SPDX-License-Identifier: MIT
# Copyright (c) 2026 Marek Cingel

"""Standalone Lua manuals retain their owner through locked portal assembly."""

import json
import os
import subprocess
import unittest
from unittest.mock import patch

from mkdocs.exceptions import PluginError

import test_portal as fixture
from test_publication import ci


class LuaSourceTests(unittest.TestCase):
    write = fixture.PortalTests.write
    git = fixture.PortalTests.git
    mkdocs = fixture.PortalTests.mkdocs

    def setUp(self):
        fixture.PortalTests.setUp(self)
        self.lua = self.base / "lua with spaces"
        actual = json.loads((fixture.ROOT / "docs-sources.json").read_text())
        self.definition = next(item for item in actual["sources"] if item["id"] == "lua")
        self.assertTrue(self.definition["required"])
        self.assertEqual(self.definition["mount"], "lua")
        for path in ci.nav_paths(self.definition["navigation"]["items"]):
            self.write(self.lua / "docs" / path, "# Manual\n")
        self.write(self.lua / "docs/api.md", "# Lua API\n\n## Structural schemas\n\n"
                   "[Core](https://github.com/OpenTLV/opentlv/blob/main/docs/index.md#home)\n\n"
                   "[Build](development.md#manual) | [Example](../examples/quick_start.lua)\n")
        self.write(self.lua / "examples/quick_start.lua", 'print("example")\n')
        self.write(self.lua / "provenance/original-readme.md", "# Historical\n\nOld build instructions.\n")
        self.write(self.lua / "docs/migration.md", "# Provenance\n\n"
                   "[Historical README](../provenance/original-readme.md)\n")
        self.lua_git("init", "-b", "main")
        self.lua_git("add", ".")
        self.lua_git("-c", "user.name=Fixture", "-c", "user.email=fixture@example.invalid",
                     "-c", "commit.gpgsign=false", "commit", "-m", "Lua docs")
        self.lua_sha = self.lua_git("rev-parse", "HEAD")
        self.write(self.core / "docs/index.md", "# Home\n\n"
                   "[Lua schemas](https://github.com/OpenTLV/opentlv-lua/blob/main/docs/api.md#structural-schemas)\n")
        self.git("add", ".")
        self.git("-c", "user.name=Fixture", "-c", "user.email=fixture@example.invalid",
                 "-c", "commit.gpgsign=false", "commit", "-m", "External Lua guide")
        self.sha = self.git("rev-parse", "HEAD")
        self.manifest = json.loads((self.portal / "docs-sources.json").read_text())
        self.manifest["sources"][0].update(revision=self.sha, link_aliases=["main"])
        self.manifest["sources"].append(dict(self.definition, revision=self.lua_sha))
        self.write(self.portal / "docs-sources.json", json.dumps(self.manifest))
        os.environ["OPENTLV_LUA_DIR"] = str(self.lua)

    def lua_git(self, *args):
        return subprocess.check_output(["git", "-C", str(self.lua), *args],
                                       stderr=subprocess.PIPE).decode().strip()

    def test_locked_strict_build_bidirectional_links_and_ownership(self):
        selected = fixture.assembly.selected_sources(self.portal)
        lock = {"manifest": self.manifest["sources"], "sources": [item for _, item in selected]}
        lock_path = self.portal / "build/sources.lock.json"
        self.write(lock_path, json.dumps(lock))
        with patch.dict(os.environ, {"OPENTLV_DOCS_LOCK": str(lock_path), "OPENTLV_DOCS_PUBLISH": "1"}):
            result = self.mkdocs()
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        site = self.portal / "site"
        home = (site / "index.html").read_text(encoding="utf-8")
        api = (site / "lua/api/index.html").read_text(encoding="utf-8")
        self.assertIn('href="lua/api/#structural-schemas"', home)
        self.assertIn('href="../../#home"', api)
        self.assertIn('href="../development/#manual"', api)
        self.assertIn(f"https://github.com/OpenTLV/opentlv-lua/blob/{self.lua_sha}/examples/quick_start.lua", api)
        self.assertIn(f"https://github.com/OpenTLV/opentlv-lua/edit/{self.lua_sha}/docs/api.md", api)
        self.assertFalse((site / "lua/provenance/original-readme/index.html").exists())
        history = (site / "lua/migration/index.html").read_text(encoding="utf-8")
        self.assertIn(f"https://github.com/OpenTLV/opentlv-lua/blob/{self.lua_sha}/provenance/original-readme.md", history)
        metadata = json.loads((site / "source-revision.json").read_text())
        self.assertEqual(metadata["commit"], self.sha)
        self.assertEqual(metadata["sources"], lock["sources"])
        owners = json.loads((self.portal / "build/assembled/owners.json").read_text())
        self.assertEqual(owners["lua/api.md"]["id"], "lua")
        self.assertNotIn("guides/lua.md", owners)
        self.assertNotIn("development/lua.md", owners)
        ci.check_navigation(self.portal / "build/assembled/docs",
                            (self.portal / "build/assembled/navigation.json").read_text())
        self.assertEqual(self.git("status", "--porcelain"), "")
        self.assertEqual(self.lua_git("status", "--porcelain"), "")

    def test_required_lua_and_missing_migrated_manual_fail_closed(self):
        with patch.dict(os.environ, {"OPENTLV_LUA_DIR": str(self.base / "absent")}):
            with self.assertRaisesRegex(PluginError, "explicitly selected"):
                fixture.assembly.assemble(self.portal)
        (self.lua / "docs/api.md").unlink()
        with patch.dict(os.environ, {"OPENTLV_DOCS_LOCAL": "1"}):
            result = self.mkdocs()
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("api.md", result.stdout + result.stderr)

    def test_missing_lua_anchor_fails_strict_build(self):
        self.write(self.lua / "docs/api.md", "# Lua API\n")
        with patch.dict(os.environ, {"OPENTLV_DOCS_LOCAL": "1"}):
            result = self.mkdocs()
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("structural-schemas", result.stdout + result.stderr)


if __name__ == "__main__":
    unittest.main()
