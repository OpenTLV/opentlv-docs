# SPDX-License-Identifier: MIT
# Copyright (c) 2026 Marek Cingel

import base64
import copy
import hashlib
import io
import json
import os
from pathlib import Path
import tarfile
import tempfile
import unittest
from unittest.mock import patch

from mkdocs.exceptions import PluginError
import test_portal
from test_portal import load_hook

wasm = load_hook("wasm")
ROOT = Path(__file__).resolve().parents[1]


def package_members(version="1.2.3"):
    """A complete fixture package; runtime notices use the reviewed bytes."""
    dist = {"opentlv.mjs": b"export {};\n", "query.mjs": b"export const query = 1;\n",
            "opentlv-core.js": b"export default async () => ({});\n",
            "opentlv-core.wasm": b"\0asm\x01\0\0\0fixture"}
    members = {f"dist/{name}": data for name, data in dist.items()}
    for name in wasm.NOTICES:
        runtime = ROOT / "notices" / Path(name).name
        members[name] = runtime.read_bytes() if runtime.is_file() else f"Fixture {name}\n".encode()
    members["package.json"] = json.dumps({
        "name": wasm.PACKAGE, "version": version, "type": "module",
        "exports": {".": {"import": "./index.mjs"}, **wasm.EXPORTS}}).encode()
    members["package-info.json"] = json.dumps({
        "name": wasm.PACKAGE, "version": version,
        "core": {"repository": "https://github.com/OpenTLV/opentlv.git", "commit": "c" * 40,
                 "tree": "d" * 40, "version_inputs": {"tag": "v9.9.9"}},
        "outputs": {name: hashlib.sha256(data).hexdigest() for name, data in dist.items()}}).encode()
    return members


def tarball(members, extra=()):
    output = io.BytesIO()
    with tarfile.open(fileobj=output, mode="w:gz", format=tarfile.PAX_FORMAT) as archive:
        for name, data in [*(("package/" + key, value) for key, value in sorted(members.items())), *extra]:
            info = tarfile.TarInfo(name)
            info.size = len(data)
            info.mtime = 499162500
            archive.addfile(info, io.BytesIO(data))
    return output.getvalue()


