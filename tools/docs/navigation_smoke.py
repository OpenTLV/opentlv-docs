# SPDX-License-Identifier: MIT
# Copyright (c) 2026 Marek Cingel

"""Check portal, product, contributor and archive navigation in a built site."""

import argparse
from functools import partial
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
import threading

from playwright.sync_api import expect, sync_playwright

import js

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
        for path in ("tools/otlv/manual/", "languages/lua/manual/api/", "languages/python/manual/guides/python/",
                     "languages/rust/manual/guides/rust/"):
            page.goto(base_url + path)
            expect(page.locator('[data-md-component="tabs"]')).to_have_count(0)
            if width == 390:
                page.locator('.md-header label[for="__drawer"]').click()
            menu = page.locator(".md-nav--primary")
            check_reader_menu(menu, base_url)
            back = menu.get_by_role("link", name="OpenTLV portal", exact=True)
            expect(back).to_be_visible()
            back.click()
            expect(page).to_have_url(base_url)
        assert page.evaluate("document.documentElement.scrollWidth <= window.innerWidth"), width
    check_formats(page, base_url)
    check_catalogs(page, base_url)
    check_development(page, base_url)
    check_content_disposition(page, base_url)


def check_reader_menu(menu, base_url):
    """Reader menus must not retain relocated archive/contributor chapters."""
    links = menu.locator("a").evaluate_all("nodes => nodes.map(node => node.href)")
    for link in links:
        assert not link.startswith((base_url + "development/history/",
                                    base_url + "development/components/")), link


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
         "development/components/lua/releases/"),
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
        for path in ("documentation/layout", "documentation/ownership", "bindings/python",
                     "bindings/rust"):
            page.goto(base_url + "development/" + path + "/")
            note = page.locator("article .admonition.note").filter(has_text="Portal context")
            expect(note).to_have_count(1)
            note.get_by_role("link", name="current portal conventions", exact=True).click()
            expect(page).to_have_url(base_url + "development/documentation/")


def check_content_disposition(page, base_url):
    """Reach preserved evidence and current owner instructions through real links."""
    archives = (
        ("Go usage before extraction", "core/guides/go/", "current Go manual",
         "languages/go/manual/guides/go/", "opentlv", "guides/go.md", ()),
        ("Go development before extraction", "core/development/go/", "current Go development guide",
         "languages/go/manual/development/go/", "opentlv", "development/go.md", ()),
        ("Python extraction guide", "core/guides/python/", "current Python manual",
         "languages/python/manual/guides/python/", "opentlv", "guides/python.md", ()),
        ("Documentation audit (#513)", "core/documentation-audit/",
         "current documentation conventions", "development/documentation/",
         "opentlv", "development/documentation-audit.md", ()),
        ("Query phase implementation audit", "core/query-phase-audit/",
         "current query verification guide", "development/query-adversarial/",
         "opentlv", "development/query-phase-audit.md", ()),
        ("Reader decode performance report", "core/reader-decode-performance/",
         "current testing entry points", "development/testing/",
         "opentlv", "development/reader-decode-performance.md", ()),
        ("C++ facade performance report", "core/cxx-facade-performance/",
         "current testing entry points", "development/testing/",
         "opentlv", "development/cxx-facade-performance.md", ()),
        ("Lua migration provenance", "lua/migration/", "current Lua build guide",
         "languages/lua/manual/development/", "opentlv-lua", "migration.md",
         ("source-inventory.json",)),
        ("Python migration provenance", "python/migration/", "current Python development guide",
         "languages/python/manual/development/python/", "opentlv-python", "migration.md",
         ("inventory", "machine-readable report", "baseline output", "imported-source output")),
        ("Python standalone build validation", "python/validation/standalone-build/",
         "current Python build guide", "languages/python/manual/development/python/",
         "opentlv-python", "validation/standalone-build.md", ("machine-readable report",)),
        ("Python CI validation", "python/validation/ci/", "current Python quality gates",
         "development/components/python/quality-gates/", "opentlv-python",
         "validation/ci.md", ("machine-readable summary",)),
        ("Python packaging validation", "python/validation/packaging/", "current Python release guide",
         "development/components/python/releases/", "opentlv-python",
         "validation/packaging.md", ("machine-readable results",)),
        ("Python source layout validation", "python/validation/layout/",
         "current Python development guide", "languages/python/manual/development/python/",
         "opentlv-python", "validation/layout.md", ()),
        ("Rust migration provenance", "rust/migration/", "current Rust development guide",
         "languages/rust/manual/development/rust/", "opentlv-rust", "migration.md",
         ("inventory", "validation.json")),
        ("Rust standalone build validation", "rust/validation/standalone-build/",
         "current Rust build guide", "languages/rust/manual/development/rust/",
         "opentlv-rust", "validation/standalone-build.md", ("machine-readable report",)),
        ("Rust CI validation", "rust/validation/ci/", "current Rust quality gates",
         "development/components/rust/quality-gates/", "opentlv-rust",
         "validation/ci.md", ("machine-readable summary",)),
        ("Rust packaging validation", "rust/validation/packaging/", "current Rust packaging guide",
         "languages/rust/manual/packaging/", "opentlv-rust", "validation/packaging.md", ("CI evidence",)),
        ("Rust source layout validation", "rust/validation/layout/",
         "current Rust development guide", "languages/rust/manual/development/rust/",
         "opentlv-rust", "validation/layout.md", ("inventory",)),
    )
    contributors = (
        ("CLI development", "cli/development/", "opentlv-cli", "development.md"),
        ("CLI versions and releases", "cli/releases/", "opentlv-cli", "releases.md"),
        ("Lua tests and CI", "lua/testing/", "opentlv-lua", "testing.md"),
        ("Lua quality gates", "lua/quality-gates/", "opentlv-lua", "quality-gates.md"),
        ("Lua implementation and ownership", "lua/implementation/", "opentlv-lua", "implementation.md"),
        ("Lua release quality gate", "lua/releases/", "opentlv-lua", "releases.md"),
        ("Python tests and CI", "python/quality-gates/", "opentlv-python", "quality-gates.md"),
        ("Python release preparation", "python/releases/", "opentlv-python", "releases.md"),
        ("Rust tests and CI", "rust/quality-gates/", "opentlv-rust", "quality-gates.md"),
    )
    for width in (1440, 390):
        page.set_viewport_size({"width": width, "height": 900})
        page.goto(base_url + "development/")
        page.locator("article").get_by_role("link", name="Historical records", exact=True).click()
        expect(page).to_have_url(base_url + "development/history/")
        go_archives = [entry for entry in archives if entry[1] in (
            "core/guides/go/", "core/development/go/")]
        go_links = [page.locator("article").get_by_role("link", name=entry[0], exact=True).count()
                    for entry in go_archives]
        assert go_links in ([0, 0], [1, 1]), "Incomplete historical Core Go archive"
        for title, path, current_label, current, repository, source, assets in archives:
            if not any(go_links) and path in ("core/guides/go/", "core/development/go/"):
                continue
            page.locator("article").get_by_role("link", name=title, exact=True).click()
            expect(page).to_have_url(base_url + "development/history/" + path)
            expect(page.locator("article h1")).to_be_visible()
            note = page.locator("article .admonition.note").filter(has_text="Historical record")
            expect(note).to_have_count(1)
            expect(note).to_contain_text("historical snapshot")
            check_edit_owner(page, repository, source)
            for label in assets:
                link = page.locator("article").get_by_role("link", name=label, exact=True)
                response = page.request.get(link.evaluate("node => node.href"))
                assert response.status == 200 and response.body(), (path, label, response.status)
                assert "text/html" not in response.headers.get("content-type", ""), (path, label)
            note.get_by_role("link", name=current_label, exact=True).click()
            expect(page).to_have_url(base_url + current)
            expect(page.locator("article h1")).to_be_visible()
            page.go_back()
            note.get_by_role("link", name="historical records", exact=True).click()
            expect(page).to_have_url(base_url + "development/history/")

        page.goto(base_url + "development/")
        page.locator("article").get_by_role("link", name="Component contributor guides", exact=True).click()
        expect(page).to_have_url(base_url + "development/components/")
        for title, path, repository, source in contributors:
            page.locator("article").get_by_role("link", name=title, exact=True).click()
            expect(page).to_have_url(base_url + "development/components/" + path)
            expect(page.locator("article h1")).to_be_visible()
            expect(page.locator('[data-md-component="tabs"]')).to_have_count(1)
            check_edit_owner(page, repository, source)
            page.go_back()
            expect(page).to_have_url(base_url + "development/components/")


