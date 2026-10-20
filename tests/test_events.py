# SPDX-License-Identifier: MIT
# Copyright (c) 2026 Marek Cingel

import copy
import base64
import hashlib
import json
import os
import sys
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "tools/docs"))
import events
import ci


class EventTests(unittest.TestCase):
    def setUp(self):
        self.sha = "a" * 40
        self.item = {"id": "core", "repository": "https://github.com/OpenTLV/opentlv"}
        self.payload = {"source": "core", "repository": "OpenTLV/opentlv", "commit": self.sha,
                        "ref": "main", "run_id": 123}
        self.run = {"conclusion": "success", "status": "completed", "event": "push",
                    "head_sha": self.sha, "head_branch": "main", "path": ".github/workflows/wasm.yml",
                    "head_repository": {"full_name": "OpenTLV/opentlv"}}
        self.target = {"object": {"type": "commit", "sha": self.sha}}
        self.relation = "identical"

    def api(self, path):
        self.assertTrue(path.startswith(self.payload["repository"] + "/"))
        if "/actions/runs/" in path:
            return self.run
        if "/git/ref/" in path:
            return self.target
        if "/git/tags/" in path:
            return {"object": {"type": "commit", "sha": self.sha}}
        if "/compare/" in path:
            return {"status": self.relation}
        if "/releases/tags/" in path:
            return self.release
        self.fail(path)

    def validate(self):
        return events.validate(self.payload, [self.item], self.api)

    def test_successful_core_main_and_annotated_release(self):
        self.assertEqual(self.validate(), self.item)
        self.payload["ref"] = self.run["head_branch"] = "v1.2.3"
        self.target = {"object": {"type": "tag", "sha": "b" * 40}}
        self.assertEqual(self.validate(), self.item)

    def test_core_proposal_pins_sha_and_replays_without_regression(self):
        self.item["revision"] = "b" * 40
        manifest = {"version": 1, "sources": [self.item]}
        self.relation = "ahead"
        proposed = events.core_proposal(self.payload, manifest, self.api)
        self.assertEqual(proposed["sources"][0]["revision"], self.sha)
        self.assertEqual(manifest["sources"][0]["revision"], "b" * 40)
        self.assertEqual(events.core_proposal(self.payload, proposed, self.api), proposed)
        self.item["revision"] = "c" * 40
        def late_api(path):
            return {"status": "behind"} if f"/compare/{'c' * 40}..." in path else self.api(path)
        self.assertEqual(events.core_proposal(self.payload, manifest, late_api), manifest)

    def test_core_proposal_rejects_release_events(self):
        self.payload["ref"] = self.run["head_branch"] = "1.2.3"
        with self.assertRaisesRegex(ValueError, "main development"):
            events.core_proposal(self.payload, {"sources": [self.item]}, self.api)

    def test_delayed_event_cannot_regress_pending_unmerged_source_proposal(self):
        pending = {"sources": [dict(self.item, revision="c" * 40)]}
        def api(path):
            if "/contents/" in path:
                return {"encoding": "base64", "content": base64.b64encode(json.dumps(pending).encode()).decode()}
            if "/compare/" + "c" * 40 in path:
                return {"status": "behind"}
            return self.api(path)
        self.assertTrue(events.pending_is_newer(self.payload, {"sources": [self.item]}, api))
        pending["sources"][0]["revision"] = self.sha
        self.assertFalse(events.pending_is_newer(self.payload, {"sources": [self.item]}, api))

    def test_missing_pending_branch_is_allowed_but_authentication_failure_is_not(self):
        from urllib.error import HTTPError
        for code in (404, 403, 500):
            def api(path):
                if "/contents/" in path:
                    raise HTTPError(path, code, "fixture", {}, None)
                return self.api(path)
            if code == 404:
                self.assertFalse(events.pending_is_newer(self.payload, {"sources": [self.item]}, api))
            else:
                with self.assertRaises(HTTPError):
                    events.pending_is_newer(self.payload, {"sources": [self.item]}, api)

    def test_core_proposal_resolves_existing_lightweight_and_annotated_tag_pins(self):
        self.item["revision"] = "v1.2.3"
        for kind in ("commit", "tag"):
            self.target = {"object": {"type": kind, "sha": self.sha}}
            proposed = events.core_proposal(self.payload, {"sources": [self.item]}, self.api)
            self.assertEqual(proposed["sources"][0]["revision"], self.sha)
        with self.assertRaisesRegex(ValueError, "resolve to a full commit"):
            events.resolve_revision("OpenTLV/opentlv", "v1.2.3",
                                    lambda _: {"object": {"type": "tag", "sha": self.sha}})

    def test_rejects_untrusted_failed_fork_and_pr_workflows(self):
        original = copy.deepcopy(self.run)
        for change in ({"conclusion": "failure"}, {"status": "in_progress"}, {"event": "pull_request"},
                       {"path": ".github/workflows/other.yml"}, {"head_sha": "b" * 40},
                       {"head_repository": {"full_name": "attacker/opentlv"}}, {"head_branch": "feature"}):
            with self.subTest(change=change):
                self.run = dict(original, **change)
                with self.assertRaisesRegex(ValueError, "trusted push"):
                    self.validate()

    def test_rejects_payload_repositories_refs_and_injection(self):
        original = dict(self.payload)
        for change in ({"source": "unknown"}, {"repository": "attacker/opentlv"},
                       {"commit": "main"}, {"commit": "a" * 40 + "\n"}, {"ref": "v1.2.3-rc.1"},
                       {"ref": "main\nversion=stable"}, {"run_id": True}, {"run_id": -1},
                       {"extra": "command"}):
            with self.subTest(change=change):
                self.payload = dict(original, **change)
                with self.assertRaises(ValueError):
                    self.validate()

    def test_rejects_moved_release_and_removed_main_history(self):
        self.payload["ref"] = self.run["head_branch"] = "1.2.3"
        self.target["object"]["sha"] = "b" * 40
        with self.assertRaisesRegex(ValueError, "no longer"):
            self.validate()
        self.payload["ref"] = self.run["head_branch"] = "main"
        self.relation = "diverged"
        with self.assertRaisesRegex(ValueError, "main history"):
            self.validate()

    def test_latest_never_regresses_or_silently_changes_history(self):
        for status, expected in (("ahead", "b" * 40), ("behind", self.sha), ("identical", "b" * 40)):
            self.relation = status
            self.assertEqual(events.newer(self.payload["repository"], self.sha, "b" * 40, self.api), expected)
        self.relation = "diverged"
        with self.assertRaisesRegex(ValueError, "diverged"):
            events.newer(self.payload["repository"], self.sha, "b" * 40, self.api)

    def component(self):
        self.item.update(id="python", repository="https://github.com/OpenTLV/opentlv-python",
                         updates={"workflow": ".github/workflows/compatibility.yml", "asset": "compatibility.json"},
                         compatibility={"feed": "old.json", "sha256": "0" * 64,
                                        "platform": "linux", "configuration": "default"})
        self.payload.update(source="python", repository="OpenTLV/opentlv-python", ref="v2.0.0")
        self.run.update(head_branch="v2.0.0", path=".github/workflows/compatibility.yml",
                        head_repository={"full_name": self.payload["repository"]})
        self.release = {"draft": False, "prerelease": False, "assets": [{"name": "compatibility.json",
                         "digest": "sha256:" + "f" * 64,
                         "browser_download_url": "https://github.com/OpenTLV/opentlv-python/releases/download/v2.0.0/compatibility.json"}]}

    def test_component_proposes_only_feed_pin_and_preserves_original(self):
        self.component()
        manifest = {"version": 1, "sources": [self.item]}
        before = copy.deepcopy(manifest)
        proposed = events.component_proposal(self.payload, manifest, self.api)
        self.assertEqual(manifest, before)
        feed = proposed["sources"][0]["compatibility"]
        self.assertEqual(feed["sha256"], "f" * 64)
        self.assertEqual(feed["platform"], "linux")
        self.assertEqual(proposed["sources"][0]["revision"], self.sha)

    def test_component_requires_producer_and_immutable_asset_digest(self):
        self.component()
        for change in ({"digest": ""}, {"digest": "md5:" + "f" * 32},
                       {"browser_download_url": "https://attacker.invalid/feed.json"}):
            with self.subTest(change=change):
                original = dict(self.release["assets"][0])
                self.release["assets"][0].update(change)
                with self.assertRaises(ValueError):
                    events.component_proposal(self.payload, {"sources": [self.item]}, self.api)
                self.release["assets"][0] = original
        self.item.pop("updates")
        with self.assertRaisesRegex(ValueError, "trusted producer"):
            self.validate()


