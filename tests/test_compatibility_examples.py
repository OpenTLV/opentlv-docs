# SPDX-License-Identifier: MIT
# Copyright (c) 2026 Marek Cingel

"""Automatic examples require evidence for the selected release and source file."""

from copy import deepcopy
import json
import unittest

from mkdocs.exceptions import PluginError

import test_examples as fixture

assembly = fixture.assembly
examples = fixture.examples


class CompatibilityExampleTests(unittest.TestCase):
    write = fixture.ExampleTests.write
    git = fixture.ExampleTests.git
    component_git = fixture.ExampleTests.component_git
    commit_component = fixture.ExampleTests.commit_component
    save_manifest = fixture.ExampleTests.save_manifest

    def setUp(self):
        fixture.ExampleTests.setUp(self)
        self.selected = assembly.selected_sources(self.portal)
        self.item = self.selected[1][1]
        self.item["compatibility"] = {"feed": "results.json", "sha256": "a" * 64,
                                      "platform": "linux-x86_64", "configuration": "default"}
        self.record = {
            "id": "python-2.3.0-linux",
            "component": {"repository": self.item["repository"], "version": "v2.3.0", "commit": self.component_sha},
            "declared_core": ">=0.7.0,<0.8.0",
            "core": {"repository": self.selected[0][1]["repository"], "version": "0.7.1", "commit": self.sha},
            "platform": "linux-x86_64", "configuration": "default", "build": "passed", "test": "passed",
            "evidence": "https://example.invalid/results/python-2.3.0-linux",
            "features": [{"id": "fixed.roundtrip", "support": "supported", "examples": [
                {"language": "python", "path": "examples/roundtrip.py", "result": "passed"}]}],
        }
        self.item["compatibility_result"] = {
            "status": "verified", "feed": {"source": "results.json", "sha256": "a" * 64},
            "core": deepcopy(self.record["core"]), "platform": "linux-x86_64",
            "configuration": "default", "record": self.record,
        }

    def render(self):
        return examples.Catalog(self.selected, assembly.git).transform(fixture.SLOT)

    def assert_withheld(self, expected):
        text = self.render()
        self.assertIn(expected, text)
        self.assertNotIn('print("Python source")', text)
        self.assertNotIn("/examples/roundtrip.py)", text)
        return text

    def test_selected_version_scope_and_declared_dependency_are_separate(self):
        text = self.render()
        self.assertIn("Component version: v2.3.0", text)
        self.assertIn("Selected Core: 0.7.1 (" + self.sha, text)
        self.assertIn("Declared Core dependency: &gt;=0.7.0,&lt;0.8.0", text)
        self.assertIn("Verified Core: 0.7.1 (" + self.sha, text)
        self.assertIn("Platform: linux-x86", text)
        self.assertIn("configuration: default", text)
        self.assertIn("[Verification evidence](https://example.invalid/results/python-2.3.0-linux)", text)
        self.assertIn("/blob/" + self.component_sha + "/examples/roundtrip.py", text)
        self.assertIn('print("Python source")', text)

    def test_no_selected_release_distinguishes_missing_failed_and_untested(self):
        self.item["included"] = False
        del self.item["revision"]
        for status, message in (("missing", "no compatibility result supplied"),
                                ("failed", "compatibility build or tests failed"),
                                ("untested", "has not passed both build and tests")):
            with self.subTest(status=status):
                self.item["compatibility_result"]["status"] = status
                self.item["compatibility_result"]["record"] = None if status == "missing" else self.record
                text = self.assert_withheld(message)
                self.assertIn("Component version: none selected", text)
                self.assertIn("Selected revision: none selected", text)
                self.assertNotIn("Repository unavailable", text)
                self.assertNotIn("Verified Core: 0.7.1", text)

    def test_missing_result_does_not_reuse_manual_examples(self):
        del self.item["compatibility_result"]
        self.assert_withheld("no compatibility result supplied")

    def test_matching_scope_and_both_clean_commits_are_required(self):
        baseline = deepcopy(self.selected)
        cases = ((0, "local", True), (1, "local", True), (0, "dirty", True), (1, "dirty", True),
                 (0, "commit", "f" * 40), (1, "commit", "f" * 40), (1, "revision", "f" * 40))
        for index, key, value in cases:
            with self.subTest(index=index, key=key):
                self.selected = deepcopy(baseline)
                self.selected[index][1][key] = value
                self.assert_withheld("result does not match this checkout or local preview")
        for key, value in (("platform", "windows"), ("configuration", "other"),
                           ("build", "failed"), ("test", "untested")):
            with self.subTest(field=key):
                self.selected = deepcopy(baseline)
                self.selected[1][1]["compatibility_result"]["record"][key] = value
                self.assert_withheld("result does not match this checkout or local preview")
        for key in ("component", "core"):
            with self.subTest(repository=key):
                self.selected = deepcopy(baseline)
                self.selected[1][1]["compatibility_result"]["record"][key]["repository"] = "https://example.invalid/other"
                self.assert_withheld("result does not match this checkout or local preview")

    def test_local_preview_keeps_edited_version_and_selected_release_provenance(self):
        self.item["local"] = True
        self.item["dirty"] = True
        self.binding["component_version"] = "2.4.0"
        self.write(self.component / "docs-examples.json", json.dumps(self.binding))
        text = self.assert_withheld("result does not match this checkout or local preview")
        self.assertIn("Component version: 2.4.0", text)
        self.assertIn("Selected release: v2.3.0 (" + self.component_sha, text)
        self.assertIn("[Verification evidence](", text)
        self.assertNotIn("Verified Core: 0.7.1", text)

    def test_stale_record_cannot_label_selected_core_version(self):
        self.record["core"]["commit"] = "f" * 40
        self.item["compatibility_result"]["core"] = deepcopy(self.record["core"])
        text = self.assert_withheld("result does not match this checkout")
        self.assertIn("Selected Core: version unknown (" + self.sha, text)
        self.assertNotIn("Selected Core: 0.7.1", text)

    def test_feature_unknown_unsupported_and_missing_are_distinct(self):
        feature = self.record["features"][0]
        for support, message in (("unknown", "Feature support is unknown"),
                                 ("unsupported", "Unsupported: this feature")):
            with self.subTest(support=support):
                feature["support"] = support
                self.assert_withheld(message)
        self.record["features"] = []
        self.assert_withheld("Feature support is unknown")

    def test_general_test_success_does_not_verify_unlisted_examples(self):
        self.record["features"][0]["examples"] = []
        self.assert_withheld("No verification result for this example")

    def test_evidence_must_match_example_path_and_language(self):
        proof = self.record["features"][0]["examples"][0]
        for key, value in (("path", "examples/other.py"), ("language", "cpp")):
            with self.subTest(field=key):
                original = proof[key]
                proof[key] = value
                self.assert_withheld("No verification result for this example")
                proof[key] = original

    def test_failed_and_untested_examples_remain_hidden_with_verified_binding(self):
        for result in ("failed", "untested"):
            with self.subTest(result=result):
                self.record["features"][0]["examples"][0]["result"] = result
                self.assert_withheld("Example test result: " + result)

    def test_missing_and_unsupported_owner_catalog_entries_remain_distinct(self):
        self.binding["examples"] = []
        self.write(self.component / "docs-examples.json", json.dumps(self.binding))
        self.assert_withheld("No example supplied for this feature")
        self.binding["examples"] = [{"feature": "fixed.roundtrip", "language": "python",
                                     "status": "unsupported", "reason": "Unavailable in this facade."}]
        self.write(self.component / "docs-examples.json", json.dumps(self.binding))
        self.assert_withheld("Unsupported: Unavailable in this facade.")

    def test_owner_version_cannot_conflict_with_selected_release(self):
        self.binding["component_version"] = "2.4.0"
        self.write(self.component / "docs-examples.json", json.dumps(self.binding))
        with self.assertRaisesRegex(PluginError, "catalog component version does not match"):
            self.render()
        del self.binding["component_version"]
        self.write(self.component / "docs-examples.json", json.dumps(self.binding))
        self.assertIn("Component version: v2.3.0", self.render())

    def test_automatic_sources_require_languages_and_reject_inline_results(self):
        self.item["examples"] = {}
        with self.assertRaisesRegex(PluginError, "explicit example languages"):
            self.render()
        self.item["examples"] = {"languages": ["python"], "results": []}
        with self.assertRaisesRegex(PluginError, "cannot use inline example results"):
            self.render()


if __name__ == "__main__":
    unittest.main()
