# SPDX-License-Identifier: MIT
# Copyright (c) 2026 Marek Cingel

"""Stage playground assets from the exact pinned npm package and verify their provenance.

The playground serves the published ``@opentlv/opentlv`` package as delivered to
users. Docs never compiles JS or Core for it. ``tools/playground/package-lock.json``
pins the exact version, registry tarball and SHA-512 integrity. Older snapshots
built from selected JS/Core sources keep their schema 1/2 manifests and are only
verified on immutable replay (``verify_legacy``).
"""

import argparse
import base64
import binascii
import hashlib
import importlib.util
import io
import json
import os
from pathlib import Path, PurePosixPath
import re
import shutil
import tarfile
from urllib.parse import quote
from urllib.request import Request, urlopen

from mkdocs.exceptions import PluginError

_spec = importlib.util.spec_from_file_location("opentlv_wasm_api", Path(__file__).with_name("api.py"))
api = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(api)

_spec = importlib.util.spec_from_file_location("opentlv_wasm_js", Path(__file__).with_name("js.py"))
js = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(js)

ROOT = Path(__file__).resolve().parents[2]
PIN = Path("tools/playground")
FILES = ("opentlv.mjs", "query.mjs", "opentlv-core.js", "opentlv-core.wasm")
MANIFEST = "wasm-source.json"
SCHEMA = 3
OUTPUT = Path("build/playground/dist")

PACKAGE = "@opentlv/opentlv"
REGISTRY = "https://registry.npmjs.org/"
# The playground imports these package subpaths; a changed export map is an
# API change that needs review rather than a silently different loader.
EXPORTS = {
    "./opentlv.mjs": {"types": "./dist/opentlv.d.mts", "import": "./dist/opentlv.mjs"},
    "./query.mjs": {"types": "./dist/query.d.mts", "import": "./dist/query.mjs"},
    "./opentlv-core.js": {"types": "./opentlv-core.d.mts", "import": "./dist/opentlv-core.js"},
    "./opentlv-core.wasm": "./dist/opentlv-core.wasm",
}
# Package notices, distributed under licenses/ by the license hook. The package
# declares that these must accompany redistributed JS/WASM assets.
NOTICES = {
    "LICENSE": "npm-opentlv-LICENSE.txt",
    "LICENSES/MIT.txt": "npm-opentlv-MIT.txt",
    "THIRD_PARTY.md": "npm-opentlv-THIRD_PARTY.txt",
    "notices/core-LICENSE.txt": "npm-opentlv-core-LICENSE.txt",
    "notices/emscripten-LICENSE.txt": "emscripten-LICENSE.txt",
    "notices/musl-COPYRIGHT.txt": "musl-COPYRIGHT.txt",
    "notices/compiler-rt-LICENSE.txt": "compiler-rt-LICENSE.txt",
}
# Reviewed publisher identity from the package's SLSA provenance statement.
PUBLISHER = {"repository": "https://github.com/OpenTLV/opentlv-js",
             "workflow": ".github/workflows/js-release.yml"}
SLSA = "https://slsa.dev/provenance/v1"
SHA = re.compile(r"[0-9a-f]{40}")
SHA256 = re.compile(r"[0-9a-f]{64}")
VERSION = re.compile(r"(0|[1-9][0-9]*)\.(0|[1-9][0-9]*)\.(0|[1-9][0-9]*)")

# Historical producers: schema 1 (Core in-tree) and 2 (standalone JS + Core).
EMSCRIPTEN = "4.0.10"


def load_pin(root=None):
    """Return the exact reviewed package pin; floating or partial pins fail."""
    root = root or ROOT
    try:
        package = json.loads((root / PIN / "package.json").read_text(encoding="utf-8"))
        lock_bytes = (root / PIN / "package-lock.json").read_bytes()
        lock = json.loads(lock_bytes)
        version = package["dependencies"][PACKAGE]
        entry = lock["packages"][f"node_modules/{PACKAGE}"]
        integrity = entry["integrity"]
    except (OSError, ValueError, KeyError, TypeError) as error:
        raise PluginError(f"Missing or invalid playground package pin in {PIN}.") from error
    resolved = f"{REGISTRY}{PACKAGE}/-/{PACKAGE.split('/')[1]}-{version}.tgz"
    if (not isinstance(version, str) or not VERSION.fullmatch(version)
            or package.get("private") is not True
            or set(package["dependencies"]) != {PACKAGE} or set(package) & {"devDependencies", "scripts"}
            or lock.get("lockfileVersion") != 3
            or set(lock["packages"]) != {"", f"node_modules/{PACKAGE}"}
            or lock["packages"][""].get("dependencies") != {PACKAGE: version}
            or entry.get("version") != version or entry.get("resolved") != resolved
            or not isinstance(integrity, str) or not integrity.startswith("sha512-")):
        raise PluginError("The playground requires one exact published package version with locked integrity.")
    try:
        sha512 = base64.b64decode(integrity[7:], validate=True).hex()
    except (ValueError, binascii.Error) as error:
        raise PluginError("Invalid playground package integrity.") from error
    if len(sha512) != 128:
        raise PluginError("Invalid playground package integrity.")
    return {"name": PACKAGE, "version": version, "resolved": resolved, "integrity": integrity,
            "sha512": sha512, "lock_sha256": hashlib.sha256(lock_bytes).hexdigest()}


