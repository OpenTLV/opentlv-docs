# SPDX-License-Identifier: MIT
# Copyright (c) 2026 Marek Cingel

"""Behavioral checks using disposable Git repositories, never the user's Core."""

import importlib.util
import json
import os
from pathlib import Path
import socket
import subprocess
import sys
import tempfile
import time
from types import SimpleNamespace
import unittest
from unittest.mock import patch
from urllib.error import URLError
from urllib.request import urlopen

from mkdocs.exceptions import PluginError

ROOT = Path(__file__).resolve().parents[1]


def load_hook(name):
    spec = importlib.util.spec_from_file_location(name, ROOT / "tools" / "docs" / f"{name}.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


assembly = load_hook("assembly")
hooks = load_hook("hooks")


class PortalTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.base = Path(self.temp.name).resolve()
        self.core = self.base / "core with spaces"
        self.portal = self.base / "portal"
        self.write(self.core / "docs/index.md", "# Home\n\n[Source](../LICENSE)\n")
        self.write(self.core / "docs/README.md", "# GitHub index\n")
        self.write(self.core / "docs/assets/README.md", "# Old asset page\n")
        self.write(self.core / "LICENSE", "Core license\n")
        self.write(self.core / ".gitignore", "ignored/\n")
        # A compiler-free stand-in for Core's generation contract. Real Doxygen
        # is also exercised separately against the selected Core checkout.
        self.write(self.core / "fixture.html", '<html><a id="api" href="https://fixture.invalid/docs/">Guide</a></html>')
        self.write(self.core / "CMakeLists.txt", f'''cmake_minimum_required(VERSION 3.20)
project(Fixture NONE)
set(DOXYGEN_EXECUTABLE "{Path(sys.executable).as_posix()}" CACHE FILEPATH "Fixture version provider")
file(WRITE "${{CMAKE_BINARY_DIR}}/Doxyfile.common" [=[WARN_AS_ERROR = YES
ALIASES = "docs{{2}}=<a href=\\"https://fixture.invalid/docs/\\1/\\">\\2</a>"
]=])
add_custom_target(c-api-docs
  COMMAND "${{CMAKE_COMMAND}}" -E make_directory "${{CMAKE_BINARY_DIR}}/docs/c-api/html"
  COMMAND "${{CMAKE_COMMAND}}" -E copy "${{CMAKE_SOURCE_DIR}}/fixture.html" "${{CMAKE_BINARY_DIR}}/docs/c-api/html/index.html")
add_custom_target(cxx-api-docs
  COMMAND "${{CMAKE_COMMAND}}" -E make_directory "${{CMAKE_BINARY_DIR}}/docs/cxx-api/html"
  COMMAND "${{CMAKE_COMMAND}}" -E copy "${{CMAKE_SOURCE_DIR}}/fixture.html" "${{CMAKE_BINARY_DIR}}/docs/cxx-api/html/index.html")
add_dependencies(cxx-api-docs c-api-docs)
''')
        self.git("init", "-b", "main")
        self.git("add", ".")
        self.git("-c", "user.name=Fixture", "-c", "user.email=fixture@example.invalid",
                 "-c", "commit.gpgsign=false", "commit", "-m", "Test fixture")
        self.sha = self.git("rev-parse", "HEAD")
        self.git("tag", "v1")
        self.git("-c", "user.name=Fixture", "-c", "user.email=fixture@example.invalid",
                 "-c", "tag.gpgsign=false", "tag", "-a", "v1-annotated", "-m", "Fixture release")
        self.write(self.portal / "docs-sources.json", json.dumps({
            "version": 1, "sources": [{"id": "core", "docs_path": "docs", "mount": "", "required": True,
            "repository": "https://github.com/OpenTLV/opentlv", "revision": self.sha}],
        }))
        self.write(self.portal / "docs/assets/README.md", "# Assets\n\n[License](../../LICENSE)\n")
        self.write(self.portal / "docs/assets/logo-mark.svg", "<svg/>")
        self.write(self.portal / "LICENSE", "Portal license\n")
        for tree in ("c-api", "cxx-api"):
            self.write(self.portal / f"build/api/docs/{tree}/html/index.html", "<html>Fixture</html>")
        clean_env = {key: value for key, value in os.environ.items() if not key.startswith("OPENTLV_")}
        clean_env["OPENTLV_CORE_DIR"] = str(self.core)
        self.env = patch.dict(os.environ, clean_env, clear=True)
        self.env.start()
        self.addCleanup(self.env.stop)

    def write(self, path, text):
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(text, encoding="utf-8")

    def git(self, *args):
        return subprocess.check_output(["git", "-C", str(self.core), *args], stderr=subprocess.PIPE).decode().strip()

    def config(self):
        root, source = assembly.assemble(self.portal)
        return SimpleNamespace(
            config_file_path=str(self.portal / "mkdocs.yml"),
            repo_url="https://github.com/OpenTLV/opentlv",
            extra={"core_source": source, "core_checkout": str(root),
                   "portal_repository": "https://github.com/OpenTLV/opentlv-docs"},
        )

    def test_clean_assembly_preserves_core_and_overlays_portal_assets(self):
        before = self.git("status", "--porcelain")
        root, source = assembly.assemble(self.portal)
        self.assertEqual(root, self.core)
        self.assertEqual(source["commit"], self.sha)
        self.assertFalse(source["local"] or source["dirty"])
        docs = self.portal / "build/assembled/docs"
        self.assertEqual((docs / "index.md").read_bytes(), (self.core / "docs/index.md").read_bytes())
        self.assertIn("# Assets", (docs / "assets/README.md").read_text())
        self.assertIn("# Old asset page", (self.core / "docs/assets/README.md").read_text())
        self.assertEqual(self.git("status", "--porcelain"), before)
        snapshot = {p.relative_to(docs): p.read_bytes() for p in docs.rglob("*") if p.is_file()}
        self.write(docs / "stale.md", "stale")
        assembly.assemble(self.portal)
        self.assertFalse((docs / "stale.md").exists())
        self.assertEqual(snapshot, {p.relative_to(docs): p.read_bytes() for p in docs.rglob("*") if p.is_file()})
        self.assertEqual((docs / "assets/logo-mark.svg").read_text(), "<svg/>")

    def test_unexpected_collision_rejected_before_replacing_output(self):
        assembly.assemble(self.portal)
        docs = self.portal / "build/assembled/docs"
        before = (docs / "index.md").read_bytes()
        self.write(self.portal / "docs/index.md", "# Unexpected replacement")
        with self.assertRaisesRegex(PluginError, "collision.*index.md.*Core and portal"):
            assembly.assemble(self.portal)
        self.assertEqual((docs / "index.md").read_bytes(), before)
        self.assertEqual((self.core / "docs/index.md").read_bytes(), before)

    def test_file_directory_collision_rejected(self):
        self.write(self.portal / "docs/index.md/child.md", "# Invalid child")
        with self.assertRaisesRegex(PluginError, "file/directory collision"):
            assembly.assemble(self.portal)

    def test_tag_and_annotated_tag_resolve_to_commit(self):
        for tag in ("v1", "v1-annotated"):
            with self.subTest(tag=tag), patch.dict(os.environ, {"OPENTLV_CORE_REF": tag}):
                self.assertEqual(assembly.selected_source(self.portal)[1]["commit"], self.sha)

    def test_branch_short_sha_and_unknown_revision_rejected(self):
        for ref in ("main", self.sha[:8], "missing-tag", "v1^", "v1~0"):
            with self.subTest(ref=ref), patch.dict(os.environ, {"OPENTLV_CORE_REF": ref}):
                with self.assertRaises(PluginError):
                    assembly.selected_source(self.portal)

    def advance_core(self):
        self.write(self.core / "LICENSE", "changed")
        self.git("add", "LICENSE")
        self.git("-c", "user.name=Fixture", "-c", "user.email=fixture@example.invalid",
                 "-c", "commit.gpgsign=false", "commit", "-m", "New fixture revision")
        return self.git("rev-parse", "HEAD")

    def test_wrong_checkout_revision_rejected_by_normal_and_release_builds(self):
        self.advance_core()
        for channel in ("development", "release"):
            with patch.dict(os.environ, {"OPENTLV_DOCS_CHANNEL": channel}):
                with self.assertRaisesRegex(PluginError, "HEAD does not match"):
                    assembly.selected_source(self.portal)

    def test_local_preview_uses_current_head_and_preserves_configured_revision(self):
        head = self.advance_core()
        before = self.git("status", "--porcelain")
        with patch.dict(os.environ, {"OPENTLV_DOCS_LOCAL": "1"}):
            result = self.mkdocs()
        self.assertEqual(result.returncode, 0, result.stderr)
        source = json.loads((self.portal / "site/source-revision.json").read_text())
        self.assertEqual(source["revision"], self.sha)
        self.assertEqual(source["commit"], head)
        self.assertTrue(source["local"])
        self.assertFalse(source["dirty"])
        html = (self.portal / "site/index.html").read_text(encoding="utf-8")
        self.assertIn(f"/blob/{head}/LICENSE", html)
        self.assertIn(f"/edit/{head}/docs/index.md", html)
        self.assertIn("Local preview", html)
        self.assertEqual(self.git("status", "--porcelain"), before)
        self.assertEqual(self.git("rev-parse", "HEAD"), head)

    def test_local_preview_does_not_require_pinned_commit_in_checkout(self):
        missing_commit = "0" * 40
        with patch.dict(os.environ, {"OPENTLV_DOCS_LOCAL": "1", "OPENTLV_CORE_REF": missing_commit}):
            _, source = assembly.selected_source(self.portal)
        self.assertEqual(source["revision"], missing_commit)
        self.assertEqual(source["commit"], self.sha)

    def test_dirty_and_untracked_sources_rejected_by_default(self):
        self.write(self.core / "docs/new.md", "# New page")
        with self.assertRaisesRegex(PluginError, "dirty"):
            assembly.selected_source(self.portal)
        (self.core / "docs/new.md").unlink()
        self.write(self.core / "docs/index.md", "# Modified")
        with self.assertRaisesRegex(PluginError, "dirty"):
            assembly.selected_source(self.portal)

    def test_local_preview_includes_changes_additions_and_deletions(self):
        head = self.advance_core()
        self.write(self.core / "docs/index.md", "# Modified")
        self.write(self.core / "docs/new.md", "# New")
        (self.core / "docs/README.md").unlink()
        self.write(self.core / "docs/ignored/debris.md", "not a source")
        with patch.dict(os.environ, {"OPENTLV_DOCS_LOCAL": "1"}):
            _, source = assembly.assemble(self.portal)
        self.assertTrue(source["local"] and source["dirty"])
        self.assertEqual(source["revision"], self.sha)
        self.assertEqual(source["commit"], head)
        docs = self.portal / "build/assembled/docs"
        self.assertEqual((docs / "index.md").read_text(), "# Modified")
        self.assertTrue((docs / "new.md").exists())
        self.assertFalse((docs / "README.md").exists())
        self.assertFalse((docs / "ignored/debris.md").exists())

    def test_source_and_edit_links_use_owning_repository(self):
        config = self.config()
        page = SimpleNamespace(file=SimpleNamespace(src_uri="index.md"))
        result = hooks.on_page_markdown("[Source](../LICENSE?raw=1#license)", page, config, [])
        self.assertEqual(result, f"[Source](https://github.com/OpenTLV/opentlv/blob/{self.sha}/LICENSE?raw=1#license)")
        self.assertEqual(page.edit_url, f"https://github.com/OpenTLV/opentlv/edit/{self.sha}/docs/index.md")
        page.file.src_uri = "assets/README.md"
        result = hooks.on_page_markdown("[License](../../LICENSE)", page, config, [])
        self.assertEqual(result, "[License](https://github.com/OpenTLV/opentlv-docs/blob/main/LICENSE)")
        self.assertEqual(page.edit_url, "https://github.com/OpenTLV/opentlv-docs/edit/main/docs/assets/README.md")
        owners_path = self.portal / "build/assembled/owners.json"
        owners = json.loads(owners_path.read_text(encoding="utf-8"))
        for language in ("python", "lua"):
            root = self.base / language
            self.write(root / "LICENSE", f"{language} license\n")
            repository = f"https://github.com/OpenTLV/opentlv-{language}"
            config.extra["core_source"]["sources"].append({
                "id": language, "repository": repository, "commit": "a" * 40, "docs_path": "manual",
            })
            page.file.src_uri = f"bindings/{language}/index.md"
            owners[page.file.src_uri] = {"id": language, "root": str(root), "path": "manual/index.md"}
            owners_path.write_text(json.dumps(owners), encoding="utf-8")
            result = hooks.on_page_markdown("[License](../LICENSE)", page, config, [])
            self.assertEqual(page.edit_url, f"{repository}/edit/{'a' * 40}/manual/index.md")
            self.assertEqual(result, f"[License]({repository}/blob/{'a' * 40}/LICENSE)")

    def test_index_rewrite_preserves_fragment_and_other_links(self):
        config = self.config()
        page = SimpleNamespace(file=SimpleNamespace(src_uri="guides/reader.md"))
        self.assertEqual(hooks.on_page_markdown("[Home](../README.md#home)", page, config, []),
                         "[Home](../index.md#home)")
        text = "[Other](writer.md) [Remote](https://example.com/) ![Image](../image.svg)"
        self.assertEqual(hooks.on_page_markdown(text, page, config, []), text)

    def test_missing_source_link_warns(self):
        config = self.config()
        page = SimpleNamespace(file=SimpleNamespace(src_uri="index.md"))
        with self.assertLogs("mkdocs.hooks.opentlv", level="WARNING"):
            hooks.on_page_markdown("[Missing](../missing.c)", page, config, [])

    def mkdocs(self):
        self.write(self.portal / "mkdocs.yml", f"""site_name: Fixture
site_url: https://opentlv.github.io/opentlv-docs/
docs_dir: docs
strict: true
repo_url: https://github.com/OpenTLV/opentlv
repo_name: OpenTLV/opentlv
theme:
  name: material
  custom_dir: '{(ROOT / 'tools/docs/overrides').as_posix()}'
  features:
    - content.action.edit
    - content.tabs.link
markdown_extensions:
  - pymdownx.superfences
  - pymdownx.blocks.tab:
      alternate_style: true
extra:
  docs_channel: development
  portal_repository: https://github.com/OpenTLV/opentlv-docs
exclude_docs: /README.md
validation:
  nav:
    omitted_files: warn
  links:
    anchors: warn
hooks:
  - '{(ROOT / 'tools/docs/assembly.py').as_posix()}'
  - '{(ROOT / 'tools/docs/hooks.py').as_posix()}'
nav:
  - Home: index.md
  - Assets: assets/README.md
""")
        return subprocess.run([sys.executable, "-m", "mkdocs", "build", "--strict"],
                              cwd=self.portal, capture_output=True, text=True, encoding="utf-8", errors="replace")

    def test_strict_build_and_published_provenance_without_optional_components(self):
        with patch.dict(os.environ, {"OPENTLV_DOCS_PUBLISH": "1"}):
            result = self.mkdocs()
        self.assertEqual(result.returncode, 0, result.stderr)
        site = self.portal / "site"
        source = json.loads((site / "source-revision.json").read_text())
        self.assertEqual(source["commit"], self.sha)
        self.assertNotIn(str(self.core), json.dumps(source))
        html = (site / "index.html").read_text(encoding="utf-8")
        self.assertRegex(html, r'<a\b[^>]*href="https://github.com/OpenTLV/opentlv"[^>]*class="md-source"')
        self.assertIn(f'https://github.com/OpenTLV/opentlv/edit/{self.sha}/docs/index.md', html)
        asset_html = (site / "assets/index.html").read_text(encoding="utf-8")
        self.assertIn('https://github.com/OpenTLV/opentlv-docs/edit/main/docs/assets/README.md', asset_html)
        self.assertIn(f"/edit/{self.sha}/docs/index.md", html)
        self.assertIn("development", html)
        self.assertTrue((site / "reference/api/cxx-api/html/index.html").exists())

    def test_publication_and_release_builds_reject_local_preview(self):
        for flag in ({"OPENTLV_DOCS_CHANNEL": "release"}, {"OPENTLV_DOCS_PUBLISH": "1"}):
            with self.subTest(flag=flag), patch.dict(os.environ, {"OPENTLV_DOCS_LOCAL": "1", **flag}):
                result = self.mkdocs()
            self.assertNotEqual(result.returncode, 0)
            self.assertIn("Local preview cannot be used for publication", result.stdout + result.stderr)

    def test_deployment_commands_reject_local_preview_before_writing(self):
        for command in ("gh-deploy", "mike"):
            with self.subTest(command=command), patch.dict(os.environ, {"OPENTLV_DOCS_LOCAL": "1"}):
                with self.assertRaisesRegex(PluginError, "Local preview cannot be used for publication"):
                    assembly.on_startup(command=command, dirty=False)
        self.assertFalse((self.portal / "build/assembled").exists())

    def test_deployment_entry_points_enforce_local_guard(self):
        from mike.mkdocs_utils import load_config

        result = self.mkdocs()  # Create a valid config before probing entry points.
        self.assertEqual(result.returncode, 0, result.stderr)
        before = (self.portal / "site/source-revision.json").read_bytes()
        with patch.dict(os.environ, {"OPENTLV_DOCS_LOCAL": "1"}):
            with self.assertRaisesRegex(PluginError, "Local preview cannot be used for publication"):
                load_config(str(self.portal / "mkdocs.yml"))
            # MkDocs runs startup before any deployment operation. This fixture
            # has no portal Git repository or remote to publish even on failure.
            result = subprocess.run([sys.executable, "-m", "mkdocs", "gh-deploy"],
                                    cwd=self.portal, capture_output=True, text=True,
                                    encoding="utf-8", errors="replace")
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("Local preview cannot be used for publication", result.stdout + result.stderr)
        self.assertEqual((self.portal / "site/source-revision.json").read_bytes(), before)

    def test_release_channel_in_config_rejects_local_preview(self):
        config = SimpleNamespace(extra={"docs_channel": "release"})
        with patch.dict(os.environ, {"OPENTLV_DOCS_LOCAL": "1"}):
            with self.assertRaisesRegex(PluginError, "Local preview cannot be used for publication"):
                assembly.on_config(config)

    def test_missing_api_reference_fails_build(self):
        self.assertEqual(self.mkdocs().returncode, 0)
        (self.portal / "build/api/docs/cxx-api/html/index.html").unlink()
        with patch.dict(os.environ, {"OPENTLV_API_DOCS_DIR": str(self.portal / "build/api/docs")}):
            result = self.mkdocs()
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("generated API reference not found", result.stdout + result.stderr)

    def test_explicitly_required_wasm_fails_when_missing(self):
        with patch.dict(os.environ, {"OPENTLV_DOCS_REQUIRE_WASM": "1"}):
            result = self.mkdocs()
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("WebAssembly module files", result.stdout + result.stderr)

    def test_external_artifacts_require_matching_provenance_and_checksums(self):
        result = self.mkdocs()
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        directory = self.portal / "build/api/docs"
        manifest_path = directory / hooks.api.MANIFEST
        original = manifest_path.read_text()
        manifest = json.loads(original)
        self.assertEqual(manifest["commit"], self.sha)
        self.assertEqual(manifest["source_sha256"], hooks.api.fingerprint(self.core))
        with patch.dict(os.environ, {"OPENTLV_API_DOCS_DIR": str(directory)}):
            for change, error in (({"commit": "0" * 40}, "does not match"),
                                  ({"source_sha256": "old"}, "does not match"),
                                  ({"local": True}, "Local API artifacts"),
                                  ({"files": {}}, "checksums")):
                self.write(manifest_path, json.dumps({**manifest, **change}))
                result = self.mkdocs()
                self.assertNotEqual(result.returncode, 0)
                self.assertIn(error, result.stdout + result.stderr)
            manifest_path.unlink()
            result = self.mkdocs()
            self.assertIn("Missing or invalid API provenance", result.stdout + result.stderr)
            self.write(manifest_path, original)
            self.write(directory / "c-api/html/index.html", "changed artifact")
            result = self.mkdocs()
            self.assertIn("checksums", result.stdout + result.stderr)

    def test_local_header_changes_invalidate_cache_at_same_head(self):
        self.assertEqual(self.mkdocs().returncode, 0)
        directory = self.portal / "build/api/docs"
        before = json.loads((directory / hooks.api.MANIFEST).read_text())
        self.write(self.core / "new-header.h", "/** local API */")
        with patch.dict(os.environ, {"OPENTLV_DOCS_LOCAL": "1", "OPENTLV_API_DOCS_DIR": str(directory)}):
            result = self.mkdocs()
            self.assertIn("does not match", result.stdout + result.stderr)
        with patch.dict(os.environ, {"OPENTLV_DOCS_LOCAL": "1"}):
            result = self.mkdocs()
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        after = json.loads((directory / hooks.api.MANIFEST).read_text())
        self.assertEqual(before["commit"], after["commit"])
        self.assertNotEqual(before["source_sha256"], after["source_sha256"])
        self.assertTrue(after["local"] and after["dirty"])

    def test_failed_generator_leaves_no_valid_artifact_manifest(self):
        self.assertEqual(self.mkdocs().returncode, 0)
        with (self.core / "CMakeLists.txt").open("a") as stream:
            stream.write('\nadd_custom_command(TARGET cxx-api-docs POST_BUILD COMMAND "${CMAKE_COMMAND}" -E false)\n')
        with patch.dict(os.environ, {"OPENTLV_DOCS_LOCAL": "1"}):
            result = self.mkdocs()
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("API command failed", result.stdout + result.stderr)
        self.assertFalse((self.portal / "build/api/docs" / hooks.api.MANIFEST).exists())

    def test_disabling_doxygen_warning_errors_is_rejected(self):
        cmake = self.core / "CMakeLists.txt"
        self.write(cmake, cmake.read_text().replace("WARN_AS_ERROR = YES", "WARN_AS_ERROR = NO"))
        with patch.dict(os.environ, {"OPENTLV_DOCS_LOCAL": "1"}):
            result = self.mkdocs()
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("must keep WARN_AS_ERROR = YES", result.stdout + result.stderr)
        self.assertFalse((self.portal / "build/api/docs" / hooks.api.MANIFEST).exists())

    def test_version_metadata_changes_invalidate_source_fingerprint(self):
        before = hooks.api.fingerprint(self.core)
        self.git("tag", "1.0.0")
        self.assertNotEqual(hooks.api.fingerprint(self.core), before)

    def test_guide_mapping_supports_readme_and_flat_html_urls(self):
        from mkdocs.structure.files import File, Files

        page = File("standards/emv/README.md", str(self.core / "docs"), str(self.portal / "site"), False)
        files = Files([page])
        text = '<a href="https://fixture.invalid/docs/standards/emv/?q=1&amp;x=2#tag">EMV</a>'
        adapted = hooks.api.adapt_html(text, "reference/api/c-api/html/index.html", "https://fixture.invalid/docs/", files)
        self.assertIn('../../../../standards/emv/index.html?q=1&amp;x=2#tag', adapted)

    def test_api_links_and_anchors_are_validated_in_both_directions(self):
        site = self.portal / "link-site"
        c_page = site / "reference/api/c-api/html/index.html"
        cxx_page = site / "reference/api/cxx-api/html/index.html"
        self.write(site / "guide/index.html", '<h1 id="guide">Guide</h1><a href="../reference/api/c-api/html/index.html#c">C</a>')
        self.write(c_page, '<h1 id="c">C</h1><a href="../../cxx-api/html/index.html#cxx">C++</a>')
        self.write(cxx_page, '<h1 id="cxx">C++</h1><a href="../../c-api/html/index.html#c">C</a><a href="../../../../guide/#guide">Guide</a>')
        hooks.api.validate_links(site)
        for page, text, error in (
            (c_page, '<h1 id="c">C</h1><a href="../../cxx-api/html/missing.html">Missing API</a>', "Broken API link"),
            (c_page, '<h1 id="c">C</h1><a href="../../">Missing API index</a>', "Broken API link"),
            (cxx_page, '<h1 id="cxx">C++</h1><a href="../../../../guide/#missing">Guide</a>', "Missing API link anchor"),
            (site / "guide/index.html", '<a href="../reference/api/c-api/html/index.html#missing">C</a>', "Missing API link anchor"),
        ):
            original = page.read_text()
            self.write(page, text)
            with self.assertRaisesRegex(PluginError, error):
                hooks.api.validate_links(site)
            self.write(page, original)

    def test_api_guide_links_relocate_and_missing_guides_fail(self):
        result = self.mkdocs()
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        html = (self.portal / "site/reference/api/c-api/html/index.html").read_text()
        self.assertIn('href="../../../../index.html"', html)
        self.assertNotIn("fixture.invalid", html)
        self.write(self.core / "fixture.html", '<a href="https://fixture.invalid/docs/missing/">Bad guide</a>')
        with patch.dict(os.environ, {"OPENTLV_DOCS_LOCAL": "1"}):
            result = self.mkdocs()
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("no assembled page", result.stdout + result.stderr)

    def test_strict_build_rejects_broken_links_and_missing_anchors(self):
        for text in ("[Missing](missing.md)", "[Source](../missing.c)", "[Anchor](#missing)"):
            with self.subTest(text=text):
                self.write(self.core / "docs/index.md", f"# Home\n\n{text}\n")
                with patch.dict(os.environ, {"OPENTLV_DOCS_LOCAL": "1"}):
                    result = self.mkdocs()
                self.assertNotEqual(result.returncode, 0, result.stderr)
                self.assertIn("WARNING", result.stderr)

    def test_live_preview_reassembles_inputs_without_rebuild_loop(self):
        result = self.mkdocs()  # Write config and verify the initial input.
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn('https://opentlv.github.io/opentlv-docs/',
                      (self.portal / 'site/index.html').read_text(encoding='utf-8'))
        self.write(self.portal / "mkdocs.local.yml", (ROOT / "mkdocs.local.yml").read_text())
        with socket.socket() as sock:
            sock.bind(("127.0.0.1", 0))
            port = sock.getsockname()[1]
        url = f"http://127.0.0.1:{port}/"
        log_path = self.base / "serve.log"
        env = dict(os.environ, OPENTLV_DOCS_LOCAL="1", PYTHONIOENCODING="utf-8")
        with log_path.open("w", encoding="utf-8") as log:
            process = subprocess.Popen(
                [sys.executable, "-m", "mkdocs", "serve", "-f", "mkdocs.local.yml", "--dev-addr", f"127.0.0.1:{port}"],
                cwd=self.portal, env=env, stdout=log, stderr=subprocess.STDOUT,
                creationflags=subprocess.CREATE_NO_WINDOW if os.name == "nt" else 0,
            )
            try:
                def wait_for(text):
                    deadline = time.monotonic() + 20
                    while time.monotonic() < deadline:
                        self.assertIsNone(process.poll(), log_path.read_text(encoding="utf-8"))
                        try:
                            with urlopen(url, timeout=1) as response:
                                self.assertEqual(response.url, url)
                                if text in response.read().decode("utf-8"):
                                    return
                        except (URLError, TimeoutError):
                            pass
                        time.sleep(0.2)
                    self.fail(log_path.read_text(encoding="utf-8"))

                wait_for("Local preview")
                self.write(self.core / "docs/index.md", "# Updated live preview\n")
                wait_for("Updated live preview")
                time.sleep(1)
                built = log_path.read_text(encoding="utf-8").count("Documentation built in")
                time.sleep(2)
                self.assertEqual(log_path.read_text(encoding="utf-8").count("Documentation built in"), built)
            finally:
                process.terminate()
                process.wait(timeout=10)


if __name__ == "__main__":
    unittest.main()
