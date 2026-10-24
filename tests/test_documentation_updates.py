# SPDX-License-Identifier: MIT
# Copyright (c) 2026 Marek Cingel
"""Trusted documentation pin updates do not claim runtime compatibility evidence."""

import base64
import copy
import json
from pathlib import Path
import sys
import tempfile
import unittest
from urllib.error import HTTPError

from mkdocs.exceptions import PluginError
import yaml

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools/docs"))
import events
import sources


class DocumentationUpdatesTests(unittest.TestCase):
    source = "python"

    def setUp(self):
        self.manifest = json.loads((ROOT / "docs-sources.json").read_text())
        self.repository = "OpenTLV/opentlv-" + self.source
        self.item = next(item for item in self.manifest["sources"] if item["id"] == self.source)
        self.item["revision"] = "b" * 40
        self.payload = {"source": self.source, "repository": self.repository,
                        "commit": "a" * 40, "ref": "main", "run_id": 123}
        self.event = {"action": "component-docs-updated", "client_payload": self.payload}
        self.run = {"status": "completed", "conclusion": "success", "event": "push",
                    "head_sha": "a" * 40, "head_branch": "main",
                    "path": ".github/workflows/" + self.source + "-main.yml",
                    "head_repository": {"full_name": self.repository}}
        self.pending = None
        self.calls = []
        self.relations = {}

    def api(self, path):
        self.calls.append(path)
        if path.startswith("OpenTLV/opentlv-docs/contents/"):
            if self.pending is None:
                raise HTTPError(path, 404, "No pending branch", {}, None)
            return {"encoding": "base64", "content": base64.b64encode(json.dumps(
                {"sources": [self.pending]}).encode()).decode()}
        self.assertTrue(path.startswith(self.repository + "/"), path)
        if "/actions/runs/" in path:
            return self.run
        if "/git/ref/heads/main" in path:
            return {"object": {"type": "commit", "sha": "d" * 40}}
        if "/compare/" in path:
            return {"status": self.relations.get(path.split("/compare/")[1], "ahead")}
        self.fail("Unexpected API call (no compatibility artifacts should be consumed): " + path)

    def propose(self):
        return events.proposal(self.event, self.manifest, self.api)

    def test_only_source_revision_changes_and_replay_after_merge_is_noop(self):
        expected = copy.deepcopy(self.manifest)
        next(item for item in expected["sources"] if item["id"] == self.source)["revision"] = "a" * 40
        self.assertEqual(self.propose(), expected)
        self.assertEqual(self.item["revision"], "b" * 40)
        self.manifest = expected
        self.assertEqual(self.propose(), expected)
        self.assertFalse(any("/artifacts" in path or "/releases" in path for path in self.calls))

    def test_duplicate_or_older_pending_notification_does_not_rewrite_proposal(self):
        for sha in ("a" * 40, "c" * 40):
            self.pending = dict(self.item, revision=sha)
            self.relations["c" * 40 + "..." + "a" * 40] = "behind"
            self.assertEqual(self.propose(), self.manifest)

    def test_newer_notification_advances_pending_proposal(self):
        self.pending = dict(self.item, revision="c" * 40)
        proposed = self.propose()
        self.assertEqual(next(item for item in proposed["sources"] if item["id"] == self.source)["revision"],
                         self.payload["commit"])

    def test_old_merged_pin_cannot_regress_and_divergence_fails(self):
        key = "b" * 40 + "..." + "a" * 40
        self.relations[key] = "behind"
        self.assertEqual(self.propose(), self.manifest)
        self.relations[key] = "diverged"
        with self.assertRaisesRegex(ValueError, "diverged"):
            self.propose()

    def test_untrusted_runs_and_fork_pr_or_incomplete_runs_are_rejected(self):
        original = self.run
        for change in ({"conclusion": "failure"}, {"status": "in_progress"}, {"event": "pull_request"},
                       {"head_sha": "f" * 40}, {"head_branch": "feature"},
                       {"path": ".github/workflows/other.yml"},
                       {"head_repository": {"full_name": "attacker/fork"}}):
            with self.subTest(change=change):
                self.run = dict(original, **change)
                with self.assertRaisesRegex(ValueError, "trusted push"):
                    self.propose()

    def test_event_kind_release_payload_and_unconfigured_sources_are_rejected(self):
        for kind in ("component-docs-released", "core-docs-updated", "unknown"):
            self.event["action"] = kind
            with self.assertRaisesRegex(ValueError, "component-docs-updated"):
                self.propose()
        self.event["action"] = "component-docs-updated"
        self.payload["ref"] = "v0.1.0"
        with self.assertRaisesRegex(ValueError, "require main"):
            self.propose()
        self.payload["ref"] = "main"
        del self.item["updates"]
        with self.assertRaisesRegex(ValueError, "evidence artifact"):
            self.propose()

    def test_rejects_wrong_repository_and_commit_outside_main_history(self):
        self.payload["repository"] = "attacker/fork"
        with self.assertRaisesRegex(ValueError, "configured source"):
            self.propose()
        self.payload["repository"] = self.repository
        self.relations["a" * 40 + "..." + "d" * 40] = "diverged"
        with self.assertRaisesRegex(ValueError, "current main history"):
            self.propose()

    def test_pending_lookup_authentication_failure_is_not_ignored(self):
        def api(path):
            if "/contents/" in path:
                raise HTTPError(path, 403, "Forbidden", {}, None)
            return self.api(path)
        with self.assertRaises(HTTPError):
            events.proposal(self.event, self.manifest, api)

    def test_manifest_explicitly_opts_in_and_rejects_ambiguous_policies(self):
        with tempfile.TemporaryDirectory() as folder:
            portal = Path(folder)
            def validate():
                (portal / "docs-sources.json").write_text(json.dumps(self.manifest))
                return sources.manifest(portal)
            self.assertTrue(validate())
            original = copy.deepcopy(self.item)
            for updates in ({"mode": "documentation"}, {"mode": "typo", "workflow": self.run["path"]},
                            {"mode": "documentation", "workflow": "../evil.py"},
                            {**original["updates"], "development_artifact": "fake"},
                            {**original["updates"], "asset": "fake.json"}):
                self.item["updates"] = updates
                with self.assertRaises(PluginError):
                    validate()
            self.item["updates"] = original["updates"]
            self.item["compatibility"] = {}
            with self.assertRaisesRegex(PluginError, "non-compatibility"):
                validate()

    def test_notification_does_not_trigger_docs_full_or_publication(self):
        release = yaml.load((ROOT / ".github/workflows/docs-release.yml").read_text(), Loader=yaml.BaseLoader)
        self.assertNotIn("component-docs-updated", release["on"]["repository_dispatch"]["types"])
        update = yaml.load((ROOT / ".github/workflows/component-updates.yml").read_text(), Loader=yaml.BaseLoader)
        self.assertIn("component-docs-updated", update["on"]["repository_dispatch"]["types"])
        self.assertNotIn("docs-full.yml", json.dumps(update))
        self.assertNotIn("deploy-pages", json.dumps(update))


class LuaDocumentationUpdatesTests(DocumentationUpdatesTests):
    source = "lua"


class RustDocumentationUpdatesTests(DocumentationUpdatesTests):
    source = "rust"


class GoDocumentationUpdatesTests(DocumentationUpdatesTests):
    source = "go"


class JSDocumentationUpdatesTests(DocumentationUpdatesTests):
    source = "js"


if __name__ == "__main__":
    unittest.main()