def fetch(url):
    request = Request(url, headers={"User-Agent": "opentlv-docs-playground"})
    try:
        with urlopen(request, timeout=60) as response:
            return response.read()
    except OSError as error:
        raise PluginError(f"Cannot download {url}: {error}") from error


def acquire(pin):
    data = fetch(pin["resolved"])
    if hashlib.sha512(data).hexdigest() != pin["sha512"]:
        raise PluginError("Playground package bytes do not match the locked integrity.")
    return data


def extract(data):
    """Read the npm tarball without extracting arbitrary paths to disk."""
    members = {}
    try:
        with tarfile.open(fileobj=io.BytesIO(data), mode="r:gz") as archive:
            for entry in archive.getmembers():
                path = PurePosixPath(entry.name)
                if entry.isdir():
                    continue
                if (not entry.isfile() or path.is_absolute() or ".." in path.parts or "\\" in entry.name
                        or path.parts[0] != "package" or len(path.parts) < 2):
                    raise PluginError(f"Unsafe playground package entry: {entry.name}")
                name = PurePosixPath(*path.parts[1:]).as_posix()
                if name in members:
                    raise PluginError(f"Duplicate playground package entry: {entry.name}")
                members[name] = archive.extractfile(entry).read()
    except (tarfile.TarError, OSError, EOFError) as error:
        raise PluginError("Invalid playground package archive.") from error
    return members


def inspect(members, pin):
    """Check the supported package API, assets and declared outputs."""
    try:
        package = json.loads(members["package.json"])
        info = json.loads(members["package-info.json"])
    except (KeyError, ValueError) as error:
        raise PluginError("Playground package metadata missing.") from error
    if package.get("name") != pin["name"] or package.get("version") != pin["version"]:
        raise PluginError("Playground package identity differs from the pin.")
    exports = package.get("exports")
    if (package.get("type") != "module" or not isinstance(exports, dict)
            or any(exports.get(key) != value for key, value in EXPORTS.items())):
        raise PluginError("Playground package API differs from the supported export map.")
    missing = [name for name in FILES if f"dist/{name}" not in members]
    if missing:
        raise PluginError(f"Playground package assets missing: {', '.join(missing)}")
    if members["dist/opentlv-core.wasm"][:8] != b"\0asm\x01\0\0\0":
        raise PluginError("Invalid WebAssembly module header.")
    if (info.get("name") != pin["name"] or info.get("version") != pin["version"]
            or info.get("outputs") != {name: hashlib.sha256(members[f"dist/{name}"]).hexdigest()
                                       for name in FILES}):
        raise PluginError("Playground package outputs differ from its declared package-info.json.")
    licenses = {name for name in members if name.startswith(("notices/", "LICENSES/"))}
    licenses.update(name for name in ("LICENSE", "THIRD_PARTY.md") if name in members)
    if licenses != set(NOTICES):
        raise PluginError("Playground package notices changed; review its distribution notices first.")
    core = info.get("core", {})
    reported = {key: core.get(key) for key in ("repository", "commit", "tree")}
    reported["tag"] = core.get("version_inputs", {}).get("tag")
    if not SHA.fullmatch(str(reported["commit"])):
        raise PluginError("Playground package does not report its Core revision.")
    return reported


