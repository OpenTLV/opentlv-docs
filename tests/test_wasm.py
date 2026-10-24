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
        self.directory = Path(temp.name).resolve()
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

    def test_standalone_artifacts_require_both_selected_sources(self):
        producer = dict(self.source, repository="https://github.com/OpenTLV/opentlv-js", commit="c" * 40)
        self.manifest.update(schema=2, js=wasm.producer_identity(producer, "d" * 64))
        self.save()
        self.assertEqual(wasm.verify(self.directory, self.source, "b" * 64, producer, "d" * 64), self.manifest)
        for change in ({"commit": "e" * 40}, {"repository": "https://github.com/other/repo"},
                       {"local": True}, {"dirty": True}, {"source_sha256": "e" * 64}):
            with self.subTest(change=change):
                self.manifest["js"] = dict(wasm.producer_identity(producer, "d" * 64), **change)
                self.save()
                with self.assertRaises(PluginError):
                    wasm.verify(self.directory, self.source, "b" * 64, producer, "d" * 64)
        self.manifest.pop("js")
        self.manifest["schema"] = 1
        self.save()
        with self.assertRaises(PluginError):
            wasm.verify(self.directory, self.source, "b" * 64, producer, "d" * 64)

    def test_standalone_build_uses_selected_js_and_core(self):
        core = self.directory / "core"
        producer_root = self.directory / "js"
        producer = dict(self.source, repository="https://github.com/OpenTLV/opentlv-js", commit="c" * 40)
        dist = self.directory / "build/wasm/dist"
        def run(command):
            if "--version" in command:
                return f"emcc (Emscripten) {wasm.EMSCRIPTEN}"
            if "--build" in command:
                dist.mkdir(parents=True)
                for name in wasm.FILES:
                    (dist / name).write_bytes((self.directory / name).read_bytes())
            return ""
        with patch.object(wasm.api, "fingerprint", side_effect=lambda root: "b" * 64 if root == core else "d" * 64), \
                patch.object(wasm.api, "run", side_effect=run) as commands:
            self.assertEqual(wasm.generate(self.directory, core, self.source, producer_root, producer), dist)
        configure = commands.call_args_list[1].args[0]
        self.assertEqual(configure[configure.index("-S") + 1], producer_root)
        self.assertIn(f"-DFETCHCONTENT_SOURCE_DIR_OPENTLV_CORE={core}", configure)
        self.assertNotIn("-DOPENTLV_BUILD_WASM=ON", configure)
        wasm.verify(dist, self.source, "b" * 64, producer, "d" * 64)

    def test_local_preview_keeps_dirty_producer_evidence_for_identical_bytes(self):
        producer = dict(self.source, repository="https://github.com/OpenTLV/opentlv-js", commit="c" * 40)
        self.manifest.update(schema=2, js=dict(wasm.producer_identity(producer, "d" * 64), local=True, dirty=True))
        self.save()
        # Git line-ending settings can differ between the build and preview
        # hosts. The exact source fingerprint still has to match, and the
        # original dirty/local evidence must never become publishable.
        wasm.verify(self.directory, dict(self.source, local=True), "b" * 64, producer, "d" * 64)
        with self.assertRaisesRegex(PluginError, "cannot be published"):
            wasm.verify(self.directory, self.source, "b" * 64, producer, "d" * 64)

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
