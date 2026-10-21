# SPDX-License-Identifier: MIT
# Copyright (c) 2026 Marek Cingel

"""Bind a prepared documentation snapshot to this exact Full CI run and attempt."""

import argparse
import hashlib
import json
import os
from pathlib import Path, PurePosixPath
import re
import tarfile

import publication

ROOT = Path(__file__).resolve().parents[2]
SHA = re.compile(r"[0-9a-f]{40}\Z")


def digest(path):
    value = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            value.update(chunk)
    return value.hexdigest()


def identity():
    result = {key: os.environ["GITHUB_" + key.upper()]
              for key in ("repository", "sha", "run_id", "run_attempt", "workflow_ref")}
    if (result["repository"] != "OpenTLV/opentlv-docs" or not SHA.fullmatch(result["sha"])
            or any(not result[key].isdigit() or int(result[key]) < 1 for key in ("run_id", "run_attempt"))):
        raise ValueError("Invalid documentation workflow identity")
    return result


def snapshots(portal, ref):
    """Record all published namespaces, including components removed from configuration."""
    trees = {}
    files = publication.run(portal, "git", "ls-tree", "-r", "--name-only", ref).splitlines()
    for catalog in files:
        if not re.fullmatch(r"(?:[a-z][a-z0-9_]*/)?versions\.json", catalog):
            continue
        prefix = catalog.removesuffix("versions.json")
        versions = json.loads(publication.run(portal, "git", "show", f"{ref}:{catalog}"))
        for item in versions:
            version = item["version"]
            if version == "latest" and not prefix:
                continue
            if not re.fullmatch(r"[0-9]+\.[0-9]+\.[0-9]+(?:-[0-9A-Za-z.-]+)?", version):
                raise ValueError("Invalid immutable snapshot version")
            path = prefix + version
            trees[path] = publication.run(portal, "git", "rev-parse", f"{ref}:{path}")
    return trees


def baseline(portal):
    remote = publication.run(portal, "git", "ls-remote", "--heads", "origin", "refs/heads/gh-pages")
    result = {"commit": None, "snapshots": {}}
    if remote:
        publication.run(portal, "git", "fetch", "origin", "refs/heads/gh-pages")
        result = {"commit": publication.run(portal, "git", "rev-parse", "FETCH_HEAD"),
                  "snapshots": snapshots(portal, "FETCH_HEAD")}
    target = portal / "build/history-baseline.json"
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")


def pack(portal):
    output = portal / "build/publication"
    execution = identity()
    if (publication.run(portal, "git", "rev-parse", "HEAD") != execution["sha"]
            or publication.run(portal, "git", "status", "--porcelain", "--untracked-files=all")):
        raise ValueError("Full CI requires the exact clean documentation infrastructure commit")
    selected = json.loads((portal / "build/selection.json").read_text(encoding="utf-8"))
    previous = json.loads((portal / "build/history-baseline.json").read_text(encoding="utf-8"))
    current = snapshots(portal, "gh-pages")
    if any(current.get(path) != tree for path, tree in previous["snapshots"].items()):
        raise ValueError("Publication changed an immutable historical snapshot")
    if previous["commit"]:
        publication.run(portal, "git", "merge-base", "--is-ancestor", previous["commit"], "gh-pages")
    pages_commit = publication.run(portal, "git", "rev-parse", "gh-pages")
    # Archive only regular contained site files. No executable archive entries.
    with tarfile.open(output / "site.tar", "w") as archive:
        for path in sorted((output / "site").rglob("*")):
            if path.is_symlink() or not path.resolve().is_relative_to((output / "site").resolve()):
                raise ValueError("Publication contains an unsafe file")
            if path.is_file():
                archive.add(path, arcname=path.relative_to(output / "site").as_posix(), recursive=False)
    evidence = {"schema": 1, "identity": execution, "selection": selected,
                "manifest_sha256": digest(portal / "docs-sources.json"),
                "pages_commit": pages_commit, "previous": previous, "snapshots": current,
                "files": {name: digest(output / name) for name in ("site.tar", "history.bundle")}}
    path = output / "evidence.json"
    path.write_text(json.dumps(evidence, indent=2) + "\n", encoding="utf-8")
    return evidence