def check_edit_owner(page, repository, source):
    edit = page.locator(f'a[href^="https://github.com/OpenTLV/{repository}/edit/"]'
                        f'[href$="/docs/{source}"]')
    expect(edit).to_have_count(1)


def check_catalogs(page, base_url):
    """Follow discovery links into the actual selected manuals and application."""
    sources = page.request.get(base_url + "source-revision.json").json()["sources"]
    standalone_js = js.ready(sources)
    wasm_manual = ("languages/wasm/manual/webassembly/" if standalone_js
                   else "development/history/core/development/webassembly/")
    languages = (
        ("C", "languages/c/", "C API reference", "api/reference/c/"),
        ("C++", "languages/cpp/", "C++ API reference", "api/reference/cpp/"),
        ("Python", "languages/python/", "Python manual", "languages/python/manual/guides/python/"),
        ("Lua", "languages/lua/", "Lua manual", "languages/lua/manual/api/"),
        ("Rust", "languages/rust/", "Rust manual", "languages/rust/manual/guides/rust/"),
        ("Go", "languages/go/", "Go manual", "languages/go/manual/guides/go/"),
        ("WebAssembly", "languages/wasm/", "WebAssembly manual", wasm_manual),
    )
    tools = (
        ("otlv CLI", "tools/otlv/", "otlv manual", "tools/otlv/manual/"),
        ("TLV playground", "tools/playground/overview/", "Open the TLV playground", "tools/playground/"),
        ("imtlv", "tools/imtlv/", None, None),
    )
    for width in (1440, 390):
        page.set_viewport_size({"width": width, "height": 900})
        for catalog, entries in (("languages/", languages), ("tools/", tools)):
            page.goto(base_url + catalog)
            section = page.locator(".md-nav--primary > ul > li").nth(
                4 if catalog == "languages/" else 5)
            check_reader_menu(section, base_url)
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
                    if title in ("Python", "Lua", "Rust", "Go", "otlv CLI") or (title == "WebAssembly" and standalone_js):
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
