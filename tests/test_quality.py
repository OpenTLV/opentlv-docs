# SPDX-License-Identifier: MIT
# Copyright (c) 2026 Marek Cingel

"""Reject incomplete, replayed or modified publication evidence."""

import copy
import hashlib
import io
import json
import os
from pathlib import Path
import sys
import tarfile
import tempfile
import unittest
from unittest.mock import patch
from urllib.error import HTTPError

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "tools/docs"))
import quality
import ci_timings
import auto_merge


class EvidenceTests(unittest.TestCase):
    def setUp(self):
        temp = tempfile.TemporaryDirectory()
        self.addCleanup(temp.cleanup)
        self.root = Path(temp.name).resolve()
        self.directory = self.root / "candidate"
        self.directory.mkdir()
        (self.root / "docs-sources.json").write_text('{"sources": []}\n')
        (self.directory / "history.bundle").write_bytes(b"fixture")
        self.env = {"GITHUB_REPOSITORY": "OpenTLV/opentlv-docs", "GITHUB_SHA": "a" * 40,
                    "GITHUB_RUN_ID": "123", "GITHUB_RUN_ATTEMPT": "2",
                    "GITHUB_WORKFLOW_REF": "OpenTLV/opentlv-docs/.github/workflows/docs-full.yml@refs/heads/main"}
        self.context = patch.dict(os.environ, self.env)
        self.context.start()
        self.addCleanup(self.context.stop)
        self.archive("latest/index.html")
        self.evidence = {"schema": 1, "identity": quality.identity(),
                         "manifest_sha256": quality.digest(self.root / "docs-sources.json"),
                         "pages_commit": "b" * 40, "selection": {"version": "latest"},
                         "previous": {"commit": "c" * 40, "snapshots": {"1.0.0": "tree"}},
                         "snapshots": {"1.0.0": "tree"}, "files": self.hashes()}
        self.save()

    def archive(self, name, kind=tarfile.REGTYPE, duplicate=False):
        with tarfile.open(self.directory / "site.tar", "w") as output:
            entry = tarfile.TarInfo(name)
            entry.type = kind
            entry.size = 1 if kind == tarfile.REGTYPE else 0
            entry.linkname = "../outside"
            output.addfile(entry, io.BytesIO(b"x") if entry.size else None)
            if duplicate:
                output.addfile(entry, io.BytesIO(b"x"))

    def hashes(self):
        return {name: quality.digest(self.directory / name) for name in ("site.tar", "history.bundle")}

    def save(self):
        (self.directory / "evidence.json").write_text(json.dumps(self.evidence))

    def verify(self, trees=None):
        def run(_root, *args):
            if args[1:3] == ("bundle", "list-heads"):
                return "b" * 40 + " refs/heads/gh-pages"
            if args[1:3] == ("ls-tree", "-r"):
                return "100644 blob " + hashlib.sha1(b"blob 1\0x").hexdigest() + "\tlatest/index.html"
            return ""
        with patch.object(quality.publication, "run", side_effect=run), \
                patch.object(quality, "snapshots", return_value=trees or {"1.0.0": "tree"}), \
                patch.object(quality.publication, "verify_site") as site:
            result = quality.verify(self.root, self.directory)
            site.assert_called_once_with(self.directory / "site/latest", {"version": "latest"})
            return result

    def test_matching_candidate_extracts_only_after_verification(self):
        self.assertEqual(self.verify(), self.evidence)
        self.assertEqual((self.directory / "site/latest/index.html").read_bytes(), b"x")

    def test_wrong_run_attempt_commit_repository_workflow_or_manifest(self):
        original = copy.deepcopy(self.evidence)
        for key, value in (("run_id", "122"), ("run_attempt", "1"), ("sha", "d" * 40),
                           ("repository", "other/repo"), ("workflow_ref", "other")):
            self.evidence = copy.deepcopy(original)
            self.evidence["identity"][key] = value
            self.save()
            with self.assertRaisesRegex(ValueError, "evidence differs"):
                self.verify()
            self.assertFalse((self.directory / "site").exists())
        self.evidence = original
        self.evidence["manifest_sha256"] = "0" * 64
        self.save()
        with self.assertRaisesRegex(ValueError, "evidence differs"):
            self.verify()

    def test_missing_modified_or_wrong_history_artifacts(self):
        (self.directory / "site.tar").write_bytes(b"modified")
        with self.assertRaisesRegex(ValueError, "checksum"):
            self.verify()
        self.archive("latest/index.html")
        self.evidence["files"] = self.hashes()
        self.evidence["pages_commit"] = "c" * 40
        self.save()
        with self.assertRaisesRegex(ValueError, "History bundle"):
            self.verify()
        (self.directory / "history.bundle").unlink()
        with self.assertRaises(FileNotFoundError):
            self.verify()

    def test_changed_historical_tree_is_rejected(self):
        with self.assertRaisesRegex(ValueError, "Immutable snapshot"):
            self.verify({"1.0.0": "changed"})

    def test_pack_rejects_wrong_or_dirty_infrastructure_checkout(self):
        for responses in (["d" * 40], ["a" * 40, " M tools/docs/quality.py"]):
            with patch.object(quality.publication, "run", side_effect=responses):
                with self.assertRaisesRegex(ValueError, "exact clean"):
                    quality.pack(self.root)

    def test_site_must_equal_the_history_tree_even_with_updated_archive_checksum(self):
        self.archive("other.html")
        self.evidence["files"] = self.hashes()
        self.save()
        with self.assertRaisesRegex(ValueError, "file set differs"):
            self.verify()

    def test_unsafe_links_traversal_and_duplicate_archive_entries(self):
        for name, kind, duplicate in (("../outside", tarfile.REGTYPE, False),
                                      ("/outside", tarfile.REGTYPE, False),
                                      ("link", tarfile.SYMTYPE, False),
                                      ("file", tarfile.LNKTYPE, False),
                                      ("file", tarfile.REGTYPE, True)):
            self.archive(name, kind, duplicate)
            self.evidence["files"] = self.hashes()
            self.save()
            with self.assertRaisesRegex(ValueError, "Unsafe"):
                self.verify()
            # Failed validation creates only an empty destination.
            (self.directory / "site").rmdir()
            self.assertFalse((self.root / "outside").exists())


