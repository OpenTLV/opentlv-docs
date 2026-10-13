# SPDX-License-Identifier: MIT
# Copyright (c) 2026 Marek Cingel

"""Read bounded compatibility evidence from an already authenticated workflow run."""

import hashlib
import io
import os
import re
import stat
from urllib.error import URLError
from urllib.parse import urlsplit
from urllib.request import HTTPRedirectHandler, Request, build_opener
import zipfile
import zlib

MAX_FEED_BYTES = 16 * 1024 * 1024
MAX_ARCHIVE_BYTES = MAX_FEED_BYTES + 64 * 1024
MAX_ARTIFACTS = 10000


class _ArtifactRedirect(HTTPRedirectHandler):
    """Signed storage downloads never receive the GitHub API credential."""

    def redirect_request(self, request, response, code, message, headers, newurl):
        target = urlsplit(newurl)
        if (target.scheme != "https" or not target.hostname
                or target.username is not None or target.password is not None):
            raise ValueError("Artifact download redirects require an HTTPS URL without credentials.")
        redirected = super().redirect_request(request, response, code, message, headers, newurl)
        if redirected is not None:
            # No redirect needs the API token: the storage URL is already signed.
            redirected.remove_header("Authorization")
            redirected.remove_header("Proxy-authorization")
            redirected.remove_header("Cookie")
        return redirected


def _download(path):
    headers = {"Accept": "application/vnd.github+json", "X-GitHub-Api-Version": "2022-11-28"}
    request = Request("https://api.github.com/repos/" + path, headers=headers)
    token = os.environ.get("GH_TOKEN")
    if token:
        request.add_unredirected_header("Authorization", "Bearer " + token)
    try:
        with build_opener(_ArtifactRedirect()).open(request, timeout=30) as response:
            length = response.headers.get("Content-Length")
            if length is not None and (not length.isdecimal() or int(length) > MAX_ARCHIVE_BYTES):
                raise ValueError("Artifact download exceeds the archive size limit.")
            raw = response.read(MAX_ARCHIVE_BYTES + 1)
    except (URLError, OSError):
        # Do not include the signed storage URL in workflow logs.
        raise ValueError("Could not download the compatibility artifact.") from None
    if len(raw) > MAX_ARCHIVE_BYTES:
        raise ValueError("Artifact download exceeds the archive size limit.")
    return raw


def _artifact(payload, item, api):
    repo = payload["repository"]
    if (not isinstance(repo, str) or not re.fullmatch(r"[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+", repo)
            or item.get("repository") != "https://github.com/" + repo
            or item.get("id") == "core" or payload.get("ref") != "main"
            or type(payload.get("run_id")) is not int or payload["run_id"] <= 0):
        raise ValueError("Development artifacts require a configured component main workflow run.")
    name = item.get("updates", {}).get("development_artifact")
    if not isinstance(name, str) or not name or len(name) > 256:
        raise ValueError("Component updates require a configured development artifact name.")
    found = []
    total = None
    seen = 0
    page = 1
    while total is None or seen < total:
        result = api(f"{repo}/actions/runs/{payload['run_id']}/artifacts?per_page=100&page={page}")
        count = result.get("total_count") if isinstance(result, dict) else None
        entries = result.get("artifacts") if isinstance(result, dict) else None
        if (type(count) is not int or not 0 <= count <= MAX_ARTIFACTS
                or not isinstance(entries, list) or len(entries) > 100
                or any(not isinstance(entry, dict) for entry in entries)
                or (total is not None and total != count)):
            raise ValueError("Workflow artifact listing is invalid or changed during pagination.")
        total = count
        seen += len(entries)
        if seen > total or (seen < total and len(entries) != 100):
            raise ValueError("Workflow artifact listing is incomplete or changed during pagination.")
        found.extend(entry for entry in entries if entry.get("name") == name)
        if len(found) > 1:
            raise ValueError("Workflow must contain exactly one configured compatibility artifact.")
        page += 1
    if len(found) != 1:
        raise ValueError("Workflow must contain exactly one configured compatibility artifact.")
    artifact = found[0]
    run = artifact.get("workflow_run")
    digest = artifact.get("digest")
    if (type(artifact.get("id")) is not int or artifact["id"] <= 0
            or artifact.get("expired") is not False
            or not isinstance(run, dict) or type(run.get("id")) is not int
            or run["id"] != payload["run_id"] or run.get("head_sha") != payload["commit"]
            or run.get("head_branch") != "main"
            or not isinstance(digest, str) or not re.fullmatch(r"sha256:[0-9a-f]{64}", digest)
            or type(artifact.get("size_in_bytes")) is not int
            or not 0 < artifact["size_in_bytes"] <= MAX_ARCHIVE_BYTES):
        raise ValueError("Compatibility artifact has expired or lacks valid run, size or digest evidence.")
    return artifact


def fetch_feed(payload, item, api, download=None):
    """Return feed bytes; callers validate the run first and the JSON schema afterwards.

    ``api`` accepts repository-relative REST paths. Optional ``download`` accepts
    the same kind of path and returns archive bytes, allowing offline validation.
    Neither archive content nor its download URL can choose executable code.
    """
    artifact = _artifact(payload, item, api)
    filename = item.get("updates", {}).get("asset", "compatibility.json")
    if (not isinstance(filename, str)
            or not re.fullmatch(r"[A-Za-z0-9_-][A-Za-z0-9_.-]*\.json", filename)):
        raise ValueError("Compatibility artifact requires a plain configured JSON filename.")
    raw = (download or _download)(f"{payload['repository']}/actions/artifacts/{artifact['id']}/zip")
    if not isinstance(raw, bytes) or len(raw) > MAX_ARCHIVE_BYTES:
        raise ValueError("Artifact download exceeds the archive size limit or is not bytes.")
    if len(raw) != artifact["size_in_bytes"]:
        raise ValueError("Compatibility artifact archive size does not match its evidence.")
    if hashlib.sha256(raw).hexdigest() != artifact["digest"].removeprefix("sha256:"):
        raise ValueError("Compatibility artifact archive SHA-256 does not match its evidence.")
    try:
        with zipfile.ZipFile(io.BytesIO(raw)) as archive:
            entries = archive.infolist()
            if len(entries) != 1:
                raise ValueError("Compatibility artifact must contain exactly one regular JSON file.")
            entry = entries[0]
            mode = stat.S_IFMT(entry.external_attr >> 16)
            if (entry.filename != filename or entry.orig_filename != filename
                    or entry.is_dir() or entry.external_attr & 0x10
                    or mode not in (0, stat.S_IFREG) or entry.flag_bits & 1
                    or entry.compress_type not in (zipfile.ZIP_STORED, zipfile.ZIP_DEFLATED)
                    or entry.file_size > MAX_FEED_BYTES):
                raise ValueError("Compatibility artifact contains an unsafe or oversized JSON file.")
            with archive.open(entry) as stream:
                feed = stream.read(MAX_FEED_BYTES + 1)
            if len(feed) > MAX_FEED_BYTES or len(feed) != entry.file_size:
                raise ValueError("Compatibility artifact JSON exceeds its declared size or size limit.")
            return feed
    except (zipfile.BadZipFile, zipfile.LargeZipFile, NotImplementedError, RuntimeError, EOFError, zlib.error):
        raise ValueError("Compatibility artifact is not a supported, intact ZIP archive.") from None
