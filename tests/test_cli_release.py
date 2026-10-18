# SPDX-License-Identifier: MIT
# Copyright (c) 2026 Marek Cingel

"""Real CLI-only mike publication, frozen history and authenticated gate evidence."""

import hashlib
import io
import json
import os
from pathlib import Path
import shutil
import sys
import unittest
from unittest.mock import patch
import zipfile

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "tools/docs"))
import cli_release
import publication
import test_publication as fixtures

ROOT = Path(__file__).resolve().parents[1]


class ReleaseEvidenceTests(unittest.TestCase):
    def setUp(self):
        self.payload = {"source": "cli", "repository": "OpenTLV/opentlv-cli", "commit": "a" * 40,
                        "ref": "v0.1.0", "run_id": 123, "run_attempt": 2}
        self.definitions = [{"id": "cli", "repository": "https://github.com/OpenTLV/opentlv-cli"}]
        self.run = {"status": "completed", "conclusion": "success", "event": "workflow_dispatch",
                    "head_branch": "main", "head_sha": "b" * 40, "run_attempt": 2,
                    "path": ".github/workflows/release.yml",
                    "head_repository": {"full_name": self.payload["repository"]}}
        self.result = {"status": "passed", "jobs": {"validation": "success", "quality": "success"},
                       "request": {"cli_sha": "a" * 40, "tag": "v0.1.0", "version": "0.1.0",
                                   "workflow_sha": "b" * 40, "run_id": "123", "run_attempt": "2"}}
        self.tag_commit = "a" * 40
        self.relation = "ahead"
        self.expired = False
        self.corrupt = False

    def archive(self):
        output = io.BytesIO()
        with zipfile.ZipFile(output, "w") as archive:
            archive.writestr("result.json", json.dumps(self.result))
        return output.getvalue()

    def api(self, path):
        if path.endswith("/actions/runs/123"):
            return self.run
        if "/artifacts?" in path:
            raw = self.archive()
            return {"total_count": 1, "artifacts": [{"id": 7, "name": "release-result-2",
                "expired": self.expired, "size_in_bytes": len(raw),
                "digest": "sha256:" + hashlib.sha256(raw).hexdigest(),
                "workflow_run": {"id": 123, "head_sha": "b" * 40, "head_branch": "main"}}]}
        if "/git/ref/tags/" in path:
            return {"object": {"type": "commit", "sha": self.tag_commit}}
        if "/compare/" in path:
            return {"status": self.relation}
        raise AssertionError(path)

    def validate(self):
        return cli_release.validate(self.payload, self.definitions, self.api,
                                    lambda path: self.archive() + (b"bad" if self.corrupt else b""))

    def test_gate_workflow_sha_can_differ_from_release_candidate(self):
        selected = self.validate()
        self.assertEqual(selected["commit"], "a" * 40)
        self.assertEqual(selected["producer"]["workflow_commit"], "b" * 40)
        self.assertEqual(selected["version"], "0.1.0")

    def test_wrong_producer_failed_run_and_stale_attempt_fail_closed(self):
        for key, value in (("conclusion", "failure"), ("status", "in_progress"), ("event", "push"),
                           ("head_branch", "feature/x"), ("path", ".github/workflows/evil.yml"),
                           ("run_attempt", 1), ("head_repository", {"full_name": "fork/cli"})):
            with self.subTest(key=key), patch.dict(self.run, {key: value}), self.assertRaises(ValueError):
                self.validate()

    def test_evidence_is_bound_to_candidate_tag_and_attempt(self):
        for key, value in (("cli_sha", "c" * 40), ("tag", "v0.2.0"), ("version", "0.2.0"),
                           ("workflow_sha", "c" * 40), ("run_id", "456"), ("run_attempt", "1")):
            with self.subTest(key=key), patch.dict(self.result["request"], {key: value}), self.assertRaises(ValueError):
                self.validate()
        with patch.dict(self.result, {"status": "failed"}), self.assertRaises(ValueError):
            self.validate()
        with patch.dict(self.result, {"jobs": {"validation": "success", "quality": "skipped"}}), self.assertRaises(ValueError):
            self.validate()

    def test_moved_tag_unrelated_history_expired_and_tampered_evidence(self):
        for key, value in (("tag_commit", "c" * 40), ("relation", "diverged"),
                           ("expired", True), ("corrupt", True)):
            with self.subTest(key=key), patch.object(self, key, value), self.assertRaises(ValueError):
                self.validate()

    def test_prereleases_and_unsafe_versions(self):
        for tag in ("v0.1.0", "v0.2.0-rc.1", "v1.0.0-alpha-beta.0"):
            self.assertEqual(cli_release.version(tag), tag[1:])
        for tag in ("0.1.0", "v01.0.0", "v1.0.0-01", "v1.0.0+build", "../1.0.0", "v1.0.0\n"):
            with self.subTest(tag=tag), self.assertRaises(ValueError):
                cli_release.version(tag)