class TimingTests(unittest.TestCase):
    def setUp(self):
        self.ctx = {"run_id": "123", "run_attempt": "2", "sha": "a" * 40}
        self.job = {"name": "Required", "run_id": 123, "run_attempt": 2, "head_sha": "a" * 40,
                    "status": "completed", "conclusion": "success",
                    "started_at": "2026-01-01T00:00:00Z", "completed_at": "2026-01-01T00:01:00Z"}

    def test_delayed_metadata_retries_same_attempt(self):
        with patch.object(ci_timings, "attempt_jobs", side_effect=[[], [self.job]]) as query, \
                patch.object(ci_timings.time, "sleep"):
            self.assertEqual(ci_timings.completed_jobs(self.ctx, ["Required"]), [self.job])
            self.assertEqual(query.call_args_list[0], query.call_args_list[1])

    def test_metadata_delayed_beyond_half_a_minute_is_awaited(self):
        pending = dict(self.job, status="in_progress", completed_at=None)
        with patch.object(ci_timings, "attempt_jobs", side_effect=[[pending]] * 6 + [[self.job]]),                 patch.object(ci_timings.time, "sleep") as sleep, patch("sys.stdout", new_callable=io.StringIO):
            self.assertEqual(ci_timings.completed_jobs(self.ctx, ["Required"]), [self.job])
        self.assertGreater(sum(call.args[0] for call in sleep.call_args_list), 60)
        self.assertLess(sum(ci_timings.METADATA_DELAYS), 240)

    def test_transient_api_errors_are_retried_and_others_fail(self):
        class Response(io.BytesIO):
            def __enter__(self):
                return self

            def __exit__(self, *args):
                pass
        for code in (502, 503):
            with patch.object(ci_timings, "urlopen", side_effect=[
                    HTTPError("url", code, "unavailable", {}, None), Response(b'{"ok": 1}')]),                     patch.object(ci_timings.time, "sleep"), patch("sys.stdout", new_callable=io.StringIO):
                self.assertEqual(ci_timings.get("/x"), {"ok": 1})
        with patch.object(ci_timings, "urlopen", side_effect=HTTPError("url", 404, "missing", {}, None)),                 patch.object(ci_timings.time, "sleep") as sleep:
            with self.assertRaises(HTTPError):
                ci_timings.get("/x")
            sleep.assert_not_called()

    def test_missing_partial_duplicate_or_stale_jobs_fail(self):
        for jobs in ([], [self.job, self.job], [dict(self.job, status="in_progress")],
                     [dict(self.job, run_attempt=1)], [dict(self.job, head_sha="b" * 40)]):
            with patch.object(ci_timings, "attempt_jobs", return_value=jobs), \
                    patch.object(ci_timings.time, "sleep"):
                with self.assertRaises(ValueError):
                    ci_timings.completed_jobs(self.ctx, ["Required"])

    def test_pr_records_head_and_tested_merge_commit_separately(self):
        env = {"GITHUB_RUN_ID": "123", "GITHUB_RUN_ATTEMPT": "2", "GITHUB_SHA": "b" * 40,
               "GITHUB_EVENT_NAME": "pull_request", "TIMING_HEAD_SHA": "a" * 40}
        run = {"id": 123, "run_attempt": 2, "head_sha": "a" * 40, "event": "pull_request",
               "html_url": "run", "run_started_at": self.job["started_at"]}
        with patch.dict(os.environ, env), patch.object(ci_timings, "get", return_value=run), \
                patch.object(ci_timings, "completed_jobs", return_value=[dict(self.job, html_url="job")]):
            report = ci_timings.current(["Required"])
            self.assertEqual(report["commit"], "a" * 40)
            self.assertEqual(report["checkout_commit"], "b" * 40)
            self.assertEqual(report["job_seconds"], 60)
            self.assertEqual(report["wall_seconds"], 60)

    def test_failed_job_rerun_reuses_earlier_job_times(self):
        env = {"GITHUB_RUN_ID": "123", "GITHUB_RUN_ATTEMPT": "2", "GITHUB_SHA": "a" * 40,
               "GITHUB_EVENT_NAME": "push"}
        # The carried-over job finished before the rerun attempt started.
        run = {"id": 123, "run_attempt": 2, "head_sha": "a" * 40, "event": "pull_request",
               "html_url": "run", "run_started_at": "2026-01-01T00:05:00Z"}
        with patch.dict(os.environ, env), patch.object(ci_timings, "get", return_value=run),                 patch.object(ci_timings, "completed_jobs", return_value=[dict(self.job, html_url="job")]):
            report = ci_timings.current(["Required"])
        self.assertEqual(report["started_at"], self.job["started_at"])
        self.assertEqual(report["wall_seconds"], 60)

    def test_negative_runner_duration_is_rejected(self):
        with self.assertRaisesRegex(ValueError, "negative"):
            ci_timings.seconds(self.job["completed_at"], self.job["started_at"])


