# SPDX-License-Identifier: MIT
# Copyright (c) 2026 Marek Cingel

"""Select CI sources and reuse the selected Core's documentation checks."""

import argparse
import json
import os
from pathlib import Path
import re
import subprocess
import sys

import yaml

import assembly
import events

ROOT = Path(__file__).resolve().parents[2]
RELEASE = re.compile(r"v?((?:0|[1-9][0-9]*)\.(?:0|[1-9][0-9]*)\.(?:0|[1-9][0-9]*))")


def select(manifest, channel, override=""):
    repository = manifest["repository"]
    if not re.fullmatch(r"https://github\.com/[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+", repository):
        raise ValueError("Core repository must be an HTTPS GitHub repository URL without a suffix.")
    revision = override or manifest["revision"]
    if not re.fullmatch(r"[0-9a-fA-F]{40}", revision):
        assembly.git(ROOT, "check-ref-format", f"refs/tags/{revision}")
    if channel not in ("development", "release"):
        raise ValueError("Channel must be development or release.")
    release = RELEASE.fullmatch(revision)
    if channel == "release" and not release:
        raise ValueError("Release builds require a Core release tag X.Y.Z or vX.Y.Z; prereleases are excluded.")
    return {"repository": repository.removeprefix("https://github.com/"),
            "revision": revision, "channel": channel,
            "version": release[1] if channel == "release" else "latest"}


def nav_paths(value):
    if isinstance(value, str):
        return {value} if value.endswith(".md") else set()
    children = value.values() if isinstance(value, dict) else value
    return set().union(*(nav_paths(child) for child in children)) if children else set()


def check_navigation(docs, portal_config):
    # The assembled sources, not a second MkDocs configuration in Core, are
    # authoritative. Only the root GitHub index is intentionally site-excluded.
    available = {path.relative_to(docs).as_posix() for path in docs.rglob("*.md")}
    required = available - {"README.md"}
    present = nav_paths(yaml.safe_load(portal_config).get("nav", []))
    stale = present - available
    if stale:
        raise ValueError("Portal navigation references missing documentation: " + ", ".join(sorted(stale)))
    missing = required - present
    if missing:
        raise ValueError("Portal navigation omits documentation: " + ", ".join(sorted(missing)))


def check_core(portal):
    selected = assembly.selected_sources(portal)
    core, source = next((root, item) for root, item in selected if item["id"] == "core")
    selection_path = portal / "build/selection.json"
    if selection_path.exists():
        selection = json.loads(selection_path.read_text(encoding="utf-8"))
        selection["commit"] = source["commit"]
        selection["sources"] = [item for _, item in selected]
        selection_path.write_text(json.dumps(selection, indent=2) + "\n", encoding="utf-8")
    for script in ("check_doc_examples.py", "test_doc_inventory.py", "check_doc_inventory.py"):
        subprocess.run([sys.executable, str(core / "scripts" / script)], cwd=core, check=True)
    assembly.assemble(portal, selected)
    check_navigation(portal / "build/assembled/docs",
                     (portal / "build/assembled/navigation.json").read_text(encoding="utf-8"))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("command", choices=("select", "fetch", "check"))
    args = parser.parse_args()
    if args.command == "check":
        check_core(ROOT)
        return
    if args.command == "fetch":
        selection = json.loads((ROOT / "build/selection.json").read_text(encoding="utf-8"))
        os.environ["OPENTLV_DOCS_CHANNEL"] = selection.get("channel", "development")
        lock = assembly.sources.fetch(ROOT, selection["revision"])
        selection["sources"] = lock["sources"]
        selection["commit"] = next(item["commit"] for item in lock["sources"] if item["id"] == "core")
        if selection.get("event_commit", selection["commit"]) != selection["commit"]:
            raise ValueError("Fetched Core differs from the verified event commit.")
        (ROOT / "build/selection.json").write_text(json.dumps(selection, indent=2) + "\n", encoding="utf-8")
        return
    core = next(item for item in assembly.sources.manifest(ROOT) if item["id"] == "core")
    selection = select(core,
                       os.environ.get("INPUT_CHANNEL") or "development",
                       os.environ.get("INPUT_CORE_REF", ""))
    if os.environ.get("GITHUB_EVENT_NAME") == "repository_dispatch":
        event = json.loads(Path(os.environ["GITHUB_EVENT_PATH"]).read_text(encoding="utf-8"))
        payload = event["client_payload"]
        item = events.validate(payload, assembly.sources.manifest(ROOT))
        if item["id"] != "core":
            raise ValueError("Core publication events must select Core.")
        if payload["ref"] == "main":
            raise ValueError("Core development events require a reviewed manifest pin update PR.")
        selection = select(core, "release", payload["ref"])
        selection["event_commit"] = payload["commit"]
    # Never silently replace the reviewed manifest pin with another revision.
    # A stale proposal or manual run must fail rather than regress latest.
    if (os.environ.get("GITHUB_EVENT_NAME") in ("push", "pull_request", "workflow_dispatch")
            and selection["channel"] == "development"):
        remote = assembly.git(ROOT, "ls-remote", "--heads", "origin", "refs/heads/gh-pages")
        if remote:
            assembly.git(ROOT, "fetch", "origin", "refs/heads/gh-pages")
            names = assembly.git(ROOT, "ls-tree", "--name-only", "FETCH_HEAD", "latest/source-revision.json")
            if names:
                previous = json.loads(assembly.git(ROOT, "show", "FETCH_HEAD:latest/source-revision.json"))
                if previous.get("repository") != core["repository"]:
                    raise ValueError("Published latest belongs to a different Core repository.")
                ref = events.resolve_revision(selection["repository"], selection["revision"])
                if events.newer(selection["repository"], previous["commit"], ref) != ref:
                    raise ValueError("Core pin is older than published latest; update docs-sources.json before publishing.")
    (ROOT / "build").mkdir(exist_ok=True)
    (ROOT / "build/selection.json").write_text(json.dumps(selection, indent=2) + "\n", encoding="utf-8")
    if os.environ.get("GITHUB_OUTPUT"):
        with open(os.environ["GITHUB_OUTPUT"], "a", encoding="utf-8") as output:
            for key in ("repository", "revision", "channel", "version"):
                value = selection[key]
                output.write(f"{key}={value}\n")


if __name__ == "__main__":
    main()