class PackageTests(unittest.TestCase):
    def setUp(self):
        temp = tempfile.TemporaryDirectory()
        self.addCleanup(temp.cleanup)
        self.root = Path(temp.name).resolve()
        (self.root / wasm.PIN).mkdir(parents=True)
        patcher = patch.object(wasm, "ROOT", self.root)
        patcher.start()
        self.addCleanup(patcher.stop)
        self.use(package_members())
        self.publisher = dict(wasm.PUBLISHER, ref="refs/heads/main", commit="e" * 40)
        self.fetch = patch.object(wasm, "fetch", side_effect=self.download)
        self.fetch.start()
        self.addCleanup(self.fetch.stop)

    def use(self, members, version="1.2.3", data=None):
        """Pin a (possibly changed) package, as a reviewed pin update would."""
        self.members = members
        self.data = data or tarball(members)
        self.served = self.data
        self.write_pin(version, "sha512-" + base64.b64encode(hashlib.sha512(self.data).digest()).decode())

    def write_pin(self, version, integrity, resolved=None, dependency=None):
        resolved = resolved or f"{wasm.REGISTRY}@opentlv/opentlv/-/opentlv-{version}.tgz"
        package = {"name": "fixture", "version": "0.0.0", "private": True,
                   "dependencies": {wasm.PACKAGE: dependency or version}}
        lock = {"name": "fixture", "version": "0.0.0", "lockfileVersion": 3, "requires": True,
                "packages": {"": {"name": "fixture", "version": "0.0.0",
                                  "dependencies": {wasm.PACKAGE: dependency or version}},
                             f"node_modules/{wasm.PACKAGE}": {"version": version, "resolved": resolved,
                                                              "integrity": integrity}}}
        (self.root / wasm.PIN / "package.json").write_text(json.dumps(package), encoding="utf-8")
        (self.root / wasm.PIN / "package-lock.json").write_text(json.dumps(lock), encoding="utf-8")
        return package, lock

    def statement(self, **changes):
        pin = wasm.load_pin()
        workflow = {"repository": self.publisher["repository"], "path": self.publisher["workflow"],
                    "ref": self.publisher["ref"]}
        workflow.update({key: value for key, value in changes.items() if key in ("repository", "path")})
        statement = {"subject": [{"name": f"pkg:npm/%40opentlv/opentlv@{pin['version']}",
                                  "digest": {"sha512": changes.get("sha512", pin["sha512"])}}],
                     "predicate": {"buildDefinition": {
                         "externalParameters": {"workflow": workflow},
                         "resolvedDependencies": [{"uri": f"git+{workflow['repository']}@refs/heads/main",
                                                   "digest": {"gitCommit": self.publisher["commit"]}}]},
                         "runDetails": {"metadata": {"invocationId":
                                                     f"{workflow['repository']}/actions/runs/1/attempts/1"}}}}
        payload = base64.b64encode(json.dumps(statement).encode()).decode()
        return {"attestations": [{"predicateType": changes.get("type", wasm.SLSA),
                                  "bundle": {"dsseEnvelope": {"payload": payload}}}]}

    def download(self, url):
        if url.endswith(".tgz"):
            return self.served
        self.assertIn("/-/npm/v1/attestations/%40opentlv%2Fopentlv@", url)
        return json.dumps(getattr(self, "attestation", None) or self.statement()).encode()

    def generate(self, **kwargs):
        return wasm.generate(self.root, **kwargs)

    def test_actual_pin_is_one_exact_locked_registry_package(self):
        pin = wasm.load_pin(ROOT)
        self.assertRegex(pin["version"], r"\A\d+\.\d+\.\d+\Z")
        self.assertEqual(pin["resolved"], f"{wasm.REGISTRY}@opentlv/opentlv/-/opentlv-{pin['version']}.tgz")
        self.assertEqual(len(pin["sha512"]), 128)

    def test_floating_partial_or_redirected_pins_fail(self):
        version, integrity = "1.2.3", wasm.load_pin()["integrity"]
        for case in ({"dependency": "^1.2.3"}, {"dependency": "latest"}, {"integrity": "sha1-AAAA"},
                     {"resolved": "https://mirror.example.invalid/opentlv-1.2.3.tgz"},
                     {"version": "1.2.3-rc.1"}):
            with self.subTest(case=case):
                self.write_pin(case.get("version", version), case.get("integrity", integrity),
                               case.get("resolved"), case.get("dependency"))
                with self.assertRaises(PluginError):
                    wasm.load_pin()
        _package, lock = self.write_pin(version, integrity)
        lock["packages"]["node_modules/other"] = {"version": "1.0.0"}
        (self.root / wasm.PIN / "package-lock.json").write_text(json.dumps(lock), encoding="utf-8")
        with self.assertRaisesRegex(PluginError, "exact published package"):
            wasm.load_pin()
        (self.root / wasm.PIN / "package-lock.json").unlink()
        with self.assertRaisesRegex(PluginError, "pin"):
            wasm.load_pin()

    def test_repeated_builds_reproduce_verified_assets_without_compilers(self):
        with patch.object(wasm.api, "run", side_effect=AssertionError("no command may run")):
            directory = self.generate()
            first = {path.name: path.read_bytes() for path in directory.iterdir()}
            self.generate()
        self.assertEqual({path.name: path.read_bytes() for path in directory.iterdir()}, first)
        for name in wasm.FILES:
            self.assertEqual(first[name], self.members[f"dist/{name}"])
        manifest = wasm.verify(directory, wasm.load_pin())
        self.assertEqual(manifest["package"]["sha256"], hashlib.sha256(self.data).hexdigest())
        self.assertEqual(manifest["core"], {"repository": "https://github.com/OpenTLV/opentlv.git",
                                            "commit": "c" * 40, "tree": "d" * 40, "tag": "v9.9.9"})
        self.assertEqual(manifest["provenance"]["commit"], "e" * 40)
        with self.assertRaisesRegex(PluginError, "signatures"):
            wasm.verify(directory, wasm.load_pin(), publish=True)

    def test_tampered_package_bytes_fail_integrity(self):
        for served in (self.data[:-1] + bytes([self.data[-1] ^ 1]),
                       tarball(dict(self.members, **{"dist/query.mjs": b"export const evil = 1;\n"}))):
            with self.subTest(size=len(served)):
                self.served = served
                with self.assertRaisesRegex(PluginError, "locked integrity"):
                    self.generate()
        self.assertFalse((self.root / wasm.OUTPUT).exists())

    def test_missing_assets_and_api_or_notice_changes_fail(self):
        def package(**changes):
            data = json.loads(self.members["package.json"])
            data.update(changes)
            return json.dumps(data).encode()
        exports = dict(wasm.EXPORTS, **{"./opentlv.mjs": "./opentlv.mjs"})
        info = json.loads(self.members["package-info.json"])
        info["outputs"]["query.mjs"] = "0" * 64
        original = dict(self.members)
        cases = (({"dist/query.mjs": None}, "assets missing"),
                 ({"dist/opentlv-core.wasm": b"not wasm"}, "header"),
                 ({"package.json": package(exports=exports)}, "API"),
                 ({"package.json": package(type="commonjs")}, "API"),
                 ({"package.json": package(name="@other/opentlv")}, "identity"),
                 ({"package-info.json": json.dumps(info).encode()}, "package-info"),
                 ({"notices/new-LICENSE.txt": b"New third-party code\n"}, "review"),
                 ({"THIRD_PARTY.md": None}, "review"),
                 ({"notices/musl-COPYRIGHT.txt": b"rewritten notice\n"}, None))
        for change, message in cases:
            with self.subTest(change=list(change)):
                members = {key: value for key, value in dict(original, **change).items() if value is not None}
                self.use(members)
                if message is None:
                    # Notice text is checked by the license hook against the reviewed copy.
                    self.assertTrue(self.generate().is_dir())
                    continue
                with self.assertRaisesRegex(PluginError, message):
                    self.generate()

    def test_unsafe_archive_entries_fail(self):
        for name in ("package/../outside", "/package/abs", "other/file"):
            with self.subTest(name=name):
                self.use(self.members, data=tarball(self.members, ((name, b"x"),)))
                with self.assertRaisesRegex(PluginError, "Unsafe"):
                    self.generate()

    def test_provenance_must_match_tarball_and_reviewed_publisher(self):
        for change in ({"repository": "https://github.com/other/opentlv-js"},
                       {"path": ".github/workflows/other.yml"}, {"sha512": "0" * 128},
                       {"type": "https://example.invalid/other"}):
            with self.subTest(change=change):
                self.attestation = self.statement(**change)
                with self.assertRaisesRegex(PluginError, "provenance"):
                    self.generate()

    def test_signature_audit_installs_lock_and_compares_installed_bytes(self):
        installed = self.root / "build/playground/npm/node_modules" / wasm.PACKAGE
        tamper = {}
        def run(command):
            if command[1] == "ci":
                self.assertIn("--ignore-scripts", command)
                self.assertEqual((Path(command[3]) / "package-lock.json").read_bytes(),
                                 (self.root / wasm.PIN / "package-lock.json").read_bytes())
                for name, data in dict(self.members, **tamper).items():
                    (installed / name).parent.mkdir(parents=True, exist_ok=True)
                    (installed / name).write_bytes(data)
            return "11.0.0" if command[1] == "--version" else ""
        with patch.object(wasm.api, "run", side_effect=run) as commands:
            manifest = wasm.verify(self.generate(signatures=True), wasm.load_pin(), publish=True)
        self.assertEqual(manifest["signatures"], {"tool": "npm audit signatures", "npm": "11.0.0"})
        self.assertIn(["audit", "signatures"], [command[1:3] for command in
                                                (call.args[0] for call in commands.call_args_list)])
        tamper["dist/opentlv-core.wasm"] = b"\0asm\x01\0\0\0changed"
        with patch.object(wasm.api, "run", side_effect=run), \
                self.assertRaisesRegex(PluginError, "differs from the verified tarball"):
            self.generate(signatures=True)
        failed = PluginError("audit failed")
        with patch.object(wasm.api, "run", side_effect=lambda command: (_ for _ in ()).throw(failed)
                          if command[1] == "audit" else run(command)), \
                self.assertRaisesRegex(PluginError, "audit failed"):
            self.generate(signatures=True)

    def test_verify_rejects_stale_pins_and_modified_or_missing_files(self):
        directory = self.generate()
        pin = wasm.load_pin()
        for change in ({"version": "9.9.9"}, {"integrity": "sha512-" + "A" * 86 + "=="},
                       {"lock_sha256": "0" * 64}):
            with self.subTest(change=change), self.assertRaisesRegex(PluginError, "reviewed pin"):
                wasm.verify(directory, dict(pin, **change))
        manifest = json.loads((directory / wasm.MANIFEST).read_text())
        for change in ({"schema": 2}, {"provenance": dict(manifest["provenance"], repository="x")},
                       {"signatures": {"tool": "unverified"}}, {"notices": {}}):
            with self.subTest(change=list(change)):
                (directory / wasm.MANIFEST).write_text(json.dumps(dict(manifest, **change)), encoding="utf-8")
                with self.assertRaises(PluginError):
                    wasm.verify(directory, pin)
        (directory / wasm.MANIFEST).write_text(json.dumps(manifest), encoding="utf-8")
        (directory / "query.mjs").write_text("tampered", encoding="utf-8")
        with self.assertRaisesRegex(PluginError, "checksums"):
            wasm.verify(directory, pin)
        (directory / "query.mjs").unlink()
        with self.assertRaisesRegex(PluginError, "module files"):
            wasm.verify(directory, pin)
        directory = self.generate()
        (directory / "musl-COPYRIGHT.txt").write_bytes(b"rewritten")
        with self.assertRaisesRegex(PluginError, "notice checksums"):
            wasm.verify(directory, pin)
        # A published site carries notices under licenses/, verified by that hook.
        wasm.verify(directory, pin, notices=False)
        (directory / wasm.MANIFEST).unlink()
        with self.assertRaisesRegex(PluginError, "provenance"):
            wasm.verify(directory, pin)

    def test_prepare_requires_assets_only_when_requested(self):
        with patch.dict(os.environ, {"OPENTLV_DOCS_REQUIRE_WASM": "0"}):
            self.assertEqual(wasm.prepare(self.root), (None, None))
        with patch.dict(os.environ, {"OPENTLV_DOCS_REQUIRE_WASM": "1"}), \
                self.assertRaisesRegex(PluginError, "required"):
            wasm.prepare(self.root)
        with patch.dict(os.environ, {"OPENTLV_WASM_DIR": str(self.root / "absent")}), \
                self.assertRaisesRegex(PluginError, "provenance"):
            wasm.prepare(self.root)
        directory = self.generate()
        with patch.dict(os.environ, {"OPENTLV_DOCS_REQUIRE_WASM": "1", "OPENTLV_DOCS_PUBLISH": "0"}):
            self.assertEqual(wasm.prepare(self.root)[0], directory)
        with patch.dict(os.environ, {"OPENTLV_DOCS_PUBLISH": "1"}), \
                self.assertRaisesRegex(PluginError, "signatures"):
            wasm.prepare(self.root)