class AutoMergeTests(unittest.TestCase):
    def test_requires_exact_pr_gate(self):
        self.assertFalse(auto_merge.required_gate([]))
        rule = {"type": "required_status_checks",
                "parameters": {"strict_required_status_checks_policy": True,
                               "required_status_checks": [{"context": "Docs PR gate"}]}}
        self.assertTrue(auto_merge.required_gate([rule]))
        rule["parameters"]["strict_required_status_checks_policy"] = False
        self.assertFalse(auto_merge.required_gate([rule]))
        rule["parameters"]["strict_required_status_checks_policy"] = True
        rule["parameters"]["required_status_checks"][0]["context"] = "Docs Main gate"
        self.assertFalse(auto_merge.required_gate([rule]))

    def test_unprotected_branch_never_calls_merge(self):
        with patch.dict(os.environ, PR_NUMBER="12", PR_HEAD="a" * 40), \
                patch.object(auto_merge, "api", side_effect=[{"allow_auto_merge": True}, [], {}]), \
                patch.object(auto_merge.subprocess, "run") as merge:
            with self.assertRaisesRegex(ValueError, "Require Docs PR gate"):
                auto_merge.main()
            merge.assert_not_called()

    def test_matching_proposal_requests_auto_merge_with_head_lease(self):
        rule = {"type": "required_status_checks",
                "parameters": {"strict_required_status_checks_policy": True,
                               "required_status_checks": [{"context": "Docs PR gate"}]}}
        pr = {"head": {"sha": "a" * 40, "repo": {"full_name": auto_merge.REPO},
                       "ref": "automation/component-core"},
              "base": {"ref": "main"}, "draft": False, "state": "open"}
        for name in ("docs-sources.json", "tools/docs/quality.py"):
            with patch.dict(os.environ, PR_NUMBER="12", PR_HEAD="a" * 40), \
                    patch.object(auto_merge, "api", side_effect=[
                        {"allow_auto_merge": True}, [rule], pr, [{"filename": name}]]), \
                    patch.object(auto_merge.subprocess, "run") as merge:
                if name == "docs-sources.json":
                    auto_merge.main()
                    self.assertIn("--auto", merge.call_args.args[0])
                    self.assertEqual(merge.call_args.args[0][-2:], ["--match-head-commit", "a" * 40])
                else:
                    with self.assertRaisesRegex(ValueError, "only accepts"):
                        auto_merge.main()
                    merge.assert_not_called()


if __name__ == "__main__":
    unittest.main()
