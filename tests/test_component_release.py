# SPDX-License-Identifier: MIT
# Copyright (c) 2026 Marek Cingel
"""Component release evidence, shared rendering and immutable publication history."""

import copy
import hashlib
import io
import json
import os
from pathlib import Path
import shutil
import sys
import tempfile
import unittest
from unittest.mock import patch
import zipfile

import yaml

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools/docs"))
import component_release as receiver
import component_publication as engine
import quality
import sources
from mkdocs.exceptions import PluginError
import test_cli_release as cli


class ComponentEvidenceTests(unittest.TestCase):
    def setUp(self):
        self.item = {"id": "python", "repository": "https://github.com/OpenTLV/opentlv-python",
                     "publication": {"workflow": ".github/workflows/python-release.yml",
                                     "artifact": "component-release-{attempt}", "asset": "release.json"}}
        self.payload = {"source": "python", "repository": "OpenTLV/opentlv-python", "commit": "a" * 40,
                        "ref": "v0.1.0", "run_id": 123, "run_attempt": 2}
        self.run = {"status": "completed", "conclusion": "success", "event": "workflow_dispatch",
                    "head_branch": "main", "head_sha": "a" * 40, "run_attempt": 2,
                    "path": self.item["publication"]["workflow"],
                    "head_repository": {"full_name": self.payload["repository"]}}
        self.receipt = {"schema": 1, "kind": "component-release", "status": "published", "source": "python",
                        "repository": self.payload["repository"], "commit": "a" * 40, "tag": "v0.1.0",
                        "version": "0.1.0", "workflow_commit": "a" * 40, "run_id": 123,
                        "run_attempt": 2, "release_id": 456}
        self.release = {"id": 456, "tag_name": "v0.1.0", "draft": False, "prerelease": False,
                        "published_at": "2026-10-21T12:00:00Z"}
        self.tag_commit = "a" * 40
        self.relation = "identical"
        self.expired = False
        self.corrupt = False

    def archive(self):
        output = io.BytesIO()
        with zipfile.ZipFile(output, "w") as bundle:
            bundle.writestr("release.json", json.dumps(self.receipt))
        return output.getvalue()

    def api(self, path):
        if path.endswith("/actions/runs/123"):
            return self.run
        if "/artifacts?" in path:
            raw = self.archive()
            return {"total_count": 1, "artifacts": [{"id": 7, "name": "component-release-2",
                "expired": self.expired, "size_in_bytes": len(raw), "digest": "sha256:" + hashlib.sha256(raw).hexdigest(),
                "workflow_run": {"id": 123, "head_sha": "a" * 40, "head_branch": "main"}}]}
        if "/releases/tags/" in path:
            return self.release
        if "/git/ref/tags/" in path:
            return {"object": {"type": "commit", "sha": self.tag_commit}}
        if "/compare/" in path:
            return {"status": self.relation}
        raise AssertionError(path)

    def validate(self):
        return receiver.validate(self.payload, [self.item], self.api,
                                 lambda path: self.archive() + (b"bad" if self.corrupt else b""))

    def test_exact_published_release_and_configured_future_component(self):
        self.assertEqual(self.validate()["producer"]["release_id"], 456)
        self.item["id"] = self.payload["source"] = self.receipt["source"] = "future"
        self.assertEqual(self.validate()["source"], "future")

    def test_preparation_and_unpublished_or_replaced_releases_do_not_authorize_docs(self):
        for change in ({"draft": True}, {"published_at": None}, {"id": 789},
                       {"tag_name": "v0.2.0"}, {"prerelease": True}):
            with self.subTest(change=change), patch.dict(self.release, change), self.assertRaises(ValueError):
                self.validate()
        for change in ({"kind": "python-release-candidate"}, {"status": "prepared"}, {"release_id": True}):
            with patch.dict(self.receipt, change), self.assertRaises(ValueError):
                self.validate()

    def test_failed_fork_stale_or_wrong_producer_fails(self):
        for change in ({"conclusion": "failure"}, {"status": "in_progress"}, {"run_attempt": 1},
                       {"event": "push"}, {"head_branch": "feature"}, {"path": ".github/workflows/other.yml"},
                       {"head_repository": {"full_name": "other/python"}}):
            with self.subTest(change=change), patch.dict(self.run, change), self.assertRaises(ValueError):
                self.validate()

    def test_receipt_identity_and_payload_validation(self):
        for key, value in {"commit": "b" * 40, "workflow_commit": "b" * 40, "tag": "v0.2.0",
                           "version": "0.2.0", "repository": "other/python", "source": "lua",
                           "run_id": 124, "run_attempt": 1, "schema": True}.items():
            with self.subTest(key=key), patch.dict(self.receipt, {key: value}), self.assertRaises(ValueError):
                self.validate()
        for key, value in {"repository": "other/python", "source": "unknown", "commit": "main",
                           "ref": "../1.0.0", "run_id": True, "run_attempt": 0}.items():
            with patch.dict(self.payload, {key: value}), self.assertRaises(ValueError):
                self.validate()

    def test_changed_tag_expired_corrupt_evidence_and_divergence(self):
        for key, value in (("tag_commit", "b" * 40), ("expired", True), ("corrupt", True), ("relation", "diverged")):
            with self.subTest(key=key), patch.object(self, key, value), self.assertRaises(ValueError):
                self.validate()

    def test_configuration_requires_explicit_attempt_scoped_policy(self):
        for policy in ({}, {**self.item["publication"], "workflow": "../bad.py"},
                       {**self.item["publication"], "artifact": "moving-receipt"},
                       {**self.item["publication"], "asset": "../release.json"}):
            with patch.dict(self.item, {"publication": policy}), self.assertRaises(ValueError):
                self.validate()

    def test_manifest_checks_publication_policy_before_any_fetch(self):
        manifest = json.loads((ROOT / "docs-sources.json").read_text())
        item = next(item for item in manifest["sources"] if item["id"] == "python")
        with tempfile.TemporaryDirectory() as folder:
            portal = Path(folder)
            for invalid in (False, {"workflow": "untrusted"},
                            {**item["publication"], "artifact": "receipt-without-attempt"}):
                item["publication"] = invalid
                (portal / "docs-sources.json").write_text(json.dumps(manifest))
                with self.assertRaises(PluginError):
                    sources.manifest(portal)

    def test_prerelease_version_is_separate_from_stable(self):
        self.payload["ref"] = self.receipt["tag"] = self.release["tag_name"] = "v0.2.0-rc.1"
        self.receipt["version"] = "0.2.0-rc.1"
        self.release["prerelease"] = True
        self.assertEqual(self.validate()["version"], "0.2.0-rc.1")

    def test_workflow_routes_release_events_to_component_path_only(self):
        full = yaml.load((ROOT / ".github/workflows/docs-full.yml").read_text(), Loader=yaml.BaseLoader)
        steps = full["jobs"]["prepare"]["steps"]
        component = next(step for step in steps if "component_release.py" in step.get("run", ""))
        self.assertEqual(component["if"], "github.event.action == 'component-release-published'")
        for step in steps:
            if any(name in step.get("run", "") for name in ("ci.py select", "wasm.py", "browser_smoke.py", "publication.py")):
                self.assertIn("!= 'component-release-published'", step["if"])
        updates = yaml.load((ROOT / ".github/workflows/component-updates.yml").read_text(), Loader=yaml.BaseLoader)
        self.assertNotIn("component-release-published", updates["on"]["repository_dispatch"]["types"])