class DevelopmentProposalTests(unittest.TestCase):
    api = EventTests.api

    def setUp(self):
        EventTests.setUp(self)
        EventTests.component(self)
        self.payload["ref"] = self.run["head_branch"] = "main"
        self.item["updates"]["development_artifact"] = "compatibility"
        self.core = {"id": "core", "repository": "https://github.com/OpenTLV/opentlv", "revision": "c" * 40}
        self.manifest = {"version": 1, "sources": [self.core, self.item]}
        self.record = {
            "id": "python-main", "channel": "development",
            "component": {"repository": self.item["repository"], "version": "main", "commit": self.sha},
            "core": {"repository": self.core["repository"], "version": "main", "commit": self.core["revision"]},
            "declared_core": "main", "platform": "linux", "configuration": "default",
            "build": "passed", "test": "passed", "evidence": "https://github.com/OpenTLV/opentlv-python/actions/runs/123",
            "features": [],
        }
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.portal = Path(self.temp.name)

    def propose(self):
        raw = json.dumps({"version": 2, "records": [self.record]}).encode("utf-8")
        with patch("event_artifacts.fetch_feed", return_value=raw):
            return events.component_proposal(self.payload, self.manifest, self.api, portal=self.portal)

    def test_development_proposal_pins_source_and_retains_exact_evidence_bytes(self):
        original = copy.deepcopy(self.manifest)
        proposed = self.propose()
        item = proposed["sources"][1]
        self.assertEqual(item["revision"], self.sha)
        self.assertEqual(self.manifest, original)
        raw = (self.portal / item["compatibility"]["feed"]).read_bytes()
        self.assertEqual(hashlib.sha256(raw).hexdigest(), item["compatibility"]["sha256"])
        self.assertEqual(json.loads(raw)["records"], [self.record])
        self.assertEqual(self.propose(), proposed)
        self.assertEqual(len(list(self.portal.rglob("*.json"))), 1)

    def test_no_proposal_for_wrong_pair_scope_or_unsuccessful_evidence(self):
        original = copy.deepcopy(self.record)
        for change in ({"component": dict(self.record["component"], commit="b" * 40)},
                       {"core": dict(self.record["core"], commit="b" * 40)},
                       {"platform": "other"}, {"configuration": "other"},
                       {"test": "failed"}, {"test": "untested"}):
            with self.subTest(change=change):
                self.record = dict(original, **change)
                with self.assertRaisesRegex(ValueError, "exact pinned Core/component"):
                    self.propose()
                self.assertEqual(list(self.portal.iterdir()), [])

    def test_development_requires_explicit_producer_opt_in(self):
        del self.item["updates"]["development_artifact"]
        with self.assertRaisesRegex(ValueError, "configured evidence artifact"):
            self.propose()

    def test_late_development_event_does_not_replace_newer_pin_or_evidence(self):
        self.item["revision"] = "b" * 40
        original = self.api
        def api(path):
            if f"/compare/{'b' * 40}..." in path:
                return {"status": "behind"}
            return original(path)
        with patch("event_artifacts.fetch_feed") as download:
            proposed = events.component_proposal(self.payload, self.manifest, api, portal=self.portal)
        self.assertEqual(proposed, self.manifest)
        download.assert_not_called()


