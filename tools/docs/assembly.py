# SPDX-License-Identifier: MIT
# Copyright (c) 2026 Marek Cingel

"""Assemble Core-owned Markdown without changing its external checkout."""

import json
import logging
import os
from pathlib import Path
import re
import shutil
import subprocess

from mkdocs.exceptions import PluginError

log = logging.getLogger("mkdocs.hooks.assembly")

# Exact, portal-owned presentation files still present in transitional Core.
# Adding a new override requires an explicit ownership decision here.
PORTAL_OVERRIDES = frozenset({
    "assets/README.md", "assets/favicon.svg", "assets/logo-mark.svg",
    "assets/opentlv.svg", "assets/opentlv-light.svg", "assets/opentlv-dark.svg",
})


def reject_local_publication(command=None, channel=None):
    if os.environ.get("OPENTLV_DOCS_LOCAL") == "1" and (
        command in ("gh-deploy", "mike")
        or os.environ.get("OPENTLV_DOCS_PUBLISH") == "1"
        or os.environ.get("OPENTLV_DOCS_CHANNEL", channel) == "release"
    ):
        raise PluginError("Local preview cannot be used for publication or release builds. Unset OPENTLV_DOCS_LOCAL.")


def on_startup(command, dirty):
    reject_local_publication(command=command)


def git(root, *args):
    result = subprocess.run(
        ["git", "-C", str(root), *args], capture_output=True, check=False,
    )
    if result.returncode:
        detail = result.stderr.decode("utf-8", errors="replace").strip()
        raise PluginError(detail or f"Git rejected the source selection: {' '.join(args)}")
    return result.stdout.decode("utf-8").strip()


def selected_source(portal):
    reject_local_publication()
    manifest = json.loads((portal / "core-source.json").read_text(encoding="utf-8"))
    root = Path(os.environ.get("OPENTLV_CORE_DIR", str(portal.parent / "opentlv"))).resolve()
    revision = os.environ.get("OPENTLV_CORE_REF", manifest["revision"])
    local = os.environ.get("OPENTLV_DOCS_LOCAL") == "1"
    # Branches and abbreviated SHAs are deliberately not reproducible selectors.
    ref = revision if re.fullmatch(r"[0-9a-fA-F]{40}", revision) else f"refs/tags/{revision}"
    if ref.startswith("refs/tags/"):
        git(root, "check-ref-format", ref)
    commit = git(root, "rev-parse", "HEAD")
    if not local:
        configured_commit = git(root, "rev-parse", "--verify", "--end-of-options", f"{ref}^{{commit}}")
        if commit != configured_commit:
            raise PluginError(f"Core checkout HEAD does not match {revision} ({configured_commit}). Check out that revision first.")
    if Path(git(root, "rev-parse", "--show-toplevel")).resolve() != root:
        raise PluginError("OPENTLV_CORE_DIR must be the Core repository root.")
    dirty = bool(git(root, "status", "--porcelain", "--untracked-files=all"))
    if dirty and not local:
        raise PluginError("Core checkout is dirty. Use a clean checkout or explicitly set OPENTLV_DOCS_LOCAL=1 for a local preview.")
    if not (root / "docs" / "index.md").is_file():
        raise PluginError(f"Core documentation not found in {root / 'docs'}")
    return root, {
        "repository": manifest["repository"], "revision": revision, "commit": commit,
        "local": local, "dirty": dirty,
    }


def reset_output(portal):
    """Only replace this hook's disposable output inside the portal build tree."""
    build = portal / "build"
    output = build / "assembled"
    if build.is_symlink() or build.resolve() != portal / "build":
        raise PluginError("The portal build directory must not redirect outside the repository.")
    if output.is_symlink() or output.resolve() != build / "assembled":
        raise PluginError("The assembly output directory must not be a link.")
    if output.exists():
        shutil.rmtree(output)
    output.mkdir(parents=True)
    return output


def assemble(portal):
    root, source = selected_source(portal)
    # Only version-controlled sources are included, with non-ignored new pages
    # added for an explicitly requested local preview. Build debris stays out.
    args = ["ls-files", "-z", "--cached"]
    if source["local"]:
        args += ["--others", "--exclude-standard"]
    paths = git(root, *args, "--", "docs/").split("\0")
    core_files = {}
    for name in sorted(set(filter(None, paths))):
        path = root / name
        if not path.exists() and source["local"]:
            continue  # A locally deleted tracked page should disappear too.
        if not path.resolve().is_relative_to(root) or path.is_symlink():
            raise PluginError(f"Documentation source must be a regular file inside Core: {name}")
        core_files[Path(name).relative_to("docs").as_posix()] = path
    portal_files = {
        path.relative_to(portal / "docs").as_posix(): path
        for path in sorted((portal / "docs").rglob("*")) if path.is_file()
    }
    # Validate the complete input set before replacing any previous assembly.
    owners = {os.path.normcase(name): name for name in core_files}
    for name in portal_files:
        key = os.path.normcase(name)
        if key in owners and (name not in PORTAL_OVERRIDES or owners[key] != name):
            raise PluginError(f"Unexpected documentation collision at '{name}' between Core and portal. Declare an intentional ownership override explicitly.")
        owners[key] = name
    for name in owners.values():
        for parent in Path(name).parents:
            if os.path.normcase(parent.as_posix()) in owners:
                raise PluginError(f"Documentation file/directory collision at '{parent.as_posix()}' involving '{name}'.")
    output = reset_output(portal)
    docs = output / "docs"
    for inputs in (core_files, portal_files):
        for name, path in inputs.items():
            target = docs / name
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(path, target)
    (output / "source-revision.json").write_text(
        json.dumps(source, indent=2) + "\n", encoding="utf-8",
    )
    log.info("Core documentation: %s%s", source["commit"], " (local preview)" if source["local"] else "")
    return root, source


def on_config(config):
    reject_local_publication(channel=config.extra.get("docs_channel"))
    portal = Path(config.config_file_path).resolve().parent
    config.docs_dir = str(portal / "build" / "assembled" / "docs")
    config.watch.append(str(portal / "docs"))
    config.watch.append(str(portal / "core-source.json"))
    config.watch.append(str(Path(__file__).resolve().parent))
    root, _source = selected_source(portal)
    config.watch.append(str(root / "docs"))
    return config


def on_pre_build(config):
    portal = Path(config.config_file_path).resolve().parent
    root, source = assemble(portal)
    config.extra["core_source"] = source
    config.extra["core_checkout"] = str(root)


def on_serve(server, config, builder):
    # MkDocs watches docs_dir automatically. Watching generated output would
    # trigger an endless rebuild loop; on_config adds the actual inputs instead.
    server.unwatch(config.docs_dir)
    return server