class CliPublicationTests(unittest.TestCase):
    git = fixtures.PublicationTests.git
    write = fixtures.PublicationTests.write
    remote_head = fixtures.PublicationTests.remote_head
    deploy_bundle = fixtures.PublicationTests.deploy_bundle
    fresh_checkout = fixtures.PublicationTests.fresh_checkout
    set_selection = fixtures.PublicationTests.set_selection

    def setUp(self):
        fixtures.PublicationTests.setUp(self)
        self.cli = self.base / "cli"
        self.cli.mkdir()
        publication.run(self.cli, "git", "init", "-b", "main")
        (self.cli / "docs").mkdir()
        (self.cli / "docs/README.md").write_text(
            "# Commands\n\n[Schema](schema.md#schema) and [source](../README.md).\n", encoding="utf-8")
        (self.cli / "docs/schema.md").write_text("# Schema\n\n[Commands](README.md).\n", encoding="utf-8")
        (self.cli / "README.md").write_text("# CLI repository\n", encoding="utf-8")
        publication.run(self.cli, "git", "add", ".")
        publication.run(self.cli, "git", "commit", "-m", "CLI source")
        self.sha = publication.run(self.cli, "git", "rev-parse", "HEAD")
        self.item = {"id": "cli", "repository": "https://github.com/OpenTLV/opentlv-cli",
                     "revision": self.sha, "docs_path": "docs", "mount": "cli", "required": True,
                     "navigation": {"title": "CLI", "section": [],
                                    "items": [{"Commands": "README.md"}, {"Schema": "schema.md"}]}}
        self.write("docs-sources.json", json.dumps({"version": 1, "sources": [
            {"id": "core", "repository": "https://github.com/OpenTLV/opentlv", "revision": "a" * 40,
             "docs_path": "docs", "mount": "", "required": True}, self.item]}))
        shutil.copytree(ROOT / "tools", self.portal / "tools", ignore=shutil.ignore_patterns("__pycache__"))
        self.git("add", ".")
        self.git("commit", "-m", "CLI publication configuration")
        self.git("push", "origin", "main")

    def cli_selection(self, tag="v0.1.0"):
        return {"source": "cli", "repository": self.item["repository"], "commit": self.sha,
                "tag": tag, "version": tag[1:], "local": False, "dirty": False,
                "producer": {"run_id": 123, "run_attempt": 1, "workflow_commit": "b" * 40}}

    def publish(self, tag="v0.1.0"):
        return cli_release.prepare(self.portal, self.cli_selection(tag), self.cli)

    def tree(self, prefix):
        return self.git("rev-parse", "gh-pages:" + prefix)

    def test_independent_versions_preserve_core_and_retry_ignores_layout_changes(self):
        fixtures.PublicationTests.prepare(self)
        self.deploy_bundle()
        self.fresh_checkout()
        self.publish()
        site = self.portal / "build/publication/site"
        self.assertTrue((site / "latest/index.html").is_file())
        self.assertIn("CLI 0.1.0", (site / "cli/0.1.0/index.html").read_text(encoding="utf-8"))
        self.assertIn(self.sha + "/README.md", (site / "cli/0.1.0/index.html").read_text(encoding="utf-8"))
        self.assertIn("stable/", (site / "cli/index.html").read_text())
        core_tree, cli_tree = self.tree("latest"), self.tree("cli/0.1.0")
        core_versions = self.git("show", "gh-pages:versions.json")
        self.deploy_bundle()
        self.fresh_checkout()
        self.publish("v0.2.0")
        self.assertEqual(self.tree("latest"), core_tree)
        self.assertEqual(self.tree("cli/0.1.0"), cli_tree)
        self.assertEqual(self.git("show", "gh-pages:versions.json"), core_versions)
        self.deploy_bundle()
        before = self.remote_head()
        self.fresh_checkout()
        self.write("mkdocs.yml", "invalid: [broken\n")
        with patch.object(cli_release, "assemble", side_effect=AssertionError("Replay must not rebuild")):
            self.publish()
        self.assertEqual(self.remote_head(), before)
        self.assertEqual(self.tree("cli/0.1.0"), cli_tree)
        self.assertEqual(self.tree("latest"), core_tree)
        self.assertEqual(self.git("rev-parse", "gh-pages"), before.split()[0])

    def test_prereleases_and_out_of_order_releases_do_not_regress_stable(self):
        for tag in ("v0.3.0-rc.1", "v0.3.0-rc.2", "v0.3.0-rc.3", "v0.2.0", "v0.1.0", "v0.4.0-rc.1"):
            self.publish(tag)
            if tag.startswith("v0.3.0-rc."):
                self.assertIn("0.3.0-rc.1/", self.git("show", "gh-pages:cli/index.html"))
            self.deploy_bundle()
            if tag != "v0.4.0-rc.1":
                self.fresh_checkout()
        versions = json.loads(self.git("show", "gh-pages:cli/versions.json"))
        self.assertEqual(next(item["version"] for item in versions if "stable" in item["aliases"]), "0.2.0")
        self.assertIn("stable/", self.git("show", "gh-pages:cli/index.html"))

    def test_retargeted_release_and_failed_build_leave_remote_unchanged(self):
        self.publish()
        self.deploy_bundle()
        before = self.remote_head()
        self.fresh_checkout()
        selection = self.cli_selection()
        selection["commit"] = "c" * 40
        with self.assertRaisesRegex(ValueError, "identity"):
            cli_release.prepare(self.portal, selection, self.cli)
        self.assertEqual(self.remote_head(), before)
        self.fresh_checkout()
        (self.cli / "docs/schema.md").write_text("# Schema\n\n[Missing](missing.md)\n", encoding="utf-8")
        publication.run(self.cli, "git", "add", ".")
        publication.run(self.cli, "git", "commit", "-m", "Broken docs")
        self.sha = publication.run(self.cli, "git", "rev-parse", "HEAD")
        with self.assertRaises(RuntimeError):
            self.publish("v0.2.0")
        self.assertEqual(self.remote_head(), before)

    def test_local_sources_and_tampered_snapshot_are_rejected(self):
        with patch.dict(os.environ, {"OPENTLV_DOCS_LOCAL": "1"}), self.assertRaises(ValueError):
            self.publish()
        (self.cli / "docs/schema.md").write_text("# Dirty\n", encoding="utf-8")
        with self.assertRaisesRegex(ValueError, "clean"):
            self.publish()
        publication.run(self.cli, "git", "restore", "docs/schema.md")
        self.publish()
        self.deploy_bundle()
        self.fresh_checkout()
        other = self.base / "tampered"
        publication.run(self.base, "git", "clone", "-b", "gh-pages", str(self.remote), str(other))
        (other / "cli/0.1.0/index.html").write_text("tampered", encoding="utf-8")
        publication.run(other, "git", "add", ".")
        publication.run(other, "git", "commit", "-m", "Corrupt historical snapshot fixture")
        publication.run(other, "git", "push")
        before = self.remote_head()
        with self.assertRaisesRegex(ValueError, "checksums"):
            self.publish()
        self.assertEqual(self.remote_head(), before)

    def test_core_publication_preserves_cli_namespace_and_concurrent_push_is_rejected(self):
        self.publish()
        self.deploy_bundle()
        cli_tree = self.tree("cli")
        self.fresh_checkout()
        self.set_selection("1.0.0")
        fixtures.PublicationTests.prepare(self)
        self.assertEqual(self.tree("cli"), cli_tree)
        self.deploy_bundle()
        self.fresh_checkout()
        self.publish("v0.2.0")
        other = self.base / "other"
        publication.run(self.base, "git", "clone", "-b", "gh-pages", str(self.remote), str(other))
        (other / "external.txt").write_text("concurrent update", encoding="utf-8")
        publication.run(other, "git", "add", ".")
        publication.run(other, "git", "commit", "-m", "Concurrent publisher")
        publication.run(other, "git", "push")
        before = self.remote_head()
        with self.assertRaises(RuntimeError):
            self.deploy_bundle()
        self.assertEqual(self.remote_head(), before)


if __name__ == "__main__":
    unittest.main()
