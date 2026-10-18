# SPDX-License-Identifier: MIT
# Copyright (c) 2026 Marek Cingel

"""Exercise actual mike builds and fast-forward deployment in disposable Git repos."""

import io
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
            (docs / "index.md").write_text("# Home\n", encoding="utf-8")
            (docs / "guides/api.md").write_text("# API\n", encoding="utf-8")
            nav = "nav:\n  - Home: index.md\n  - Guides:\n    - API: guides/api.md\n"
            ci.check_navigation(docs, nav)
            with self.assertRaisesRegex(ValueError, "guides/api.md"):
                ci.check_navigation(docs, "nav:\n  - Home: index.md\n# guides/api.md\n")
            # New pages must be discoverable even without any Core mkdocs.yml.
            (docs / "guides/README.md").write_text("# Guides\n", encoding="utf-8")
            with self.assertRaisesRegex(ValueError, "guides/README.md"):
                ci.check_navigation(docs, nav)

    def test_removed_cli_pages_fail_navigation_check(self):
        with tempfile.TemporaryDirectory() as temp:
            docs = Path(temp)
            (docs / "index.md").write_text("# Home\n", encoding="utf-8")
            with self.assertRaisesRegex(ValueError, "missing documentation: cli/README.md"):
                ci.check_navigation(docs, "nav:\n  - Home: index.md\n  - CLI: cli/README.md\n")


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
        sources = [{"id": "core", "repository": metadata["repository"], "revision": self.selection["revision"],
                    "commit": commit, "required": True, "included": True, "local": False, "dirty": False}]
        self.selection["sources"] = sources
        metadata["sources"] = sources
        self.write("build/sources.lock.json", json.dumps({"sources": sources}))
        self.write("docs/source-revision.json", json.dumps(metadata))

    def prepare(self):
        return publication.prepare(self.portal, self.selection)

    def add_component(self, included=True, commit="c" * 40):
        item = {"id": "python", "repository": "https://github.com/OpenTLV/python",
                "revision": "v2", "required": False, "included": included,
                "local": False, "dirty": False}
        if included:
            item["commit"] = commit
        else:
            item["reason"] = "repository unavailable"
        self.selection["sources"].append(item)
        metadata = json.loads((self.portal / "docs/source-revision.json").read_text())
        metadata["sources"] = self.selection["sources"]
        self.write("docs/source-revision.json", json.dumps(metadata))
        self.write("build/sources.lock.json", json.dumps({"sources": self.selection["sources"]}))

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

    def test_existing_release_locks_component_commit_and_inclusion(self):
        self.set_selection("1.0.0")
        self.add_component()
        self.prepare()
        self.deploy_bundle()
        before = self.remote_head()
        for included, commit in ((True, "d" * 40), (False, "c" * 40)):
            self.fresh_checkout()
            self.set_selection("1.0.0")
            self.add_component(included, commit)
            with self.assertRaisesRegex(ValueError, "different source set"):
                self.prepare()
            self.assertEqual(self.remote_head(), before)
        self.fresh_checkout()
        self.set_selection("1.0.0")
        self.add_component()
        self.prepare()  # The identical complete source set remains rebuildable.

    def test_component_metadata_and_lock_cannot_disagree_with_selection(self):
        self.add_component()
        self.selection["sources"][1]["commit"] = "d" * 40
        with self.assertRaisesRegex(ValueError, "source lock differs"):
            self.prepare()
        with self.assertRaisesRegex(ValueError, "source set differs"):
            publication.verify_site(self.portal / "docs", self.selection)
        self.selection["sources"][1]["dirty"] = True
        metadata = json.loads((self.portal / "docs/source-revision.json").read_text())
        metadata["sources"] = self.selection["sources"]
        self.write("docs/source-revision.json", json.dumps(metadata))
        with self.assertRaisesRegex(ValueError, "clean, immutable source set"):
            publication.verify_site(self.portal / "docs", self.selection)

    def test_existing_release_locks_compatibility_evidence(self):
        def prepare_selection(result_id):
            self.set_selection("1.0.0")
            self.add_component()
            self.selection["sources"][1]["compatibility_result"] = {
                "status": "verified", "record": {"id": result_id},
                "feed": {"source": "https://example.invalid/results.json", "sha256": "e" * 64},
            }
            metadata = json.loads((self.portal / "docs/source-revision.json").read_text())
            metadata["sources"] = self.selection["sources"]
            self.write("docs/source-revision.json", json.dumps(metadata))
            self.write("build/sources.lock.json", json.dumps({"sources": self.selection["sources"]}))

        prepare_selection("original-record")
        self.prepare()
        self.deploy_bundle()
        before = self.remote_head()
        self.fresh_checkout()
        prepare_selection("replacement-record")
        with self.assertRaisesRegex(ValueError, "different source set"):
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

    def test_wasm_publication_checks_exact_core_manifest_and_payload(self):
        self.set_selection("1.0.0")
        directory = self.portal / "docs/playground/wasm"
        directory.mkdir(parents=True)
        for name in publication.wasm.FILES:
            data = b"\0asm\x01\0\0\0" if name.endswith(".wasm") else b"export {};\n"
            if name == "query.mjs":
                data = b"export {};\r\n"
            (directory / name).write_bytes(data)
        manifest = {"schema": 1, "repository": "https://github.com/OpenTLV/opentlv",
                    "commit": self.selection["commit"], "local": False, "dirty": False,
                    "source_sha256": "f" * 64, "emscripten": publication.wasm.EMSCRIPTEN,
                    "files": publication.wasm.hashes(directory)}
        self.write("docs/playground/wasm/wasm-source.json", json.dumps(manifest))
        metadata = json.loads((self.portal / "docs/source-revision.json").read_text())
        with patch.dict(os.environ, {"OPENTLV_DOCS_REQUIRE_WASM": "1", "GIT_CONFIG_COUNT": "3",
                                    "GIT_CONFIG_KEY_2": "core.autocrlf", "GIT_CONFIG_VALUE_2": "true"}):
            with self.assertRaisesRegex(ValueError, "WebAssembly"):
                publication.verify_site(self.portal / "docs", self.selection)
            metadata["wasm"] = dict(manifest, manifest="playground/wasm/wasm-source.json")
            self.write("docs/source-revision.json", json.dumps(metadata))
            publication.verify_site(self.portal / "docs", self.selection)
            (directory / "query.mjs").write_text("tampered", encoding="utf-8")
            with self.assertRaisesRegex(Exception, "checksums"):
                publication.verify_site(self.portal / "docs", self.selection)
            (directory / "query.mjs").write_bytes(b"export {};\r\n")
            self.prepare()
            self.deploy_bundle()
            before = self.remote_head()
            # Replaying a release reuses its archived bytes even when today's
            # renderer or generated assets differ.
            original = self.git("rev-parse", "gh-pages:1.0.0")
            self.fresh_checkout()
            self.set_selection("1.0.0")
            self.write("docs/playground/wasm/query.mjs", "export const changed = true;")
            self.write("mkdocs.yml", "invalid: [changed renderer\n")
            self.prepare()
            self.assertEqual(self.git("rev-parse", "gh-pages:1.0.0"), original)
            self.assertEqual(self.remote_head(), before)


