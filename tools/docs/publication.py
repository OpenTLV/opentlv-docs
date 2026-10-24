# SPDX-License-Identifier: MIT
# Copyright (c) 2026 Marek Cingel

"""Prepare mike history and a Pages artifact in a disposable CI checkout; never push."""

import io
import json
import os
from pathlib import Path
import re
import subprocess
import sys
import zipfile

import wasm

from ci import RELEASE

ROOT = Path(__file__).resolve().parents[2]


def run(root, *args, env=None):
    result = subprocess.run(args, cwd=root, env=env, capture_output=True, text=True,
                            encoding="utf-8", errors="replace")
    if result.returncode:
        raise RuntimeError(f"Command failed: {' '.join(map(str, args))}\n{result.stdout}\n{result.stderr}")
    return result.stdout.strip()


def release_aliases(version, versions):
    stable = next((item["version"] for item in versions if "stable" in item["aliases"]), None)
    if stable is None:
        return ["stable"]
    if not RELEASE.fullmatch(stable):
        raise ValueError("Existing stable alias does not point to an X.Y.Z release.")
    number = lambda text: tuple(map(int, text.split(".")))
    return ["stable"] if number(version) >= number(stable) else []


def verify_site(site, selection):
    source = json.loads((site / "source-revision.json").read_text(encoding="utf-8"))
    api = source.get("api", {})
    if (source.get("local") is not False or source.get("dirty") is not False
            or source.get("commit") != selection["commit"]
            or source.get("repository") != "https://github.com/" + selection["repository"]
            or api.get("commit") != selection["commit"]
            or api.get("local") is not False or api.get("dirty") is not False):
        raise ValueError("Publication requires clean site and API metadata for the selected Core commit.")
    selected = selection["sources"]
    if source.get("sources") != selected:
        raise ValueError("Publication source set differs from the validated selection.")
    for item in selected:
        if (item.get("local") is not False or item.get("dirty") is not False
                or (item.get("included") and not re.fullmatch(r"[0-9a-f]{40}", item.get("commit", "")))
                or (item.get("required") and not item.get("included"))):
            raise ValueError("Publication requires a clean, immutable source set.")
    if os.environ.get("OPENTLV_DOCS_REQUIRE_WASM") == "1" or "wasm" in source:
        metadata = source.get("wasm", {})
        if (metadata.get("commit") != selection["commit"]
                or metadata.get("repository") != source["repository"]
                or metadata.get("local") is not False or metadata.get("dirty") is not False):
            raise ValueError("Publication requires WebAssembly for the exact clean Core source.")
        directory = site / "playground/wasm"
        _root, js_source = wasm.js_selection([(None, item) for item in selected])
        verified = wasm.verify(directory, source, metadata.get("source_sha256"), js_source,
                               metadata.get("js", {}).get("source_sha256"))
        if metadata != dict(verified, manifest="playground/wasm/wasm-source.json"):
            raise ValueError("Published WebAssembly provenance differs from the site metadata.")


