# SPDX-License-Identifier: MIT
# Copyright (c) 2026 Marek Cingel

"""Ship exact license bytes with each new portal or component snapshot."""

import hashlib
import html
from importlib.metadata import distribution
import importlib.util
import json
from pathlib import Path
import re

from mkdocs.exceptions import PluginError
from mkdocs.plugins import event_priority
from mkdocs.structure.files import File

_spec = importlib.util.spec_from_file_location("opentlv_licensing_wasm", Path(__file__).with_name("wasm.py"))
wasm = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(wasm)

ROOT = Path(__file__).resolve().parents[2]
PREFIX = "licenses"
MANIFEST = "licenses/manifest.json"
# Historical snapshots record the toolchain of their source-built playground.
TOOLCHAIN = "4.0.10"
TOOLCHAIN_COMMIT = "b7dc6e5747465580df5984e723b9d1f10d8e804b"
# Reviewed runtime notice bytes, kept in notices/. The pinned npm package must
# ship exactly these bytes; a change requires a new distribution review.
RUNTIME_NOTICES = {
    "emscripten-LICENSE.txt": "620a78084fc7ca97c0b5dea9abf891f3ffcadfdbf305276f099c9c4e12fc1d86",
    "musl-COPYRIGHT.txt": "f9bc4423732350eb0b3f7ed7e91d530298476f8fec0c6c427a1c04ade22655af",
    "compiler-rt-LICENSE.txt": "1a8f1058753f1ba890de984e48f0242a3a5c29a6a8f2ed9fd813f36985387e8d",
}


def read_notice(path):
    path = Path(path)
    if path.is_symlink() or not path.is_file() or not path.read_bytes().strip():
        raise PluginError(f"Missing, empty or symlinked license notice: {path}")
    return path.read_bytes()


def theme_notices():
    package = distribution("mkdocs-material")
    candidates = [path for path in package.files or []
                  if ".dist-info/" in str(path) and path.name == "LICENSE"]
    if len(candidates) != 1:
        raise PluginError("Cannot identify the installed Material for MkDocs license.")
    notices = {"material-LICENSE.txt": read_notice(package.locate_file(candidates[0]))}
    # Retain all icon-set notices shipped by the selected theme, including icons
    # chosen implicitly by its templates and Markdown extensions.
    for family, name in (("material", "LICENSE"), ("fontawesome", "LICENSE.txt"),
                         ("octicons", "LICENSE"), ("simple", "LICENSE.md")):
        notices[f"icons-{family}-LICENSE.txt"] = read_notice(
            package.locate_file(f"material/templates/.icons/{family}/{name}"))
    return notices, package.version


def playground_identity(manifest):
    package = manifest["package"]
    return {"package": package["name"], "version": package["version"], "integrity": package["integrity"]}


def playground_notices(root, manifest, directory):
    """Read the staged package notices and require the reviewed runtime bytes."""
    names = set(wasm.NOTICES.values())
    if (manifest.get("schema") != wasm.SCHEMA or not isinstance(manifest.get("notices"), dict)
            or set(manifest["notices"]) != names):
        raise PluginError("Playground runtime changed; review its distribution notices first.")
    notices = {}
    for name in sorted(names):
        notices[name] = read_notice(Path(directory) / name)
        if hashlib.sha256(notices[name]).hexdigest() != manifest["notices"][name]:
            raise PluginError(f"Playground package notice differs from its provenance: {name}")
    for name, digest in RUNTIME_NOTICES.items():
        reviewed = read_notice(root / "notices" / name)
        if hashlib.sha256(reviewed).hexdigest() != digest or notices[name] != reviewed:
            raise PluginError(f"Toolchain license differs from reviewed upstream bytes: {name}")
    return notices


def bundle(root, checkouts, sources, playground=None):
    notices, version = theme_notices()
    notices["portal-LICENSE.txt"] = read_notice(root / "LICENSE")
    notices["THIRD_PARTY.txt"] = read_notice(root / "THIRD_PARTY.md")
    notices["Apache-2.0.txt"] = read_notice(root / "LICENSES/Apache-2.0.txt")
    identities = []
    for source in sources:
        if not source.get("included"):
            continue
        key = source["id"]
        if not re.fullmatch(r"[a-z][a-z0-9_]*", key) or key not in checkouts:
            raise PluginError(f"Missing license source checkout: {key}")
        notices[f"{key}-LICENSE.txt"] = read_notice(Path(checkouts[key]) / "LICENSE")
        identities.append({name: source[name] for name in ("id", "repository", "commit")})
    metadata = {"schema": 1, "theme": {"name": "mkdocs-material", "version": version},
                "sources": identities}
    if playground is not None:
        manifest, directory = playground
        notices.update(playground_notices(root, manifest, directory))
        metadata["playground"] = playground_identity(manifest)
    # Static HTML keeps this page independent of the portal's Markdown routing
    # and makes every notice available in offline copies and versioned aliases.
    links = "\n".join(f'<li><a href="{html.escape(name)}">{html.escape(name)}</a></li>'
                      for name in sorted(notices))
    notices["index.html"] = ("<!doctype html><html lang=\"en\"><meta charset=\"utf-8\">"
                             "<title>Licenses and third-party notices</title>"
                             "<h1>Licenses and third-party notices</h1>"
                             "<p>These notices accompany this documentation snapshot. "
                             "Each component retains its own license and copyright.</p>"
                             f"<ul>{links}</ul><p><a href=\"manifest.json\">"
                             "Versions, source revisions and SHA-256 checksums</a></p></html>").encode()
    metadata["files"] = {name: hashlib.sha256(data).hexdigest() for name, data in notices.items()}
    return notices, metadata


