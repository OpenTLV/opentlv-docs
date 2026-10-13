# SPDX-License-Identifier: MIT
# Copyright (c) 2026 Marek Cingel

"""Authenticate event evidence against GitHub; payloads never choose repositories or code."""

import copy
import hashlib
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


def validate(payload, definitions, api=None):
    api = api or github
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
    policy = item.get("updates", {})
    if item["id"] != "core" and ref == "main" and not policy.get("development_artifact"):
        raise ValueError("Component development updates require a configured evidence artifact.")
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


def newer(repo, previous, candidate, api=None):
    """Keep latest monotonic even when push/manual/dispatch runs arrive out of order."""
    api = api or github
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


def resolve_revision(repo, revision, api=None):
    """Resolve an existing manifest pin without trusting a moving branch."""
    api = api or github
    if isinstance(revision, str) and SHA.fullmatch(revision.lower()):
        return revision.lower()
    if not isinstance(revision, str) or not revision:
        raise ValueError("Source pin requires a tag or full commit SHA.")
    target = api(f"{repo}/git/ref/tags/{quote(revision, safe='')}")["object"]
    for _ in range(5):
        if target.get("type") == "commit" and SHA.fullmatch(target.get("sha", "")):
            return target["sha"]
        if target.get("type") != "tag" or not SHA.fullmatch(target.get("sha", "")):
            break
        target = api(f"{repo}/git/tags/{target['sha']}")["object"]
    raise ValueError("Source tag must resolve to a full commit SHA.")


def core_proposal(payload, manifest, api=None):
    """Propose a persistent main pin; a replay must not undo a merged update."""
    api = api or github
    result = copy.deepcopy(manifest)
    item = validate(payload, result["sources"], api)
    if item["id"] != "core" or payload["ref"] != "main":
        raise ValueError("Core pin proposals require a main development event.")
    repo = repository(item)
    previous = resolve_revision(repo, item["revision"], api)
    item["revision"] = newer(repo, previous, payload["commit"], api)
    return result


def component_proposal(payload, manifest, api=None, *, portal=None):
    """Prepare a reviewed update; never replace evidence from an arbitrary feed URL."""
    api = api or github
    result = copy.deepcopy(manifest)
    item = validate(payload, result["sources"], api)
    if item["id"] == "core" or "compatibility" not in item:
        raise ValueError("Component updates require compatibility-based selection.")
    if payload["ref"] == "main":
        if portal is None:
            raise ValueError("Development evidence requires a portal directory.")
        if item.get("revision") and newer(repository(item), item["revision"], payload["commit"], api) != payload["commit"]:
            return result
        import compatibility
        import event_artifacts

        raw = event_artifacts.fetch_feed(payload, item, api)
        feed = compatibility.validate_feed(json.loads(raw.decode("utf-8"), object_pairs_hook=compatibility._unique_object))
        core = next(source for source in result["sources"] if source["id"] == "core")
        settings = item["compatibility"]
        core_commit = resolve_revision(repository(core), core["revision"], api)
        verified = compatibility.select(feed, settings, item["repository"], core["repository"], core_commit,
                                        channel="development", component_commit=payload["commit"])
        if verified["status"] != "verified":
            raise ValueError("Development evidence must verify the exact pinned Core/component pair and scope.")
        digest = hashlib.sha256(raw).hexdigest()
        name = f"compatibility/{item['id']}/{digest}.json"
        path = compatibility._contained(Path(portal).resolve(), name)
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(raw)
        settings.update(feed=name, sha256=digest)
        item["revision"] = payload["commit"]
        return result
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
    item["revision"] = payload["commit"]
    return result


if __name__ == "__main__":
    root = Path(__file__).resolve().parents[2]
    event = json.loads(Path(os.environ["GITHUB_EVENT_PATH"]).read_text(encoding="utf-8"))
    manifest = json.loads((root / "docs-sources.json").read_text(encoding="utf-8"))
    payload = event["client_payload"]
    # Source configuration is reviewed repository data, never supplied by events.
    import sources
    sources.manifest(root)
    proposed = (core_proposal(payload, manifest) if payload.get("source") == "core"
                else component_proposal(payload, manifest, portal=root))
    (root / "docs-sources.json").write_text(json.dumps(proposed, indent=2) + "\n", encoding="utf-8")
