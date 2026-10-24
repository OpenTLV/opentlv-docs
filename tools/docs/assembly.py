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

_js_spec = importlib.util.spec_from_file_location("opentlv_docs_js", Path(__file__).with_name("js.py"))
js = importlib.util.module_from_spec(_js_spec)
_js_spec.loader.exec_module(js)

_spec = importlib.util.spec_from_file_location("opentlv_docs_sources", Path(__file__).with_name("sources.py"))
sources = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(sources)

_spec = importlib.util.spec_from_file_location("opentlv_docs_examples", Path(__file__).with_name("examples.py"))
examples = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(examples)

_spec = importlib.util.spec_from_file_location("opentlv_docs_onboarding", Path(__file__).with_name("onboarding.py"))
onboarding = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(onboarding)

_spec = importlib.util.spec_from_file_location("opentlv_docs_formats", Path(__file__).with_name("formats.py"))
formats = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(formats)

_spec = importlib.util.spec_from_file_location("opentlv_docs_content", Path(__file__).with_name("content.py"))
content = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(content)
git = sources.git

log = logging.getLogger("mkdocs.hooks.assembly")

# Exact, portal-owned presentation files still present in transitional Core.
# Adding a new override requires an explicit ownership decision here.
PORTAL_OVERRIDES = frozenset({
    "index.md",
    "assets/README.md", "assets/favicon.svg", "assets/logo-mark.svg",
    "assets/opentlv.svg", "assets/opentlv-light.svg", "assets/opentlv-dark.svg",
    "playground/index.md", "playground/playground.js", "playground/playground.css",
})

# Exact pages extracted from Core into the standalone CLI. This is an ownership
# transfer, not a directory overlay: all other collisions still fail.
CLI_MIGRATED_PAGES = {
    "cli/README.md": ("docs/cli/README.md", "docs/README.md"),
    "cli/json-schema.md": ("docs/cli/json-schema.md", "docs/json-schema.md"),
}

# Core 0.7.1 predates the documentation-ownership/quality-gates pages, Go/WASM
# migration baselines and Lua extraction. Match its immutable commit, never missing files.
CORE_071_COMMIT = "e12a52ff69a64468eecab084795a0530c273efea"
CORE_GO_ARCHIVES = frozenset((
    "guides/go.md", "development/go.md", "development/go-migration/README.md",
))


def without_core_go_archives(items):
    """Remove only the complete Go archive group retired by Core #686."""
    result = []
    for entry in items:
        if isinstance(entry, str):
            if entry not in CORE_GO_ARCHIVES:
                result.append(entry)
            continue
        for title, value in entry.items():
            if isinstance(value, list):
                children = without_core_go_archives(value)
                if children:
                    result.append({title: children})
            elif value not in CORE_GO_ARCHIVES:
                result.append({title: value})
    return result


def cli_replaces_core(name, previous, owner):
    paths = CLI_MIGRATED_PAGES.get(name)
    return bool(paths and isinstance(previous, dict) and isinstance(owner, dict)
                and previous["id"] == "core" and previous["path"] == paths[0]
                and owner["id"] == "cli" and owner["path"] == paths[1])


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
    core_root, core = next((root, item) for root, item in selected if item["id"] == "core")
    if (core_root is not None and core.get("repository") == "https://github.com/OpenTLV/opentlv"
            and core.get("commit") != CORE_071_COMMIT):
        docs = core_root / core["docs_path"]
        present = {name for name in CORE_GO_ARCHIVES if (docs / name).is_file()}
        if not present and not (core_root / "bindings/go").exists():
            result = without_core_go_archives(result)
        # Partial removals retain navigation entries, so strict validation fails.
    if (core.get("repository") == "https://github.com/OpenTLV/opentlv"
            and core.get("commit") == CORE_071_COMMIT):
        def historical(items):
            result = []
            for entry in items:
                if entry in (
                    {"Core quality gates": "development/quality-gates.md"},
                    {"Documentation ownership": "development/documentation-ownership.md"},
                    {"Go migration baseline": "development/go-migration/README.md"},
                    {"WASM migration baseline": "development/wasm-migration/README.md"},
                ):
                    continue
                result.append({title: historical(value) if isinstance(value, list) else value
                               for title, value in entry.items()})
            return result

        result = historical(result)
        for entry in result:
            if not isinstance(entry, dict):
                continue
            if "Development" in entry:
                entry["Development"].append({"Historical Core Lua development": "development/lua.md"})
            for title in ("Languages", "Bindings", "Language APIs"):
                if title in entry:
                    entry[title].append({"Historical Core Lua API": "guides/lua.md"})
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
        manual_items = nav["items"]
        if js.bootstrap(item):
            manual_items = [entry for entry in manual_items if "webassembly.md" not in entry.values()]
        items = sources.prefix_nav(manual_items, item["mount"])
        parent.append({nav["title"]: content.relocate(items, result)})
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
        if key in names:
            exact = names[key] == name
            if exact and cli_replaces_core(name, owner, previous):
                return  # Retain CLI ownership even if Core is enumerated later.
            portal_override = (owner == "portal" and isinstance(previous, dict)
                               and previous["id"] == "core" and name in PORTAL_OVERRIDES)
            if not exact or not (portal_override or cli_replaces_core(name, previous, owner)):
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
    if any(item["id"] == "cli" and item["included"] for _, item in selected):
        for name in CLI_MIGRATED_PAGES:
            if owners.get(name, {}).get("id") == "core":
                raise PluginError(f"Selected CLI must supply migrated documentation: {name}")
    # The virtual sibling keeps the original relative-link base and Core owner.
    # Its rendered destination belongs to Development, as defined in navigation.
    first_program = onboarding.FIRST_PROGRAM
    split_onboarding = (portal / "docs/getting-started/overview.md").is_file()
    if split_onboarding:
        if first_program not in inputs or owners[first_program]["id"] != "core":
            raise PluginError("Portal onboarding requires the Core first-program source.")
        add(onboarding.CORE_BUILD, inputs[first_program], owners[first_program])
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
        if (folded in ("source-revision.json", "api", "api/reference",
                       "api/reference/c-api", "api/reference/cxx-api", "api/reference/api-source.json")
                or folded.startswith(("source-revision.json/", "api/reference/c-api/",
                                      "api/reference/cxx-api/", "api/reference/api-source.json/"))):
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
    if split_onboarding:
        original = rendered.get(first_program, inputs[first_program].read_text(encoding="utf-8"))
        rendered[first_program], rendered[onboarding.CORE_BUILD] = onboarding.split(original)
        rendered[first_program] = onboarding.standalone_go(rendered[first_program], selected)
    if (portal / "docs/formats/overview.md").is_file():
        for name in formats.PLANS:
            if name not in inputs or not isinstance(owners[name], dict) or owners[name]["id"] != "core":
                raise PluginError(f"Formats presentation requires the Core source: {name}")
        for target in formats.PLANS.keys() - formats.MERGES.keys():
            parts = [target] + [name for name, destination in formats.MERGES.items() if destination == target]
            rendered[target] = formats.render(target, [
                (name, rendered.get(name, inputs[name].read_text(encoding="utf-8"))) for name in parts
            ])
            owners[target]["parts"] = [owners[name]["path"] for name in parts]
        for name in formats.MERGES:
            del inputs[name]
            del owners[name]
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
        if "compatibility" in item and not os.environ.get("OPENTLV_DOCS_LOCK"):
            settings = item["compatibility"]
            feed = (f"build/compatibility/{settings['sha256']}.json"
                    if settings["feed"].startswith("https:") else settings["feed"])
            config.watch.append(str(portal / feed))
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
