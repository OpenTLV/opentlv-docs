# SPDX-License-Identifier: MIT
# Copyright (c) 2026 Marek Cingel

"""Explicit Git inputs shared by local assembly, CI and publication."""

import importlib.util
import json
import logging
import os
from pathlib import Path, PurePosixPath
import re
import subprocess
from urllib.parse import urlsplit

from mkdocs.exceptions import PluginError

log = logging.getLogger("mkdocs.hooks.sources")
MANIFEST = "docs-sources.json"

_spec = importlib.util.spec_from_file_location("opentlv_docs_compatibility", Path(__file__).with_name("compatibility.py"))
compatibility = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(compatibility)


def git(root, *args):
    result = subprocess.run(["git", "-C", str(root), *args], capture_output=True)
    if result.returncode:
        raise PluginError(result.stderr.decode("utf-8", errors="replace").strip()
                          or "Git rejected the source selection.")
    return result.stdout.decode("utf-8").strip()


def relative_path(value, empty=False):
    if not isinstance(value, str) or (not value and not empty):
        raise PluginError(f"Expected a contained POSIX relative path: {value!r}")
    if (any(ord(char) < 32 for char in value)
            or "\\" in value or ":" in value or "\0" in value
            or (value and any(part in ("", ".", "..") for part in value.split("/")))
            or PurePosixPath(value).is_absolute()):
        raise PluginError(f"Expected a contained POSIX relative path: {value!r}")
    return value


def revision_ref(revision):
    if not isinstance(revision, str) or not revision:
        raise PluginError("Every source requires an explicit tag or full commit SHA.")
    if re.fullmatch(r"[0-9a-fA-F]{40}", revision):
        return revision
    ref = f"refs/tags/{revision}"
    git(Path.cwd(), "check-ref-format", ref)
    return ref


def manifest(portal):
    data = json.loads((portal / MANIFEST).read_text(encoding="utf-8"))
    if not isinstance(data, dict) or data.get("version") != 1 or not isinstance(data.get("sources"), list):
        raise PluginError("docs-sources.json requires version 1 and a sources list.")
    ids = set()
    for item in data["sources"]:
        if not isinstance(item, dict):
            raise PluginError("Source entries must be objects.")
        identifier = item.get("id", "")
        if not isinstance(identifier, str) or not re.fullmatch(r"[a-z][a-z0-9_]*", identifier) or identifier in ids:
            raise PluginError(f"Invalid or duplicate source id: {identifier!r}")
        ids.add(identifier)
        repository = item.get("repository", "")
        if not isinstance(repository, str) or any(ord(char) < 33 for char in repository):
            raise PluginError(f"Invalid repository URL for {identifier}.")
        url = urlsplit(repository)
        # file URLs support offline Git fixtures and private local mirrors.
        if (url.scheme not in ("https", "file") or not url.path or url.query
                or url.fragment or url.username or url.password
                or (url.scheme == "https" and not url.netloc)):
            raise PluginError(f"Invalid repository URL for {identifier}.")
        if "compatibility_result" in item:
            raise PluginError("Compatibility results belong to the generated source lock.")
        if "updates" in item:
            updates = item["updates"]
            if (identifier == "core" or "compatibility" not in item or not isinstance(updates, dict)
                    or set(updates) != {"workflow", "asset"}
                    or not isinstance(updates["workflow"], str)
                    or not re.fullmatch(r"\.github/workflows/[A-Za-z0-9_.-]+\.ya?ml", updates["workflow"])
                    or not isinstance(updates["asset"], str)
                    or not re.fullmatch(r"[A-Za-z0-9_-][A-Za-z0-9_.-]*\.json", updates["asset"])):
                raise PluginError("updates requires a trusted workflow and JSON asset on a compatibility source.")
        if "compatibility" in item:
            if identifier == "core" or "revision" in item:
                raise PluginError("Only non-Core sources may select compatibility instead of an explicit revision.")
            compatibility.validate_settings(item["compatibility"])
            examples = item.get("examples", {})
            languages = examples.get("languages") if isinstance(examples, dict) else None
            if (not isinstance(languages, list) or not languages
                    or not all(isinstance(lang, str) and lang in ("c", "cpp", "rust", "python", "lua", "go") for lang in languages)
                    or len(set(languages)) != len(languages) or "results" in examples):
                raise PluginError("Compatibility selection requires explicit example languages and no inline results.")
        else:
            revision_ref(item.get("revision"))
        relative_path(item.get("docs_path"))
        relative_path(item.get("mount"), empty=identifier == "core")
        if type(item.get("required")) is not bool:
            raise PluginError(f"{identifier}: required must be a boolean.")
        if identifier == "core":
            if not item["required"] or item["docs_path"] != "docs" or item["mount"] != "":
                raise PluginError("Core must be required, with docs_path 'docs' and an empty mount.")
            if "navigation" in item:
                raise PluginError("Core navigation belongs to mkdocs.yml.")
        else:
            nav = item.get("navigation", {})
            if (not isinstance(nav, dict) or not isinstance(nav.get("title"), str)
                    or not nav["title"] or not isinstance(nav.get("section"), list)
                    or not all(isinstance(x, str) and x for x in nav["section"])
                    or not isinstance(nav.get("items"), list) or not nav["items"]):
                raise PluginError(f"{identifier}: navigation requires title, section and items.")
            prefix_nav(nav["items"], item["mount"])
    if "core" not in ids:
        raise PluginError("The manifest requires a Core source.")
    return data["sources"]