class EventPublicationTests(unittest.TestCase):
    """Replay real publication jobs, mocking only GitHub's event evidence API."""

    git = PublicationTests.git
    write = PublicationTests.write
    set_selection = PublicationTests.set_selection
    prepare = PublicationTests.prepare
    remote_head = PublicationTests.remote_head
    deploy_bundle = PublicationTests.deploy_bundle
    fresh_checkout = PublicationTests.fresh_checkout

    def setUp(self):
        PublicationTests.setUp(self)
        self.core = self.base / "core"
        self.core.mkdir()
        publication.run(self.core, "git", "init", "-b", "main")
        (self.core / "docs").mkdir()
        self.releases = {}
        for version in ("1.0.0", "2.0.0"):
            (self.core / "docs/index.md").write_text(f"# Core {version}\n", encoding="utf-8")
            publication.run(self.core, "git", "add", ".")
            publication.run(self.core, "git", "commit", "-m", f"Core {version}")
            publication.run(self.core, "git", "tag", version)
            self.releases[version] = publication.run(self.core, "git", "rev-parse", "HEAD")
        manifest = {"version": 1, "sources": [{
            "id": "core", "repository": "https://github.com/OpenTLV/opentlv",
            "revision": self.releases["1.0.0"], "docs_path": "docs", "mount": "", "required": True,
        }]}
        self.write("docs-sources.json", json.dumps(manifest))
        self.git("add", "docs-sources.json")
        self.git("commit", "-m", "Pin fixture Core")
        self.git("push", "origin", "main")
        # Keep the configured GitHub identity while fetching actual local Git
        # commits and tags. No GitHub or Core build is needed for this fixture.
        config = patch.dict(os.environ, {
            "GIT_CONFIG_COUNT": "3", "GIT_CONFIG_KEY_2": f"url.{self.core.as_uri()}.insteadOf",
            "GIT_CONFIG_VALUE_2": "https://github.com/OpenTLV/opentlv",
        })
        config.start()
        self.addCleanup(config.stop)

    def select_event(self, version, conclusion="success"):
        payload = {"source": "core", "repository": "OpenTLV/opentlv",
                   "commit": self.releases[version], "ref": version, "run_id": 123}
        event_path = self.portal / "build/event.json"
        self.write("build/event.json", json.dumps({"client_payload": payload}))

        def github_response(request, timeout):
            path = request.full_url.removeprefix("https://api.github.com/repos/OpenTLV/opentlv/")
            if path == "actions/runs/123":
                result = {"conclusion": conclusion, "status": "completed", "event": "push",
                          "head_sha": payload["commit"], "head_branch": version,
                          "path": ".github/workflows/wasm.yml",
                          "head_repository": {"full_name": payload["repository"]}}
            elif path == f"git/ref/tags/{version}":
                result = {"object": {"type": "commit", "sha": publication.run(
                    self.core, "git", "rev-parse", f"refs/tags/{version}")}}
            else:
                self.fail(f"Unexpected GitHub request: {request.full_url}")
            return io.StringIO(json.dumps(result))

        with patch.dict(os.environ, {"GITHUB_EVENT_NAME": "repository_dispatch",
                                     "GITHUB_EVENT_PATH": str(event_path)}), \
                patch.object(ci, "ROOT", self.portal), \
                patch.object(ci.events, "urlopen", side_effect=github_response):
            for command in ("select", "fetch"):
                with patch.object(sys, "argv", ["ci.py", command]):
                    ci.main()
        self.selection = json.loads((self.portal / "build/selection.json").read_text(encoding="utf-8"))
        self.assertEqual(self.selection["commit"], payload["commit"])
        self.assertEqual(self.selection["event_commit"], payload["commit"])
        self.assertEqual(self.selection["version"], version)
        self.assertEqual(self.selection["channel"], "release")
        self.assertEqual(publication.run(self.portal / "build/sources/core", "git", "rev-parse", "HEAD"),
                         payload["commit"])
        # API generation is outside this publication fixture; keep its existing
        # clean metadata stub while using the real fetched source lock verbatim.
        metadata = {"repository": "https://github.com/OpenTLV/opentlv", "commit": payload["commit"],
                    "local": False, "dirty": False,
                    "api": {"commit": payload["commit"], "local": False, "dirty": False},
                    "sources": self.selection["sources"]}
        self.write("docs/source-revision.json", json.dumps(metadata))

    def remote_file(self, path):
        return publication.run(self.remote, "git", "show", f"refs/heads/gh-pages:{path}")

    def test_duplicate_release_event_preserves_versions_aliases_and_newer_history(self):
        self.select_event("1.0.0")
        first_selection = self.selection
        self.prepare()
        self.deploy_bundle()
        first_metadata = self.remote_file("1.0.0/source-revision.json")

        self.fresh_checkout()
        self.select_event("2.0.0")
        self.prepare()
        self.deploy_bundle()
        before = self.remote_head().split()[0]
        versions = json.loads(self.remote_file("versions.json"))
        stable = self.remote_file("stable/source-revision.json")
        default = self.remote_file("index.html")
        newer_tree = publication.run(self.remote, "git", "rev-parse", "gh-pages:2.0.0")

        self.fresh_checkout()
        self.select_event("1.0.0")
        self.assertEqual(self.selection, first_selection)
        self.prepare()
        self.deploy_bundle()
        self.assertEqual(self.remote_file("1.0.0/source-revision.json"), first_metadata)
        self.assertEqual(json.loads(self.remote_file("versions.json")), versions)
        self.assertEqual({item["version"] for item in versions}, {"1.0.0", "2.0.0"})
        self.assertEqual(next(item["version"] for item in versions if "stable" in item["aliases"]), "2.0.0")
        self.assertEqual(self.remote_file("stable/source-revision.json"), stable)
        self.assertEqual(self.remote_file("index.html"), default)
        self.assertEqual(publication.run(self.remote, "git", "rev-parse", "gh-pages:2.0.0"), newer_tree)
        publication.run(self.remote, "git", "merge-base", "--is-ancestor", before, "gh-pages")

    def test_failed_event_and_failed_event_build_preserve_last_publication(self):
        self.select_event("1.0.0")
        self.prepare()
        self.deploy_bundle()
        before = self.remote_head()
        versions = self.remote_file("versions.json")
        stable = self.remote_file("stable/source-revision.json")

        self.fresh_checkout()
        with self.assertRaisesRegex(ValueError, "trusted push"):
            self.select_event("2.0.0", conclusion="failure")
        self.assertEqual(self.remote_head(), before)
        self.assertFalse((self.portal / "build/selection.json").exists())
        self.assertFalse((self.portal / "build/publication/history.bundle").exists())

        self.fresh_checkout()
        self.select_event("2.0.0")
        self.write("docs/index.md", "# Broken update\n\n[Missing](missing.md)\n")
        with self.assertRaisesRegex(RuntimeError, "Command failed"):
            self.prepare()
        self.assertEqual(self.remote_head(), before)
        self.assertEqual(self.remote_file("versions.json"), versions)
        self.assertEqual(self.remote_file("stable/source-revision.json"), stable)
        self.assertFalse((self.portal / "build/publication/history.bundle").exists())


if __name__ == "__main__":
    unittest.main()