def provenance(pin):
    """Match the registry's SLSA statement to the exact tarball and reviewed publisher.

    This is a content check of the statement; ``npm audit signatures`` verifies
    the registry signatures and Sigstore attestation bundles cryptographically.
    """
    url = f"{REGISTRY}-/npm/v1/attestations/{quote(pin['name'], safe='')}@{pin['version']}"
    try:
        attestations = json.loads(fetch(url))["attestations"]
        bundle = next(item["bundle"] for item in attestations if item["predicateType"] == SLSA)
        statement = json.loads(base64.b64decode(bundle["dsseEnvelope"]["payload"]))
        build = statement["predicate"]["buildDefinition"]
        workflow = build["externalParameters"]["workflow"]
        dependency = build["resolvedDependencies"][0]
        subject = statement["subject"]
        identity = {"repository": workflow["repository"], "workflow": workflow["path"],
                    "ref": workflow["ref"], "commit": dependency["digest"]["gitCommit"],
                    "invocation": statement["predicate"]["runDetails"]["metadata"]["invocationId"]}
    except (KeyError, IndexError, TypeError, ValueError, StopIteration) as error:
        raise PluginError("Playground package has no valid SLSA provenance statement.") from error
    if (subject != [{"name": f"pkg:npm/{quote(pin['name'], safe='/')}@{pin['version']}",
                     "digest": {"sha512": pin["sha512"]}}]
            or {key: identity[key] for key in PUBLISHER} != PUBLISHER
            or not SHA.fullmatch(str(identity["commit"]))
            or not str(dependency.get("uri", "")).startswith(f"git+{PUBLISHER['repository']}@")
            or not str(identity["invocation"]).startswith(PUBLISHER["repository"] + "/actions/runs/")):
        raise PluginError("Playground package provenance differs from the tarball or reviewed publisher.")
    return identity


def verify_signatures(portal, members):
    """Install from the lockfile, audit signatures and compare the installed bytes."""
    npm = shutil.which("npm") or "npm"
    staging = portal / "build/playground/npm"
    if staging.exists():
        shutil.rmtree(staging)
    staging.mkdir(parents=True)
    for name in ("package.json", "package-lock.json"):
        shutil.copyfile(ROOT / PIN / name, staging / name)
    api.run([npm, "ci", "--prefix", staging, "--ignore-scripts", "--no-audit", "--no-fund"])
    api.run([npm, "audit", "signatures", "--prefix", staging])
    installed = staging / "node_modules" / PACKAGE
    for name in (*(f"dist/{item}" for item in FILES), *NOTICES, "package-info.json"):
        path = installed / name
        if path.is_symlink() or not path.is_file() or path.read_bytes() != members[name]:
            raise PluginError(f"Installed playground package differs from the verified tarball: {name}")
    return {"tool": "npm audit signatures", "npm": api.run([npm, "--version"])}


def hashes(directory, names=FILES):
    result = {}
    for name in (*names, MANIFEST):
        path = directory / name
        if path.is_symlink() or not path.resolve().is_relative_to(directory.resolve()):
            raise PluginError("WebAssembly artifacts must be regular contained files.")
        if name == MANIFEST:
            continue
        if not path.is_file():
            raise PluginError(f"WebAssembly module files missing: {name}")
        result[name] = hashlib.sha256(path.read_bytes()).hexdigest()
    if "opentlv-core.wasm" in names and (directory / "opentlv-core.wasm").read_bytes()[:8] != b"\0asm\x01\0\0\0":
        raise PluginError("Invalid WebAssembly module header.")
    return result


def identity(pin):
    """Package fields recorded in the manifest and compared on every replay."""
    return {key: pin[key] for key in ("name", "version", "resolved", "integrity", "lock_sha256")}


def generate(portal, signatures=False):
    pin = load_pin()
    data = acquire(pin)
    members = extract(data)
    core = inspect(members, pin)
    source = provenance(pin)
    audited = verify_signatures(portal, members) if signatures else None
    directory = portal / OUTPUT
    if directory.is_symlink() or not directory.resolve().is_relative_to(portal.resolve()):
        raise PluginError("Playground build directory must stay inside the portal.")
    if directory.exists():
        shutil.rmtree(directory)
    directory.mkdir(parents=True)
    for name in FILES:
        (directory / name).write_bytes(members[f"dist/{name}"])
    for name, target in NOTICES.items():
        (directory / target).write_bytes(members[name])
    manifest = {"schema": SCHEMA, "package": dict(identity(pin), sha256=hashlib.sha256(data).hexdigest()),
                "provenance": source, "signatures": audited, "core": core,
                "files": hashes(directory), "notices": hashes(directory, tuple(NOTICES.values()))}
    (directory / MANIFEST).write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
    return directory


