# SPDX-License-Identifier: MIT
# Copyright (c) 2026 Marek Cingel

import copy
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

    def test_duplicate_event_has_same_selection(self):
        self.assertEqual(self.validate(), self.validate())

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

    def test_event_selects_exact_development_commit_and_release_tag(self):
        selected = self.select()
        self.assertEqual((selected["revision"], selected["event_commit"]), ("b" * 40, "b" * 40))
        self.assertEqual(selected["version"], "latest")
        self.payload["ref"] = "v1.2.3"
        selected = self.select()
        self.assertEqual((selected["revision"], selected["version"], selected["channel"]), ("v1.2.3", "1.2.3", "release"))

    def test_portal_push_and_old_notification_keep_published_core(self):
        previous = {"repository": self.core["repository"], "commit": "c" * 40}
        real_newer = events.newer
        with patch.object(events, "newer", side_effect=lambda repo, old, new: real_newer(repo, old, new, lambda _: {"status": "behind"})):
            self.assertEqual(self.select(previous)["revision"], "c" * 40)
            self.env["GITHUB_EVENT_NAME"] = "push"
            self.assertEqual(self.select(previous)["revision"], "c" * 40)
        self.env["GITHUB_EVENT_NAME"] = "pull_request"
        self.assertEqual(self.select(previous)["revision"], "a" * 40)

    def test_fetch_rejects_tag_moved_after_event_verification(self):
        (self.portal / "build").mkdir()
        (self.portal / "build/selection.json").write_text(json.dumps({"revision": "v1.2.3", "event_commit": "b" * 40}))
        with patch.object(ci, "ROOT", self.portal), patch.object(sys, "argv", ["ci.py", "fetch"]), \
                patch.object(ci.assembly.sources, "fetch", return_value={"sources": [{"id": "core", "commit": "c" * 40}]}):
            with self.assertRaisesRegex(ValueError, "verified event"):
                ci.main()
