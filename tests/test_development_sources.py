# SPDX-License-Identifier: MIT
# Copyright (c) 2026 Marek Cingel

"""Keep verified development snapshots separate from stable release selection."""

from copy import deepcopy
import json
import os
import sys
import unittest
from unittest.mock import patch

from mkdocs.exceptions import PluginError

import test_compatibility_sources as fixture
from test_publication import ci

assembly = fixture.assembly


class DevelopmentSourceTests(unittest.TestCase):
    write = fixture.CompatibilitySourceTests.write
    git = fixture.CompatibilitySourceTests.git
    mkdocs = fixture.CompatibilitySourceTests.mkdocs
    component_git = fixture.CompatibilitySourceTests.component_git
    commit_component = fixture.CompatibilitySourceTests.commit_component
    save_manifest = fixture.CompatibilitySourceTests.save_manifest
    save_feed = fixture.CompatibilitySourceTests.save_feed
    assemble = fixture.CompatibilitySourceTests.assemble
    lock = fixture.CompatibilitySourceTests.lock

    def setUp(self):
        fixture.CompatibilitySourceTests.setUp(self)
        self.stable_sha = self.component_sha
        self.write(self.component / "examples/roundtrip.py", 'print("Development Python source")\n')
        self.binding["component_version"] = "main"
        self.write(self.component / "docs-examples.json", json.dumps(self.binding))
        self.commit_component()
        self.development_sha = self.component_git("rev-parse", "HEAD")
        self.record["channel"] = "release"
        self.development = deepcopy(self.record)
        self.development.update(id="python-main-exact-core", channel="development")
        self.development["component"].update(version="main", commit=self.development_sha)
        self.development["core"]["version"] = "main"
        self.feed = {"version": 2, "records": [self.record, self.development]}
        self.source["revision"] = self.development_sha
        self.save_feed()

    def test_development_uses_pinned_snapshot_and_exact_core_evidence(self):
        selected = assembly.selected_sources(self.portal)[1][1]
        self.assertEqual(selected["commit"], self.development_sha)
        self.assertEqual(selected["revision"], self.source["revision"])
        self.assertEqual(selected["compatibility_result"]["record"], self.development)
        self.assertEqual(selected["compatibility_result"]["schema_version"], 2)
        self.assertEqual(selected["compatibility_result"]["core"]["commit"], self.sha)
        self.assertIn("Development Python source", self.assemble())
        self.assertEqual(self.component_git("status", "--porcelain"), "")

    def test_development_lock_replays_v2_evidence_without_feed(self):
        selected = self.lock()
        (self.portal / "results.json").unlink()
        with patch.dict(os.environ, {"OPENTLV_DOCS_LOCK": str(self.portal / "build/sources.lock.json")}):
            self.assertEqual([item for _, item in assembly.selected_sources(self.portal)], selected)
            self.assertIn("Development Python source", self.assemble())
            changed = deepcopy(selected)
            changed[1]["compatibility_result"]["record"]["core"]["commit"] = "f" * 40
            self.write(self.portal / "build/sources.lock.json", json.dumps({
                "manifest": self.manifest["sources"], "sources": changed,
            }))
            with self.assertRaisesRegex(PluginError, "compatibility"):
                assembly.selected_sources(self.portal)

    def test_missing_exact_proof_omits_optional_and_rejects_required_snapshot(self):
        original = deepcopy(self.development)
        for mismatch in ("component", "core", "platform"):
            with self.subTest(mismatch=mismatch):
                self.development = deepcopy(original)
                if mismatch == "platform":
                    self.development["platform"] = "another-platform"
                else:
                    self.development[mismatch]["commit"] = "f" * 40
                self.feed["records"] = [self.record, self.development]
                self.source["required"] = False
                self.save_feed()
                selected = assembly.selected_sources(self.portal)[1][1]
                self.assertFalse(selected["included"])
                self.assertEqual(selected["compatibility_result"]["status"], "missing")
                self.assertIsNone(selected["compatibility_result"]["record"])
                self.source["required"] = True
                self.save_manifest()
                with self.assertRaisesRegex(PluginError, "no verified compatible .*missing"):
                    assembly.selected_sources(self.portal)

    def test_release_ignores_development_pin_and_selects_verified_stable_release(self):
        self.component_git("checkout", "--detach", self.stable_sha)
        before = (self.portal / "docs-sources.json").read_bytes()
        with patch.dict(os.environ, {"OPENTLV_DOCS_CHANNEL": "release"}):
            selected = assembly.selected_sources(self.portal)[1][1]
            self.assertEqual(selected["commit"], self.stable_sha)
            self.assertEqual(selected["revision"], self.stable_sha)
            self.assertEqual(selected["compatibility_result"]["record"], self.record)
            text = self.assemble()
        self.assertIn('print("Python source")', text)
        self.assertNotIn("Development Python source", text)
        self.assertEqual((self.portal / "docs-sources.json").read_bytes(), before)

    def test_release_never_uses_snapshot_when_stable_evidence_is_absent(self):
        self.feed["records"] = [self.development]
        self.save_feed()
        with patch.dict(os.environ, {"OPENTLV_DOCS_CHANNEL": "release"}):
            selected = assembly.selected_sources(self.portal)[1][1]
            self.assertFalse(selected["included"])
            self.assertEqual(selected["compatibility_result"]["status"], "missing")
            self.source["required"] = True
            self.save_manifest()
            with self.assertRaisesRegex(PluginError, "no verified compatible .*missing"):
                assembly.selected_sources(self.portal)

    def test_ci_fetch_keeps_release_channel_and_replays_stable_lock_offline(self):
        self.git("tag", "v0.7.1")
        selection = ci.select(self.manifest["sources"][0], "release", "v0.7.1")
        self.manifest["sources"][0]["repository"] = self.core.as_uri()
        self.source["repository"] = self.component.as_uri()
        for record in self.feed["records"]:
            record["core"]["repository"] = self.core.as_uri()
            record["component"]["repository"] = self.component.as_uri()
        self.save_feed()
        self.write(self.portal / "build/selection.json", json.dumps(selection))
        with patch.object(ci, "ROOT", self.portal), patch.object(sys, "argv", ["ci.py", "fetch"]), \
                patch.dict(os.environ, {"OPENTLV_DOCS_CHANNEL": "development"}):
            ci.main()
            self.assertEqual(os.environ["OPENTLV_DOCS_CHANNEL"], "release")
        selected = json.loads((self.portal / "build/selection.json").read_text(encoding="utf-8"))
        lock = json.loads((self.portal / "build/sources.lock.json").read_text(encoding="utf-8"))
        self.assertEqual(selected["channel"], "release")
        self.assertEqual(lock["channel"], "release")
        self.assertEqual(selected["commit"], self.sha)
        self.assertEqual(selected["sources"], lock["sources"])
        self.assertEqual(lock["manifest"][1]["revision"], self.development_sha)
        self.assertEqual(lock["sources"][1]["commit"], self.stable_sha)
        self.assertEqual(lock["sources"][1]["compatibility_result"]["schema_version"], 2)
        self.assertEqual(assembly.sources.git(self.portal / "build/sources/python", "rev-parse", "HEAD"),
                         self.stable_sha)
        (self.portal / "results.json").unlink()
        with patch.dict(os.environ, {
            "OPENTLV_DOCS_CHANNEL": "release", "OPENTLV_DOCS_SOURCE_ROOT": str(self.portal / "build/sources"),
            "OPENTLV_DOCS_LOCK": str(self.portal / "build/sources.lock.json"),
        }):
            os.environ.pop("OPENTLV_CORE_DIR", None)
            self.assertEqual([item for _, item in assembly.selected_sources(self.portal)], lock["sources"])
            os.environ.pop("OPENTLV_DOCS_CHANNEL")
            self.assertEqual([item for _, item in assembly.selected_sources(self.portal)], lock["sources"])
            os.environ["OPENTLV_DOCS_CHANNEL"] = "development"
            with self.assertRaisesRegex(PluginError, "channel"):
                assembly.selected_sources(self.portal)


if __name__ == "__main__":
    unittest.main()
