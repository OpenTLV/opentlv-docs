# SPDX-License-Identifier: MIT
# Copyright (c) 2026 Marek Cingel

"""Source links for CLI-only snapshots; no Core API or WASM build hooks."""

from pathlib import Path
import hashlib
import json
import posixpath
import sys
from urllib.parse import quote

sys.path.insert(0, str(Path(__file__).resolve().parent))
import hooks


def on_page_markdown(markdown, page, config, files):
    source = config.extra["sources"][0]
    repo = source["repository"]
    path = source["docs_path"] + "/" + page.file.src_uri
    page.edit_url = f"{repo}/edit/{source['commit']}/{quote(path, safe='/')}"
    return hooks.rewrite_source_links(
        markdown, page, Path(config.extra["cli_checkout"]), source, repo,
        source["commit"], source["docs_path"], posixpath.dirname(page.file.src_uri))


def on_page_content(content, page, config, files):
    return hooks.on_page_content(content, page, config, files)


def on_post_build(config):
    site = Path(config.site_dir)
    metadata = dict(config.extra["release_identity"], files={
        path.relative_to(site).as_posix(): hashlib.sha256(path.read_bytes()).hexdigest()
        for path in site.rglob("*") if path.is_file() and path != site / "source-revision.json"})
    (site / "source-revision.json").write_text(json.dumps(metadata, indent=2) + "\n", encoding="utf-8")
