# SPDX-License-Identifier: MIT
# Copyright (c) 2026 Marek Cingel

"""Validate a manual Docs version request with read-only repository permissions."""

from datetime import date
import hashlib
import json
import os
from pathlib import Path
import re
import subprocess
from urllib.error import HTTPError
from urllib.request import Request, urlopen

ROOT = Path(__file__).resolve().parents[2]
REPOSITORY = "OpenTLV/opentlv-docs"
TAG = re.compile(r"v(0|[1-9][0-9]*)\.(0|[1-9][0-9]*)\.(0|[1-9][0-9]*)\Z")


def release_notes(text, tag):
    if not TAG.fullmatch(tag):
        raise ValueError("Docs tag must be canonical vMAJOR.MINOR.PATCH")
    sections = re.split(r"^## ", text, flags=re.MULTILINE)[1:]
    if sections and sections[0].partition("\n")[0] == "[Unreleased]":
        if sections.pop(0).removeprefix("[Unreleased]").strip():
            raise ValueError("Close the Docs changelog before requesting a version")
    if not sections:
        raise ValueError("Missing Docs release notes")
    heading, _, body = sections[0].partition("\n")
    match = re.fullmatch(r"\[" + re.escape(tag[1:]) + r"\] - (\d{4}-\d{2}-\d{2})", heading)
    if not match or date.fromisoformat(match[1]) > date.today():
        raise ValueError("Newest closed Docs changelog must match the tag and a nonfuture date")
    if not re.search(r"^- \S", body, re.MULTILINE):
        raise ValueError("Missing Docs release notes")
    return "## " + heading + "\n\n" + body.strip() + "\n"


def absent(tag):
    for suffix in (f"git/ref/tags/{tag}", f"releases/tags/{tag}"):
        request = Request(f"https://api.github.com/repos/{REPOSITORY}/{suffix}", headers={
            "Accept": "application/vnd.github+json", "User-Agent": "OpenTLV-Docs-release",
            "Authorization": "Bearer " + os.environ["GH_TOKEN"],
        })
        try:
            with urlopen(request, timeout=60):
                pass
        except HTTPError as error:
            if error.code != 404:
                raise
        else:
            raise ValueError(f"Docs tag or release already exists: {tag}")


def prepare(portal, env):
    # Repository dispatch payloads never opt in to Docs version publication.
    if env["GITHUB_EVENT_NAME"] != "workflow_dispatch":
        return None
    channel, tag = env.get("INPUT_CHANNEL", "development"), env.get("INPUT_TAG", "")
    publish = env.get("INPUT_PUBLISH", "false") == "true"
    if publish and env["GITHUB_REF"] != "refs/heads/main":
        raise ValueError("Manual publication requires main")
    if channel == "release" and publish and not tag:
        raise ValueError("Manual release publication requires a Docs tag")
    if not tag:
        return None
    if channel != "release":
        raise ValueError("A Docs tag requires channel=release")
    core_ref = env.get("INPUT_CORE_REF", "")
    if not TAG.fullmatch(core_ref if core_ref.startswith("v") else "v" + core_ref):
        raise ValueError("A Docs version requires an explicit stable Core release tag")
    notes = release_notes((portal / "CHANGELOG.md").read_text(encoding="utf-8"), tag)
    identity = {key: env["GITHUB_" + key.upper()] for key in
                ("repository", "sha", "run_id", "run_attempt", "workflow_ref")}
    if (identity["repository"] != REPOSITORY or not re.fullmatch(r"[0-9a-f]{40}", identity["sha"])
            or identity["workflow_ref"] != f"{REPOSITORY}/.github/workflows/docs-release.yml@{env['GITHUB_REF']}"
            or any(not identity[key].isdigit() or int(identity[key]) < 1 for key in ("run_id", "run_attempt"))):
        raise ValueError("Invalid Docs release workflow identity")
    def git(*args):
        return subprocess.check_output(["git", *args], cwd=portal, text=True).strip()
    if git("rev-parse", "HEAD") != identity["sha"] or git("status", "--porcelain", "--untracked-files=all"):
        raise ValueError("Docs version requires the exact clean workflow commit")
    absent(tag)
    return {"schema": 1, "identity": identity, "tag": tag, "version": tag[1:],
            "core_ref": core_ref, "publish": publish, "notes": notes,
            "manifest_sha256": hashlib.sha256((portal / "docs-sources.json").read_bytes()).hexdigest()}


def main():
    request = prepare(ROOT, os.environ)
    requested = bool(request and request["publish"])
    digest = ""
    if request:
        path = ROOT / "build/version-request/request.json"
        path.parent.mkdir(parents=True, exist_ok=True)
        raw = (json.dumps(request, indent=2) + "\n").encode("utf-8")
        path.write_bytes(raw)
        digest = hashlib.sha256(raw).hexdigest()
    with open(os.environ["GITHUB_OUTPUT"], "a", encoding="utf-8") as output:
        output.write(f"versioned={str(requested).lower()}\nrequest_sha256={digest}\n")


if __name__ == "__main__":
    main()