def prepare(portal, selection):
    if not re.fullmatch(r"[0-9a-f]{40}", selection["commit"]):
        raise ValueError("Publication requires a resolved full Core commit SHA.")
    channel, version = selection["channel"], selection["version"]
    if channel == "release":
        tag = RELEASE.fullmatch(selection["revision"])
        if not tag or tag[1] != version:
            raise ValueError("Release version must match the selected Core release tag.")
    elif channel != "development" or version != "latest":
        raise ValueError("Development publication must use latest.")
    env = dict(os.environ, OPENTLV_DOCS_PUBLISH="1", OPENTLV_DOCS_CHANNEL=channel)
    lock_path = portal / "build/sources.lock.json"
    lock = json.loads(lock_path.read_text(encoding="utf-8"))
    if lock.get("sources") != selection["sources"]:
        raise ValueError("Publication source lock differs from the validated selection.")
    env["OPENTLV_DOCS_LOCK"] = str(lock_path)
    if env.get("OPENTLV_DOCS_LOCAL") == "1":
        raise ValueError("Local preview cannot be published.")
    # Errors contacting the remote must never be mistaken for a first deployment.
    remote = run(portal, "git", "ls-remote", "--heads", "origin", "refs/heads/gh-pages")
    versions = []
    if remote:
        run(portal, "git", "fetch", "origin", "refs/heads/gh-pages:refs/heads/gh-pages")
        if run(portal, "git", "ls-tree", "--name-only", "gh-pages", "versions.json"):
            versions = json.loads(run(portal, "git", "show", "gh-pages:versions.json"))
    elif subprocess.run(["git", "show-ref", "--verify", "--quiet", "refs/heads/gh-pages"],
                        cwd=portal).returncode == 0:
        raise ValueError("Use a fresh disposable checkout; a local-only gh-pages branch already exists.")
    previous = None
    if channel == "release" and any(item["version"] == version for item in versions):
        previous = json.loads(run(portal, "git", "show", f"gh-pages:{version}/source-revision.json"))
        if (previous.get("commit") != selection["commit"]
                or previous.get("repository") != "https://github.com/" + selection["repository"]):
            raise ValueError("An existing release cannot be replaced with a different Core source.")
        if previous.get("sources") != selection.get("sources"):
            raise ValueError("An existing release cannot be replaced with a different source set.")
        # A matching source set does not make a rebuild immutable: the theme,
        # navigation and renderer may have changed. Reuse the original bytes.
        return export_history(portal, version, selection)
    aliases = release_aliases(version, versions) if channel == "release" else []
    mike = [sys.executable, "-c", "from mike.driver import main; raise SystemExit(main())"]
    # Copy aliases include JSON, API assets and all other non-HTML files too.
    # Pages artifacts cannot contain mike's default symbolic-link aliases.
    run(portal, *mike, "deploy", "--alias-type=copy", "--update-aliases",
        "--title", "latest (development)" if version == "latest" else version,
        version, *aliases, env=env)
    verify_site(portal / "site", selection)
    has_stable = bool(aliases) or any("stable" in item["aliases"] for item in versions)
    run(portal, *mike, "set-default", "stable" if has_stable else "latest", env=env)
    return export_history(portal, version, selection)


def export_history(portal, version, selection, verify=verify_site):
    """Export the complete history without changing any stored snapshot."""
    output = portal / "build/publication"
    output.mkdir(parents=True, exist_ok=False)
    # Git archive applies working-tree conversions too. Preserve the verified
    # bytes rather than applying a contributor's global Windows autocrlf setting.
    archive = subprocess.check_output(["git", "-c", "core.autocrlf=false", "archive", "--format=zip", "gh-pages"], cwd=portal)
    with zipfile.ZipFile(io.BytesIO(archive)) as files:
        for item in files.infolist():
            path = Path(item.filename)
            if (path.is_absolute() or ".." in path.parts or "\\" in item.filename
                    or (item.external_attr >> 16) & 0o170000 == 0o120000):
                raise ValueError(f"Unsafe path or symlink in publication: {item.filename}")
        files.extractall(output / "site")
    verify(output / "site" / version, selection)
    run(portal, "git", "bundle", "create", str(output / "history.bundle"), "refs/heads/gh-pages")
    return run(portal, "git", "rev-parse", "gh-pages")


def main():
    selection = json.loads((ROOT / "build/selection.json").read_text(encoding="utf-8"))
    commit = prepare(ROOT, selection)
    if os.environ.get("GITHUB_OUTPUT"):
        with open(os.environ["GITHUB_OUTPUT"], "a", encoding="utf-8") as output:
            output.write(f"pages_commit={commit}\n")
    print(f"Prepared gh-pages {commit}; no remote publication performed.")


if __name__ == "__main__":
    main()
