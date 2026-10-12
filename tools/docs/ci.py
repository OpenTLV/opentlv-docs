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
    required = {path.relative_to(docs).as_posix() for path in docs.rglob("*.md")}
    required.discard("README.md")
    present = nav_paths(yaml.safe_load(portal_config).get("nav", []))
    missing = required - present
    if missing:
        raise ValueError("Portal navigation omits documentation: " + ", ".join(sorted(missing)))


def check_core(portal):
    core, source = assembly.selected_source(portal)
    # Pin a tag's resolved commit for every subsequent build in this job.
    os.environ["OPENTLV_CORE_REF"] = source["commit"]
    selection_path = portal / "build/selection.json"
    if selection_path.exists():
        selection = json.loads(selection_path.read_text(encoding="utf-8"))
        selection["commit"] = source["commit"]
        selection_path.write_text(json.dumps(selection, indent=2) + "\n", encoding="utf-8")
    if os.environ.get("GITHUB_ENV"):
        with open(os.environ["GITHUB_ENV"], "a", encoding="utf-8") as output:
            output.write(f"OPENTLV_CORE_REF={source['commit']}\n")
    for script in ("check_doc_examples.py", "test_doc_inventory.py", "check_doc_inventory.py"):
        subprocess.run([sys.executable, str(core / "scripts" / script)], cwd=core, check=True)
    assembly.assemble(portal)
    check_navigation(portal / "build/assembled/docs",
                     (portal / "mkdocs.yml").read_text(encoding="utf-8"))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("command", choices=("select", "check"))
    args = parser.parse_args()
    if args.command == "check":
        check_core(ROOT)
        return
    selection = select(json.loads((ROOT / "core-source.json").read_text(encoding="utf-8")),
                       os.environ.get("INPUT_CHANNEL") or "development",
                       os.environ.get("INPUT_CORE_REF", ""))
    (ROOT / "build").mkdir(exist_ok=True)
    (ROOT / "build/selection.json").write_text(json.dumps(selection, indent=2) + "\n", encoding="utf-8")
    with open(os.environ["GITHUB_OUTPUT"], "a", encoding="utf-8") as output:
        for key, value in selection.items():
            output.write(f"{key}={value}\n")


if __name__ == "__main__":
    main()
