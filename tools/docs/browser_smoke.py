# SPDX-License-Identifier: MIT
# Copyright (c) 2026 Marek Cingel

"""Exercise real browser imports and parsing under the prepared version prefixes."""

import argparse
from functools import partial
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
import json
from pathlib import Path
import threading

from playwright.sync_api import sync_playwright, expect


def check(site, version):
    versions = json.loads((site / "versions.json").read_text(encoding="utf-8"))
    selected = next(item for item in versions if item["version"] == version)
    prefixes = [version, *selected.get("aliases", [])]
    # Also exercise the GitHub project mount, not just a localhost root.
    class Handler(SimpleHTTPRequestHandler):
        # Windows registry MIME mappings can label .js as text/plain. Use the
        # standard module/WASM types served by GitHub Pages on every platform.
        extensions_map = {**SimpleHTTPRequestHandler.extensions_map,
                          ".js": "text/javascript", ".mjs": "text/javascript", ".wasm": "application/wasm"}

        def do_GET(self):
            if self.path.startswith("/opentlv-docs/"):
                self.path = self.path[len("/opentlv-docs"):]
            super().do_GET()

        def log_message(self, *_args):
            pass

    server = ThreadingHTTPServer(("127.0.0.1", 0), partial(Handler, directory=str(site)))
    worker = threading.Thread(target=server.serve_forever, daemon=True)
    worker.start()
    try:
        with sync_playwright() as playwright:
            browser = playwright.chromium.launch()
            for prefix in prefixes:
                page = browser.new_page()
                failures = []
                diagnostics = []
                page.on("console", lambda message: diagnostics.append(message.text) if message.type == "error" else None)
                page.on("pageerror", lambda error: failures.append(str(error)))
                page.on("response", lambda response: failures.append(response.url)
                        if response.status >= 400 and response.url.startswith("http://127.0.0.1:") else None)
                page.goto(f"http://127.0.0.1:{server.server_port}/opentlv-docs/{prefix}/playground/")
                try:
                    expect(page.locator("#otlv-pg-status")).to_contain_text("loaded.", timeout=30000)
                except AssertionError as error:
                    raise AssertionError(f"{error}\nBrowser diagnostics: {diagnostics}\nFailed assets: {failures}") from error
                expect(page.locator("#otlv-pg-parse")).to_be_enabled()
                page.locator("#otlv-pg-format").select_option("ber")
                page.locator("#otlv-pg-input").fill("04 01 41")
                page.locator("#otlv-pg-parse").click()
                expect(page.locator("#otlv-pg-error")).to_be_hidden()
                expect(page.locator("#otlv-pg-output")).not_to_be_empty()
                page.get_by_role("tab", name="JSON", exact=True).click()
                result = json.loads(page.locator(".otlv-pg-json").inner_text())
                assert result["format"] == "ber" and not result.get("error"), result
                assert len(result["elements"]) == 1, result
                page.locator("#otlv-pg-input").fill("04 02 41")
                page.locator("#otlv-pg-parse").click()
                expect(page.locator("#otlv-pg-error")).to_contain_text("Parse error")
                assert not failures, failures
                page.close()
                print(f"Browser playground passed: {prefix}")
            browser.close()
    finally:
        server.shutdown()
        server.server_close()
        worker.join()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("site", type=Path)
    parser.add_argument("--version")
    args = parser.parse_args()
    selection = Path(__file__).resolve().parents[2] / "build/selection.json"
    version = args.version or json.loads(selection.read_text(encoding="utf-8"))["version"]
    check(args.site.resolve(), version)