def on_files(files, config):
    for file in files:
        destination = file.dest_uri.casefold()
        if destination == PREFIX or destination.startswith(PREFIX + "/"):
            raise PluginError(f"Documentation cannot replace license output: {file.src_uri}")
    sources = config.extra["sources"]
    checkouts = config.extra["license_checkouts"]
    playground = None
    if any(file.dest_uri == "playground/wasm/opentlv-core.wasm" for file in files):
        manifest = files.get_file_from_path("playground/wasm/wasm-source.json")
        data = json.loads(manifest.content_string) if manifest is not None else {}
        if data.get("schema") != wasm.SCHEMA or not manifest.abs_src_path:
            raise PluginError("Playground runtime changed; review its distribution notices first.")
        # The package notices are staged next to the manifest, not published there.
        playground = (data, Path(manifest.abs_src_path).parent)
    notices, metadata = bundle(ROOT, checkouts, sources, playground)
    for name, data in notices.items():
        files.append(File.generated(config, f"{PREFIX}/{name}", content=data))
    files.append(File.generated(config, MANIFEST, content=json.dumps(metadata, indent=2) + "\n"))
    config.extra["license_manifest"] = metadata
    return files


def verify_site(site, expected=None):
    site = Path(site)
    try:
        if (site / PREFIX).is_symlink() or not (site / PREFIX).resolve().is_relative_to(site.resolve()):
            raise ValueError("License directory escapes snapshot")
        metadata = json.loads(read_notice(site / MANIFEST))
        if metadata.get("schema") != 1 or not isinstance(metadata.get("files"), dict):
            raise ValueError("Invalid license manifest")
        if expected is not None and metadata != expected:
            raise ValueError("License manifest changed after assembly")
        required = {"index.html", "portal-LICENSE.txt", "THIRD_PARTY.txt", "Apache-2.0.txt",
                    "material-LICENSE.txt", "icons-material-LICENSE.txt", "icons-fontawesome-LICENSE.txt",
                    "icons-octicons-LICENSE.txt", "icons-simple-LICENSE.txt"}
        required.update(f"{item['id']}-LICENSE.txt" for item in metadata["sources"])
        if (site / "playground/wasm/opentlv-core.wasm").exists():
            required.update(RUNTIME_NOTICES)
            if "playground" in metadata:
                required.update(wasm.NOTICES.values())
                if any(metadata["files"].get(name) != digest for name, digest in RUNTIME_NOTICES.items()):
                    raise ValueError("Playground runtime notices differ from reviewed bytes")
            elif metadata.get("emscripten") != {"version": TOOLCHAIN, "commit": TOOLCHAIN_COMMIT}:
                raise ValueError("Missing playground toolchain notices")
        if not required.issubset(metadata["files"]):
            raise ValueError("Incomplete license manifest")
        for name, digest in metadata["files"].items():
            if not re.fullmatch(r"[a-zA-Z0-9_.-]+", name) or name in (".", ".."):
                raise ValueError("Unsafe license path")
            path = site / PREFIX / name
            if not path.resolve().is_relative_to(site.resolve()):
                raise ValueError("License path escapes snapshot")
            if hashlib.sha256(read_notice(path)).hexdigest() != digest:
                raise ValueError(f"License checksum mismatch: {name}")
    except (OSError, ValueError, KeyError, TypeError) as error:
        raise PluginError(f"Invalid distributed license notices: {error}") from error
    return metadata


def verify_record(site, source):
    """Verify new snapshot notices while preserving historical release replay."""
    if "licensing" not in source:
        return  # Published snapshots predating this contract stay immutable.
    record = source["licensing"]
    digest = hashlib.sha256(read_notice(Path(site) / MANIFEST)).hexdigest()
    if record != {"manifest": MANIFEST, "sha256": digest}:
        raise PluginError("Distributed license provenance differs from the snapshot.")
    verify_site(site)


@event_priority(-100)
def on_post_build(config):
    verify_site(config.site_dir, config.extra["license_manifest"])
    # Run after both the portal and component metadata writers. Component file
    # manifests exclude source-revision.json, so adding this record is safe.
    path = Path(config.site_dir) / "source-revision.json"
    if path.exists():
        source = json.loads(path.read_text(encoding="utf-8"))
        source["licensing"] = {"manifest": MANIFEST, "sha256": hashlib.sha256(
            read_notice(Path(config.site_dir) / MANIFEST)).hexdigest()}
        path.write_text(json.dumps(source, indent=2) + "\n", encoding="utf-8")
