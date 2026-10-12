# SPDX-License-Identifier: MIT
# Copyright (c) 2026 Marek Cingel

"""Exercise actual mike builds and fast-forward deployment in disposable Git repos."""

import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "tools/docs"))
import ci
import publication


class SelectionTests(unittest.TestCase):
    manifest = {"repository": "https://github.com/OpenTLV/opentlv", "revision": "a" * 40}

    def test_default_development_and_release_tag_selection(self):
        self.assertEqual(ci.select(self.manifest, "development")["revision"], "a" * 40)
        for tag in ("1.2.3", "v1.2.3"):
            self.assertEqual(ci.select(self.manifest, "release", tag)["version"], "1.2.3")

    def test_release_rejects_branches_shas_prereleases_and_unsafe_refs(self):
        for ref in ("main", "a" * 40, "1.2.3-rc.1", "01.2.3", "x\nrepository=evil", "../../x"):
            with self.subTest(ref=ref), self.assertRaises(Exception):
                ci.select(self.manifest, "release", ref)

    def test_actual_portal_navigation_is_checked(self):
        with tempfile.TemporaryDirectory() as temp:
            docs = Path(temp)
            (docs / "guides").mkdir()
            (docs / "README.md").write_text("# GitHub index\n", encoding="utf-8")
            (docs / "guides/api.md").write_text("# API\n", encoding="utf-8")
            nav = "nav:\n  - Guides:\n    - API: guides/api.md\n"
            ci.check_navigation(docs, nav)
            with self.assertRaisesRegex(ValueError, "guides/api.md"):
                ci.check_navigation(docs, "nav:\n  - Home: index.md\n# guides/api.md\n")
            # New pages must be discoverable even without any Core mkdocs.yml.
            (docs / "guides/README.md").write_text("# Guides\n", encoding="utf-8")
            with self.assertRaisesRegex(ValueError, "guides/README.md"):
                ci.check_navigation(docs, nav)


