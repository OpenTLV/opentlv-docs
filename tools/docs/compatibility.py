# SPDX-License-Identifier: MIT
# Copyright (c) 2026 Marek Cingel

"""Import immutable external compatibility results; never execute their tests."""

from copy import deepcopy
import hashlib
import json
import os
from pathlib import Path, PurePosixPath
import re
import tempfile
from urllib.error import URLError
from urllib.parse import urlsplit
from urllib.request import build_opener, HTTPRedirectHandler

from mkdocs.exceptions import PluginError

OUTCOMES = ("passed", "failed", "untested")
IDENTIFIER = re.compile(r"[a-z][a-z0-9]*(?:[._-][a-z0-9]+)*\Z")
SEMVER = re.compile(
    r"v?(0|[1-9][0-9]*)\.(0|[1-9][0-9]*)\.(0|[1-9][0-9]*)"
    r"(?:-([0-9A-Za-z-]+(?:\.[0-9A-Za-z-]+)*))?"
    r"(?:\+([0-9A-Za-z-]+(?:\.[0-9A-Za-z-]+)*))?\Z"
)
MAX_BYTES = 16 * 1024 * 1024


def fail(message):
    raise PluginError("Compatibility results: " + message)


def _plain(value, label):
    if not isinstance(value, str) or not value.strip() or any(ord(c) < 32 or ord(c) == 127 for c in value):
        fail(f"{label} must be nonempty single-line text")
    return value


def _object(value, fields, label):
    if not isinstance(value, dict) or set(value) != set(fields):
        fail(f"{label} requires exactly {', '.join(sorted(fields))}")


def _url(value, label, repository=False):
    _plain(value, label)
    try:
        url = urlsplit(value)
        port = url.port
    except ValueError:
        fail(f"invalid {label} URL")
    if (any(c.isspace() for c in value) or "\\" in value or url.username is not None
            or url.password is not None or (url.scheme != "https" and not (repository and url.scheme == "file"))
            or (url.scheme == "https" and (not url.hostname or port == 0))
            or (repository and (not url.path or url.query or url.fragment))):
        fail(f"{label} must be a credential-free {'HTTPS or file' if repository else 'HTTPS'} URL")
    return value


def _relative(value, label):
    _plain(value, label)
    if ("\\" in value or ":" in value or PurePosixPath(value).is_absolute()
            or any(p in ("", ".", "..") for p in value.split("/"))):
        fail(f"{label} must be a contained POSIX relative path")
    return value


def _commit(value):
    if not isinstance(value, str) or not re.fullmatch(r"[0-9a-f]{40}", value):
        fail("commit must be a full lowercase SHA")
    return value


def _version(value):
    match = SEMVER.fullmatch(value) if isinstance(value, str) else None
    if not match or (match[4] and any(x.isdigit() and len(x) > 1 and x.startswith("0")
                                    for x in match[4].split("."))):
        fail("component version must be a semantic version (optional v prefix)")
    return tuple(int(match[i]) for i in (1, 2, 3)), match[4]


def validate_settings(value):
    """Validate an opt-in source's pinned feed and requested verification scope."""
    _object(value, ("feed", "sha256", "platform", "configuration"), "settings")
    feed = _plain(value["feed"], "feed")
    if feed.startswith("https:"):
        _url(feed, "feed")
    else:
        _relative(feed, "feed")
    if not isinstance(value["sha256"], str) or not re.fullmatch(r"[0-9a-f]{64}", value["sha256"]):
        fail("sha256 must be a full lowercase digest of the feed bytes")
    _plain(value["platform"], "platform")
    _plain(value["configuration"], "configuration")
    return value


def validate_feed(data):
    """Validate release/development evidence without treating branch labels as releases."""
    _object(data, ("version", "records"), "feed")
    if type(data["version"]) is not int or data["version"] not in (1, 2) or not isinstance(data["records"], list):
        fail("feed requires version 1 or 2 and a records list")
    ids, scopes, releases, core_versions = set(), set(), {}, {}
    for record in data["records"]:
        fields = ("id", "component", "declared_core", "core", "platform", "configuration",
                  "build", "test", "evidence", "features")
        _object(record, fields + (("channel",) if data["version"] == 2 else ()), "record")
        channel = record.get("channel", "release")
        if channel not in ("release", "development"):
            fail("record channel must be release or development")
        identifier = _plain(record["id"], "record id")
        if identifier in ids:
            fail(f"duplicate record id: {identifier}")
        ids.add(identifier)
        for kind in ("component", "core"):
            identity = record[kind]
            _object(identity, ("repository", "version", "commit"), kind)
            _url(identity["repository"], f"{kind} repository", repository=True)
            _plain(identity["version"], f"{kind} version")
            _commit(identity["commit"])
        component, core = record["component"], record["core"]
        if channel == "release":
            version, prerelease = _version(component["version"])
            # Prefixes and build metadata do not distinguish release precedence.
            release_key = (component["repository"], version, prerelease)
            if release_key in releases and releases[release_key] != component["commit"]:
                fail("contradictory component version commits")
            releases[release_key] = component["commit"]
            core_key = (core["repository"], core["version"])
            if core_key in core_versions and core_versions[core_key] != core["commit"]:
                fail("contradictory Core version commits")
            core_versions[core_key] = core["commit"]
        # Development labels may repeat across commits. Only the exact component
        # and Core SHAs identify their immutable verification scope.
        for field in ("declared_core", "platform", "configuration"):
            _plain(record[field], field)
        for field in ("build", "test"):
            if record[field] not in OUTCOMES:
                fail(f"{field} must be passed, failed or untested")
        if record["test"] == "passed" and record["build"] != "passed":
            fail("passed tests require a passed build")
        _url(record["evidence"], "evidence")
        scope = (component["repository"], component["commit"], core["repository"], core["commit"],
                 record["platform"], record["configuration"])
        if scope in scopes:
            fail("duplicate or contradictory verification scope; publish one immutable record per exact pair and scope")
        scopes.add(scope)
        if not isinstance(record["features"], list):
            fail("features must be a list")
        features = set()
        for feature in record["features"]:
            _object(feature, ("id", "support", "examples"), "feature")
            name = feature["id"]
            if not isinstance(name, str) or not IDENTIFIER.fullmatch(name) or name in features:
                fail("invalid or duplicate feature id")
            features.add(name)
            if feature["support"] not in ("supported", "unsupported", "unknown"):
                fail("feature support must be supported, unsupported or unknown")
            if not isinstance(feature["examples"], list):
                fail("feature examples must be a list")
            examples = set()
            for example in feature["examples"]:
                _object(example, ("language", "path", "result"), "example")
                language = example["language"]
                if not isinstance(language, str) or not IDENTIFIER.fullmatch(language):
                    fail("invalid example language identifier")
                _relative(example["path"], "example path")
                if example["result"] not in OUTCOMES:
                    fail("example result must be passed, failed or untested")
                if example["result"] == "passed" and feature["support"] != "supported":
                    fail("passed examples require supported features")
                if language in examples:
                    fail("duplicate example language within feature")
                examples.add(language)
    return data