def prefix_nav(value, mount):
    if isinstance(value, str):
        relative_path(value)
        if not value.endswith(".md"):
            raise PluginError("Component navigation must reference Markdown files.")
        return f"{mount}/{value}"
    if isinstance(value, list):
        return [prefix_nav(child, mount) for child in value]
    if isinstance(value, dict) and len(value) == 1:
        title, child = next(iter(value.items()))
        if isinstance(title, str) and title:
            return {title: prefix_nav(child, mount)}
    raise PluginError("Invalid component navigation; use standard MkDocs lists and titles.")


def checkout_root(portal, item):
    override = os.environ.get(f"OPENTLV_{item['id'].upper()}_DIR")
    if override:
        return Path(override).resolve()
    if os.environ.get("OPENTLV_DOCS_SOURCE_ROOT"):
        return (Path(os.environ["OPENTLV_DOCS_SOURCE_ROOT"]) / item["id"]).resolve()
    name = urlsplit(item["repository"]).path.rstrip("/").split("/")[-1].removesuffix(".git")
    return (portal.parent / name).resolve()


def resolve(portal):
    definitions = manifest(portal)
    local = os.environ.get("OPENTLV_DOCS_LOCAL") == "1"
    lock_path = os.environ.get("OPENTLV_DOCS_LOCK")
    locked = None
    if lock_path:
        if local:
            raise PluginError("Unset OPENTLV_DOCS_LOCK for a local preview.")
        lock = json.loads(Path(lock_path).read_text(encoding="utf-8"))
        if lock.get("manifest") != definitions:
            raise PluginError("Source lock does not match docs-sources.json; fetch sources again.")
        locked = lock["sources"]
        if [s.get("id") for s in locked] != [s["id"] for s in definitions]:
            raise PluginError("Source lock has a different component set.")
    result = []
    # Resolve Core first even when it is not first in the manifest. Return the
    # original order so source locks and publication retain their existing shape.
    for index in sorted(range(len(definitions)), key=lambda i: definitions[i]["id"] != "core"):
        definition = definitions[index]
        item = dict(definition)
        expected = locked[index] if locked else None
        automatic = "compatibility" in item
        revision = (os.environ.get("OPENTLV_CORE_REF", item.get("revision"))
                    if item["id"] == "core" else item.get("revision"))
        if expected:
            for key in definition:
                if key != "revision" and expected.get(key) != definition[key]:
                    raise PluginError("Source lock configuration mismatch.")
            if item["id"] != "core" and not automatic and expected["revision"] != revision:
                raise PluginError("Source lock revision mismatch.")
            if os.environ.get("OPENTLV_CORE_REF") and item["id"] == "core" and revision != expected["revision"]:
                raise PluginError("Core override conflicts with the source lock.")
            revision = expected.get("revision")
        if automatic:
            core = next(source for _, source in result if source["id"] == "core")
            item = compatible_source(portal, item, core, expected=expected)
            if item["compatibility_result"]["status"] != "verified":
                if os.environ.get(f"OPENTLV_{item['id'].upper()}_DIR"):
                    raise PluginError(f"{item['id']}: explicit directory override conflicts with compatibility omission.")
                if expected and (expected.get("included") is not False or expected.get("reason") != item["reason"]):
                    raise PluginError("Source lock compatibility omission mismatch.")
                result.append((None, dict(expected) if expected else item))
                continue
            revision = item["revision"]
            if expected and expected.get("revision") != revision:
                raise PluginError("Source lock compatibility revision mismatch.")
        item.update(revision=revision, local=local, dirty=False)
        ref = revision_ref(revision)
        root = checkout_root(portal, item)
        if expected and expected.get("included") is False:
            if item["required"]:
                raise PluginError("A required source cannot be omitted from the lock.")
            if os.environ.get(f"OPENTLV_{item['id'].upper()}_DIR"):
                raise PluginError(f"{item['id']}: explicit directory override conflicts with locked omission.")
            result.append((None, dict(expected)))
            continue
        if not root.exists():
            if item["required"] or expected or os.environ.get(f"OPENTLV_{item['id'].upper()}_DIR"):
                raise PluginError(f"Required or explicitly selected checkout is missing: {item['id']} ({root})")
            item.update(included=False, reason="checkout missing")
            result.append((None, item))
            continue
        if Path(git(root, "rev-parse", "--show-toplevel")).resolve() != root:
            raise PluginError(f"OPENTLV_{item['id'].upper()}_DIR must be the repository root.")
        commit = git(root, "rev-parse", "HEAD")
        if not local:
            wanted = expected.get("commit") if expected else git(root, "rev-parse", "--verify", "--end-of-options", f"{ref}^{{commit}}")
            if not isinstance(wanted, str) or not re.fullmatch(r"[0-9a-f]{40}", wanted) or commit != wanted:
                raise PluginError(f"{item['id']}: checkout HEAD does not match {revision} ({wanted}). Check out that revision first.")
        dirty = bool(git(root, "status", "--porcelain", "--untracked-files=all"))
        if dirty and not local:
            raise PluginError(f"{item['id']}: checkout is dirty. Use OPENTLV_DOCS_LOCAL=1 for a local preview.")
        docs = root / item["docs_path"]
        if not docs.resolve().is_relative_to(root) or not docs.is_dir():
            raise PluginError(f"Documentation not found inside {item['id']}: {item['docs_path']}")
        if item["id"] == "core" and not (docs / "index.md").is_file():
            raise PluginError("Core documentation requires docs/index.md.")
        item.update(commit=commit, included=True, dirty=dirty)
        result.append((root, item))
    by_id = {item["id"]: (root, item) for root, item in result}
    return [by_id[item["id"]] for item in definitions]


