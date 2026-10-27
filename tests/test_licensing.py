# SPDX-License-Identifier: MIT
# Copyright (c) 2026 Marek Cingel

"""REUSE annotations, license texts and copyright holders are repository contracts."""

from pathlib import Path
from types import SimpleNamespace
import hashlib
import importlib.util
import json
import re
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch

import yaml
from mkdocs.exceptions import PluginError
from mkdocs.config import load_config
from mkdocs.structure.files import Files, File

try:
    import tomllib
except ModuleNotFoundError:  # Python 3.10; CI reads REUSE.toml with 3.12.
    tomllib = None

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location("license_hook", ROOT / "tools/docs/licensing.py")
licensing = importlib.util.module_from_spec(spec)
spec.loader.exec_module(licensing)
HOLDER = "2026 Marek Cingel"
# REUSE-IgnoreStart
# Copyright lines of headers, REUSE metadata and LICENSE files, in any comment syntax.
NOTICE = re.compile(r'^[\s#/*;{-]*(?:Copyright \(c\)|SPDX-FileCopyrightText:?\s*=?)\s*"?(.+)$',
                    re.MULTILINE)
# REUSE-IgnoreEnd
# REUSE does not read examples between these markers as the file's own metadata.
IGNORED = re.compile(rb"REUSE-IgnoreStart.*?REUSE-IgnoreEnd", re.DOTALL)


def tracked():
    return subprocess.run(["git", "ls-files", "--cached", "--others", "--exclude-standard"],
                          cwd=ROOT, check=True, capture_output=True, text=True).stdout.splitlines()


def annotations():
    return tomllib.loads((ROOT / "REUSE.toml").read_text(encoding="utf-8"))["annotations"]


class LicensingTests(unittest.TestCase):
    @unittest.skipIf(tomllib is None, "tomllib requires Python 3.11")
    def test_annotations_list_existing_unheadered_files_explicitly(self):
        files = set(tracked())
        listed = [path for annotation in annotations() for path in annotation["path"]]
        self.assertEqual(len(listed), len(set(listed)))
        for path in listed:
            # A glob would also cover new sources, which must carry their own header.
            self.assertFalse(set("*?[") & set(path), path)
            self.assertIn(path, files)
            data = IGNORED.sub(b"", (ROOT / path).read_bytes())
            self.assertNotIn(b"SPDX-License-Identifier", data, path)
        for annotation in annotations()[:2]:
            self.assertEqual(annotation["SPDX-FileCopyrightText"], HOLDER)
            self.assertEqual(annotation["SPDX-License-Identifier"], "MIT")

    def test_reuse_license_text_matches_repository_license(self):
        license_text = (ROOT / "LICENSE").read_text(encoding="utf-8")
        template = (ROOT / "LICENSES/MIT.txt").read_text(encoding="utf-8")
        # The texts differ only in the copyright line and their line wrapping.
        # REUSE-IgnoreStart
        license_text = license_text.replace(f"Copyright (c) {HOLDER}", "Copyright (c) <year> <copyright holders>")
        # REUSE-IgnoreEnd
        self.assertEqual(license_text.split(), template.split())
        self.assertEqual(sorted(path.name for path in (ROOT / "LICENSES").iterdir()), ["Apache-2.0.txt", "LLVM-exception.txt", "MIT.txt", "NCSA.txt"])

    def test_organization_is_not_a_copyright_holder(self):
        notices = 0
        for path in tracked():
            data = (ROOT / path).read_bytes()
            if b"\0" in data:
                continue
            for holder in NOTICE.findall(data.decode("utf-8")):
                notices += 1
                self.assertNotIn("OpenTLV", holder, path)
        self.assertGreater(notices, 60)


