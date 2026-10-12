# SPDX-License-Identifier: MIT
# Copyright (c) 2026 Marek Cingel

"""MkDocs hooks: adapt relative links and publish the generated API references.

Links that leave docs/ point at the GitHub repository, and links to the GitHub
index docs/README.md point at the site landing page docs/index.md.

The Doxygen HTML for the C and C++ APIs is added to the site as static files
under reference/api/, so it is validated by the strict build like any page.
The WebAssembly module used by the playground is added under playground/wasm/.
"""

import logging
import html
import importlib.util
import json
import os
from pathlib import Path
import posixpath
import re
from urllib.parse import quote, unquote, urlsplit, urlunsplit

from mkdocs.exceptions import PluginError
from mkdocs.structure.files import File

log = logging.getLogger("mkdocs.hooks.opentlv")

_api_spec = importlib.util.spec_from_file_location("opentlv_docs_api", Path(__file__).with_name("api.py"))
api = importlib.util.module_from_spec(_api_spec)
_api_spec.loader.exec_module(api)

# Directory holding the c-api/html and cxx-api/html trees produced by the
# c-api-docs and cxx-api-docs CMake targets. The two trees stay siblings, as
# the C++ reference links to C declarations through a relative path.
API_DIR_ENV = "OPENTLV_API_DOCS_DIR"
API_TREES = ("c-api", "cxx-api")
API_SITE_PREFIX = "reference/api"

# Directory holding the opentlv-wasm artifacts (opentlv.mjs, opentlv-core.js,
# opentlv-core.wasm). They need an Emscripten build, so they are optional
# locally, where the playground then explains it is unavailable. Future
# publication can require them through OPENTLV_DOCS_REQUIRE_WASM=1.
WASM_DIR_ENV = "OPENTLV_WASM_DIR"
WASM_DIR_DEFAULT = os.path.join("build-wasm", "bindings", "wasm", "dist")
WASM_REQUIRE_ENV = "OPENTLV_DOCS_REQUIRE_WASM"
WASM_FILES = ("opentlv.mjs", "opentlv-core.js", "opentlv-core.wasm")
WASM_SITE_PREFIX = "playground/wasm"

# Inline Markdown links: [text](target). Image links are left alone.
LINK = re.compile(r"(?<!!)(\[[^\]]*\]\()([^)\s]+)(\))")


def on_config(config):
    config.extra["docs_channel"] = os.environ.get("OPENTLV_DOCS_CHANNEL", config.extra["docs_channel"])
    if config.extra["docs_channel"] not in ("development", "release"):
        raise PluginError("OPENTLV_DOCS_CHANNEL must be development or release.")
    return config


def on_files(files, config):
    portal = Path(config.config_file_path).resolve().parent
    api_dir, manifest = api.prepare(
        portal, Path(config.extra["core_checkout"]), config.extra["core_source"],
        os.environ.get(API_DIR_ENV),
    )
    for tree in API_TREES:
        html_dir = os.path.join(api_dir, tree, "html")
        for root, _dirs, names in os.walk(html_dir):
            for name in sorted(names):
                rel = os.path.relpath(os.path.join(root, name), html_dir).replace(os.sep, "/")
                uri = f"{API_SITE_PREFIX}/{tree}/html/{rel}"
                path = Path(root) / name
                if path.suffix == ".html":
                    content = api.adapt_html(path.read_text(encoding="utf-8"), uri, manifest["guide_base"], files)
                    files.append(File.generated(config, uri, content=content))
                else:
                    files.append(File.generated(config, uri, abs_src_path=str(path.resolve())))
    metadata = dict(config.extra["core_source"])
    metadata["api"] = {key: value for key, value in manifest.items() if key != "files"}
    metadata["api"]["manifest"] = f"{API_SITE_PREFIX}/{api.MANIFEST}"
    (portal / "build/assembled/source-revision.json").write_text(
        json.dumps(metadata, indent=2) + "\n", encoding="utf-8",
    )
    files.append(File.generated(config, f"{API_SITE_PREFIX}/{api.MANIFEST}",
                                abs_src_path=str(api_dir / api.MANIFEST)))
    add_wasm_files(files, config)
    files.append(File.generated(
        config, "source-revision.json",
        abs_src_path=str(portal / "build" / "assembled" / "source-revision.json"),
    ))
    return files


def on_post_build(config):
    api.validate_links(Path(config.site_dir).resolve(), all_links=True)


def add_wasm_files(files, config):
    wasm_dir = os.environ.get(WASM_DIR_ENV, WASM_DIR_DEFAULT)
    missing = [name for name in WASM_FILES if not os.path.isfile(os.path.join(wasm_dir, name))]
    if missing:
        message = (
            f"WebAssembly module files {', '.join(missing)} not found in '{wasm_dir}'; the playground "
            "will be unavailable. Build them as described in docs/development/webassembly.md "
            f"(or set {WASM_DIR_ENV})."
        )
        if os.environ.get(WASM_REQUIRE_ENV) == "1":
            raise PluginError(message)
        log.info(message)
        return
    for name in WASM_FILES:
        files.append(
            File.generated(
                config,
                f"{WASM_SITE_PREFIX}/{name}",
                abs_src_path=os.path.abspath(os.path.join(wasm_dir, name)),
            )
        )


