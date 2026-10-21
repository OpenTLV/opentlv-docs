# SPDX-License-Identifier: MIT
# Copyright (c) 2026 Marek Cingel

"""Exercise actual Material navigation, complete inventories and product isolation."""

import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

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
                          "bindings/python/index.md", "bindings/lua/index.md", "guides/rust.md",
                          "guides/go.md", "development/webassembly.md"),
            "Development": ("concepts/architecture.md", "concepts/error-model.md",
                            "concepts/field-policies.md", "concepts/definition-boundaries.md",
                            "formats/format-roadmap.md", "development/documentation-layout.md"),
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
