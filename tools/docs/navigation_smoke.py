# SPDX-License-Identifier: MIT
# Copyright (c) 2026 Marek Cingel

"""Check desktop tabs, mobile drawers and product return links in a built site."""

import argparse
from functools import partial
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
import threading

from playwright.sync_api import expect, sync_playwright

SECTIONS = ("Home", "Tutorials", "API", "Standards", "Languages", "Tools", "Development")
LANDINGS = ("", "tutorials/", "api/", "standards/", "languages/", "tools/", "development/")


def check_navigation(page, base_url):
    for width in (1440, 390):
        page.set_viewport_size({"width": width, "height": 900})
        page.goto(base_url)
        if width == 1440:
            menu = page.locator('[data-md-component="tabs"]')
            expect(menu).to_be_visible()
            expect(menu.locator("a")).to_have_text(list(SECTIONS))
        else:
            page.locator('.md-header label[for="__drawer"]').click()
            menu = page.locator(".md-nav--primary")
            expect(menu).to_be_visible()
            expect(menu.locator(":scope > ul > li")).to_have_count(7)
        # Material renders the active Home entry as a TOC label on mobile.
        # Visit it last so each click targets a different page.
        for index in (1, 2, 3, 4, 5, 6, 0):
            title, path = SECTIONS[index], LANDINGS[index]
            # Navigate via actual controls, reopening the mobile drawer after
            # each page load. Section index links share labels with toggles.
            link = menu.get_by_role("link", name=title, exact=True)
            expect(link).to_be_visible()
            link.click()
            expect(page).to_have_url(base_url + path)
            expect(page.locator("article h1")).to_be_visible()
            assert page.evaluate("document.documentElement.scrollWidth <= window.innerWidth"), (width, path)
            if width == 390:
                page.locator('.md-header label[for="__drawer"]').click()
                back = menu.locator(":scope > ul > li.md-nav__item--active.md-nav__item--nested > nav > label.md-nav__title")
                if back.count():
                    back.click()
        page.goto(base_url + "tutorials/")
        if width == 390:
            page.locator('.md-header label[for="__drawer"]').click()
        page.locator(".md-nav--primary").get_by_role("link", name="Choose a processing API", exact=True).click()
        expect(page).to_have_url(base_url + "tutorials/processing/")
        for path in ("tools/otlv/manual/", "languages/lua/manual/api/", "languages/python/manual/guides/python/"):
            page.goto(base_url + path)
            expect(page.locator('[data-md-component="tabs"]')).to_have_count(0)
            if width == 390:
                page.locator('.md-header label[for="__drawer"]').click()
            menu = page.locator(".md-nav--primary")
            back = menu.get_by_role("link", name="OpenTLV portal", exact=True)
            expect(back).to_be_visible()
            back.click()
            expect(page).to_have_url(base_url)
        assert page.evaluate("document.documentElement.scrollWidth <= window.innerWidth"), width
    check_formats(page, base_url)
    check_catalogs(page, base_url)
    check_development(page, base_url)


def check_development(page, base_url):
    """Follow contributor tasks into canonical manuals and current conventions."""
    targets = (
        ("Architecture", "development/architecture/", "Core architecture overview",
         "development/architecture/architecture/"),
        ("Building from Source", "development/building/", "Python build and workspace guide",
         "languages/python/manual/development/python/"),
        ("Contributing", "development/contributing/", "documentation ownership and portal conventions",
         "development/documentation/"),
        ("Testing and Quality Gates", "development/testing/", "Core quality gates",
         "development/quality-gates/"),
        ("CI and Release Process", "development/releases/", "release quality gate",
         "languages/lua/manual/releases/"),
    )
    for width in (1440, 390):
        page.set_viewport_size({"width": width, "height": 900})
        for title, overview, detail_title, detail in targets:
            page.goto(base_url + "development/")
            page.locator("article").get_by_role("link", name=title, exact=True).click()
            expect(page).to_have_url(base_url + overview)
            expect(page.locator("article h1")).to_contain_text(title)
            assert page.evaluate("document.documentElement.scrollWidth <= window.innerWidth"), (width, overview)
            page.locator("article").get_by_role("link", name=detail_title, exact=True).click()
            expect(page).to_have_url(base_url + detail)
            expect(page.locator("article h1")).to_be_visible()
        for path in ("documentation/layout", "documentation/ownership", "documentation/audit-513",
                     "bindings/python"):
            page.goto(base_url + "development/" + path + "/")
            note = page.locator("article .admonition.note").filter(has_text="Portal context")
            expect(note).to_have_count(1)
            note.get_by_role("link", name="current portal conventions", exact=True).click()
            expect(page).to_have_url(base_url + "development/documentation/")


