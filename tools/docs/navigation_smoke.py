# SPDX-License-Identifier: MIT
# Copyright (c) 2026 Marek Cingel

"""Check desktop tabs, mobile drawers and product return links in a built site."""

import argparse
from functools import partial
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
import threading

from playwright.sync_api import expect, sync_playwright

SECTIONS = ("Home", "Getting Started", "Formats", "Bindings", "Tools", "Development")
LANDINGS = ("", "getting-started/", "formats/", "bindings/", "tools/", "development/")


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
            expect(menu.locator(":scope > ul > li")).to_have_count(6)
        # Material renders the active Home entry as a TOC label on mobile.
        # Visit it last so each click targets a different page.
        for index in (1, 2, 3, 4, 5, 0):
            title, path = SECTIONS[index], LANDINGS[index]
            # Navigate via actual controls, reopening the mobile drawer after
            # each page load. Section index links share labels with toggles.
            link = menu.get_by_role("link", name=title, exact=True)
            expect(link).to_be_visible()
            link.click()
            expect(page).to_have_url(base_url + path)
            expect(page.locator("article h1")).to_be_visible()
            if width == 390:
                page.locator('.md-header label[for="__drawer"]').click()
                back = menu.locator(":scope > ul > li.md-nav__item--active.md-nav__item--nested > nav > label.md-nav__title")
                if back.count():
                    back.click()
        page.goto(base_url + "getting-started/")
        if width == 390:
            page.locator('.md-header label[for="__drawer"]').click()
        page.locator(".md-nav--primary").get_by_role("link", name="Choose a processing API", exact=True).click()
        expect(page).to_have_url(base_url + "getting-started/processing/")
        for path in ("tools/otlv/manual/", "bindings/lua/manual/api/", "bindings/python/manual/guides/python/"):
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


def check_catalogs(page, base_url):
    """Follow discovery links into the actual selected manuals and application."""
    bindings = (
        ("C", "bindings/c/", "C API reference", "bindings/c/reference/"),
        ("C++", "bindings/cpp/", "C++ API reference", "bindings/cpp/reference/"),
        ("Python", "bindings/python/", "Python manual", "bindings/python/manual/guides/python/"),
        ("Lua", "bindings/lua/", "Lua manual", "bindings/lua/manual/api/"),
        ("Rust", "bindings/rust/", "Rust manual", "bindings/rust/manual/"),
        ("Go", "bindings/go/", "Go manual", "bindings/go/manual/"),
        ("WebAssembly", "bindings/wasm/", "WebAssembly manual", "bindings/wasm/development/"),
    )
    tools = (
        ("otlv CLI", "tools/otlv/", "otlv manual", "tools/otlv/manual/"),
        ("TLV playground", "tools/playground/overview/", "Open the TLV playground", "tools/playground/"),
        ("imtlv", "tools/imtlv/", None, None),
    )
    for width in (1440, 390):
        page.set_viewport_size({"width": width, "height": 900})
        for catalog, entries in (("bindings/", bindings), ("tools/", tools)):
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
    targets = (
        ("Fixed-width TLV", "formats/fixed/configurable/"),
        ("Variable-width TLV", "formats/variable/"),
        ("Packed Tag/Length", "formats/packed/"),
        ("Escaped lengths", "formats/escaped/"),
        ("BER-TLV", "formats/asn1/ber/"),
        ("DER-TLV", "formats/asn1/der/"),
        ("CER-TLV", "formats/asn1/cer/"),
        ("EMV", "formats/emv/"),
        ("Bluetooth LTV", "formats/bluetooth/"),
        ("LLDP", "formats/lldp/"),
        ("DHCPv4 options", "formats/dhcp/"),
        ("NFC Type 2", "formats/nfc/"),
    )
    for width in (1440, 390):
        page.set_viewport_size({"width": width, "height": 900})
        for title, path in targets:
            page.goto(base_url + "formats/")
            assert page.evaluate("document.documentElement.scrollWidth <= window.innerWidth"), width
            page.locator("article").get_by_role("link", name=title, exact=True).click()
            expect(page).to_have_url(base_url + path)
            expect(page.locator("article h1")).to_be_visible()
            assert page.locator("article h2").evaluate_all("nodes => nodes.map(node => node.id)") == [
                "overview", "format-structure", "encoding-rules", "supported-capabilities",
                "examples", "limitations", "references",
            ], path
            assert page.evaluate("document.documentElement.scrollWidth <= window.innerWidth"), (width, path)
        for kind, fragment in (("der", "schema-aware-validation-and-encoding"),
                               ("cer", "canonical-string-segmentation")):
            page.goto(base_url + f"formats/asn1/{kind}/#{fragment}")
            expect(page.locator("#" + fragment)).to_be_visible()
            for source in (f"formats/asn1/{kind}.md", f"standards/{kind}/README.md"):
                expect(page.locator(f'a[href*="/blob/"][href$="/docs/{source}"]')).to_have_count(1)
                expect(page.locator(f'a[href*="/edit/"][href$="/docs/{source}"]')).not_to_have_count(0)
        page.goto(base_url + "formats/")
        page.locator("article").get_by_role("link", name="Core format guide", exact=True).click()
        expect(page).to_have_url(base_url + "formats/guide/")
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