class LegacySnapshotTests(unittest.TestCase):
    """Schema 1/2 snapshots built from selected sources stay verifiable on replay."""

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
        return wasm.verify_legacy(self.directory, self.source, "b" * 64)

    def test_four_module_files_are_verified(self):
        self.assertEqual(self.verify(), self.manifest)
        self.assertIn("query.mjs", self.manifest["files"])

    def test_standalone_artifacts_require_both_selected_sources(self):
        producer = dict(self.source, repository="https://github.com/OpenTLV/opentlv-js", commit="c" * 40)
        self.manifest.update(schema=2, js=wasm.producer_identity(producer, "d" * 64))
        self.save()
        self.assertEqual(wasm.verify_legacy(self.directory, self.source, "b" * 64, producer, "d" * 64),
                         self.manifest)
        for change in ({"commit": "e" * 40}, {"repository": "https://github.com/other/repo"},
                       {"local": True}, {"dirty": True}, {"source_sha256": "e" * 64}):
            with self.subTest(change=change):
                self.manifest["js"] = dict(wasm.producer_identity(producer, "d" * 64), **change)
                self.save()
                with self.assertRaises(PluginError):
                    wasm.verify_legacy(self.directory, self.source, "b" * 64, producer, "d" * 64)
        self.manifest.pop("js")
        self.manifest["schema"] = 1
        self.save()
        with self.assertRaises(PluginError):
            wasm.verify_legacy(self.directory, self.source, "b" * 64, producer, "d" * 64)

    def test_local_preview_keeps_dirty_producer_evidence_for_identical_bytes(self):
        producer = dict(self.source, repository="https://github.com/OpenTLV/opentlv-js", commit="c" * 40)
        self.manifest.update(schema=2, js=dict(wasm.producer_identity(producer, "d" * 64), local=True, dirty=True))
        self.save()
        wasm.verify_legacy(self.directory, dict(self.source, local=True), "b" * 64, producer, "d" * 64)
        with self.assertRaisesRegex(PluginError, "cannot be published"):
            wasm.verify_legacy(self.directory, self.source, "b" * 64, producer, "d" * 64)

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

    def test_missing_query_modified_bytes_and_invalid_header_fail(self):
        path = self.directory / "query.mjs"
        path.write_text("modified", encoding="utf-8")
        with self.assertRaisesRegex(PluginError, "checksums"):
            self.verify()
        path.unlink()
        with self.assertRaisesRegex(PluginError, "module files"):
            self.verify()
        path.write_bytes(b"export {};")
        (self.directory / "opentlv-core.wasm").write_text("not wasm", encoding="utf-8")
        with self.assertRaisesRegex(PluginError, "header"):
            self.verify()


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


if __name__ == "__main__":
    unittest.main()