def verify(portal, directory, *, extract=True):
    evidence = json.loads((directory / "evidence.json").read_text(encoding="utf-8"))
    if (evidence.get("schema") != 1 or evidence.get("identity") != identity()
            or evidence.get("manifest_sha256") != digest(portal / "docs-sources.json")
            or not SHA.fullmatch(str(evidence.get("pages_commit", "")))):
        raise ValueError("Full CI evidence differs from this repository, commit, run, attempt or manifest")
    if evidence.get("files") != {name: digest(directory / name) for name in ("site.tar", "history.bundle")}:
        raise ValueError("Prepared publication checksum mismatch")
    publication.run(portal, "git", "bundle", "verify", str(directory / "history.bundle"))
    refs = publication.run(portal, "git", "bundle", "list-heads", str(directory / "history.bundle"))
    if refs != evidence["pages_commit"] + " refs/heads/gh-pages":
        raise ValueError("History bundle differs from verified Pages commit")
    # Verify the bundle's immutable trees independently in the gate checkout.
    publication.run(portal, "git", "fetch", str(directory / "history.bundle"),
                    "refs/heads/gh-pages:refs/heads/gh-pages")
    current = snapshots(portal, "gh-pages")
    if (current != evidence["snapshots"]
            or any(current.get(path) != tree for path, tree in evidence["previous"]["snapshots"].items())):
        raise ValueError("Immutable snapshot evidence differs from prepared history")
    if evidence["previous"]["commit"]:
        publication.run(portal, "git", "merge-base", "--is-ancestor",
                        evidence["previous"]["commit"], "gh-pages")
    site = directory / "site"
    if extract:
        site.mkdir(exist_ok=False)
        with tarfile.open(directory / "site.tar") as archive:
            names = set()
            for entry in archive.getmembers():
                path = PurePosixPath(entry.name)
                if (not entry.isfile() or path.is_absolute() or ".." in path.parts
                        or path.as_posix() != entry.name
                        or "\\" in entry.name or ":" in entry.name or entry.name in names
                        or not (site / entry.name).resolve().is_relative_to(site.resolve())):
                    raise ValueError("Unsafe or duplicate publication archive entry")
                names.add(entry.name)
            # The Pages site must be the exact tree stored in the history bundle.
            records = publication.run(portal, "git", "ls-tree", "-r", "-z", "gh-pages").split("\0")
            tracked = {}
            for record in filter(None, records):
                metadata, name = record.split("\t", 1)
                mode, kind, oid = metadata.split()
                if kind != "blob" or mode not in ("100644", "100755"):
                    raise ValueError("History contains an unsupported file")
                tracked[name] = oid
            if set(tracked) != names:
                raise ValueError("Pages archive file set differs from history")
            for entry in archive.getmembers():
                raw = archive.extractfile(entry).read()
                oid = hashlib.sha1(b"blob " + str(len(raw)).encode("ascii") + b"\0" + raw).hexdigest()
                if oid != tracked[entry.name]:
                    raise ValueError("Pages archive bytes differ from history")
            # All entries were checked before extracting any bytes.
            for entry in archive.getmembers():
                target = site / entry.name
                target.parent.mkdir(parents=True, exist_ok=True)
                target.write_bytes(archive.extractfile(entry).read())
    selected = evidence["selection"]
    if selected.get("source") not in (None, "core"):
        import component_publication
        if not re.fullmatch(r"[a-z][a-z0-9_]*", selected["source"]):
            raise ValueError("Invalid component publication namespace")
        component_publication.verify_site(site / selected["source"] / selected["version"], selected)
    else:
        publication.verify_site(site / selected["version"], selected)
    return evidence


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("command", choices=("baseline", "pack", "verify"))
    parser.add_argument("--directory", type=Path, default=ROOT / "build/candidate")
    args = parser.parse_args()
    if args.command == "baseline":
        baseline(ROOT)
    elif args.command == "pack":
        pack(ROOT)
    else:
        evidence = verify(ROOT, args.directory)
        if os.environ.get("GITHUB_OUTPUT"):
            with open(os.environ["GITHUB_OUTPUT"], "a", encoding="utf-8") as output:
                output.write(f"pages_commit={evidence['pages_commit']}\n")
                output.write(f"evidence_sha256={digest(args.directory / 'evidence.json')}\n")


if __name__ == "__main__":
    main()