class ComponentPublicationTests(unittest.TestCase):
    git = cli.CliPublicationTests.git
    write = cli.CliPublicationTests.write
    remote_head = cli.CliPublicationTests.remote_head
    deploy_bundle = cli.CliPublicationTests.deploy_bundle
    fresh_checkout = cli.CliPublicationTests.fresh_checkout
    set_selection = cli.CliPublicationTests.set_selection
    tree = cli.CliPublicationTests.tree

    def setUp(self):
        cli.CliPublicationTests.setUp(self)
        environment = patch.dict(os.environ, {"PYTHONDONTWRITEBYTECODE": "1"})
        environment.start()
        self.addCleanup(environment.stop)
        manifest = json.loads((self.portal / "docs-sources.json").read_text())
        for name in ("lua", "python", "future"):
            item = copy.deepcopy(self.item)
            item.update(id=name, mount=name, repository="https://github.com/OpenTLV/opentlv-" + name)
            item["navigation"]["title"] = name.title()
            item["publication"] = {"workflow": ".github/workflows/release.yml",
                                   "artifact": "component-release-{attempt}", "asset": "release.json"}
            manifest["sources"].append(item)
        self.write("docs-sources.json", json.dumps(manifest))
        self.git("add", ".")
        self.git("commit", "-m", "Component fixture configuration")
        self.git("push", "origin", "main")

    def component_selection(self, name, tag="v0.1.0"):
        return {**cli.CliPublicationTests.cli_selection(self, tag), "source": name,
                "repository": "https://github.com/OpenTLV/opentlv-" + name}

    def publish(self, name, tag="v0.1.0"):
        return engine.prepare(self.portal, self.component_selection(name, tag), self.cli)

    def test_components_preserve_each_other_and_full_gate_tracks_all_snapshots(self):
        # Component snapshots link back to the portal root published by Core.
        cli.fixtures.PublicationTests.prepare(self)
        self.deploy_bundle()
        self.fresh_checkout()
        for name in ("cli", "lua", "python", "future"):
            if self.remote_head():
                self.git("fetch", "origin", "refs/heads/gh-pages:refs/heads/gh-pages")
            before = {prefix: self.tree(prefix) for prefix in ("cli", "lua", "python", "future")
                      if self.git("branch", "--list", "gh-pages") and
                      self.git("ls-tree", "--name-only", "gh-pages", prefix)}
            if name == "python":
                quality.baseline(self.portal)
            self.publish(name)
            for prefix, tree in before.items():
                self.assertEqual(self.tree(prefix), tree)
            if name == "python":
                self.write("build/selection.json", json.dumps(self.component_selection(name)))
                env = {"GITHUB_REPOSITORY": "OpenTLV/opentlv-docs", "GITHUB_SHA": self.git("rev-parse", "HEAD"),
                       "GITHUB_RUN_ID": "123", "GITHUB_RUN_ATTEMPT": "2",
                       "GITHUB_WORKFLOW_REF": "OpenTLV/opentlv-docs/.github/workflows/docs-release.yml@refs/heads/main"}
                with patch.dict(os.environ, env):
                    evidence = quality.pack(self.portal)
                    target = self.portal / "build/candidate"
                    target.mkdir()
                    for filename in ("site.tar", "history.bundle", "evidence.json"):
                        shutil.copyfile(self.portal / "build/publication" / filename, target / filename)
                    self.assertEqual(quality.verify(self.portal, target), evidence)
                    self.assertTrue((target / "site/python/0.1.0/index.html").is_file())
            self.deploy_bundle()
            self.fresh_checkout()
        self.git("fetch", "origin", "refs/heads/gh-pages:refs/heads/gh-pages")
        self.assertEqual(set(quality.snapshots(self.portal, "gh-pages")),
                         {name + "/0.1.0" for name in ("cli", "lua", "python", "future")})
        original = self.tree("python/0.1.0")
        self.write("mkdocs.yml", "invalid: [broken\n")
        with patch.object(engine, "assemble", side_effect=AssertionError("Replay rebuilt docs")):
            self.publish("python")
        self.assertEqual(self.tree("python/0.1.0"), original)
        self.fresh_checkout()
        with self.assertRaisesRegex(ValueError, "identity"):
            engine.prepare(self.portal, {**self.component_selection("python"), "commit": "b" * 40}, self.cli)

    def test_prereleases_older_releases_and_failed_build_preserve_publication(self):
        for tag in ("v0.3.0-rc.1", "v0.2.0", "v0.1.0", "v0.4.0-rc.1"):
            self.publish("lua", tag)
            self.deploy_bundle()
            self.fresh_checkout()
        self.git("fetch", "origin", "refs/heads/gh-pages:refs/heads/gh-pages")
        catalog = json.loads(self.git("show", "gh-pages:lua/versions.json"))
        self.assertEqual(next(item["version"] for item in catalog if "stable" in item["aliases"]), "0.2.0")
        before = self.remote_head()
        with patch.object(engine, "assemble", side_effect=RuntimeError("Bad docs")), self.assertRaises(RuntimeError):
            self.publish("lua", "v0.5.0")
        self.assertEqual(self.remote_head(), before)

    def test_generated_landing_page_has_no_false_edit_link(self):
        (self.cli / "docs/README.md").rename(self.cli / "docs/guide.md")
        (self.cli / "docs/schema.md").write_text("# Schema\n\n[Guide](guide.md).\n")
        cli.publication.run(self.cli, "git", "add", ".")
        cli.publication.run(self.cli, "git", "commit", "-m", "Docs without root index")
        self.sha = cli.publication.run(self.cli, "git", "rev-parse", "HEAD")
        manifest = json.loads((self.portal / "docs-sources.json").read_text())
        for item in manifest["sources"]:
            if item["id"] == "python":
                item["navigation"]["items"][0] = {"Guide": "guide.md"}
        self.write("docs-sources.json", json.dumps(manifest))
        self.publish("python")
        site = self.portal / "build/publication/site/python/0.1.0"
        html = (site / "index.html").read_text(encoding="utf-8")
        self.assertIn("OpenTLV Python 0.1.0", html)
        self.assertNotIn("/edit/", html)
        self.assertIn(self.sha, (site / "guide/index.html").read_text(encoding="utf-8"))


if __name__ == "__main__":
    unittest.main()