class PublicationTests(unittest.TestCase):
    def setUp(self):
        temp = tempfile.TemporaryDirectory()
        self.addCleanup(temp.cleanup)
        self.base = Path(temp.name).resolve()
        self.remote = self.base / "remote.git"
        self.portal = self.base / "portal"
        self.portal.mkdir()
        env = {key: value for key, value in os.environ.items()
               if not key.startswith(("OPENTLV_", "GITHUB_", "GIT_"))}
        env.update(GIT_AUTHOR_NAME="Fixture", GIT_AUTHOR_EMAIL="fixture@example.invalid",
                   GIT_COMMITTER_NAME="Fixture", GIT_COMMITTER_EMAIL="fixture@example.invalid",
                   GIT_CONFIG_COUNT="2", GIT_CONFIG_KEY_0="commit.gpgsign", GIT_CONFIG_VALUE_0="false",
                   GIT_CONFIG_KEY_1="core.autocrlf", GIT_CONFIG_VALUE_1="false")
        context = patch.dict(os.environ, env, clear=True)
        context.start()
        self.addCleanup(context.stop)
        self.git("init", "--bare", str(self.remote))
        self.git("init", "-b", "main")
        self.git("remote", "add", "origin", str(self.remote))
        self.write(".gitignore", "site/\nbuild/\n")
        self.write("mkdocs.yml", "site_name: Fixture\nsite_url: https://example.invalid/docs/\n"
                   "theme:\n  name: material\nextra:\n  version:\n    provider: mike\n"
                   "strict: true\nvalidation:\n  links:\n    not_found: warn\n    anchors: warn\n"
                   "nav:\n  - Home: index.md\n")
        self.write("docs/index.md", "# Home\n\nFixture documentation.\n")
        self.write("docs/static.json", '{"fixture": true}\n')
        self.set_selection()
        self.git("add", ".")
        self.git("commit", "-m", "Fixture")
        self.git("push", "origin", "main")

    def git(self, *args):
        return publication.run(self.portal, "git", *args)

    def write(self, name, text):
        path = self.portal / name
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(text, encoding="utf-8")

    def set_selection(self, tag=None, commit="a" * 40):
        self.selection = ci.select(SelectionTests.manifest, "release" if tag else "development", tag or "")
        self.selection["commit"] = commit
        metadata = {"repository": "https://github.com/OpenTLV/opentlv", "commit": commit,
                    "local": False, "dirty": False,
                    "api": {"commit": commit, "local": False, "dirty": False}}
        self.write("docs/source-revision.json", json.dumps(metadata))

    def prepare(self):
        return publication.prepare(self.portal, self.selection)

    def remote_head(self):
        return self.git("ls-remote", "origin", "refs/heads/gh-pages")

    def deploy_bundle(self):
        # Mirror the deployment job: import only the staged history, then one push.
        deploy = self.base / f"deploy-{len(list(self.base.glob('deploy-*')))}"
        publication.run(self.base, "git", "clone", "--branch", "main", str(self.remote), str(deploy))
        publication.run(deploy, "git", "fetch", str(self.portal / "build/publication/history.bundle"),
                        "refs/heads/gh-pages:refs/heads/gh-pages")
        publication.run(deploy, "git", "push", "origin", "refs/heads/gh-pages:refs/heads/gh-pages")

    def fresh_checkout(self):
        self.portal = self.base / f"portal-{len(list(self.base.glob('portal*')))}"
        publication.run(self.base, "git", "clone", "--branch", "main", str(self.remote), str(self.portal))

    def test_first_publication_releases_history_and_stable_are_preserved(self):
        self.prepare()
        site = self.portal / "build/publication/site"
        self.assertIn("latest/", (site / "index.html").read_text())
        self.assertEqual(self.remote_head(), "")
        self.deploy_bundle()
        for tag in ("v2.0.0", "1.0.0", None):
            self.fresh_checkout()
            self.set_selection(tag)
            self.prepare()
            site = self.portal / "build/publication/site"
            self.assertTrue((site / "latest/index.html").is_file())
            self.assertTrue((site / "2.0.0/index.html").is_file())
            self.assertEqual((site / "stable/static.json").read_bytes(), (site / "2.0.0/static.json").read_bytes())
            self.assertIn("stable/", (site / "index.html").read_text())
            versions = json.loads((site / "versions.json").read_text())
            self.assertEqual(next(item["version"] for item in versions if "stable" in item["aliases"]), "2.0.0")
            self.deploy_bundle()

    def test_failed_build_and_failed_default_update_never_change_remote(self):
        self.prepare()
        self.deploy_bundle()
        before = self.remote_head()
        self.fresh_checkout()
        self.set_selection()
        self.write("docs/index.md", "# Broken\n\n[Missing](missing.md)\n")
        with self.assertRaisesRegex(RuntimeError, "Command failed"):
            self.prepare()
        self.assertEqual(self.remote_head(), before)
        self.fresh_checkout()
        self.set_selection()
        original = publication.run

        def fail_default(root, *args, **kwargs):
            if "set-default" in args:
                raise RuntimeError("Injected default failure")
            return original(root, *args, **kwargs)

        with patch.object(publication, "run", side_effect=fail_default):
            with self.assertRaisesRegex(RuntimeError, "Injected default failure"):
                self.prepare()
        self.assertEqual(self.remote_head(), before)
        self.assertFalse((self.portal / "build/publication/history.bundle").exists())

    def test_mismatched_metadata_and_local_mode_cannot_publish(self):
        with patch.dict(os.environ, {"OPENTLV_DOCS_LOCAL": "1"}):
            with self.assertRaisesRegex(ValueError, "Local preview"):
                self.prepare()
        self.selection["commit"] = "b" * 40
        with self.assertRaisesRegex(ValueError, "clean site and API metadata"):
            self.prepare()
        self.assertEqual(self.remote_head(), "")
        self.assertFalse((self.portal / "build/publication/history.bundle").exists())

    def test_existing_release_rejects_moved_core_tag(self):
        self.set_selection("1.0.0")
        self.prepare()
        self.deploy_bundle()
        before = self.remote_head()
        self.fresh_checkout()
        self.set_selection("1.0.0", "b" * 40)
        with self.assertRaisesRegex(ValueError, "different Core source"):
            self.prepare()
        self.assertEqual(self.remote_head(), before)

    def test_concurrent_remote_update_rejects_stale_publication(self):
        self.prepare()
        self.deploy_bundle()
        self.fresh_checkout()
        self.set_selection("1.0.0")
        self.prepare()
        stale = self.portal
        self.fresh_checkout()
        self.set_selection("2.0.0")
        self.prepare()
        self.deploy_bundle()
        before = self.remote_head()
        self.portal = stale
        with self.assertRaisesRegex(RuntimeError, "Command failed"):
            self.deploy_bundle()
        self.assertEqual(self.remote_head(), before)


if __name__ == "__main__":
    unittest.main()