class DistributedLicenseTests(unittest.TestCase):
    def setUp(self):
        temp = tempfile.TemporaryDirectory()
        self.addCleanup(temp.cleanup)
        self.root = Path(temp.name)
        self.component = self.root / "component"
        self.component.mkdir()
        (self.component / "LICENSE").write_bytes(b"Fixture contributor notice\r\nKeep exact bytes.\r\n")
        self.sources = [{"id": "core", "repository": "https://github.com/OpenTLV/opentlv",
                         "commit": "a" * 40, "included": True}]

    def bundle(self, with_wasm=True):
        return licensing.bundle(ROOT, {"core": self.component}, self.sources, with_wasm)

    def stage(self):
        notices, metadata = self.bundle()
        directory = self.root / "site/licenses"
        directory.mkdir(parents=True)
        for name, data in notices.items():
            (directory / name).write_bytes(data)
        (directory / "manifest.json").write_text(json.dumps(metadata), encoding="utf-8")
        wasm = self.root / "site/playground/wasm/opentlv-core.wasm"
        wasm.parent.mkdir(parents=True)
        wasm.write_bytes(b"\0asm\1\0\0\0")
        return directory, metadata

    def test_exact_upstream_and_selected_component_notice_bytes(self):
        notices, metadata = self.bundle()
        self.assertEqual(notices["core-LICENSE.txt"], (self.component / "LICENSE").read_bytes())
        self.assertIn(b"Permission is hereby granted", notices["material-LICENSE.txt"])
        self.assertEqual(metadata["sources"], [{key: self.sources[0][key]
                                              for key in ("id", "repository", "commit")}])
        for name, digest in licensing.RUNTIME_NOTICES.items():
            self.assertEqual(hashlib.sha256(notices[name]).hexdigest(), digest)
        without_runtime, metadata = self.bundle(False)
        self.assertNotIn("emscripten", metadata)
        self.assertNotIn("emscripten-LICENSE.txt", without_runtime)

    def test_missing_empty_and_changed_source_notices_fail(self):
        notice = self.component / "LICENSE"
        notice.write_bytes(b"")
        with self.assertRaises(PluginError):
            self.bundle()
        notice.unlink()
        with self.assertRaises(PluginError):
            self.bundle()
        notice.write_text("Component license", encoding="utf-8")
        original = licensing.read_notice
        def changed(path):
            return b"rewritten" if Path(path).name == "musl-COPYRIGHT.txt" else original(path)
        with patch.object(licensing, "read_notice", side_effect=changed), self.assertRaises(PluginError):
            self.bundle()

    def test_artifact_rejects_modified_missing_and_unlisted_runtime_notices(self):
        directory, metadata = self.stage()
        licensing.verify_site(directory.parent, metadata)
        path = directory / "musl-COPYRIGHT.txt"
        original = path.read_bytes()
        path.write_bytes(b"modified")
        with self.assertRaises(PluginError):
            licensing.verify_site(directory.parent)
        path.unlink()
        with self.assertRaises(PluginError):
            licensing.verify_site(directory.parent)
        path.write_bytes(original)
        del metadata["files"][path.name]
        (directory / "manifest.json").write_text(json.dumps(metadata), encoding="utf-8")
        with self.assertRaises(PluginError):
            licensing.verify_site(directory.parent)

    def test_snapshot_provenance_rejects_rewritten_manifest(self):
        directory, metadata = self.stage()
        manifest = directory / "manifest.json"
        source = {"licensing": {"manifest": licensing.MANIFEST,
                                "sha256": hashlib.sha256(manifest.read_bytes()).hexdigest()}}
        licensing.verify_record(directory.parent, source)
        metadata["theme"]["version"] = "different"
        manifest.write_text(json.dumps(metadata), encoding="utf-8")
        with self.assertRaises(PluginError):
            licensing.verify_record(directory.parent, source)
        # Old immutable releases do not gain a new distribution contract on replay.
        licensing.verify_record(self.root / "old-release", {})

    def test_unsafe_manifest_paths_are_rejected(self):
        directory, metadata = self.stage()
        metadata["files"]["../outside"] = "a" * 64
        (directory / "manifest.json").write_text(json.dumps(metadata), encoding="utf-8")
        with self.assertRaises(PluginError):
            licensing.verify_site(directory.parent)

    def test_changed_playground_toolchain_requires_new_notice_review(self):
        config = SimpleNamespace(extra={"sources": self.sources, "license_checkouts": {"core": self.component}})
        wasm = File("playground/wasm/opentlv-core.wasm", str(self.root), str(self.root / "site"), True)
        manifest = File("playground/wasm/wasm-source.json", str(self.root), str(self.root / "site"), True)
        manifest.content_string = json.dumps({"emscripten": "unreviewed"})
        for files in (Files([wasm]), Files([wasm, manifest])):
            with self.assertRaisesRegex(PluginError, "toolchain changed"):
                licensing.on_files(files, config)

    def test_actual_theme_build_links_local_notices_from_nested_pages(self):
        docs = self.root / "docs"
        (docs / "nested").mkdir(parents=True)
        (docs / "index.md").write_text("# Home\n", encoding="utf-8")
        (docs / "nested/page.md").write_text("# Nested\n", encoding="utf-8")
        (docs / "source-revision.json").write_text("{}", encoding="utf-8")
        runtime = docs / "playground/wasm"
        runtime.mkdir(parents=True)
        (runtime / "opentlv-core.wasm").write_bytes(b"\0asm\1\0\0\0")
        (runtime / "wasm-source.json").write_text(json.dumps({"emscripten": licensing.TOOLCHAIN}), encoding="utf-8")
        config = {"site_name": "Fixture", "docs_dir": str(docs), "site_dir": str(self.root / "site"),
                  "theme": {"name": "material", "custom_dir": str(ROOT / "tools/docs/overrides")},
                  "hooks": [str(ROOT / "tools/docs/licensing.py")], "plugins": [],
                  "extra": {"sources": self.sources, "license_checkouts": {"core": str(self.component)}}}
        path = self.root / "mkdocs.yml"
        path.write_text(yaml.safe_dump(config), encoding="utf-8")
        result = subprocess.run([sys.executable, "-B", "-m", "mkdocs", "build", "--strict", "-f", str(path)],
                                capture_output=True, text=True, encoding="utf-8", errors="replace")
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        site = self.root / "site"
        self.assertIn('href="../../licenses/index.html"', (site / "nested/page/index.html").read_text())
        self.assertIn("Material for MkDocs", (site / "index.html").read_text())
        for name in licensing.RUNTIME_NOTICES:
            self.assertEqual((site / "licenses" / name).read_bytes(), (ROOT / "notices" / name).read_bytes())
        licensing.verify_record(site, json.loads((site / "source-revision.json").read_text()))
        # A source page must not shadow the static notices, even by case folding.
        loaded = load_config(str(path))
        collision = File("LICENSES/index.html", str(docs), str(site), True)
        with self.assertRaisesRegex(PluginError, "cannot replace"):
            licensing.on_files(Files([collision]), loaded)


if __name__ == "__main__":
    unittest.main()