class EventIntegrationTests(unittest.TestCase):
    def setUp(self):
        temp = tempfile.TemporaryDirectory()
        self.addCleanup(temp.cleanup)
        self.portal = Path(temp.name)
        self.core = {"id": "core", "repository": "https://github.com/OpenTLV/opentlv", "revision": "a" * 40}
        self.payload = {"source": "core", "repository": "OpenTLV/opentlv", "commit": "b" * 40,
                        "ref": "main", "run_id": 123}
        self.event_path = self.portal / "event.json"
        self.env = {"GITHUB_EVENT_NAME": "repository_dispatch", "GITHUB_EVENT_PATH": str(self.event_path),
                    "GITHUB_OUTPUT": str(self.portal / "outputs")}

    def select(self, previous=None):
        self.event_path.write_text(json.dumps({"client_payload": self.payload}), encoding="utf-8")
        def git(_root, command, *_args):
            return {"ls-remote": "remote" if previous else "", "fetch": "", "check-ref-format": "",
                    "ls-tree": "latest/source-revision.json", "show": json.dumps(previous)}[command]
        with patch.dict(os.environ, self.env, clear=True), patch.object(ci, "ROOT", self.portal), \
                patch.object(ci.assembly.sources, "manifest", return_value=[self.core]), \
                patch.object(ci.assembly, "git", side_effect=git), \
                patch.object(ci.events, "validate", return_value=self.core), \
                patch.object(sys, "argv", ["ci.py", "select"]):
            ci.main()
        return json.loads((self.portal / "build/selection.json").read_text())

    def test_development_requires_proposal_and_release_selects_exact_tag(self):
        with self.assertRaisesRegex(ValueError, "manifest pin update PR"):
            self.select()
        self.payload["ref"] = "v1.2.3"
        selected = self.select()
        self.assertEqual((selected["revision"], selected["version"], selected["channel"]), ("v1.2.3", "1.2.3", "release"))
        self.assertEqual(selected["event_commit"], "b" * 40)

    def test_stale_manifest_fails_without_silently_overriding_reviewed_pin(self):
        previous = {"repository": self.core["repository"], "commit": "c" * 40}
        real_newer = events.newer
        with patch.object(events, "newer", side_effect=lambda repo, old, new: real_newer(repo, old, new, lambda _: {"status": "behind"})):
            for event in ("push", "pull_request", "workflow_dispatch"):
                self.env["GITHUB_EVENT_NAME"] = event
                with self.assertRaisesRegex(ValueError, "older than published latest"):
                    self.select(previous)
        self.env["GITHUB_EVENT_NAME"] = "pull_request"
        self.assertEqual(self.select()["revision"], "a" * 40)

    def test_fetch_rejects_tag_moved_after_event_verification(self):
        (self.portal / "build").mkdir()
        (self.portal / "build/selection.json").write_text(json.dumps({"revision": "v1.2.3", "event_commit": "b" * 40}))
        with patch.dict(os.environ, {}, clear=True), patch.object(ci, "ROOT", self.portal), \
                patch.object(sys, "argv", ["ci.py", "fetch"]), \
                patch.object(ci.assembly.sources, "fetch", return_value={"sources": [{"id": "core", "commit": "c" * 40}]}):
            with self.assertRaisesRegex(ValueError, "verified event"):
                ci.main()
