# SPDX-License-Identifier: MIT
# Copyright (c) 2026 Marek Cingel

"""Authenticate CLI releases and publish immutable, independently versioned docs."""

import hashlib
import json
import os
from pathlib import Path
import re
import event_artifacts
import events
import sources
import component_publication
from component_publication import assemble, verify_site

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


def prepare(portal, selection, checkout=None):
    if selection.get("source") != "cli":
        raise ValueError("CLI publication requires a CLI release identity.")
    return component_publication.prepare(portal, selection, checkout)


def main():
    if not os.environ.get("GH_TOKEN"):
        raise ValueError("Configure OPENTLV_CLI_READ_TOKEN with read access to CLI release artifacts.")
    event = json.loads(Path(os.environ["GITHUB_EVENT_PATH"]).read_text(encoding="utf-8"))
    if event.get("action") != "cli-docs-released":
        raise ValueError("Expected cli-docs-released dispatch.")
    selection = validate(event["client_payload"], sources.manifest(ROOT))
    (ROOT / "build").mkdir(exist_ok=True)
    (ROOT / "build/selection.json").write_text(json.dumps(selection, indent=2) + "\n", encoding="utf-8")
    commit = prepare(ROOT, selection)
    if os.environ.get("GITHUB_OUTPUT"):
        with open(os.environ["GITHUB_OUTPUT"], "a", encoding="utf-8") as output:
            output.write(f"pages_commit={commit}\n")
    print(f"Prepared CLI {selection['version']} at gh-pages {commit}; no remote publication performed.")


if __name__ == "__main__":
    main()
