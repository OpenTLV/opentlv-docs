# SPDX-License-Identifier: MIT
# Copyright (c) 2026 Marek Cingel

"""Authenticate CLI releases and publish immutable, independently versioned docs."""

import hashlib
import json
import os
from pathlib import Path
import re
import shutil
import sys

import yaml

import ci
import event_artifacts
import events
import publication
import sources

ROOT = Path(__file__).resolve().parents[2]
TAG = re.compile(r"v((?:0|[1-9][0-9]*)\.(?:0|[1-9][0-9]*)\.(?:0|[1-9][0-9]*)(?:-[0-9A-Za-z-]+(?:\.[0-9A-Za-z-]+)*)?)\Z")


def version(tag):
    match = TAG.fullmatch(tag) if isinstance(tag, str) else None
    if not match or ("-" in tag and any(
            part.isdigit() and len(part) > 1 and part.startswith("0")
            for part in tag.split("-", 1)[1].split("."))):
        raise ValueError("CLI release requires vMAJOR.MINOR.PATCH with an optional SemVer prerelease.")
    return match[1]


def validate(payload, definitions, api=None, download=None):
    """Bind a dispatch to the successful gate's exact request, attempt and tag."""
    api = api or events.github
    if (not isinstance(payload, dict)
            or set(payload) != {"source", "repository", "commit", "ref", "run_id", "run_attempt"}
            or payload["source"] != "cli"):
        raise ValueError("Expected a CLI release notification.")
    item = next((item for item in definitions if item["id"] == "cli"), None)
    if item is None or payload["repository"] != events.repository(item):
        raise ValueError("CLI notification must identify the configured repository.")
    selected_version = version(payload["ref"])
    if (not isinstance(payload["commit"], str) or not events.SHA.fullmatch(payload["commit"])
            or any(type(payload[key]) is not int or payload[key] <= 0 for key in ("run_id", "run_attempt"))):
        raise ValueError("CLI notification requires a full commit SHA and positive run identity.")
    repo = payload["repository"]
    run = api(f"{repo}/actions/runs/{payload['run_id']}")
    if (run.get("status") != "completed" or run.get("conclusion") != "success"
            or run.get("event") != "workflow_dispatch" or run.get("head_branch") != "main"
            or run.get("path") != ".github/workflows/release.yml"
            or run.get("head_repository", {}).get("full_name") != repo
            or run.get("run_attempt") != payload["run_attempt"]
            or not isinstance(run.get("head_sha"), str) or not events.SHA.fullmatch(run["head_sha"])):
        raise ValueError("CLI release requires the successful trusted release gate and current attempt.")
    evidence_source = dict(item, updates={"asset": "result.json",
        "development_artifact": f"release-result-{payload['run_attempt']}"})
    evidence_payload = dict(payload, ref="main", commit=run["head_sha"])
    raw = event_artifacts.fetch_feed(evidence_payload, evidence_source, api, download)
    result = json.loads(raw)
    request = result.get("request", {})
    expected = {"cli_sha": payload["commit"], "tag": payload["ref"], "version": selected_version,
                "workflow_sha": run["head_sha"], "run_id": str(payload["run_id"]),
                "run_attempt": str(payload["run_attempt"])}
    if (result.get("status") != "passed"
            or result.get("jobs") != {"validation": "success", "quality": "success"}
            or any(request.get(key) != value for key, value in expected.items())):
        raise ValueError("CLI release evidence does not authorize the notified tag, commit and run.")
    if events.resolve_revision(repo, payload["ref"], api) != payload["commit"]:
        raise ValueError("CLI release tag moved away from its validated commit.")
    relation = api(f"{repo}/compare/{payload['commit']}...{run['head_sha']}")
    if relation.get("status") not in ("ahead", "identical"):
        raise ValueError("CLI release commit is not in the trusted workflow history.")
    return {"source": "cli", "repository": item["repository"], "commit": payload["commit"],
            "tag": payload["ref"], "version": selected_version, "local": False, "dirty": False,
            "producer": {"run_id": payload["run_id"], "run_attempt": payload["run_attempt"],
                         "workflow_commit": run["head_sha"], "evidence_sha256": hashlib.sha256(raw).hexdigest()}}


