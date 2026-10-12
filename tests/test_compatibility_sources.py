# SPDX-License-Identifier: MIT
# Copyright (c) 2026 Marek Cingel

"""Exercise imported selection through real Git checkouts, assembly and locks."""

from copy import deepcopy
import hashlib
import json
import os
import unittest
from unittest.mock import patch

from mkdocs.exceptions import PluginError

import test_examples
import test_portal as fixture

assembly = fixture.assembly


class CompatibilitySourceTests(unittest.TestCase):
    write = test_examples.ExampleTests.write
    git = test_examples.ExampleTests.git
    mkdocs = test_examples.ExampleTests.mkdocs
    component_git = test_examples.ExampleTests.component_git
    commit_component = test_examples.ExampleTests.commit_component
    save_manifest = test_examples.ExampleTests.save_manifest
    assemble = test_examples.ExampleTests.assemble

    def setUp(self):
        test_examples.ExampleTests.setUp(self)
        self.source = self.manifest["sources"][1]
        del self.source["revision"]
        self.source["compatibility"] = {"feed": "results.json", "sha256": "0" * 64,
                                        "platform": "linux-x86_64", "configuration": "default"}
        self.record = {
            "id": "python-2.3.0-core-0.7.1-linux-default",
            "component": {"repository": self.source["repository"], "version": "2.3.0", "commit": self.component_sha},
            "declared_core": ">=0.6.0,<0.8.0",
            "core": {"repository": self.manifest["sources"][0]["repository"], "version": "0.7.1", "commit": self.sha},
            "platform": "linux-x86_64", "configuration": "default", "build": "passed", "test": "passed",
            "evidence": "https://example.invalid/results/immutable-record",
            "features": [{"id": "fixed.roundtrip", "support": "supported", "examples": [
                {"language": "python", "path": "examples/roundtrip.py", "result": "passed"}]}],
        }
        self.feed = {"version": 1, "records": [self.record]}
        self.save_feed()

    def save_feed(self):
        raw = json.dumps(self.feed).encode("utf-8")
        (self.portal / "results.json").write_bytes(raw)
        self.source["compatibility"]["sha256"] = hashlib.sha256(raw).hexdigest()
        self.save_manifest()

    def lock(self):
        selected = [item for _, item in assembly.selected_sources(self.portal)]
        self.write(self.portal / "build/sources.lock.json", json.dumps({
            "manifest": self.manifest["sources"], "sources": selected,
        }))
        return selected

    def test_strict_site_displays_versions_and_scoped_evidence(self):
        result = self.mkdocs()
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        html = (self.portal / "site/index.html").read_text(encoding="utf-8")
        for text in ("2.3.0", "0.7.1", "Python source", "immutable-record"):
            self.assertIn(text, html)
        metadata = json.loads((self.portal / "site/source-revision.json").read_text())
        binding = metadata["sources"][1]
        self.assertEqual(binding["revision"], self.component_sha)
        self.assertEqual(binding["compatibility_result"]["record"], self.record)
        self.assertEqual(self.component_git("status", "--porcelain"), "")

    def test_newer_failed_release_does_not_replace_verified_release(self):
        newer = deepcopy(self.record)
        newer.update(id="newer-failed", test="failed")
        newer["component"].update(version="2.10.0", commit="e" * 40)
        self.feed["records"].append(newer)
        self.save_feed()
        selected = assembly.selected_sources(self.portal)[1][1]
        self.assertEqual(selected["commit"], self.component_sha)
        self.assertEqual(selected["compatibility_result"]["record"]["component"]["version"], "2.3.0")

    def test_missing_failed_untested_optional_omissions_render_without_binding(self):
        for state in ("missing", "failed", "untested"):
            with self.subTest(state=state):
                self.record["test"] = state if state != "missing" else "passed"
                self.feed["records"] = [] if state == "missing" else [self.record]
                self.save_feed()
                result = self.mkdocs()
                self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
                metadata = json.loads((self.portal / "site/source-revision.json").read_text())
                self.assertFalse(metadata["sources"][1]["included"])
                self.assertEqual(metadata["sources"][1]["compatibility_result"]["status"], state)
                html = (self.portal / "site/index.html").read_text(encoding="utf-8")
                self.assertNotIn("Python source", html)
                self.assertIn("Core source", html)
                self.assertIn("no verified compatible release", html)
                selected = self.lock()
                (self.portal / "results.json").unlink()
                with patch.dict(os.environ, {"OPENTLV_DOCS_LOCK": str(self.portal / "build/sources.lock.json")}):
                    self.assertEqual([item for _, item in assembly.selected_sources(self.portal)], selected)

    def test_required_missing_compatibility_is_an_error(self):
        self.source["required"] = True
        self.feed["records"] = []
        self.save_feed()
        with self.assertRaisesRegex(PluginError, "no verified compatible release: missing"):
            assembly.selected_sources(self.portal)

    def test_lock_replays_evidence_without_access_to_original_feed(self):
        selected = self.lock()
        (self.portal / "results.json").unlink()
        with patch.dict(os.environ, {"OPENTLV_DOCS_LOCK": str(self.portal / "build/sources.lock.json")}):
            self.assertEqual([item for _, item in assembly.selected_sources(self.portal)], selected)
            self.assertIn("Python source", self.assemble())

    def test_lock_rejects_mismatched_component_and_core_evidence(self):
        original = self.lock()
        for field in ("component", "core"):
            selected = deepcopy(original)
            selected[1]["compatibility_result"]["record"][field]["commit"] = "f" * 40
            self.write(self.portal / "build/sources.lock.json", json.dumps({
                "manifest": self.manifest["sources"], "sources": selected,
            }))
            with self.subTest(field=field), patch.dict(os.environ, {
                "OPENTLV_DOCS_LOCK": str(self.portal / "build/sources.lock.json"),
            }), self.assertRaisesRegex(PluginError, "compatibility"):
                assembly.selected_sources(self.portal)

    def test_changed_feed_digest_rejects_before_replacing_assembly(self):
        original = self.assemble()
        (self.portal / "results.json").write_text('{"version":1,"records":[]}', encoding="utf-8")
        with self.assertRaisesRegex(PluginError, "sha256"):
            self.assemble()
        self.assertEqual((self.portal / "build/assembled/docs/index.md").read_text(encoding="utf-8"), original)

    def test_core_can_follow_binding_in_manifest(self):
        self.manifest["sources"].reverse()
        self.save_manifest()
        self.assertEqual([item["id"] for _, item in assembly.selected_sources(self.portal)], ["python", "core"])
        self.assertIn("Python source", self.assemble())

    def test_fetch_imports_before_binding_checkout_and_locks_commit(self):
        self.manifest["sources"][0]["repository"] = self.core.as_uri()
        self.source["repository"] = self.component.as_uri()
        self.record["core"]["repository"] = self.core.as_uri()
        self.record["component"]["repository"] = self.component.as_uri()
        self.manifest["sources"].reverse()
        self.save_feed()
        lock = assembly.sources.fetch(self.portal, self.sha)
        self.assertEqual(lock["sources"][0]["commit"], self.component_sha)
        with patch.dict(os.environ, {
            "OPENTLV_DOCS_SOURCE_ROOT": str(self.portal / "build/sources"),
            "OPENTLV_DOCS_LOCK": str(self.portal / "build/sources.lock.json"),
        }):
            os.environ.pop("OPENTLV_CORE_DIR", None)
            self.assertEqual([item for _, item in assembly.selected_sources(self.portal)], lock["sources"])

    def test_invalid_selection_settings_do_not_silently_fall_back(self):
        original = deepcopy(self.source)
        changes = ({"revision": self.component_sha}, {"examples": {}},
                   {"examples": {"languages": ["python"], "results": []}})
        for change in changes:
            with self.subTest(change=change):
                self.manifest["sources"][1] = dict(original, **change)
                self.save_manifest()
                with self.assertRaises(PluginError):
                    assembly.selected_sources(self.portal)


if __name__ == "__main__":
    unittest.main()