def verify(directory, pin, publish=False, notices=True):
    """Verify staged or published assets against the reviewed pin; fail closed."""
    if (directory / MANIFEST).is_symlink():
        raise PluginError("WebAssembly provenance must be a regular file.")
    try:
        manifest = json.loads((directory / MANIFEST).read_text(encoding="utf-8"))
    except (OSError, ValueError) as error:
        raise PluginError("Missing or invalid WebAssembly provenance; run tools/docs/wasm.py.") from error
    package = manifest.get("package") if isinstance(manifest, dict) else None
    source = manifest.get("provenance") if isinstance(manifest, dict) else None
    if (not isinstance(package, dict) or type(manifest.get("schema")) is not int
            or manifest["schema"] != SCHEMA
            or {key: package.get(key) for key in identity(pin)} != identity(pin)
            or set(package) != {*identity(pin), "sha256"}
            or not SHA256.fullmatch(str(package.get("sha256", "")))
            or not isinstance(source, dict)
            or {key: source.get(key) for key in PUBLISHER} != PUBLISHER
            or not SHA.fullmatch(str(source.get("commit", "")))
            or not SHA.fullmatch(str(manifest.get("core", {}).get("commit", "")))):
        raise PluginError("Playground package provenance does not match the reviewed pin; run tools/docs/wasm.py.")
    signatures = manifest.get("signatures")
    if signatures is not None and (not isinstance(signatures, dict)
                                   or signatures.get("tool") != "npm audit signatures"):
        raise PluginError("Invalid playground package signature evidence.")
    if publish and signatures is None:
        raise PluginError("Publication requires verified npm registry signatures; "
                          "run tools/docs/wasm.py --verify-signatures.")
    if manifest.get("files") != hashes(directory):
        raise PluginError("WebAssembly artifact checksums do not match provenance.")
    if (not isinstance(manifest.get("notices"), dict) or set(manifest["notices"]) != set(NOTICES.values())
            or not all(SHA256.fullmatch(str(value)) for value in manifest["notices"].values())):
        raise PluginError("Playground package notices are missing from provenance.")
    if notices and manifest["notices"] != hashes(directory, tuple(NOTICES.values())):
        raise PluginError("Playground package notice checksums do not match provenance.")
    return manifest


def prepare(portal):
    override = os.environ.get("OPENTLV_WASM_DIR")
    directory = Path(override).resolve() if override else portal / OUTPUT
    required = os.environ.get("OPENTLV_DOCS_REQUIRE_WASM") == "1"
    if not override and not directory.exists() and not required:
        return None, None
    if not override and not directory.exists():
        raise PluginError("WebAssembly module files are required; run tools/docs/wasm.py first.")
    return directory, verify(directory, load_pin(), os.environ.get("OPENTLV_DOCS_PUBLISH") == "1")


def js_selection(selected):
    """Historical schema 2 snapshots name the selected standalone JS producer."""
    if js.ready([item for _root, item in selected]):
        return next((root, item) for root, item in selected if item["id"] == "js")
    return None, None


def producer_identity(source, fingerprint):
    return {key: source[key] for key in ("repository", "commit", "local", "dirty")} | {
        "source_sha256": fingerprint}


def verify_legacy(directory, source, source_hash, js_source=None, js_hash=None):
    """Verify an immutable schema 1/2 snapshot built from selected sources."""
    if (directory / MANIFEST).is_symlink():
        raise PluginError("WebAssembly provenance must be a regular file.")
    try:
        manifest = json.loads((directory / MANIFEST).read_text(encoding="utf-8"))
    except (OSError, ValueError) as error:
        raise PluginError("Missing or invalid WebAssembly provenance; run tools/docs/wasm.py.") from error
    if (not isinstance(manifest, dict) or type(manifest.get("schema")) is not int
            or manifest["schema"] != (2 if js_source else 1)
            or manifest.get("repository") != source["repository"]
            or manifest.get("commit") != source["commit"]
            or not SHA.fullmatch(str(manifest.get("commit", "")))
            or not SHA256.fullmatch(str(manifest.get("source_sha256", "")))
            or manifest.get("source_sha256") != source_hash
            or manifest.get("emscripten") != EMSCRIPTEN):
        raise PluginError("WebAssembly provenance does not match selected sources or toolchain.")
    if (manifest.get("local") is not False or manifest.get("dirty") is not False) and not source["local"]:
        raise PluginError("Local WebAssembly artifacts cannot be published.")
    if js_source:
        producer = manifest.get("js", {})
        if (not isinstance(producer, dict)
                or not SHA.fullmatch(str(js_source.get("commit", "")))
                or not SHA256.fullmatch(str(js_hash or ""))
                or producer.get("repository") != js_source["repository"]
                or producer.get("commit") != js_source["commit"]
                or producer.get("source_sha256") != js_hash):
            raise PluginError("WebAssembly JS provenance does not match selected sources.")
        if (producer.get("local") is not False or producer.get("dirty") is not False) and not source["local"]:
            raise PluginError("Local WebAssembly JS artifacts cannot be published.")
    if manifest.get("files") != hashes(directory):
        raise PluginError("WebAssembly artifact checksums do not match provenance.")
    return manifest


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--verify-signatures", action="store_true",
                        help="install with npm ci and require npm audit signatures (Full CI)")
    args = parser.parse_args()
    print(generate(ROOT, args.verify_signatures))