class _HTTPSRedirect(HTTPRedirectHandler):
    def redirect_request(self, request, response, code, message, headers, newurl):
        _url(newurl, "feed redirect")
        return super().redirect_request(request, response, code, message, headers, newurl)


def _download(source):
    with build_opener(_HTTPSRedirect()).open(source, timeout=30) as response:
        return response.read(MAX_BYTES + 1)


def _contained(portal, name):
    path = portal / name
    if (not path.resolve().is_relative_to(portal)
            or any(p.is_symlink() for p in (path, *path.parents) if p.is_relative_to(portal))):
        fail("feed files and cache must stay inside the portal without symlinks")
    return path


def _unique_object(pairs):
    result = {}
    for key, value in pairs:
        if key in result:
            fail(f"duplicate JSON object key: {key}")
        result[key] = value
    return result


def load(portal, settings, allow_download=False):
    """Read verified bytes; remote retrieval is restricted to explicit preparation."""
    validate_settings(settings)
    portal = Path(portal).resolve()
    remote = settings["feed"].startswith("https:")
    path = _contained(portal, f"build/compatibility/{settings['sha256']}.json" if remote else settings["feed"])
    downloaded = False
    try:
        if remote and not path.exists():
            if not allow_download:
                fail("pinned feed cache is missing; fetch sources before building")
            raw = _download(settings["feed"])
            downloaded = True
        else:
            with path.open("rb") as stream:
                raw = stream.read(MAX_BYTES + 1)
    except (OSError, URLError, ValueError) as error:
        fail(f"cannot read feed: {error}")
    if len(raw) > MAX_BYTES:
        fail("feed exceeds the 16 MiB limit")
    if hashlib.sha256(raw).hexdigest() != settings["sha256"]:
        fail("feed sha256 does not match the pinned digest")
    try:
        feed = validate_feed(json.loads(raw.decode("utf-8"), object_pairs_hook=_unique_object))
    except (ValueError, UnicodeError) as error:
        fail(f"feed is not valid UTF-8 JSON: {error}")
    if downloaded:
        temporary = None
        try:
            path.parent.mkdir(parents=True, exist_ok=True)
            _contained(portal, path.relative_to(portal))
            with tempfile.NamedTemporaryFile(dir=path.parent, delete=False) as stream:
                temporary = Path(stream.name)
                stream.write(raw)
            os.replace(temporary, path)
        except OSError as error:
            fail(f"cannot cache verified feed: {error}")
        finally:
            if temporary is not None and temporary.exists():
                temporary.unlink()
    return feed


def select(feed, settings, component_repository, core_repository, core_commit, *,
           channel="release", component_commit=None):
    """Choose a stable release, or evidence for an explicitly pinned development pair."""
    validate_settings(settings)
    validate_feed(feed)
    _url(component_repository, "component repository", repository=True)
    _url(core_repository, "Core repository", repository=True)
    _commit(core_commit)
    if channel not in ("release", "development"):
        fail("selection channel must be release or development")
    if component_commit is not None:
        _commit(component_commit)
    development = channel == "development" and component_commit is not None
    candidates = [record for record in feed["records"]
                  if record["component"]["repository"] == component_repository
                  and record["core"]["repository"] == core_repository
                  and record["core"]["commit"] == core_commit
                  and record["platform"] == settings["platform"]
                  and record["configuration"] == settings["configuration"]
                  and (component_commit is None or record["component"]["commit"] == component_commit)
                  and ((development and record.get("channel") == "development")
                       or (record.get("channel", "release") == "release"
                           and _version(record["component"]["version"])[1] is None))]
    passed = [record for record in candidates if record["build"] == record["test"] == "passed"]
    record = max(passed or candidates,
                 key=lambda r: (r["id"] if development else
                                (_version(r["component"]["version"])[0], r["component"]["version"], r["id"])),
                 default=None)
    status = ("verified" if passed else "missing" if record is None else
              "failed" if "failed" in (record["build"], record["test"]) else "untested")
    selection = {"status": status, "feed": {"source": settings["feed"], "sha256": settings["sha256"]},
                 "core": {"repository": core_repository, "commit": core_commit,
                          "version": record["core"]["version"] if record else None},
                 "platform": settings["platform"], "configuration": settings["configuration"],
                 "record": deepcopy(record)}
    if feed["version"] == 2:
        selection["schema_version"] = 2
    return selection
