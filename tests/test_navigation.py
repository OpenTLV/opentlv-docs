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
SECTIONS = ["Home", "Getting Started", "Formats", "Bindings", "Tools", "Development"]


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

    def test_six_sections_landings_and_complete_inventory(self):
        config, files, nav = self.material_navigation()
        self.assertEqual([item.title for item in nav.items], SECTIONS)
        landings = [item if item.is_page else item.children[0] for item in nav.items]
        self.assertEqual([page.url for page in landings],
                         ["", "getting-started/", "formats/", "bindings/", "tools/", "development/"])
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
        self.assertIn('href="bindings/c/guides/reader/#preserved-anchor"', home)
        self.assertIn('href="tools/otlv/manual/#preserved-anchor"', home)
        self.assertIn('href="bindings/lua/manual/api/#preserved-anchor"', home)
        search = json.loads((site / "search/search_index.json").read_text(encoding="utf-8"))
        self.assertTrue(any(item["location"] == "bindings/c/guides/reader/" for item in search["docs"]))
        self.assertFalse(any(item["location"].startswith("guides/") for item in search["docs"]))
        tabs = home.split('data-md-component="tabs"', 1)[1].split("</nav>", 1)[0]
        for title in SECTIONS:
            self.assertIn(title, tabs)
        for title in ("CLI", "Lua", "Python"):
            self.assertNotIn(title, tabs)
        for path in ("tools/otlv/manual", "bindings/lua/manual/api", "bindings/python/manual/guides/python"):
            html = (site / path / "index.html").read_text(encoding="utf-8")
            self.assertNotIn('data-md-component="tabs"', html)
            self.assertIn("Return to the OpenTLV portal", html)
            self.assertIn('id="preserved-anchor"', html)
            self.assertIn('data-md-type="navigation"', html)
        for old in ("cli", "lua/api", "python/guides/python", "guides/reader", "playground"):
            self.assertFalse((site / old / "index.html").exists(), old)

    def test_historical_landing_fallback_is_revision_specific(self):
        from types import SimpleNamespace
        text = (fixture.ROOT / "docs/development/index.md").read_text()
        page = SimpleNamespace(file=SimpleNamespace(src_uri="development/index.md"))
        core = dict(self.selected[0][1], commit=fixture.assembly.CORE_071_COMMIT)
        config = SimpleNamespace(extra={"core_source": core})
        result = navigation.on_page_markdown(text, page, config, [])
        self.assertNotIn("](quality-gates.md)", result)
        self.assertNotIn("](documentation-ownership.md)", result)
        core["commit"] = "a" * 40
        self.assertEqual(navigation.on_page_markdown(text, page, config, []), text)

    def test_output_collision_fails_and_api_links_use_canonical_routes(self):
        config, files, nav = self.material_navigation()
        html = fixture.hooks.api.adapt_html(
            '<a href="https://fixture.invalid/docs/guides/reader/#preserved-anchor">Reader</a>',
            "reference/api/c-api/html/index.html", "https://fixture.invalid/docs/", files)
        self.assertIn('../../../../bindings/c/guides/reader/index.html#preserved-anchor', html)
        files.append(File("bindings/c/guides/reader.md", str(self.root / "docs"), str(self.root / "site"), True))
        from mkdocs.exceptions import PluginError
        with self.assertRaisesRegex(PluginError, "Portal output collision"):
            navigation.on_nav(nav, config, files)


if __name__ == "__main__":
    unittest.main()
