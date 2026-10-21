# SPDX-License-Identifier: MIT
# Copyright (c) 2026 Marek Cingel
"""Authenticate configured component release receipts before preparing documentation."""

import hashlib
import json
import os
from pathlib import Path
import re
from urllib.parse import quote

import component_publication
import event_artifacts
import events
import sources

ROOT = Path(__file__).resolve().parents[2]


settings = sources.publication_settings


def validate(payload, definitions, api=None, download=None):
    api = api or events.github
    if not isinstance(payload, dict) or set(payload) != {
            "source", "repository", "commit", "ref", "run_id", "run_attempt"}:
        raise ValueError("Expected a component release notification.")
    item = next((item for item in definitions if item["id"] == payload["source"]), None)
    if item is None or payload["repository"] != events.repository(item):
        raise ValueError("Release notification must identify a configured repository.")
    policy = settings(item)
    version = component_publication.version(payload["ref"])
    if (not isinstance(payload["commit"], str) or not events.SHA.fullmatch(payload["commit"])
            or any(type(payload[key]) is not int or payload[key] <= 0 for key in ("run_id", "run_attempt"))):
        raise ValueError("Release requires an exact commit and positive run identity.")
    repo = payload["repository"]
    run = api(f"{repo}/actions/runs/{payload['run_id']}")
    if (run.get("status") != "completed" or run.get("conclusion") != "success"
            or run.get("event") != "workflow_dispatch" or run.get("head_branch") != "main"
            or run.get("path") != policy["workflow"] or run.get("run_attempt") != payload["run_attempt"]
            or run.get("head_repository", {}).get("full_name") != repo
            or not isinstance(run.get("head_sha"), str) or not events.SHA.fullmatch(run["head_sha"])):
        raise ValueError("Release requires a successful trusted workflow and current attempt.")
    evidence_source = dict(item, updates={"asset": policy["asset"],
        "development_artifact": policy["artifact"].format(attempt=payload["run_attempt"])})
    raw = event_artifacts.fetch_feed(dict(payload, ref="main", commit=run["head_sha"]),
                                    evidence_source, api, download)
    receipt = json.loads(raw)
    expected = {"schema": 1, "kind": "component-release", "status": "published",
                "source": item["id"], "repository": repo, "commit": payload["commit"],
                "tag": payload["ref"], "version": version, "workflow_commit": run["head_sha"],
                "run_id": payload["run_id"], "run_attempt": payload["run_attempt"]}
    if (not isinstance(receipt, dict) or type(receipt.get("schema")) is not int
            or set(receipt) != set(expected) | {"release_id"}
            or any(receipt.get(key) != value for key, value in expected.items())
            or any(type(receipt.get(key)) is not int for key in ("run_id", "run_attempt"))
            or type(receipt.get("release_id")) is not int or receipt["release_id"] <= 0):
        raise ValueError("Release receipt does not authorize this tag, commit and run.")
    release = api(f"{repo}/releases/tags/{quote(payload['ref'], safe='')}")
    if (release.get("id") != receipt["release_id"] or release.get("tag_name") != payload["ref"]
            or release.get("draft") is not False or not release.get("published_at")
            or release.get("prerelease") != ("-" in version)):
        raise ValueError("Receipt requires the matching published GitHub release.")
    if events.resolve_revision(repo, payload["ref"], api) != payload["commit"]:
        raise ValueError("Release tag moved away from its verified commit.")
    if api(f"{repo}/compare/{payload['commit']}...{run['head_sha']}").get("status") not in ("ahead", "identical"):
        raise ValueError("Release commit is outside trusted workflow history.")
    return {"source": item["id"], "repository": item["repository"], "commit": payload["commit"],
            "tag": payload["ref"], "version": version, "local": False, "dirty": False,
            "producer": {"run_id": payload["run_id"], "run_attempt": payload["run_attempt"],
                         "workflow_commit": run["head_sha"], "release_id": receipt["release_id"],
                         "evidence_sha256": hashlib.sha256(raw).hexdigest()}}


def main():
    if not os.environ.get("GH_TOKEN"):
        raise ValueError("Configure OPENTLV_COMPONENT_READ_TOKEN with read access to component release artifacts.")
    event = json.loads(Path(os.environ["GITHUB_EVENT_PATH"]).read_text(encoding="utf-8"))
    if event.get("action") != "component-release-published":
        raise ValueError("Expected component-release-published dispatch.")
    selection = validate(event["client_payload"], sources.manifest(ROOT))
    (ROOT / "build").mkdir(exist_ok=True)
    (ROOT / "build/selection.json").write_text(json.dumps(selection, indent=2) + "\n", encoding="utf-8")
    commit = component_publication.prepare(ROOT, selection)
    if os.environ.get("GITHUB_OUTPUT"):
        with open(os.environ["GITHUB_OUTPUT"], "a", encoding="utf-8") as output:
            output.write(f"pages_commit={commit}\n")
    print(f"Prepared {selection['source']} {selection['version']} at {commit}; deployment is separate.")


if __name__ == "__main__":
    main()