def compatible_source(portal, item, core, *, expected=None, download=False):
    """Select once, then preserve the exact evidence in the publication source set."""
    settings = item["compatibility"]
    if expected is not None:
        evidence = expected.get("compatibility_result")
        if not isinstance(evidence, dict):
            raise PluginError("Source lock is missing compatibility evidence.")
        record = evidence.get("record")
        feed = {"version": 1, "records": [record] if record is not None else []}
    else:
        feed = compatibility.load(portal, settings, allow_download=download)
    selection = compatibility.select(feed, settings, item["repository"], core["repository"], core["commit"])
    if expected is not None and selection != evidence:
        raise PluginError("Source lock compatibility evidence does not match the selected sources.")
    item = dict(item, compatibility_result=selection)
    if selection["status"] == "verified":
        item["revision"] = selection["record"]["component"]["commit"]
        if expected and expected.get("included") and expected.get("commit") != item["revision"]:
            raise PluginError("Source lock component commit differs from compatibility evidence.")
    else:
        reason = "no verified compatible release: " + selection["status"]
        if item["required"]:
            raise PluginError(f"{item['id']}: {reason}")
        item.update(included=False, reason=reason, local=os.environ.get("OPENTLV_DOCS_LOCAL") == "1", dirty=False)
    return item


def fetch(portal, core_revision):
    """Populate fresh managed checkouts; never mutate workspace overrides."""
    definitions = manifest(portal)
    base = portal / "build" / "sources"
    if base.resolve() != base or (portal / "build").resolve() != portal / "build":
        raise PluginError("Managed sources must stay inside the portal build directory.")
    base.mkdir(parents=True, exist_ok=True)
    selected = []
    for definition in sorted(definitions, key=lambda item: item["id"] != "core"):
        item = dict(definition)
        if item["id"] == "core":
            item["revision"] = core_revision
        elif "compatibility" in item:
            core = next(source for source in selected if source["id"] == "core")
            item = compatible_source(portal, item, core, download=True)
            if item["compatibility_result"]["status"] != "verified":
                selected.append(item)
                continue
        ref = revision_ref(item["revision"])
        root = base / item["id"]
        # Refuse stale checkouts rather than reset user data or reuse stale tags.
        if root.exists() or root.is_symlink():
            raise PluginError(f"Managed checkout already exists: {root}. Use a fresh build/sources directory.")
        probe = subprocess.run(["git", "ls-remote", "--", item["repository"]], capture_output=True)
        if probe.returncode:
            if item["required"]:
                raise PluginError(f"Required repository is unavailable: {item['id']}")
            log.info("Optional repository unavailable: %s", item["id"])
            item.update(included=False, reason="repository unavailable", local=False, dirty=False)
        else:
            git(base, "clone", "--no-checkout", "--", item["repository"], str(root))
            commit = git(root, "rev-parse", "--verify", "--end-of-options", f"{ref}^{{commit}}")
            git(root, "checkout", "--detach", commit)
            item.update(included=True, commit=commit, local=False, dirty=False)
        selected.append(item)
    by_id = {item["id"]: item for item in selected}
    lock = {"manifest": definitions, "sources": [by_id[item["id"]] for item in definitions]}
    path = portal / "build/sources.lock.json"
    path.write_text(json.dumps(lock, indent=2) + "\n", encoding="utf-8")
    return lock