def verify_site(site, selection):
    metadata = json.loads((site / "source-revision.json").read_text(encoding="utf-8"))
    for key in ("source", "repository", "commit", "tag", "version", "local", "dirty"):
        if metadata.get(key) != selection[key]:
            raise ValueError("CLI snapshot identity differs from the validated release.")
    files = metadata.get("files")
    if not isinstance(files, dict) or not files or "index.html" not in files:
        raise ValueError("CLI snapshot requires a complete file digest manifest.")
    actual = {path.relative_to(site).as_posix(): hashlib.sha256(path.read_bytes()).hexdigest()
              for path in site.rglob("*") if path.is_file() and path != site / "source-revision.json"}
    if actual != files:
        raise ValueError("CLI snapshot file checksums differ from its immutable manifest.")


def assemble(portal, checkout, item, selection):
    """Copy only tracked docs; use portal configuration and trusted hooks."""
    if (sources.git(checkout, "rev-parse", "HEAD") != selection["commit"]
            or sources.git(checkout, "status", "--porcelain", "--untracked-files=all")):
        raise ValueError("CLI documentation requires the exact clean release checkout.")
    output = portal / "build/cli"
    docs = output / "docs"
    docs.mkdir(parents=True, exist_ok=False)
    paths = sources.git(checkout, "ls-files", "-z", "--", ":(literal)" + item["docs_path"] + "/")
    for name in filter(None, paths.split("\0")):
        path = checkout / name
        if path.is_symlink() or not path.is_file() or not path.resolve().is_relative_to(checkout):
            raise ValueError("CLI documentation sources must be contained regular files.")
        relative = path.relative_to(checkout / item["docs_path"])
        if relative.as_posix().casefold() == "source-revision.json":
            raise ValueError("CLI source cannot replace publication provenance.")
        target = docs / relative
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(path, target)
    config = yaml.safe_load((portal / "mkdocs.yml").read_text(encoding="utf-8"))
    # Retain the portal's presentation, without executing Core assembly/build hooks.
    config.update(site_name="OpenTLV CLI " + selection["version"],
                  site_description="OpenTLV command-line documentation",
                  site_url=config["site_url"].rstrip("/") + "/cli/",
                  repo_url=item["repository"], repo_name=events.repository(item),
                  docs_dir=str(docs), site_dir=str(output / "site"),
                  hooks=[str(portal / "tools/docs/cli_hooks.py")],
                  nav=item["navigation"]["items"] + [{"OpenTLV portal": config["site_url"]}],
                  exclude_docs="", extra_css=[], extra_javascript=[], plugins=["search"])
    config["theme"] = dict(config["theme"], custom_dir=str(portal / "tools/docs/overrides"))
    for key in ("logo", "favicon"):
        config["theme"].pop(key, None)
    source = dict(item, commit=selection["commit"], revision=selection["tag"], mount="",
                  included=True, local=False, dirty=False)
    config["extra"] = {"docs_channel": "release", "sources": [source],
                       "cli_checkout": str(checkout), "version": {"provider": "mike", "alias": True},
                       "release_identity": dict(selection, infrastructure_commit=sources.git(portal, "rev-parse", "HEAD"))}
    ci.check_navigation(docs, yaml.safe_dump(config))
    path = output / "mkdocs.yml"
    path.write_text(yaml.safe_dump(config, sort_keys=False), encoding="utf-8")
    return path


