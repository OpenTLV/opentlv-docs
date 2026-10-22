# SPDX-License-Identifier: MIT
# Copyright (c) 2026 Marek Cingel

"""Exercise actual Material navigation, complete inventories and product isolation."""

import copy
import json
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch

from mkdocs.config import load_config
from mkdocs.structure.files import File, Files
from mkdocs.structure.nav import get_navigation
import yaml

import test_portal as fixture
from test_publication import ci

navigation = fixture.load_hook("navigation")
SECTIONS = ["Home", "Tutorials", "API", "Standards", "Languages", "Tools", "Development"]


class NavigationTests(unittest.TestCase):
    def setUp(self):
        temp = tempfile.TemporaryDirectory()
        self.addCleanup(temp.cleanup)
        self.root = Path(temp.name)
        self.config = yaml.safe_load((fixture.ROOT / "mkdocs.yml").read_text())
        definitions = json.loads((fixture.ROOT / "docs-sources.json").read_text())["sources"]
        self.selected = [(None, dict(item, included=True, commit=item["revision"]))
                         for item in definitions]
        self.config["nav"] = fixture.assembly.navigation(self.config["nav"], self.selected)
        self.config["extra"]["sources"] = [item for _, item in self.selected]
        self.config["hooks"] = [str(fixture.ROOT / "tools/docs/navigation.py")]
        self.config["theme"]["custom_dir"] = str(fixture.ROOT / "tools/docs/overrides")
        for key in ("logo", "favicon"):
            self.config["theme"].pop(key)
        self.config["extra_css"] = []
        self.config["extra_javascript"] = []
        for name in ci.nav_paths(self.config["nav"]):
            path = self.root / "docs" / name
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text("# Manual\n\n## Preserved anchor\n\nTechnical content.\n")
        (self.root / "docs/index.md").write_text(
            "# Home\n\n[Reader](guides/reader.md#preserved-anchor)\n\n"
            "[CLI](cli/README.md#preserved-anchor)\n\n"
            "[Lua](lua/api.md#preserved-anchor)\n")
        for name in (navigation.content.HISTORY_INDEX, navigation.content.COMPONENT_INDEX):
            shutil.copyfile(fixture.ROOT / "docs" / name, self.root / "docs" / name)
        self.path = self.root / "mkdocs.yml"
        self.path.write_text(yaml.safe_dump(self.config, sort_keys=False))

    def material_navigation(self):
        config = load_config(str(self.path))
        files = Files([File(name, str(self.root / "docs"), str(self.root / "site"), True)
                       for name in ci.nav_paths(self.config["nav"])])
        navigation.on_files(files, config)
        full = get_navigation(files, config)
        return config, files, navigation.on_nav(full, config, files)

    def test_seven_sections_landings_and_complete_inventory(self):
        config, files, nav = self.material_navigation()
        self.assertEqual([item.title for item in nav.items], SECTIONS)
        landings = [item if item.is_page else item.children[0] for item in nav.items]
        self.assertEqual([page.url for page in landings],
                         ["", "tutorials/", "api/", "standards/", "languages/", "tools/", "development/"])
        self.assertTrue(all(page.is_index for page in landings))
        self.assertFalse(files.get_file_from_path("getting-started/README.md").page.is_index)
        ci.check_navigation(self.root / "docs", self.path.read_text())
        # An undeclared page must still fail; splitting menus is not an exclusion.
        (self.root / "docs/lua/lost.md").write_text("# Lost content\n")
        with self.assertRaisesRegex(ValueError, "omits documentation: lua/lost.md"):
            ci.check_navigation(self.root / "docs", self.path.read_text())
        product_paths = set(config.extra["product_navigation"])
        portal_paths = {page.file.src_uri for page in nav.pages}
        self.assertFalse(portal_paths & product_paths)
        self.assertEqual(portal_paths | product_paths, ci.nav_paths(self.config["nav"]))
        for page in nav.pages:
            self.assertNotIn(page.file.src_uri, product_paths)
            for neighbor in (page.previous_page, page.next_page):
                if neighbor:
                    self.assertNotIn(neighbor.file.src_uri, product_paths)

    def test_sections_separate_learning_public_contracts_and_internal_design(self):
        _config, files, nav = self.material_navigation()

        def section(name):
            page = files.get_file_from_path(name).page
            item = page
            while item.parent:
                item = item.parent
            return item.title

        expected = {
            "Tutorials": ("getting-started/README.md", "concepts/learning-model.md",
                          "guides/processing.md", "guides/examples.md", "guides/cxx-examples.md",
                          "formats/format-examples.md"),
            "API": ("guides/reader.md", "guides/writer.md", "guides/document.md",
                    "guides/queries.md", "guides/schemas.md", "guides/codecs.md",
                    "concepts/core-types.md", "concepts/format-contract.md",
                    "reference/c-api.md", "reference/cxx-api.md",
                    "formats/fixed/configurable.md", "formats/custom/README.md"),
            "Standards": ("formats/asn1/ber.md", "formats/asn1/der.md", "formats/asn1/cer.md",
                          "standards/emv/README.md", "formats/bluetooth/README.md",
                          "formats/nfc/README.md", "formats/dhcp/README.md", "formats/lldp/README.md"),
            "Languages": ("bindings/c/index.md", "bindings/cpp/index.md",
                          "bindings/python/index.md", "bindings/lua/index.md", "bindings/rust/index.md",
                          "guides/go.md", "development/webassembly.md"),
            "Development": ("concepts/architecture.md", "concepts/error-model.md",
                            "concepts/field-policies.md", "concepts/definition-boundaries.md",
                            "formats/format-roadmap.md", "development/documentation-layout.md",
                            "development/rust.md"),
        }
        for title, names in expected.items():
            for name in names:
                with self.subTest(section=title, source=name):
                    self.assertEqual(section(name), title)
                    # Output moves retain the original source identity used by
                    # component ownership and edit/source links.
                    page = files.get_file_from_path(name).page
                    self.assertEqual(page.file.src_uri, name)
                    self.assertEqual(page.file.abs_src_path, str(self.root / "docs" / name))
        self.assertEqual([item.title for item in nav.items], SECTIONS)

    def test_product_context_scopes_menu_footer_and_version_selector(self):
        config, files, nav = self.material_navigation()
        before_features = list(config.theme["features"])
        for name, (product, source) in config.extra["product_navigation"].items():
            page = files.get_file_from_path(name).page
            context = navigation.on_page_context({"config": config, "nav": nav}, page, config, nav)
            self.assertIs(context["nav"], product)
            self.assertEqual(product.items[0].title, "OpenTLV portal")
            self.assertEqual(product.items[0].url, "")
            self.assertNotIn("navigation.tabs", context["config"].theme["features"])
            self.assertNotIn("version", context["config"].extra)
            self.assertEqual(config.theme["features"], before_features)
            self.assertIn("version", config.extra)
            for neighbor in (page.previous_page, page.next_page):
                if neighbor:
                    self.assertTrue(neighbor.file.src_uri.startswith(source["mount"] + "/"))
        context = {"config": config, "nav": nav}
        self.assertIs(navigation.on_page_context(context, nav.homepage, config, nav), context)

    def test_reviewed_archives_and_contributor_guides_belong_to_development(self):
        config, files, nav = self.material_navigation()
        product_paths = set(config.extra["product_navigation"])
        archived = set(navigation.content.ARCHIVES)
        contributor = set(navigation.content.COMPONENT_GUIDES)
        for name in archived | contributor:
            with self.subTest(name=name):
                page = files.get_file_from_path(name).page
                self.assertNotIn(name, product_paths)
                self.assertEqual(page.file.src_uri, name)
                top = page
                while top.parent:
                    top = top.parent
                self.assertEqual(top.title, "Development")
                self.assertIn(page, nav.pages)
                context = {"nav": nav, "config": config}
                self.assertIs(navigation.on_page_context(context, page, config, nav), context)
                for neighbor in (page.previous_page, page.next_page):
                    if neighbor:
                        self.assertNotIn(neighbor.file.src_uri, product_paths)
        # Check representative user-visible destinations independently of the
        # route table, including paths that would otherwise match product rules.
        for source, url in {
            "guides/python.md": "development/history/core/guides/python/",
            "lua/migration.md": "development/history/lua/migration/",
            "python/validation/ci.md": "development/history/python/validation/ci/",
            "cli/development.md": "development/components/cli/development/",
            "lua/testing.md": "development/components/lua/testing/",
            "python/releases.md": "development/components/python/releases/",
        }.items():
            self.assertEqual(files.get_file_from_path(source).page.url, url)
        for name, (manual, _source) in config.extra["product_navigation"].items():
            self.assertTrue(all(page.file.src_uri not in archived | contributor for page in manual.pages))
            self.assertIn(name, {page.file.src_uri for page in manual.pages})

    def test_archival_context_preserves_source_body_and_is_portal_only(self):
        config, files, _nav = self.material_navigation()
        original = "# Original title\n\n## Contract\n\nOriginal evidence.\n\n```sh\nrun_original --flag\n```\n"
        for name in navigation.content.ARCHIVES:
            with self.subTest(name=name):
                page = files.get_file_from_path(name).page
                page.edit_url = "https://owner.invalid/edit/source.md"
                result = navigation.on_page_markdown(original, page, config, files)
                self.assertTrue(result.startswith('# Original title\n\n!!! note "Historical record"'))
                self.assertTrue(result.endswith(original.partition("\n")[2]))
                self.assertTrue(page.meta["search"]["exclude"])
                self.assertEqual(page.edit_url, "https://owner.invalid/edit/source.md")
                page.meta = {}
                self.assertEqual(navigation.on_page_markdown(original, page, config, Files([])), original)
                self.assertNotIn("search", page.meta)
        for name in navigation.content.COMPONENT_GUIDES:
            page = files.get_file_from_path(name).page
            self.assertEqual(navigation.on_page_markdown(original, page, config, files), original)
            self.assertNotIn("search", page.meta)

    def test_optional_absent_manual_keeps_inventory_and_indexes_honest(self):
        base = yaml.safe_load((fixture.ROOT / "mkdocs.yml").read_text())["nav"]
        original = copy.deepcopy(self.selected)
        for _checkout, source in self.selected:
            if source["id"] in {"lua", "python"}:
                source["included"] = False
        self.config["nav"] = fixture.assembly.navigation(base, self.selected)
        self.config["extra"]["sources"] = [source for _, source in self.selected]
        self.path.write_text(yaml.safe_dump(self.config, sort_keys=False))
        config, files, nav = self.material_navigation()
        paths = ci.nav_paths(self.config["nav"])
        self.assertFalse(any(name.startswith(("lua/", "python/")) for name in paths))
        self.assertIn("guides/python.md", paths)
        history = files.get_file_from_path("development/history.md").page
        index = navigation.on_page_markdown("<!-- opentlv-content: history -->", history, config, files)
        self.assertNotIn("../lua/", index)
        self.assertNotIn("../python/", index)
        self.assertIn("../bindings/python/index.md", index)
        self.assertEqual([item.title for item in nav.items], SECTIONS)
        # An absent optional component contributes no references. A missing
        # registered page in a present component remains an inventory error.
        full = fixture.assembly.navigation(base, original)
        (self.root / "docs/python/validation/ci.md").unlink()
        with self.assertRaisesRegex(ValueError, "references missing documentation: python/validation/ci.md"):
            ci.check_navigation(self.root / "docs", yaml.safe_dump({"nav": full}))
        self.assertEqual(original[2][1]["navigation"], self.selected[2][1]["navigation"])

    def test_strict_material_build_uses_new_routes_and_separate_menus(self):
        result = subprocess.run([sys.executable, "-B", "-m", "mkdocs", "build", "--strict"],
                                cwd=self.root, capture_output=True, text=True, encoding="utf-8")
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        site = self.root / "site"
        home = (site / "index.html").read_text(encoding="utf-8")
        self.assertIn('href="api/guides/reader/#preserved-anchor"', home)
        self.assertIn('href="tools/otlv/manual/#preserved-anchor"', home)
        self.assertIn('href="languages/lua/manual/api/#preserved-anchor"', home)
        search = json.loads((site / "search/search_index.json").read_text(encoding="utf-8"))
        locations = {item["location"] for item in search["docs"]}
        for path in ("tutorials/first-program/", "api/guides/reader/", "api/reference/c/",
                     "api/reference/cpp/", "api/formats/fixed/configurable/", "standards/asn1/ber/",
                     "languages/python/", "languages/lua/manual/api/", "development/documentation/"):
            self.assertIn(path, locations)
        self.assertIn("development/history/", locations)
        self.assertIn("development/components/python/releases/", locations)
        self.assertFalse(any(path.startswith(("development/history/core/", "development/history/lua/",
                                             "development/history/python/"))
                             for path in locations))
        for path in ("development/history/core/guides/python", "development/history/lua/migration",
                     "development/history/python/validation/ci", "development/components/lua/testing"):
            html = (site / path / "index.html").read_text(encoding="utf-8")
            self.assertIn('data-md-component="tabs"', html)
            self.assertNotIn("Return to the OpenTLV portal", html)
            self.assertIn('id="preserved-anchor"', html)
            self.assertIn("Technical content.", html)
            if "/history/" in path:
                self.assertIn("Historical record", html)
                self.assertIn("not a current verification", html)
        self.assertFalse(any(path.startswith(("getting-started/", "guides/", "formats/", "bindings/"))
                             for path in locations))
        tabs = home.split('data-md-component="tabs"', 1)[1].split("</nav>", 1)[0]
        for title in SECTIONS:
            self.assertIn(title, tabs)
        for title in ("CLI", "Lua", "Python"):
            self.assertNotIn(title, tabs)
        for path in ("tools/otlv/manual", "languages/lua/manual/api", "languages/python/manual/guides/python"):
            html = (site / path / "index.html").read_text(encoding="utf-8")
            self.assertNotIn('data-md-component="tabs"', html)
            self.assertIn("Return to the OpenTLV portal", html)
            self.assertIn('id="preserved-anchor"', html)
            self.assertIn('data-md-type="navigation"', html)
        for old in ("cli", "lua/api", "python/guides/python", "guides/reader", "playground",
                    "getting-started", "getting-started/first-program", "formats", "formats/asn1/ber",
                    "formats/fixed/configurable", "bindings", "bindings/c/reference",
                    "bindings/cpp/reference", "bindings/lua/manual/api", "bindings/python/manual/guides/python",
                    "development/architecture/format-contract"):
            self.assertFalse((site / old / "index.html").exists(), old)
        for old in ("languages/python/core-transition", "languages/lua/manual/migration",
                    "languages/python/manual/validation/ci", "tools/otlv/manual/development",
                    "development/documentation/audit-513", "development/reader-decode-performance"):
            self.assertFalse((site / old / "index.html").exists(), old)

    def test_historical_core_keeps_languages_and_separate_product_manuals(self):
        base = yaml.safe_load((fixture.ROOT / "mkdocs.yml").read_text())["nav"]
        self.selected[0][1]["commit"] = fixture.assembly.CORE_071_COMMIT
        self.config["nav"] = fixture.assembly.navigation(base, self.selected)
        paths = ci.nav_paths(self.config["nav"])
        self.assertIn("guides/lua.md", paths)
        self.assertIn("development/lua.md", paths)
        self.assertNotIn("development/quality-gates.md", paths)
        self.assertNotIn("development/documentation-ownership.md", paths)
        for name in paths:
            path = self.root / "docs" / name
            path.parent.mkdir(parents=True, exist_ok=True)
            if not path.exists():
                path.write_text("# Historical Core\n")
        self.path.write_text(yaml.safe_dump(self.config, sort_keys=False))
        config, files, nav = self.material_navigation()
        self.assertEqual([item.title for item in nav.items], SECTIONS)
        historical_lua = files.get_file_from_path("guides/lua.md").page
        self.assertEqual(historical_lua.url, "languages/lua/core-transition/")
        self.assertEqual(historical_lua.parent.title, "Languages")
        manual_lua = files.get_file_from_path("lua/api.md").page
        self.assertEqual(manual_lua.url, "languages/lua/manual/api/")
        self.assertIn("lua/api.md", config.extra["product_navigation"])
        self.assertNotIn("guides/lua.md", config.extra["product_navigation"])
        self.assertEqual(files.get_file_from_path("development/documentation-audit.md").page.url,
                         "development/history/core/documentation-audit/")
        # The exact immutable version still builds with all retained records.
        # Only its two known later additions may be absent.
        for name in ("development/quality-gates.md", "development/documentation-ownership.md"):
            (self.root / "docs" / name).unlink()
        self.config["extra"]["core_source"] = self.selected[0][1]
        self.path.write_text(yaml.safe_dump(self.config, sort_keys=False))
        result = subprocess.run([sys.executable, "-B", "-m", "mkdocs", "build", "--strict"],
                                cwd=self.root, capture_output=True, text=True, encoding="utf-8")
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.selected[0][1]["commit"] = "a" * 40
        current = fixture.assembly.navigation(base, self.selected)
        with self.assertRaisesRegex(ValueError, "references missing documentation"):
            ci.check_navigation(self.root / "docs", yaml.safe_dump({"nav": current}))

    def test_independent_manuals_keep_original_records_routes_and_search(self):
        engine = fixture.load_hook("component_publication")
        for identifier in ("lua", "python"):
            with self.subTest(source=identifier):
                item = copy.deepcopy(next(item for _, item in self.selected if item["id"] == identifier))
                portal = (self.root / identifier).resolve()
                portal.mkdir()
                (portal / "mkdocs.yml").write_text(yaml.safe_dump(self.config, sort_keys=False))
                shutil.copytree(fixture.ROOT / "tools/docs", portal / "tools/docs",
                                ignore=shutil.ignore_patterns("__pycache__"))
                checkout = (self.root / (identifier + "-source")).resolve()
                names = ci.nav_paths(item["navigation"]["items"])
                original = "# Owner manual\n\n## Evidence\n\nOriginal command and validation record.\n"
                for name in names:
                    target = checkout / "docs" / name
                    target.parent.mkdir(parents=True, exist_ok=True)
                    target.write_text(original, encoding="utf-8")
                selection = dict(source=identifier, repository=item["repository"], commit="a" * 40,
                                 tag="v0.1.0", version="0.1.0", local=False, dirty=False)

                def source_git(_checkout, *args):
                    if args == ("rev-parse", "HEAD"):
                        return selection["commit"]
                    if args[0] == "status":
                        return ""
                    if args[0] == "ls-files":
                        return "\0".join("docs/" + name for name in sorted(names))
                    raise AssertionError(args)

                with patch.object(engine.sources, "git", side_effect=source_git):
                    path = engine.assemble(portal, checkout, item, selection)
                manual = yaml.safe_load(path.read_text(encoding="utf-8"))
                self.assertEqual(manual["nav"][1:-1], item["navigation"]["items"])
                self.assertEqual([Path(name).name for name in manual["hooks"]], ["component_hooks.py"])
                result = subprocess.run([sys.executable, "-B", "-m", "mkdocs", "build", "--strict", "-f", str(path)],
                                        cwd=portal, capture_output=True, text=True, encoding="utf-8")
                self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
                site = portal / "build" / identifier / "site"
                search = json.loads((site / "search/search_index.json").read_text(encoding="utf-8"))
                locations = {entry["location"] for entry in search["docs"]}
                self.assertIn("migration/", locations)
                if identifier == "python":
                    self.assertIn("validation/ci/", locations)
                for name in names:
                    source = portal / "build" / identifier / "docs" / name
                    self.assertEqual(source.read_text(encoding="utf-8"), original)
                    destination = File(name, str(source.parent), str(site), True).dest_uri
                    html = (site / destination).read_text(encoding="utf-8")
                    self.assertNotIn("not a current verification", html)
                    self.assertIn('id="evidence"', html)
                self.assertFalse((site / "development/history").exists())
                self.assertFalse((site / "development/components").exists())

    def test_historical_landing_fallback_is_revision_specific(self):
        from types import SimpleNamespace
        core = dict(self.selected[0][1], commit=fixture.assembly.CORE_071_COMMIT)
        config = SimpleNamespace(extra={"core_source": core})
        for name in ("index", "testing", "releases", "documentation"):
            text = (fixture.ROOT / f"docs/development/{name}.md").read_text(encoding="utf-8")
            page = SimpleNamespace(file=SimpleNamespace(src_uri=f"development/{name}.md"))
            core["commit"] = fixture.assembly.CORE_071_COMMIT
            result = navigation.on_page_markdown(text, page, config, Files([]))
            self.assertNotIn("](quality-gates.md)", result)
            self.assertNotIn("](documentation-ownership.md)", result)
            core["commit"] = "a" * 40
            self.assertEqual(navigation.on_page_markdown(text, page, config, Files([])), text)

    def test_development_context_preserves_owner_text_and_requires_portal(self):
        from types import SimpleNamespace
        config, files, _nav = self.material_navigation()
        original = "# Owner title\n\n## Contract\n\nOriginal details.\n\n```sh\npython generator.py\n```\n"
        for name in navigation.DEVELOPMENT_NOTES:
            page = files.get_file_from_path(name).page
            result = navigation.on_page_markdown(original, page, config, files)
            self.assertTrue(result.startswith('# Owner title\n\n!!! note "Portal context"'))
            self.assertTrue(result.endswith(original.partition("\n")[2]))
            self.assertIn("[current portal conventions](documentation.md)", result)
            self.assertEqual(navigation.on_page_markdown(original, page, config, Files([])), original)
            self.assertEqual(page.file.src_uri, name)
        page = SimpleNamespace(file=SimpleNamespace(src_uri="concepts/architecture.md"))
        self.assertEqual(navigation.on_page_markdown(original, page, config, files), original)

    def test_output_collision_fails_and_api_links_use_canonical_routes(self):
        config, files, nav = self.material_navigation()
        html = fixture.hooks.api.adapt_html(
            '<a href="https://fixture.invalid/docs/guides/reader/#preserved-anchor">Reader</a>',
            "api/reference/c-api/html/index.html", "https://fixture.invalid/docs/", files)
        self.assertIn('../../../guides/reader/index.html#preserved-anchor', html)
        files.append(File("api/guides/reader.md", str(self.root / "docs"), str(self.root / "site"), True))
        from mkdocs.exceptions import PluginError
        with self.assertRaisesRegex(PluginError, "Portal output collision"):
            navigation.on_nav(nav, config, files)


if __name__ == "__main__":
    unittest.main()
