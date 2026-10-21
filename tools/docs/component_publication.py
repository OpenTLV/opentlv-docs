# SPDX-License-Identifier: MIT
# Copyright (c) 2026 Marek Cingel

"""Build immutable component snapshots with the portal's trusted renderer."""

import hashlib
import json
import os
from pathlib import Path
import re
import shutil
import sys

import yaml

import ci
import events
import publication
import sources

TAG = re.compile(r"v((?:0|[1-9][0-9]*)\.(?:0|[1-9][0-9]*)\.(?:0|[1-9][0-9]*)(?:-[0-9A-Za-z-]+(?:\.[0-9A-Za-z-]+)*)?)\Z")


def version(tag):
    match = TAG.fullmatch(tag) if isinstance(tag, str) else None
    if not match or ("-" in tag and any(
            part.isdigit() and len(part) > 1 and part.startswith("0")
            for part in tag.split("-", 1)[1].split("."))):
        raise ValueError("Component release requires vMAJOR.MINOR.PATCH with an optional SemVer prerelease.")
    return match[1]


def verify_site(site, selection):
    metadata = json.loads((site / "source-revision.json").read_text(encoding="utf-8"))
    for key in ("source", "repository", "commit", "tag", "version", "local", "dirty"):
        if metadata.get(key) != selection[key]:
            raise ValueError("Component snapshot identity differs from the validated release.")
    files = metadata.get("files")
    if not isinstance(files, dict) or not files or "index.html" not in files:
        raise ValueError("Component snapshot requires a complete file digest manifest.")
    actual = {path.relative_to(site).as_posix(): hashlib.sha256(path.read_bytes()).hexdigest()
              for path in site.rglob("*") if path.is_file() and path != site / "source-revision.json"}
    if actual != files:
        raise ValueError("Component snapshot file checksums differ from its immutable manifest.")


def assemble(portal, checkout, item, selection):
    """Copy only tracked docs; use portal configuration and trusted hooks."""
    if (sources.git(checkout, "rev-parse", "HEAD") != selection["commit"]
            or sources.git(checkout, "status", "--porcelain", "--untracked-files=all")):
        raise ValueError("Component documentation requires the exact clean release checkout.")
    output = portal / "build" / item["id"]
    docs = output / "docs"
    docs.mkdir(parents=True, exist_ok=False)
    paths = sources.git(checkout, "ls-files", "-z", "--", ":(literal)" + item["docs_path"] + "/")
    for name in filter(None, paths.split("\0")):
        path = checkout / name
        if path.is_symlink() or not path.is_file() or not path.resolve().is_relative_to(checkout):
            raise ValueError("Component documentation sources must be contained regular files.")
        relative = path.relative_to(checkout / item["docs_path"])
        if relative.as_posix().casefold() == "source-revision.json":
            raise ValueError("Component source cannot replace publication provenance.")
        target = docs / relative
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(path, target)
    generated_index = not any((docs / name).exists() for name in ("index.md", "README.md"))
    navigation = item["navigation"]["items"]
    if generated_index:
        def links(items):
            for entry in items:
                for title, target in entry.items():
                    if isinstance(target, list):
                        yield from links(target)
                    else:
                        yield f"- [{title}]({target})"
        (docs / "index.md").write_text("# OpenTLV " + item["navigation"]["title"] + " " +
                                      selection["version"] + "\n\n" + "\n".join(links(navigation)) + "\n",
                                      encoding="utf-8")
        navigation = [{"Overview": "index.md"}, *navigation]
    config = yaml.safe_load((portal / "mkdocs.yml").read_text(encoding="utf-8"))
    # Retain the portal's presentation, without executing Core assembly/build hooks.
    config.update(site_name="OpenTLV " + item["navigation"]["title"] + " " + selection["version"],
                  site_description="OpenTLV " + item["navigation"]["title"] + " documentation",
                  site_url=config["site_url"].rstrip("/") + "/" + item["id"] + "/",
                  repo_url=item["repository"], repo_name=events.repository(item),
                  docs_dir=str(docs), site_dir=str(output / "site"),
                  hooks=[str(portal / "tools/docs/component_hooks.py")],
                  nav=navigation + [{"OpenTLV portal": config["site_url"]}],
                  exclude_docs="", extra_css=[], extra_javascript=[], plugins=["search"])
    config["theme"] = dict(config["theme"], custom_dir=str(portal / "tools/docs/overrides"))
    for key in ("logo", "favicon"):
        config["theme"].pop(key, None)
    source = dict(item, commit=selection["commit"], revision=selection["tag"], mount="",
                  included=True, local=False, dirty=False)
    config["extra"] = {"docs_channel": "release", "sources": [source],
                       "component_generated_index": generated_index,
                       "component_checkout": str(checkout), "version": {"provider": "mike", "alias": True},
                       "release_identity": dict(selection, infrastructure_commit=sources.git(portal, "rev-parse", "HEAD"))}
    ci.check_navigation(docs, yaml.safe_dump(config))
    path = output / "mkdocs.yml"
    path.write_text(yaml.safe_dump(config, sort_keys=False), encoding="utf-8")
    return path