def prepare(portal, selection, checkout=None):
    if (selection.get("source") != "cli" or version(selection.get("tag")) != selection.get("version")
            or not events.SHA.fullmatch(selection.get("commit", ""))
            or selection.get("local") is not False or selection.get("dirty") is not False
            or os.environ.get("OPENTLV_DOCS_LOCAL") == "1"):
        raise ValueError("CLI publication requires a clean validated release identity.")
    item = next(item for item in sources.manifest(portal) if item["id"] == "cli")
    if selection["repository"] != item["repository"]:
        raise ValueError("CLI publication repository differs from configuration.")
    run = publication.run
    remote = run(portal, "git", "ls-remote", "--heads", "origin", "refs/heads/gh-pages")
    versions = []
    if remote:
        run(portal, "git", "fetch", "origin", "refs/heads/gh-pages:refs/heads/gh-pages")
        if run(portal, "git", "ls-tree", "--name-only", "gh-pages", "cli/versions.json"):
            versions = json.loads(run(portal, "git", "show", "gh-pages:cli/versions.json"))
    elif run(portal, "git", "branch", "--list", "gh-pages"):
        raise ValueError("Use a fresh checkout; local-only gh-pages cannot authorize publication.")
    prefix = "cli/" + selection["version"]
    if any(item["version"] == selection["version"] for item in versions):
        return publication.export_history(portal, prefix, selection, verify_site)
    if remote and run(portal, "git", "ls-tree", "--name-only", "gh-pages", prefix):
        raise ValueError("CLI snapshot path exists without a registered version.")
    if checkout is None:
        checkout = portal / "build/cli-source"
        if checkout.exists():
            raise ValueError("CLI managed checkout already exists; use a fresh build directory.")
        checkout.parent.mkdir(parents=True, exist_ok=True)
        run(portal, "git", "clone", "--no-checkout", "--", item["repository"], str(checkout))
        commit = run(checkout, "git", "rev-parse", "--verify", "--end-of-options", f"refs/tags/{selection['tag']}^{{commit}}")
        if commit != selection["commit"]:
            raise ValueError("Fetched CLI tag differs from the authenticated release.")
        run(checkout, "git", "checkout", "--detach", commit)
    config = assemble(portal, checkout, item, selection)
    aliases = publication.release_aliases(selection["version"], versions) if "-" not in selection["version"] else []
    mike = [sys.executable, "-B", "-c", "from mike.driver import main; raise SystemExit(main())"]
    run(portal, *mike, "deploy", "--config-file", str(config), "--deploy-prefix", "cli",
        "--alias-type=copy", "--update-aliases", "--title", "CLI " + selection["version"],
        selection["version"], *aliases)
    verify_site(portal / "build/cli/site", selection)
    has_stable = bool(aliases) or any("stable" in item["aliases"] for item in versions)
    # Preserve the initial prerelease entry point until a stable release exists.
    # Catalog ordering must not implicitly choose a different default on replay.
    if has_stable or not versions:
        default = "stable" if has_stable else selection["version"]
        run(portal, *mike, "set-default", "--config-file", str(config), "--deploy-prefix", "cli", default)
    return publication.export_history(portal, prefix, selection, verify_site)


def main():
    if not os.environ.get("GH_TOKEN"):
        raise ValueError("Configure OPENTLV_CLI_READ_TOKEN with read access to CLI release artifacts.")
    event = json.loads(Path(os.environ["GITHUB_EVENT_PATH"]).read_text(encoding="utf-8"))
    if event.get("action") != "cli-docs-released":
        raise ValueError("Expected cli-docs-released dispatch.")
    selection = validate(event["client_payload"], sources.manifest(ROOT))
    commit = prepare(ROOT, selection)
    if os.environ.get("GITHUB_OUTPUT"):
        with open(os.environ["GITHUB_OUTPUT"], "a", encoding="utf-8") as output:
            output.write(f"pages_commit={commit}\n")
    print(f"Prepared CLI {selection['version']} at gh-pages {commit}; no remote publication performed.")


if __name__ == "__main__":
    main()
