# SPDX-License-Identifier: MIT
# Copyright (c) 2026 Marek Cingel

"""Multi-repository integration with independent local Git histories."""

import copy
import json
import os
import subprocess
import unittest
from unittest.mock import patch

from mkdocs.exceptions import PluginError

import test_portal as fixture
from test_publication import ci, publication

assembly = fixture.assembly


class MultiRepositoryTests(unittest.TestCase):
    write = fixture.PortalTests.write
    git = fixture.PortalTests.git
    mkdocs = fixture.PortalTests.mkdocs

    def setUp(self):
        fixture.PortalTests.setUp(self)
        self.component = self.base / "python"
        self.write(self.component / "manual/index.md", "# Python\n\n[License](../LICENSE)\n")
        self.write(self.component / "LICENSE", "Python license\n")
        self.component_git("init", "-b", "main")
        self.commit_component()
        self.component_sha = self.component_git("rev-parse", "HEAD")
        self.component_git("tag", "v2")
        self.manifest = json.loads((self.portal / "docs-sources.json").read_text())
        self.manifest["sources"].append({
            "id": "python", "repository": "https://github.com/OpenTLV/python",
            "revision": "v2", "docs_path": "manual", "mount": "bindings/python",
            "required": False,
            "navigation": {"title": "Python", "section": ["Bindings"],
                           "items": [{"Overview": "index.md"}]},
        })
        self.save_manifest()

    def component_git(self, *args):
        return subprocess.check_output(["git", "-C", str(self.component), *args], stderr=subprocess.PIPE).decode().strip()

    def commit_component(self):
        self.component_git("add", ".")
        self.component_git("-c", "user.name=Fixture", "-c", "user.email=fixture@example.invalid",
                           "-c", "commit.gpgsign=false", "commit", "-m", "Component docs")

    def save_manifest(self):
        self.write(self.portal / "docs-sources.json", json.dumps(self.manifest))

    def metadata(self):
        return json.loads((self.portal / "site/source-revision.json").read_text())

    def test_strict_build_independent_revisions_navigation_and_ownership(self):
        result = self.mkdocs()
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        metadata = self.metadata()
        self.assertEqual([s["commit"] for s in metadata["sources"]], [self.sha, self.component_sha])
        self.assertNotIn(str(self.component), json.dumps(metadata))
        html = (self.portal / "site/bindings/python/index.html").read_text(encoding="utf-8")
        self.assertIn(f"https://github.com/OpenTLV/python/edit/{self.component_sha}/manual/index.md", html)
        self.assertIn(f"https://github.com/OpenTLV/python/blob/{self.component_sha}/LICENSE", html)
        self.assertIn("Bindings", html)
        assembly.assemble(self.portal)
        # Assembly metadata has no API addition; repeated assemblies are deterministic.
        first = (self.portal / "build/assembled/source-revision.json").read_bytes()
        assembly.assemble(self.portal)
        self.assertEqual(first, (self.portal / "build/assembled/source-revision.json").read_bytes())
        self.assertEqual(self.component_git("status", "--porcelain"), "")

    def test_locked_multi_repository_mike_publication(self):
        result = self.mkdocs()
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        selected = self.metadata()["sources"]
        self.write(self.portal / "build/sources.lock.json", json.dumps({
            "manifest": self.manifest["sources"], "sources": selected,
        }))
        self.write(self.portal / ".gitignore", "build/\nsite/\n")
        remote = self.base / "publication.git"
        env = {"GIT_AUTHOR_NAME": "Fixture", "GIT_AUTHOR_EMAIL": "fixture@example.invalid",
               "GIT_COMMITTER_NAME": "Fixture", "GIT_COMMITTER_EMAIL": "fixture@example.invalid",
               "GIT_CONFIG_COUNT": "1", "GIT_CONFIG_KEY_0": "commit.gpgsign", "GIT_CONFIG_VALUE_0": "false"}
        with patch.dict(os.environ, env):
            publication.run(self.portal, "git", "init", "--bare", str(remote))
            publication.run(self.portal, "git", "init", "-b", "main")
            publication.run(self.portal, "git", "remote", "add", "origin", str(remote))
            publication.run(self.portal, "git", "add", ".")
            publication.run(self.portal, "git", "commit", "-m", "Publication fixture")
            selection = ci.select(self.manifest["sources"][0], "development")
            selection.update(commit=self.sha, sources=selected)
            publication.prepare(self.portal, selection)
        site = self.portal / "build/publication/site/latest"
        self.assertTrue((site / "bindings/python/index.html").is_file())
        self.assertEqual(json.loads((site / "source-revision.json").read_text())["sources"], selected)
        self.assertEqual(publication.run(self.portal, "git", "ls-remote", "origin", "refs/heads/gh-pages"), "")

    def test_optional_missing_is_recorded_and_removed_from_navigation(self):
        self.manifest["sources"][1]["repository"] = "https://github.com/OpenTLV/absent"
        self.save_manifest()
        result = self.mkdocs()
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertFalse(self.metadata()["sources"][1]["included"])
        self.assertNotIn("bindings/python", (self.portal / "site/index.html").read_text(encoding="utf-8"))
        self.manifest["sources"][1]["required"] = True
        self.save_manifest()
        with self.assertRaisesRegex(PluginError, "missing"):
            assembly.assemble(self.portal)

    def test_omitted_optional_links_remain_external(self):
        self.manifest["sources"][1]["repository"] = "https://github.com/OpenTLV/absent"
        self.save_manifest()
        target = "https://github.com/OpenTLV/absent/blob/v2/manual/index.md#python"
        self.write(self.core / "docs/index.md", f"# Home\n\n[Optional component]({target})\n")
        with patch.dict(os.environ, {"OPENTLV_DOCS_LOCAL": "1"}):
            result = self.mkdocs()
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertIn(target, (self.portal / "site/index.html").read_text(encoding="utf-8"))

    def test_optional_invalid_revision_and_dirty_checkout_are_errors(self):
        self.manifest["sources"][1]["revision"] = "main"
        self.save_manifest()
        with self.assertRaises(PluginError):
            assembly.assemble(self.portal)
        self.manifest["sources"][1]["revision"] = "v2"
        self.save_manifest()
        self.write(self.component / "manual/index.md", "# Local\n")
        with self.assertRaisesRegex(PluginError, "dirty"):
            assembly.assemble(self.portal)
        with patch.dict(os.environ, {"OPENTLV_DOCS_LOCAL": "1"}):
            result = self.mkdocs()
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertTrue(self.metadata()["sources"][1]["dirty"])

    def test_explicit_workspace_override_and_missing_override(self):
        self.manifest["sources"][1]["repository"] = "https://github.com/OpenTLV/elsewhere"
        self.save_manifest()
        with patch.dict(os.environ, {"OPENTLV_PYTHON_DIR": str(self.component)}):
            self.assertTrue(assembly.assemble(self.portal)[1]["sources"][1]["included"])
        with patch.dict(os.environ, {"OPENTLV_PYTHON_DIR": str(self.base / "missing")}):
            with self.assertRaisesRegex(PluginError, "explicitly selected"):
                assembly.assemble(self.portal)

    def test_cross_repository_links_and_anchors_in_both_directions(self):
        self.write(self.component / "manual/index.md",
                   f'# Python\n\n[Core][core]\n\n[core]: https://github.com/OpenTLV/opentlv/blob/{self.sha}/docs/index.md#home\n')
        self.commit_component()
        component_sha = self.component_git("rev-parse", "HEAD")
        self.manifest["sources"][1]["revision"] = component_sha
        self.save_manifest()
        self.write(self.core / "docs/index.md",
                   f'# Home\n\n<a href="https://github.com/OpenTLV/python/blob/{component_sha}/manual/index.md#python">Python</a>\n')
        with patch.dict(os.environ, {"OPENTLV_DOCS_LOCAL": "1"}):
            result = self.mkdocs()
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        html = (self.portal / "site/index.html").read_text(encoding="utf-8")
        self.assertIn('href="bindings/python/#python"', html)
        html = (self.portal / "site/bindings/python/index.html").read_text(encoding="utf-8")
        self.assertIn('href="../../#home"', html)
        for target in ("index.md#missing", "missing.md"):
            self.write(self.core / "docs/index.md", f'# Home\n\n[Python](https://github.com/OpenTLV/python/blob/{component_sha}/manual/{target})\n')
            with patch.dict(os.environ, {"OPENTLV_DOCS_LOCAL": "1"}):
                result = self.mkdocs()
            self.assertNotEqual(result.returncode, 0, result.stdout + result.stderr)

    def test_collision_and_unsafe_paths_fail_before_replacing_assembly(self):
        assembly.assemble(self.portal)
        output = self.portal / "build/assembled/docs/index.md"
        before = output.read_bytes()
        for changes in ({"mount": "../outside"}, {"docs_path": "../outside"}, {"id": "core"},
                        {"mount": "INDEX.md"}, {"mount": "API/Reference/C-API"}, {"mount": "SOURCE-REVISION.JSON"}):
            original = dict(self.manifest["sources"][1])
            self.manifest["sources"][1].update(changes)
            self.save_manifest()
            with self.assertRaises(PluginError):
                assembly.assemble(self.portal)
            self.assertEqual(output.read_bytes(), before)
            self.manifest["sources"][1] = original

    def test_invalid_registration_metadata_preserves_previous_ownership(self):
        assembly.assemble(self.portal)
        output = self.portal / "build/assembled"
        before = {name: (output / name).read_bytes()
                  for name in ("docs/index.md", "owners.json", "source-revision.json")}
        original = copy.deepcopy(self.manifest)
        invalid = []
        for scope, key, value in (("manifest", "version", True), ("manifest", "source", []),
                                  ("source", "revison", "v3"), ("source", "owner", "core"),
                                  ("navigation", "itmes", [])):
            candidate = copy.deepcopy(original)
            target = (candidate if scope == "manifest" else candidate["sources"][1]
                      if scope == "source" else candidate["sources"][1]["navigation"])
            target[key] = value
            invalid.append(json.dumps(candidate))
        serialized = json.dumps(original)
        invalid.extend((serialized.replace('"version": 1', '"version": 1, "version": 1'),
                        serialized.replace('"revision": "v2"', '"revision": "v2", "revision": "v3"'),
                        serialized.replace('"title": "Python"', '"title": "Python", "title": "Other"')))
        for value in invalid:
            with self.subTest(manifest=value):
                self.write(self.portal / "docs-sources.json", value)
                with self.assertRaises(PluginError):
                    assembly.assemble(self.portal)
                self.assertEqual(before, {name: (output / name).read_bytes() for name in before})

    def test_duplicate_repository_registration_rejected_before_checkout(self):
        original = copy.deepcopy(self.manifest)
        for repository in ("https://github.com/OpenTLV/python", "https://github.com/OpenTLV/python.git/",
                           "https://GITHUB.COM/opentlv/PYTHON"):
            with self.subTest(repository=repository):
                self.manifest = copy.deepcopy(original)
                duplicate = copy.deepcopy(self.manifest["sources"][1])
                duplicate.update(id="other", repository=repository, mount="other")
                duplicate["navigation"]["title"] = "Other"
                self.manifest["sources"].append(duplicate)
                self.save_manifest()
                with self.assertRaisesRegex(PluginError, "Duplicate documentation registration"):
                    assembly.sources.manifest(self.portal)
        # Independently owned documentation trees within one repository remain
        # valid when their source directories and portal mounts are distinct.
        duplicate["docs_path"] = "other-manual"
        self.save_manifest()
        self.assertEqual(len(assembly.sources.manifest(self.portal)), 3)

    def test_local_and_non_github_repositories_keep_distinct_git_suffixes(self):
        other = self.base / "python.git"
        self.write(other / "manual/index.md", "# Independent repository\n")
        assembly.git(other, "init", "-b", "main")
        assembly.git(other, "add", ".")
        assembly.git(other, "-c", "user.name=Fixture", "-c", "user.email=fixture@example.invalid",
                     "-c", "commit.gpgsign=false", "commit", "-m", "Independent repository")
        source = self.manifest["sources"][1]
        source.update(repository=self.component.as_uri(), revision=self.component_sha)
        second = copy.deepcopy(source)
        second.update(id="other", repository=other.as_uri(), mount="other",
                      revision=assembly.git(other, "rev-parse", "HEAD"))
        second["navigation"]["title"] = "Other"
        self.manifest["sources"].append(second)
        self.save_manifest()
        with patch.dict(os.environ, {"OPENTLV_PYTHON_DIR": str(self.component), "OPENTLV_OTHER_DIR": str(other)}):
            selected = assembly.selected_sources(self.portal)
        self.assertEqual([root for root, _ in selected[1:]], [self.component, other])
        self.assertNotEqual(selected[1][1]["commit"], selected[2][1]["commit"])
        # Other HTTPS servers need not treat a .git suffix or path case as aliases.
        source["repository"] = "https://git.example.invalid/python"
        for repository in ("https://git.example.invalid/python.git", "https://git.example.invalid/Python"):
            with self.subTest(repository=repository):
                second["repository"] = repository
                self.save_manifest()
                self.assertEqual(len(assembly.sources.manifest(self.portal)), 3)

    def test_overlapping_component_mounts_fail_even_when_optional_source_absent(self):
        original = copy.deepcopy(self.manifest)
        for mount in ("bindings/python", "Bindings/Python", "bindings/python/extra", "bindings"):
            with self.subTest(mount=mount):
                self.manifest = copy.deepcopy(original)
                duplicate = copy.deepcopy(self.manifest["sources"][1])
                duplicate.update(id="absent", repository="https://github.com/OpenTLV/absent", mount=mount)
                duplicate["navigation"]["title"] = "Other"
                self.manifest["sources"].append(duplicate)
                self.save_manifest()
                with self.assertRaisesRegex(PluginError, "Overlapping documentation mounts"):
                    assembly.assemble(self.portal)

    def test_fetch_from_git_and_lock_survives_moved_tag(self):
        self.manifest["sources"][0]["repository"] = self.core.as_uri()
        self.manifest["sources"][1]["repository"] = self.component.as_uri()
        self.save_manifest()
        lock = assembly.sources.fetch(self.portal, self.sha)
        self.assertEqual(lock["sources"][1]["commit"], self.component_sha)
        env = {"OPENTLV_DOCS_SOURCE_ROOT": str(self.portal / "build/sources"),
               "OPENTLV_DOCS_LOCK": str(self.portal / "build/sources.lock.json")}
        with patch.dict(os.environ, env):
            os.environ.pop("OPENTLV_CORE_DIR", None)
            selected = assembly.selected_sources(self.portal)
            self.assertEqual(selected[1][1]["commit"], self.component_sha)
            result = self.mkdocs()
            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
            self.assertEqual(self.metadata()["sources"], lock["sources"])
            managed = selected[1][0]
            self.write(managed / "manual/index.md", "# New tag target\n")
            assembly.git(managed, "add", ".")
            assembly.git(managed, "-c", "user.name=Fixture", "-c", "user.email=fixture@example.invalid",
                         "-c", "commit.gpgsign=false", "commit", "-m", "Move tag")
            assembly.git(managed, "tag", "-f", "v2")
            with self.assertRaisesRegex(PluginError, "HEAD does not match"):
                assembly.selected_sources(self.portal)
            assembly.git(managed, "checkout", "--detach", self.component_sha)
            self.assertEqual(assembly.selected_sources(self.portal)[1][1]["commit"], self.component_sha)
            self.manifest["sources"][1]["mount"] = "other"
            self.save_manifest()
            with self.assertRaisesRegex(PluginError, "lock does not match"):
                assembly.selected_sources(self.portal)

    def test_fetch_optional_unavailable_but_invalid_tag_is_not_silenced(self):
        self.manifest["sources"][0]["repository"] = self.core.as_uri()
        self.manifest["sources"][1]["repository"] = (self.base / "absent.git").as_uri()
        self.save_manifest()
        lock = assembly.sources.fetch(self.portal, self.sha)
        self.assertFalse(lock["sources"][1]["included"])
        with patch.dict(os.environ, {
            "OPENTLV_DOCS_SOURCE_ROOT": str(self.portal / "build/sources"),
            "OPENTLV_DOCS_LOCK": str(self.portal / "build/sources.lock.json"),
        }):
            os.environ.pop("OPENTLV_CORE_DIR", None)
            self.assertEqual(assembly.selected_sources(self.portal)[1][1], lock["sources"][1])
        # A new portal avoids changing any already fetched checkout.
        other = self.base / "other"
        self.manifest["sources"][1].update(repository=self.component.as_uri(), revision="no-such-tag")
        self.write(other / "docs-sources.json", json.dumps(self.manifest))
        with self.assertRaises(PluginError):
            assembly.sources.fetch(other, self.sha)


if __name__ == "__main__":
    unittest.main()
