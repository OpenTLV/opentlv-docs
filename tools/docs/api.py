# SPDX-License-Identifier: MIT
# Copyright (c) 2026 Marek Cingel

"""Generate and verify Core-owned Doxygen artifacts; adapt only published copies."""

import hashlib
from functools import lru_cache
from html import escape, unescape
from html.parser import HTMLParser
import importlib.util
import json
import logging
import os
from pathlib import Path
import posixpath
import re
import shutil
import subprocess
from urllib.parse import quote, unquote, urlsplit, urlunsplit

from mkdocs.exceptions import PluginError

log = logging.getLogger("mkdocs.hooks.api")
TREES = ("c-api", "cxx-api")
MANIFEST = "api-source.json"
PREFIX = "reference/api"


def run(args):
    try:
        result = subprocess.run([str(arg) for arg in args], capture_output=True,
                                text=True, encoding="utf-8", errors="replace")
    except OSError as error:
        raise PluginError(f"Cannot run {args[0]}: {error}") from error
    if result.returncode:
        raise PluginError(f"API command failed: {' '.join(map(str, args))}\n{result.stdout}\n{result.stderr}")
    return result.stdout.strip()


def fingerprint(core):
    """Hash actual tracked/non-ignored source bytes, including local changes."""
    names = run(["git", "-C", core, "ls-files", "-z", "--cached", "--others", "--exclude-standard"])
    digest = hashlib.sha256()
    # Core's generated version header also depends on branch, tags and history.
    for args in (("rev-parse", "HEAD"), ("rev-parse", "--abbrev-ref", "HEAD"),
                 ("describe", "--always", "--tags", "--abbrev=0", "--match", "[0-9]*", "HEAD"),
                 ("rev-list", "--count", "HEAD"),
                 ("for-each-ref", "--format=%(refname) %(objectname)", "refs/tags")):
        digest.update(run(["git", "-C", core, *args]).encode("utf-8") + b"\0")
    for name in sorted(set(filter(None, names.split("\0")))):
        path = core / name
        if path.is_symlink() or not path.resolve().is_relative_to(core):
            raise PluginError(f"API source must stay inside Core: {name}")
        digest.update(name.encode("utf-8") + b"\0")
        digest.update(hashlib.sha256(path.read_bytes()).digest() if path.is_file() else b"deleted")
    return digest.hexdigest()


def hashes(directory):
    result = {}
    for tree in TREES:
        if not (directory / tree / "html/index.html").is_file():
            raise PluginError(f"generated API reference not found in '{directory / tree / 'html'}'")
        for path in sorted((directory / tree).rglob("*")):
            if path.is_symlink() or not path.resolve().is_relative_to(directory.resolve()):
                raise PluginError(f"API artifact must not redirect outside its directory: {path}")
            if path.is_file():
                result[path.relative_to(directory).as_posix()] = hashlib.sha256(path.read_bytes()).hexdigest()
    return result


def verify(directory, source, source_hash):
    try:
        manifest = json.loads((directory / MANIFEST).read_text(encoding="utf-8"))
    except (OSError, ValueError) as error:
        raise PluginError(f"Missing or invalid API provenance in {directory / MANIFEST}. Regenerate with tools/docs/api.py.") from error
    if not isinstance(manifest, dict) or manifest.get("schema") != 1:
        raise PluginError("Unsupported API provenance schema; regenerate the references.")
    if (manifest.get("repository") != source["repository"]
            or manifest.get("commit") != source["commit"]
            or manifest.get("source_sha256") != source_hash):
        raise PluginError("API provenance does not match the selected Core sources; regenerate the references.")
    if (manifest.get("local") is not False or manifest.get("dirty") is not False) and not source["local"]:
        raise PluginError("Local API artifacts cannot be used for publication or normal builds.")
    if not isinstance(manifest.get("guide_base"), str) or not manifest["guide_base"].startswith(("https://", "http://")):
        raise PluginError("Invalid API guide URL in provenance.")
    if manifest.get("files") != hashes(directory):
        raise PluginError("API artifact checksums do not match provenance; regenerate the references.")
    return manifest


