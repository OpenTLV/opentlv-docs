# SPDX-License-Identifier: MIT
# Copyright (c) 2026 Marek Cingel

"""Build playground assets and verify their exact source provenance."""

import hashlib
import importlib.util
import json
import os
from pathlib import Path
import re
import shutil

from mkdocs.exceptions import PluginError

_spec = importlib.util.spec_from_file_location("opentlv_wasm_api", Path(__file__).with_name("api.py"))
api = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(api)

FILES = ("opentlv.mjs", "query.mjs", "opentlv-core.js", "opentlv-core.wasm")
MANIFEST = "wasm-source.json"
EMSCRIPTEN = "4.0.10"


def hashes(directory):
    result = {}
    for name in (*FILES, MANIFEST):
        path = directory / name
        if path.is_symlink() or not path.resolve().is_relative_to(directory.resolve()):
            raise PluginError("WebAssembly artifacts must be regular contained files.")
        if name == MANIFEST:
            continue
        if not path.is_file():
            raise PluginError(f"WebAssembly module files missing: {name}")
        result[name] = hashlib.sha256(path.read_bytes()).hexdigest()
    if (directory / "opentlv-core.wasm").read_bytes()[:8] != b"\0asm\x01\0\0\0":
        raise PluginError("Invalid WebAssembly module header.")
    return result


def verify(directory, source, source_hash):
    if (directory / MANIFEST).is_symlink():
        raise PluginError("WebAssembly provenance must be a regular file.")
    try:
        manifest = json.loads((directory / MANIFEST).read_text(encoding="utf-8"))
    except (OSError, ValueError) as error:
        raise PluginError("Missing or invalid WebAssembly provenance; run tools/docs/wasm.py.") from error
    if (not isinstance(manifest, dict) or type(manifest.get("schema")) is not int or manifest["schema"] != 1
            or manifest.get("repository") != source["repository"]
            or manifest.get("commit") != source["commit"]
            or not re.fullmatch(r"[0-9a-f]{40}", str(manifest.get("commit", "")))
            or not re.fullmatch(r"[0-9a-f]{64}", str(manifest.get("source_sha256", "")))
            or manifest.get("source_sha256") != source_hash
            or manifest.get("emscripten") != EMSCRIPTEN):
        raise PluginError("WebAssembly provenance does not match selected sources or toolchain.")
    if (manifest.get("local") is not False or manifest.get("dirty") is not False) and not source["local"]:
        raise PluginError("Local WebAssembly artifacts cannot be published.")
    if manifest.get("files") != hashes(directory):
        raise PluginError("WebAssembly artifact checksums do not match provenance.")
    return manifest


def generate(portal, core, source):
    before = api.fingerprint(core)
    # Resolve .bat entry points too when running from an activated Windows SDK.
    version = api.run([shutil.which("emcc") or "emcc", "--version"])
    if not version.splitlines() or f" {EMSCRIPTEN} " not in version.splitlines()[0] + " ":
        raise PluginError(f"Playground requires Emscripten {EMSCRIPTEN}.")
    build = portal / "build/wasm"
    if build.is_symlink() or build.resolve() != portal / "build/wasm":
        raise PluginError("WASM build directory must stay inside the portal.")
    if build.exists():
        shutil.rmtree(build)
    api.run([shutil.which("emcmake") or "emcmake", "cmake", "-S", core, "-B", build, "-G", "Ninja",
             "-DCMAKE_BUILD_TYPE=Release", "-DOPENTLV_BUILD_WASM=ON",
             "-DOPENTLV_BUILD_CXX=OFF", "-DOPENTLV_BUILD_CLI=OFF",
             "-DOPENTLV_BUILD_TESTS=OFF", "-DOPENTLV_BUILD_EXAMPLES=OFF",
             "-DOPENTLV_BUILD_WASM_TESTS=OFF", "-DOPENTLV_WARNINGS_AS_ERRORS=ON"])
    api.run(["cmake", "--build", build, "--target", "opentlv-wasm", "--parallel"])
    if api.fingerprint(core) != before:
        raise PluginError("Core changed during the WebAssembly build.")
    directory = build / "bindings/wasm/dist"
    manifest = {"schema": 1, "repository": source["repository"], "commit": source["commit"],
                "local": source["local"], "dirty": source["dirty"], "source_sha256": before,
                "emscripten": EMSCRIPTEN, "files": hashes(directory)}
    (directory / MANIFEST).write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
    return directory


def prepare(portal, core, source):
    override = os.environ.get("OPENTLV_WASM_DIR")
    directory = Path(override).resolve() if override else portal / "build/wasm/bindings/wasm/dist"
    required = os.environ.get("OPENTLV_DOCS_REQUIRE_WASM") == "1"
    if not override and not directory.exists() and not required:
        return None, None
    if not override and not directory.exists():
        raise PluginError("WebAssembly module files are required; run tools/docs/wasm.py first.")
    return directory, verify(directory, source, api.fingerprint(core))


if __name__ == "__main__":
    import assembly

    root = Path(__file__).resolve().parents[2]
    core, source = assembly.selected_source(root)
    print(generate(root, core, source))