def prepare(portal, selection, checkout=None):
    if (not isinstance(selection.get("source"), str)
            or not re.fullmatch(r"[a-z][a-z0-9_]*", selection["source"]) or selection["source"] == "core"
            or version(selection.get("tag")) != selection.get("version")
            or not events.SHA.fullmatch(selection.get("commit", ""))
            or selection.get("local") is not False or selection.get("dirty") is not False
            or os.environ.get("OPENTLV_DOCS_LOCAL") == "1"):
        raise ValueError("Component publication requires a clean validated release identity.")
    item = next((item for item in sources.manifest(portal) if item["id"] == selection["source"]), None)
    if item is None or selection["repository"] != item["repository"]:
        raise ValueError("Component publication repository differs from configuration.")
    if item["id"] != "cli":
        sources.publication_settings(item)
    run = publication.run
    remote = run(portal, "git", "ls-remote", "--heads", "origin", "refs/heads/gh-pages")
    versions = []
    if remote:
        run(portal, "git", "fetch", "origin", "refs/heads/gh-pages:refs/heads/gh-pages")
        if run(portal, "git", "ls-tree", "--name-only", "gh-pages", item["id"] + "/versions.json"):
            versions = json.loads(run(portal, "git", "show", "gh-pages:" + item["id"] + "/versions.json"))
    elif run(portal, "git", "branch", "--list", "gh-pages"):
        raise ValueError("Use a fresh checkout; local-only gh-pages cannot authorize publication.")
    prefix = item["id"] + "/" + selection["version"]
    if any(item["version"] == selection["version"] for item in versions):
        return publication.export_history(portal, prefix, selection, verify_site)
    if remote and run(portal, "git", "ls-tree", "--name-only", "gh-pages", prefix):
        raise ValueError("Component snapshot path exists without a registered version.")
    if checkout is None:
        checkout = portal / "build" / (item["id"] + "-source")
        if checkout.exists():
            raise ValueError("Component managed checkout already exists; use a fresh build directory.")
        checkout.parent.mkdir(parents=True, exist_ok=True)
        run(portal, "git", "clone", "--no-checkout", "--", item["repository"], str(checkout))
        commit = run(checkout, "git", "rev-parse", "--verify", "--end-of-options", f"refs/tags/{selection['tag']}^{{commit}}")
        if commit != selection["commit"]:
            raise ValueError("Fetched Component tag differs from the authenticated release.")
        run(checkout, "git", "checkout", "--detach", commit)
    config = assemble(portal, checkout, item, selection)
    aliases = publication.release_aliases(selection["version"], versions) if "-" not in selection["version"] else []
    mike = [sys.executable, "-B", "-c", "from mike.driver import main; raise SystemExit(main())"]
    run(portal, *mike, "deploy", "--config-file", str(config), "--deploy-prefix", item["id"],
        "--alias-type=copy", "--update-aliases", "--title", item["navigation"]["title"] + " " + selection["version"],
        selection["version"], *aliases)
    verify_site(portal / "build" / item["id"] / "site", selection)
    has_stable = bool(aliases) or any("stable" in item["aliases"] for item in versions)
    # Preserve the initial prerelease entry point until a stable release exists.
    # Catalog ordering must not implicitly choose a different default on replay.
    if has_stable or not versions:
        default = "stable" if has_stable else selection["version"]
        run(portal, *mike, "set-default", "--config-file", str(config), "--deploy-prefix", item["id"], default)
    return publication.export_history(portal, prefix, selection, verify_site)