def on_page_markdown(markdown, page, config, files):
    portal = Path(config.config_file_path).resolve().parent
    portal_owned = (portal / "docs" / page.file.src_uri).is_file()
    source = config.extra["core_source"]
    root = portal if portal_owned else Path(config.extra["core_checkout"])
    owner_path = portal / "build/assembled/owners.json"
    owner = json.loads(owner_path.read_text(encoding="utf-8")).get(page.file.src_uri) if owner_path.exists() else None
    repo_path = "docs/" + page.file.src_uri
    if isinstance(owner, dict):
        source = next(item for item in config.extra["core_source"]["sources"] if item["id"] == owner["id"])
        root, repo_path = Path(owner["root"]), owner["path"]
    docs_path = "docs" if portal_owned else source.get("docs_path", "docs")
    page_dir = posixpath.dirname(posixpath.relpath(repo_path, docs_path))
    repo_url = config.repo_url.rstrip("/") if portal_owned else source["repository"].rstrip("/")
    ref = "main" if portal_owned else source["commit"]
    page.edit_url = f"{repo_url}/edit/{ref}/{quote(repo_path, safe='/')}"

    def rewrite(match):
        prefix, target, suffix = match.groups()
        if re.match(r"^([a-z][a-z0-9+.-]*:|#|/)", target, re.IGNORECASE):
            return match.group(0)
        parts = urlsplit(target)
        path = unquote(parts.path)
        resolved = posixpath.normpath(posixpath.join(page_dir, path))
        if resolved == "README.md" and source.get("id", "core") == "core":
            target = urlunsplit(("", "", posixpath.relpath('index.md', page_dir or '.'), parts.query, parts.fragment))
            return f"{prefix}{target}{suffix}"
        if resolved != ".." and not resolved.startswith("../"):
            return match.group(0)
        repo_path = posixpath.normpath(posixpath.join(docs_path, resolved))
        local_path = root / repo_path
        if not local_path.resolve().is_relative_to(root) or not local_path.exists():
            # A warning fails the strict build, like a broken link inside docs/.
            log.warning("%s: link to '%s' does not exist in the repository", page.file.src_uri, target)
        kind = "tree" if local_path.is_dir() else "blob"
        target = urlunsplit(("", "", f"{repo_url}/{kind}/{ref}/{quote(repo_path, safe='/')}", parts.query, parts.fragment))
        return f"{prefix}{target}{suffix}"

    # Imported example sources can themselves contain Markdown-looking text.
    # Never adapt links inside fenced source code.
    output, fence = [], None
    for line in markdown.splitlines(keepends=True):
        match = re.match(r"^ {0,3}(`{3,}|~{3,})(.*)$", line.rstrip("\r\n"))
        if fence:
            if match and match[1][0] == fence[0] and len(match[1]) >= len(fence) and not match[2].strip():
                fence = None
            output.append(line)
        elif match:
            fence = match[1]
            output.append(line)
        else:
            output.append(LINK.sub(rewrite, line))
    return "".join(output)


def on_page_content(content, page, config, files):
    """Map revision-qualified repository documentation links after Markdown parsing.

    This covers inline/reference links and HTML links without rewriting examples
    inside code blocks. Unrelated external links keep their original targets.
    """
    def rewrite(match):
        prefix, encoded, suffix = match.groups()
        target = html.unescape(encoded)
        parts = urlsplit(target)
        path = unquote(urlunsplit((parts.scheme, parts.netloc, parts.path, "", "")))
        for source in config.extra["core_source"]["sources"]:
            repository = source["repository"].removesuffix(".git").rstrip("/")
            for revision in {source["revision"], source.get("commit", source["revision"])}:
                base = f"{repository}/blob/{revision}/{source['docs_path']}/"
                if not path.startswith(base):
                    continue
                if not source["included"]:
                    # Missing optional components remain usable external links.
                    return match.group(0)
                relative = path[len(base):]
                if source["id"] == "core" and relative == "README.md":
                    relative = "index.md"
                uri = posixpath.normpath(posixpath.join(source["mount"], relative))
                destination = files.get_file_from_path(uri)
                if destination is None:
                    raise PluginError(f"Cross-repository link has no assembled target: {target}")
                from mkdocs.utils import get_relative_url
                url = get_relative_url(destination.url, page.file.url)
                url = urlunsplit(("", "", url, parts.query, parts.fragment))
                return prefix + html.escape(url, quote=True) + suffix
        return match.group(0)

    parts = re.split(r'(<pre\b[^>]*>.*?</pre>|<code\b[^>]*>.*?</code>)', content,
                     flags=re.IGNORECASE | re.DOTALL)
    return "".join(part if index % 2 else re.sub(
        r'(\b(?:href|src)\s*=\s*["\x27])([^"\x27]*)(["\x27])', rewrite, part,
        flags=re.IGNORECASE) for index, part in enumerate(parts))
