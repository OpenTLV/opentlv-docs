# SPDX-License-Identifier: MIT
# Copyright (c) 2026 Marek Cingel

"""Assemble repository-owned Markdown and navigation without editing sources."""

import copy
import importlib.util
import json
import logging
import os
from pathlib import Path
import shutil
import yaml

from mkdocs.exceptions import PluginError

_spec = importlib.util.spec_from_file_location("opentlv_docs_sources", Path(__file__).with_name("sources.py"))
sources = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(sources)

_spec = importlib.util.spec_from_file_location("opentlv_docs_examples", Path(__file__).with_name("examples.py"))
examples = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(examples)
git = sources.git

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


def selected_sources(portal):
    reject_local_publication()
    return sources.resolve(portal)


def selected_source(portal):
    return next((root, item) for root, item in selected_sources(portal) if item["id"] == "core")


def navigation(base, selected):
    result = copy.deepcopy(base)
    for _root, item in selected:
        if item["id"] == "core" or not item["included"]:
            continue
        nav = item["navigation"]
        parent = result
        for title in nav["section"]:
            matches = [entry[title] for entry in parent if isinstance(entry, dict) and title in entry]
            if len(matches) > 1 or (matches and not isinstance(matches[0], list)):
                raise PluginError(f"Ambiguous navigation destination: {title}")
            if not matches:
                parent.append({title: []})
            parent = matches[0] if matches else parent[-1][title]
        if any(isinstance(entry, dict) and nav["title"] in entry for entry in parent):
            raise PluginError(f"Duplicate navigation title: {nav['title']}")
        parent.append({nav["title"]: sources.prefix_nav(nav["items"], item["mount"])})
    return result


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


def assemble(portal, selected=None):
    selected = selected if selected is not None else selected_sources(portal)
    root, source = next((root, item) for root, item in selected if item["id"] == "core")
    inputs, owners, names = {}, {}, {}

    def add(name, path, owner):
        key = name.casefold()
        previous = owners.get(names.get(key))
        if key in names and not (owner == "portal" and isinstance(previous, dict) and previous["id"] == "core"
                                 and name in PORTAL_OVERRIDES and names[key] == name):
            raise PluginError(f"Unexpected documentation collision at '{name}' between Core and portal or components.")
        names[key] = name
        inputs[name] = path
        owners[name] = owner if owner == "portal" else dict(owner)

    for checkout, item in selected:
        if not item["included"]:
            continue
        args = ["ls-files", "-z", "--cached"]
        if item["local"]:
            args += ["--others", "--exclude-standard"]
        paths = git(checkout, *args, "--", ":(literal)" + item["docs_path"] + "/").split("\0")
        for name in sorted(set(filter(None, paths))):
            path = checkout / name
            if not path.exists() and item["local"]:
                continue
            if not path.resolve().is_relative_to(checkout) or path.is_symlink() or not path.is_file():
                raise PluginError(f"Documentation source must be a regular file inside {item['id']}: {name}")
            relative = Path(name).relative_to(item["docs_path"]).as_posix()
            target = (Path(item["mount"]) / relative).as_posix()
            add(target, path, {"id": item["id"], "path": name, "root": str(checkout)})
    for path in sorted((portal / "docs").rglob("*")):
        if path.is_file():
            if path.is_symlink() or not path.resolve().is_relative_to(portal / "docs"):
                raise PluginError("Portal documentation must stay inside docs/.")
            add(path.relative_to(portal / "docs").as_posix(), path, "portal")
    for name in names.values():
        for parent in Path(name).parents:
            if parent.as_posix().casefold() in names:
                raise PluginError(f"Documentation file/directory collision at '{parent.as_posix()}' involving '{name}'.")
    # Reserve generated output paths too: component assets cannot shadow API HTML.
    for name in inputs:
        folded = name.casefold()
        if (folded in ("source-revision.json", "reference", "reference/api")
                or folded.startswith(("source-revision.json/", "reference/api/"))):
            raise PluginError(f"Documentation collision with generated output: {name}")
    config_file = portal / "mkdocs.yml"
    nav = navigation(yaml.safe_load(config_file.read_text(encoding="utf-8")).get("nav", []), selected) if config_file.exists() else []
    catalog = examples.Catalog(selected, git)
    rendered = {}
    for name, path in inputs.items():
        if name.endswith(".md"):
            original = path.read_text(encoding="utf-8")
            if "<!-- opentlv-examples:" in original or examples.END in original:
                rendered[name] = catalog.transform(original)
    output = reset_output(portal)
    docs = output / "docs"
    for name, path in inputs.items():
        target = docs / name
        target.parent.mkdir(parents=True, exist_ok=True)
        if name in rendered:
            target.write_text(rendered[name], encoding="utf-8", newline="\n")
        else:
            shutil.copyfile(path, target)
    metadata = dict(source, sources=[item for _, item in selected], example_inputs=catalog.inputs)
    (output / "source-revision.json").write_text(json.dumps(metadata, indent=2) + "\n", encoding="utf-8")
    (output / "owners.json").write_text(json.dumps(owners, indent=2) + "\n", encoding="utf-8")
    (output / "navigation.json").write_text(json.dumps({"nav": nav}, indent=2) + "\n", encoding="utf-8")
    for _, item in selected:
        log.info("Documentation source %s: %s", item["id"], item.get("commit", item.get("reason")))
    return root, metadata


def on_config(config):
    reject_local_publication(channel=config.extra.get("docs_channel"))
    portal = Path(config.config_file_path).resolve().parent
    config.docs_dir = str(portal / "build" / "assembled" / "docs")
    config.watch.append(str(portal / "docs"))
    config.watch.append(str(portal / sources.MANIFEST))
    config.watch.append(str(Path(__file__).resolve().parent))
    selected = selected_sources(portal)
    root = next(root for root, item in selected if item["id"] == "core")
    for checkout, item in selected:
        if checkout:
            config.watch.append(str(checkout / item["docs_path"]))
    catalog = examples.Catalog(selected, git)
    checkouts = {item["id"]: checkout for checkout, item in selected}
    for item in catalog.inputs:
        config.watch.append(str(checkouts[item["source"]] / item["path"]))
    config.extra["base_navigation"] = copy.deepcopy(config.nav)
    for name in ("tlv/include", "tlv/resources", "tlv++/include", "tools/docs", "cmake", "CMakeLists.txt"):
        if (root / name).exists():
            config.watch.append(str(root / name))
    return config


def on_pre_build(config):
    portal = Path(config.config_file_path).resolve().parent
    selected = selected_sources(portal)
    root, source = assemble(portal, selected)
    config.nav = navigation(config.extra["base_navigation"], selected)
    config.extra["sources"] = source["sources"]
    config.extra["sources_dirty"] = any(item["dirty"] for item in source["sources"])
    config.extra["core_source"] = source
    config.extra["core_checkout"] = str(root)


def on_serve(server, config, builder):
    # MkDocs watches docs_dir automatically. Watching generated output would
    # trigger an endless rebuild loop; on_config adds the actual inputs instead.
    server.unwatch(config.docs_dir)
    return server
