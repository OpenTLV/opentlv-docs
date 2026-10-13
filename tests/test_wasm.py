# SPDX-License-Identifier: MIT
# Copyright (c) 2026 Marek Cingel

import copy
import json
import os
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

from mkdocs.exceptions import PluginError
import test_portal
from test_portal import load_hook

wasm = load_hook("wasm")


class WasmTests(unittest.TestCase):
    def setUp(self):
        temp = tempfile.TemporaryDirectory()
        self.addCleanup(temp.cleanup)
        self.directory = Path(temp.name)
        for name in wasm.FILES:
            (self.directory / name).write_bytes(b"\0asm\x01\0\0\0" if name.endswith(".wasm") else b"export {};")
        self.source = {"repository": "https://github.com/OpenTLV/opentlv", "commit": "a" * 40,
                       "local": False, "dirty": False}
        self.manifest = dict(self.source, schema=1, source_sha256="b" * 64,
                             emscripten=wasm.EMSCRIPTEN, files=wasm.hashes(self.directory))
        self.save()

    def save(self):
        (self.directory / wasm.MANIFEST).write_text(json.dumps(self.manifest), encoding="utf-8")

    def verify(self):
        return wasm.verify(self.directory, self.source, "b" * 64)

    def test_four_module_files_are_verified(self):
        self.assertEqual(self.verify(), self.manifest)
        self.assertIn("query.mjs", self.manifest["files"])

    def test_rejects_mismatched_sources_toolchain_local_and_checksums(self):
        original = copy.deepcopy(self.manifest)
        for change in ({"commit": "c" * 40}, {"repository": "https://github.com/other/repo"},
                       {"source_sha256": "c" * 64}, {"emscripten": "unselected"},
                       {"local": True}, {"dirty": True}, {"files": {}}):
            with self.subTest(change=change):
                self.manifest = dict(original, **change)
                self.save()
                with self.assertRaises(PluginError):
                    self.verify()

    def test_missing_query_and_modified_bytes_fail(self):
        path = self.directory / "query.mjs"
        path.write_text("modified", encoding="utf-8")
        with self.assertRaisesRegex(PluginError, "checksums"):
            self.verify()
        path.unlink()
        with self.assertRaisesRegex(PluginError, "module files"):
            self.verify()

    def test_missing_manifest_and_invalid_module_header_fail(self):
        (self.directory / wasm.MANIFEST).unlink()
        with self.assertRaisesRegex(PluginError, "provenance"):
            self.verify()
        self.save()
        (self.directory / "opentlv-core.wasm").write_text("not wasm", encoding="utf-8")
        with self.assertRaisesRegex(PluginError, "header"):
            self.verify()

    def test_explicit_missing_directory_never_silently_omitted(self):
        with patch.dict(os.environ, {"OPENTLV_WASM_DIR": str(self.directory / "absent")}):
            with patch.object(wasm.api, "fingerprint", return_value="b" * 64):
                with self.assertRaisesRegex(PluginError, "provenance"):
                    wasm.prepare(self.directory, self.directory, self.source)


class PlaygroundOwnershipTests(unittest.TestCase):
    def test_portal_owns_ui_with_old_core_and_after_extraction(self):
        fixture = test_portal.PortalTests()
        fixture.setUp()
        self.addCleanup(fixture.doCleanups)
        assembly = load_hook("assembly")
        for name in ("index.md", "playground.js", "playground.css"):
            fixture.write(fixture.core / "docs/playground" / name, "old UI")
            fixture.write(fixture.portal / "docs/playground" / name, "portal UI")
        fixture.git("add", ".")
        fixture.git("-c", "user.name=Fixture", "-c", "user.email=fixture@example.invalid", "commit", "-m", "Old UI")
        with patch.dict(os.environ, {"OPENTLV_DOCS_LOCAL": "1"}):
            assembly.assemble(fixture.portal)
            for name in ("index.md", "playground.js", "playground.css"):
                self.assertEqual((fixture.portal / "build/assembled/docs/playground" / name).read_text(), "portal UI")
                (fixture.core / "docs/playground" / name).unlink()
            assembly.assemble(fixture.portal)
            self.assertEqual((fixture.portal / "build/assembled/docs/playground/playground.js").read_text(), "portal UI")