def check_catalogs(page, base_url):
    """Follow discovery links into the actual selected manuals and application."""
    languages = (
        ("C", "languages/c/", "C API reference", "api/reference/c/"),
        ("C++", "languages/cpp/", "C++ API reference", "api/reference/cpp/"),
        ("Python", "languages/python/", "Python manual", "languages/python/manual/guides/python/"),
        ("Lua", "languages/lua/", "Lua manual", "languages/lua/manual/api/"),
        ("Rust", "languages/rust/", "Rust manual", "languages/rust/manual/"),
        ("Go", "languages/go/", "Go manual", "languages/go/manual/"),
        ("WebAssembly", "languages/wasm/", "WebAssembly manual", "languages/wasm/development/"),
    )
    tools = (
        ("otlv CLI", "tools/otlv/", "otlv manual", "tools/otlv/manual/"),
        ("TLV playground", "tools/playground/overview/", "Open the TLV playground", "tools/playground/"),
        ("imtlv", "tools/imtlv/", None, None),
    )
    for width in (1440, 390):
        page.set_viewport_size({"width": width, "height": 900})
        for catalog, entries in (("languages/", languages), ("tools/", tools)):
            for title, overview, manual_title, manual in entries:
                page.goto(base_url + catalog)
                page.locator("article").get_by_role("link", name=title, exact=True).click()
                expect(page).to_have_url(base_url + overview)
                expect(page.locator("article h1")).to_contain_text(title)
                expect(page.locator("article")).to_contain_text("Status:")
                assert page.evaluate("document.documentElement.scrollWidth <= window.innerWidth"), (width, overview)
                if manual:
                    page.locator("article").get_by_role("link", name=manual_title, exact=True).click()
                    expect(page).to_have_url(base_url + manual)
                    expect(page.locator("article h1")).to_be_visible()
                    if title in ("Python", "Lua", "otlv CLI"):
                        expect(page.locator('[data-md-component="tabs"]')).to_have_count(0)
                        page.get_by_role("link", name="Return to the OpenTLV portal", exact=True).click()
                        expect(page).to_have_url(base_url)
                else:
                    expect(page.locator("article")).to_contain_text("planned; not available")
            page.goto(base_url + catalog)
            page.locator("article").get_by_role("link", name="product registration convention").click()
            expect(page).to_have_url(base_url + "development/product-catalogs/")


def check_formats(page, base_url):
    catalogs = (
        ("api/formats/", (
            ("Fixed-width TLV", "api/formats/fixed/configurable/"),
            ("Variable-width TLV", "api/formats/variable/"),
            ("Packed Tag/Length", "api/formats/packed/"),
            ("Escaped lengths", "api/formats/escaped/"),
        )),
        ("standards/", (
            ("BER-TLV", "standards/asn1/ber/"),
            ("DER-TLV", "standards/asn1/der/"),
            ("CER-TLV", "standards/asn1/cer/"),
            ("EMV", "standards/emv/"),
            ("Bluetooth LTV", "standards/bluetooth/"),
            ("LLDP", "standards/lldp/"),
            ("DHCPv4 options", "standards/dhcp/"),
            ("NFC Type 2", "standards/nfc/"),
        )),
    )
    for width in (1440, 390):
        page.set_viewport_size({"width": width, "height": 900})
        page.goto(base_url + "api/")
        page.locator("article").get_by_role("link", name="Generic formats", exact=True).click()
        expect(page).to_have_url(base_url + "api/formats/")
        for catalog, targets in catalogs:
            for title, path in targets:
                page.goto(base_url + catalog)
                assert page.evaluate("document.documentElement.scrollWidth <= window.innerWidth"), width
                page.locator("article").get_by_role("link", name=title, exact=True).click()
                expect(page).to_have_url(base_url + path)
                expect(page.locator("article h1")).to_be_visible()
                assert page.locator("article h2").evaluate_all("nodes => nodes.map(node => node.id)") == [
                    "overview", "format-structure", "encoding-rules", "supported-capabilities",
                    "examples", "limitations", "references",
                ], path
                assert page.evaluate("document.documentElement.scrollWidth <= window.innerWidth"), (width, path)
                catalog_title = "Generic formats" if catalog == "api/formats/" else "Standards catalog"
                back = page.locator("article").get_by_role("link", name=catalog_title, exact=True)
                if path == "api/formats/escaped/":
                    # This existing guide has no appended catalog link; its
                    # Material section index supplies the return navigation.
                    menu = page.locator(".md-nav--primary")
                    if width == 390:
                        page.locator('.md-header label[for="__drawer"]').click()
                        menu.locator('nav[data-md-level="2"] > label.md-nav__title').filter(
                            has_text="Generic formats").click()
                    back = menu.get_by_role("link", name="Generic formats", exact=True)
                back.click()
                expect(page).to_have_url(base_url + catalog)
        for kind, fragment in (("der", "schema-aware-validation-and-encoding"),
                               ("cer", "canonical-string-segmentation")):
            page.goto(base_url + f"standards/asn1/{kind}/#{fragment}")
            expect(page.locator("#" + fragment)).to_be_visible()
            for source in (f"formats/asn1/{kind}.md", f"standards/{kind}/README.md"):
                expect(page.locator(f'a[href*="/blob/"][href$="/docs/{source}"]')).to_have_count(1)
                expect(page.locator(f'a[href*="/edit/"][href$="/docs/{source}"]')).not_to_have_count(0)
        page.goto(base_url + "api/formats/")
        page.locator("article").get_by_role("link", name="Core format guide", exact=True).click()
        expect(page).to_have_url(base_url + "api/formats/guide/")
        expect(page.locator("#reading-one-element")).to_have_count(1)


def check(site, prefix=""):
    prefix = prefix.strip("/")
    mount = "/" + prefix + "/" if prefix else "/"

    class Handler(SimpleHTTPRequestHandler):
        def do_GET(self):
            if self.path.startswith(mount):
                self.path = "/" + self.path[len(mount):]
            super().do_GET()

        def log_message(self, *_args):
            pass

    server = ThreadingHTTPServer(("127.0.0.1", 0), partial(Handler, directory=str(site)))
    worker = threading.Thread(target=server.serve_forever, daemon=True)
    worker.start()
    try:
        with sync_playwright() as playwright:
            browser = playwright.chromium.launch()
            page = browser.new_page()
            base = f"http://127.0.0.1:{server.server_port}" + mount
            check_navigation(page, base)
            browser.close()
            print("Desktop/mobile portal and product navigation passed: " + base)
    finally:
        server.shutdown()
        server.server_close()
        worker.join()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("site", type=Path)
    parser.add_argument("--prefix", default="", help="Virtual URL mount, e.g. opentlv-docs/latest")
    args = parser.parse_args()
    check(args.site.resolve(), args.prefix)
