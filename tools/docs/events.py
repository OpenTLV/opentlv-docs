# SPDX-License-Identifier: MIT
# Copyright (c) 2026 Marek Cingel

"""Authenticate event evidence against GitHub; payloads never choose repositories or code."""

import copy
import json
import os
from pathlib import Path
import re
from urllib.parse import quote
from urllib.request import Request, urlopen

SHA = re.compile(r"[0-9a-f]{40}\Z")
RELEASE = re.compile(r"v?(?:0|[1-9][0-9]*)\.(?:0|[1-9][0-9]*)\.(?:0|[1-9][0-9]*)\Z")


def github(path):
    headers = {"Accept": "application/vnd.github+json", "X-GitHub-Api-Version": "2022-11-28"}
    if os.environ.get("GH_TOKEN"):
        headers["Authorization"] = "Bearer " + os.environ["GH_TOKEN"]
    request = Request("https://api.github.com/repos/" + path, headers=headers)
    with urlopen(request, timeout=30) as response:
        return json.load(response)


def repository(item):
    value = item["repository"]
    if not re.fullmatch(r"https://github\.com/[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+", value):
        raise ValueError("Automated sources require a configured GitHub repository.")
    return value.removeprefix("https://github.com/")


def validate(payload, definitions, api=github):
    if not isinstance(payload, dict) or set(payload) != {"source", "repository", "commit", "ref", "run_id"}:
        raise ValueError("Event requires source, repository, commit, ref and run_id.")
    item = next((item for item in definitions if item["id"] == payload["source"]), None)
    if item is None or payload["repository"] != repository(item):
        raise ValueError("Event repository is not the configured source.")
    repo = repository(item)
    commit, ref, run_id = payload["commit"], payload["ref"], payload["run_id"]
    if not isinstance(commit, str) or not SHA.fullmatch(commit) or type(run_id) is not int or run_id <= 0:
        raise ValueError("Event requires a full commit SHA and positive workflow run ID.")
    if not isinstance(ref, str) or (ref != "main" and not RELEASE.fullmatch(ref)):
        raise ValueError("Only main and stable release tags may update documentation.")
    if item["id"] != "core" and ref == "main":
        raise ValueError("Components notify stable releases only.")
    policy = item.get("updates", {})
    workflow = ".github/workflows/wasm.yml" if item["id"] == "core" else policy.get("workflow")
    if not isinstance(workflow, str) or not re.fullmatch(r"\.github/workflows/[A-Za-z0-9_.-]+\.ya?ml", workflow):
        raise ValueError("Component updates require an explicitly trusted producer workflow.")
    run = api(f"{repo}/actions/runs/{run_id}")
    if (run.get("conclusion") != "success" or run.get("status") != "completed"
            or run.get("event") != "push" or run.get("head_sha") != commit
            or run.get("head_branch") != ref or run.get("path") != workflow
            or run.get("head_repository", {}).get("full_name") != repo):
        raise ValueError("Event does not identify a successful trusted push workflow.")
    kind = "heads" if ref == "main" else "tags"
    target = api(f"{repo}/git/ref/{kind}/{quote(ref, safe='')}")["object"]
    for _ in range(5):
        if target["type"] != "tag":
            break
        target = api(f"{repo}/git/tags/{target['sha']}")["object"]
    if ref == "main":
        relation = api(f"{repo}/compare/{commit}...{target['sha']}")
        if relation.get("status") not in ("ahead", "identical"):
            raise ValueError("Development commit is not on the current main history.")
    elif target.get("type") != "commit" or target.get("sha") != commit:
        raise ValueError("Release tag no longer identifies the notified commit.")
    return item


def newer(repo, previous, candidate, api=github):
    """Keep latest monotonic even when push/manual/dispatch runs arrive out of order."""
    previous, candidate = previous.lower(), candidate.lower()
    if not SHA.fullmatch(previous) or not SHA.fullmatch(candidate):
        raise ValueError("Latest selection requires full commit SHAs.")
    if previous == candidate:
        return candidate
    status = api(f"{repo}/compare/{previous}...{candidate}").get("status")
    if status in ("ahead", "identical"):
        return candidate
    if status == "behind":
        return previous
    raise ValueError("Latest Core histories diverged; select and review a new baseline explicitly.")


def component_proposal(payload, manifest, api=github):
    """Prepare a reviewed update; never replace evidence from an arbitrary feed URL."""
    result = copy.deepcopy(manifest)
    item = validate(payload, result["sources"], api)
    if item["id"] == "core" or "compatibility" not in item:
        raise ValueError("Component releases require compatibility-based selection.")
    release = api(f"{repository(item)}/releases/tags/{quote(payload['ref'], safe='')}")
    if release.get("draft") or release.get("prerelease"):
        raise ValueError("Only published stable component releases are accepted.")
    name = item["updates"].get("asset", "compatibility.json")
    assets = [asset for asset in release.get("assets", []) if asset.get("name") == name]
    if len(assets) != 1:
        raise ValueError("Release must contain exactly one configured compatibility asset.")
    asset = assets[0]
    digest = asset.get("digest", "")
    expected_url = f"https://github.com/{repository(item)}/releases/download/{quote(payload['ref'], safe='')}/{quote(name, safe='')}"
    if (not re.fullmatch(r"sha256:[0-9a-f]{64}", digest)
            or asset.get("browser_download_url") != expected_url):
        raise ValueError("Compatibility asset requires a GitHub SHA-256 digest and repository release URL.")
    item["compatibility"].update(feed=expected_url, sha256=digest.removeprefix("sha256:"))
    return result


if __name__ == "__main__":
    root = Path(__file__).resolve().parents[2]
    event = json.loads(Path(os.environ["GITHUB_EVENT_PATH"]).read_text(encoding="utf-8"))
    manifest = json.loads((root / "docs-sources.json").read_text(encoding="utf-8"))
    proposed = component_proposal(event["client_payload"], manifest)
    (root / "docs-sources.json").write_text(json.dumps(proposed, indent=2) + "\n", encoding="utf-8")
