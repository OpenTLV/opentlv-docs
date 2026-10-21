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