def generate(portal, core, source):
    """A fresh CMake directory prevents cache/configuration and stale HTML leakage."""
    before = fingerprint(core)
    build = portal / "build/api"
    if build.is_symlink() or build.resolve() != portal / "build/api":
        raise PluginError("The API build directory must not redirect outside the portal.")
    if build.exists():
        shutil.rmtree(build)
    flags = ["-DOPENTLV_BUILD_DOCS=ON"]
    flags += [f"-DOPENTLV_BUILD_{name}=OFF" for name in
              ("CXX", "CLI", "TESTS", "EXAMPLES", "WASM", "PYTHON", "BENCHMARKS", "FUZZING")]
    log.info("Generating C and C++ API references from Core %s", source["commit"])
    run(["cmake", "-S", core, "-B", build, *flags])
    common = (build / "Doxyfile.common").read_text(encoding="utf-8")
    if not re.search(r"^WARN_AS_ERROR\s*=\s*YES\s*$", common, re.MULTILINE):
        raise PluginError("Core Doxygen configuration must keep WARN_AS_ERROR = YES.")
    # Read the expanded Core alias, rather than duplicating its configuration.
    match = re.search(r'href=\\"(https?://[^"\\]+)\\1', common)
    if not match:
        raise PluginError("Cannot identify the Core @docs guide URL in Doxyfile.common.")
    cache = (build / "CMakeCache.txt").read_text(encoding="utf-8")
    executable = re.search(r"^DOXYGEN_EXECUTABLE:FILEPATH=(.+)$", cache, re.MULTILINE)
    if not executable:
        raise PluginError("CMake did not record the Doxygen executable.")
    version = run([executable[1].strip(), "--version"])
    run(["cmake", "--build", build, "--target", "cxx-api-docs"])
    if run(["git", "-C", core, "rev-parse", "HEAD"]) != source["commit"] or fingerprint(core) != before:
        raise PluginError("Core sources changed during API generation; retry the build.")
    directory = build / "docs"
    manifest = {
        "schema": 1, "repository": source["repository"], "commit": source["commit"],
        "source_sha256": before, "local": source["local"], "dirty": source["dirty"],
        "doxygen_version": version, "guide_base": match[1], "files": hashes(directory),
    }
    (directory / MANIFEST).write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
    return directory, manifest


def prepare(portal, core, source, override=None):
    source_hash = fingerprint(core)
    if override is not None:
        directory = Path(override).resolve()
        return directory, verify(directory, source, source_hash)
    directory = portal / "build/api/docs"
    try:
        manifest = verify(directory, source, source_hash)
    except PluginError:
        return generate(portal, core, source)
    log.info("Reusing verified API references from Core %s", source["commit"])
    return directory, manifest


def adapt_html(text, uri, guide_base, files):
    """Rewrite Core's guide URLs using MkDocs' actual output paths."""
    def rewrite(match):
        url = unescape(match[2])
        if not url.startswith(guide_base):
            return match[0]
        parts = urlsplit(url[len(guide_base):])
        path = unquote(parts.path).rstrip("/")
        candidates = (f"{path}.md", f"{path}/index.md", f"{path}/README.md") if path else ("index.md",)
        target = next((files.get_file_from_path(name) for name in candidates
                       if files.get_file_from_path(name) is not None), None)
        if target is None:
            raise PluginError(f"API guide link has no assembled page: {url} in {uri}")
        relative = posixpath.relpath(target.dest_uri, posixpath.dirname(uri))
        return f'{match[1]}{escape(urlunsplit(("", "", quote(relative, safe="/"), parts.query, parts.fragment)), quote=True)}{match[3]}'
    return re.sub(r'(\bhref\s*=\s*[\"\x27])([^\"\x27]*)([\"\x27])', rewrite, text, flags=re.IGNORECASE)


class Links(HTMLParser):
    def __init__(self, text):
        super().__init__(convert_charrefs=True)
        self.ids = set()
        self.hrefs = []
        self.feed(text)

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        for key in ("id", "name" if tag == "a" else "id"):
            if attrs.get(key):
                self.ids.add(attrs[key])
        if tag in ("a", "area") and "href" in attrs:
            self.hrefs.append(attrs["href"])


def validate_links(site, all_links=False):
    """Validate links between C API, C++ API and guides, including IDs."""
    site = site.resolve()
    pages = {path.resolve(): Links(path.read_text(encoding="utf-8")) for path in site.rglob("*.html")}
    api_root = (site / PREFIX).resolve()

    @lru_cache(maxsize=None)
    def destination(path):
        target = path.resolve()
        if target.is_dir():
            target /= "index.html"
        return target, target.is_file()

    def tree(path):
        if path.is_relative_to(api_root):
            parts = path.relative_to(api_root).parts
            return parts[0] if parts else "api"
        return None

    for page, parsed in pages.items():
        for href in parsed.hrefs:
            parts = urlsplit(href)
            if parts.scheme or parts.netloc or parts.path.startswith("/"):
                continue
            target = Path(os.path.abspath(page.parent / unquote(parts.path))) if parts.path else page
            # Doxygen owns navigation within each reference (including its
            # version-specific self-fragments); this checks integration edges.
            if tree(page) == tree(target) and (tree(page) is not None or not all_links):
                continue
            target, exists = destination(target)
            if not target.is_relative_to(site):
                raise PluginError(f"API link escapes the site: {page.name}: {href}")
            if not exists:
                raise PluginError(f"Broken API link in {page.relative_to(site)}: {href}")
            if parts.fragment and target in pages and unquote(parts.fragment) not in pages[target].ids:
                raise PluginError(f"Missing API link anchor in {page.relative_to(site)}: {href}")


if __name__ == "__main__":
    portal = Path(__file__).resolve().parents[2]
    spec = importlib.util.spec_from_file_location("assembly", Path(__file__).with_name("assembly.py"))
    assembly = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(assembly)
    core, source = assembly.selected_source(portal)
    directory, _ = generate(portal, core, source)
    print(f"Verified API artifacts: {directory}")
