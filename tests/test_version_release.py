# SPDX-License-Identifier: MIT
# Copyright (c) 2026 Marek Cingel

"""Exercise the read-only request and the actual privileged inline publisher offline."""

from contextlib import redirect_stdout
import copy
import hashlib
import io
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch
from urllib.error import HTTPError
from urllib.parse import urlsplit, parse_qs
from urllib.request import HTTPRedirectHandler

import yaml

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools/docs"))
import version_release

NOTES = "# Changelog\n\n## [0.1.0] - 2026-01-01\n\n### Added\n\n- Verified Docs release.\n"
IDENTITY = {"repository": "OpenTLV/opentlv-docs", "sha": "a" * 40, "run_id": "123", "run_attempt": "2",
            "workflow_ref": "OpenTLV/opentlv-docs/.github/workflows/docs-release.yml@refs/heads/main"}


def environment():
    return {**{"GITHUB_" + k.upper(): v for k, v in IDENTITY.items()},
            "GITHUB_EVENT_NAME": "workflow_dispatch", "GITHUB_REF": "refs/heads/main",
            "INPUT_CHANNEL": "release", "INPUT_CORE_REF": "v0.8.0", "INPUT_TAG": "v0.1.0",
            "INPUT_PUBLISH": "true", "GH_TOKEN": "offline-test-token"}


def workflow():
    return yaml.load((ROOT / ".github/workflows/docs-release.yml").read_text(encoding="utf-8"),
                     Loader=yaml.BaseLoader)


def digest(raw):
    return hashlib.sha256(raw).hexdigest()


class RequestTests(unittest.TestCase):
    def setUp(self):
        temp = tempfile.TemporaryDirectory()
        self.addCleanup(temp.cleanup)
        self.root = Path(temp.name)
        (self.root / "CHANGELOG.md").write_text(NOTES, encoding="utf-8")
        (self.root / "docs-sources.json").write_text('{"sources": []}\n', encoding="utf-8")
        self.env = environment()

    def prepare(self):
        with patch.object(version_release.subprocess, "check_output", side_effect=[IDENTITY["sha"], ""]), \
                patch.object(version_release, "absent"):
            return version_release.prepare(self.root, self.env)

    def test_independent_docs_version_and_selected_notes(self):
        (self.root / "CHANGELOG.md").write_text(NOTES + "\n## [0.0.1] - 2025-01-01\n\n- Old.\n")
        request = self.prepare()
        self.assertEqual(request["tag"], "v0.1.0")
        self.assertEqual(request["core_ref"], "v0.8.0")
        self.assertEqual(request["identity"], IDENTITY)
        self.assertEqual(request["notes"], NOTES.removeprefix("# Changelog\n\n"))
        self.assertEqual(version_release.release_notes(NOTES.replace("## [0", "## [Unreleased]\n\n## [0"),
                                                       "v0.1.0"), request["notes"])

    def test_missing_invalid_tag_core_ref_and_wrong_branch(self):
        for key, values in {"INPUT_TAG": ["", "0.1.0", "v01.1.0", "v0.1", "v0.1.0-rc1", "v0.1.0\n", "v0.1.0/evil"],
                            "INPUT_CORE_REF": ["", "main", "c" * 40, "v0.8.0-rc1"],
                            "GITHUB_REF": ["refs/heads/feature/test", "refs/tags/v0.1.0"],
                            "INPUT_CHANNEL": ["development"]}.items():
            for value in values:
                with self.subTest(key=key, value=value), patch.dict(self.env, {key: value}):
                    with self.assertRaises(ValueError):
                        self.prepare()

    def test_missing_empty_mismatched_unreleased_and_future_notes(self):
        for text in ("# Changelog\n", NOTES.replace("0.1.0", "0.2.0"), NOTES.replace("2026-01-01", "2999-01-01"),
                     NOTES.replace("2026-01-01", "2026-02-30"), NOTES.replace("- Verified Docs release.", ""),
                     NOTES.replace("[0.1.0] - 2026-01-01", "[Unreleased]"),
                     NOTES.replace("[0.1.0]", "[v0.1.0]")):
            with self.subTest(text=text), self.assertRaises(ValueError):
                version_release.release_notes(text, "v0.1.0")
        (self.root / "CHANGELOG.md").unlink()
        with self.assertRaises(FileNotFoundError):
            self.prepare()

    def test_dispatch_never_requests_a_version_even_with_tag_payload(self):
        self.env["GITHUB_EVENT_NAME"] = "repository_dispatch"
        (self.root / "CHANGELOG.md").unlink()
        with patch.object(version_release, "absent") as remote:
            self.assertIsNone(version_release.prepare(self.root, self.env))
            remote.assert_not_called()

    def test_verification_and_development_remain_usable_without_tag(self):
        for channel in ("development", "release"):
            with patch.dict(self.env, INPUT_CHANNEL=channel, INPUT_TAG="", INPUT_PUBLISH="false",
                            GITHUB_REF="refs/heads/candidate"):
                self.assertIsNone(self.prepare())
        with patch.dict(self.env, INPUT_CHANNEL="development", INPUT_TAG=""):
            self.assertIsNone(self.prepare())
        with patch.dict(self.env, INPUT_PUBLISH="false"):
            self.assertFalse(self.prepare()["publish"])

    def test_dirty_wrong_commit_and_workflow_identity(self):
        for results in (["b" * 40], [IDENTITY["sha"], " M CHANGELOG.md"]):
            with patch.object(version_release.subprocess, "check_output", side_effect=results), \
                    self.assertRaisesRegex(ValueError, "exact clean"):
                version_release.prepare(self.root, self.env)
        for key in ("GITHUB_REPOSITORY", "GITHUB_WORKFLOW_REF", "GITHUB_RUN_ATTEMPT", "GITHUB_SHA"):
            with patch.dict(self.env, {key: "invalid"}), self.assertRaises(ValueError):
                self.prepare()

    def test_sealed_request_output_binds_notes_and_only_opts_in_when_publishing(self):
        output = self.root / "outputs"
        for publish in ("false", "true"):
            with patch.dict(os.environ, self.env | {"INPUT_PUBLISH": publish, "GITHUB_OUTPUT": str(output)}), \
                    patch.object(version_release, "ROOT", self.root), patch.object(version_release, "absent"), \
                    patch.object(version_release.subprocess, "check_output", side_effect=[IDENTITY["sha"], ""]):
                version_release.main()
            raw = (self.root / "build/version-request/request.json").read_bytes()
            self.assertEqual(json.loads(raw)["publish"], publish == "true")
            self.assertTrue(output.read_text().endswith(f"versioned={publish}\nrequest_sha256={digest(raw)}\n"))

    def test_absence_rejects_existing_tag_release_and_non404_errors(self):
        def missing(request, **kwargs):
            raise HTTPError(request.full_url, 404, "not found", {}, None)
        with patch.dict(os.environ, self.env), patch.object(version_release, "urlopen", side_effect=missing):
            version_release.absent("v0.1.0")
        for existing in ("git/ref/tags", "releases/tags"):
            def response(request, **kwargs):
                if existing in request.full_url:
                    return io.BytesIO(b'{}')
                return missing(request)
            with patch.dict(os.environ, self.env), patch.object(version_release, "urlopen", side_effect=response), \
                    self.assertRaisesRegex(ValueError, "already exists"):
                version_release.absent("v0.1.0")
        for code in (401, 403, 429, 500):
            with patch.dict(os.environ, self.env), patch.object(version_release, "urlopen",
                    side_effect=HTTPError("url", code, "failure", {}, None)), self.assertRaises(HTTPError):
                version_release.absent("v0.1.0")


class PublisherTests(unittest.TestCase):
    def setUp(self):
        temp = tempfile.TemporaryDirectory()
        self.addCleanup(temp.cleanup)
        self.root = Path(temp.name)
        old = Path.cwd()
        os.chdir(self.root)
        self.addCleanup(os.chdir, old)
        self.env = environment() | {"FULL": "success", "DEPLOY": "success", "PAGES_COMMIT": "b" * 40,
                                   "PAGE_URL": "https://opentlv.github.io/opentlv-docs/",
                                   "GITHUB_OUTPUT": str(self.root / "outputs")}
        self.request = {"schema": 1, "identity": IDENTITY.copy(), "tag": "v0.1.0", "version": "0.1.0",
                        "core_ref": "v0.8.0", "publish": True, "notes": version_release.release_notes(NOTES, "v0.1.0"),
                        "manifest_sha256": "f" * 64}
        self.candidate = self.root / "build/candidate"
        self.candidate.mkdir(parents=True)
        for name in ("site.tar", "history.bundle"):
            (self.candidate / name).write_bytes(name.encode())
        self.evidence = {"schema": 1, "identity": IDENTITY.copy(), "manifest_sha256": "f" * 64,
                         "pages_commit": "b" * 40,
                         "selection": {"repository": "OpenTLV/opentlv", "channel": "release", "version": "0.8.0",
                                       "revision": "v0.8.0", "commit": "c" * 40},
                         "files": {name: digest((self.candidate / name).read_bytes())
                                   for name in ("site.tar", "history.bundle")}}
        self.request_path = self.root / "build/version-request/request.json"
        self.request_path.parent.mkdir()
        self.save()
        step = next(s for s in workflow()["jobs"]["version"]["steps"] if s.get("id") == "publish")
        self.code = compile(step["run"].split("python - <<'PY'\n", 1)[1].rsplit("\nPY", 1)[0],
                            "docs-release.yml:publisher", "exec")
        self.calls = []
        self.tag_exists = False
        self.release_exists = False
        self.drafts = []
        self.fail = None
        self.bad_asset = False
        self.digest_mode = "present"
        self.uploaded = {}
        self.download_change = None
        self.asset_id = None
        self.check_redirect = False

    def save(self):
        for path, data, key in ((self.request_path, self.request, "REQUEST_SHA256"),
                                (self.candidate / "evidence.json", self.evidence, "EVIDENCE_SHA256")):
            raw = json.dumps(data).encode()
            path.write_bytes(raw)
            self.env[key] = digest(raw)

    def api(self, request, **kwargs):
        parts = urlsplit(request.full_url)
        path = parts.path.removeprefix("/repos/OpenTLV/opentlv-docs/")
        method = request.get_method()
        self.calls.append((method, path, request.data))
        if path == self.fail:
            raise HTTPError(request.full_url, 500, "simulated failure", {}, None)
        if method == "GET" and path.startswith("git/ref/"):
            if not self.tag_exists:
                raise HTTPError(request.full_url, 404, "not found", {}, None)
            result = {"object": {"sha": IDENTITY["sha"]}}
        elif method == "GET" and path.startswith("releases/tags/"):
            if not self.release_exists:
                raise HTTPError(request.full_url, 404, "not found", {}, None)
            result = {"tag_name": "v0.1.0"}
        elif method == "GET" and path == "releases":
            page = int(parse_qs(parts.query)["page"][0])
            result = self.drafts[(page - 1) * 100:page * 100]
        elif method == "POST" and path == "git/refs":
            self.assertEqual(json.loads(request.data), {"ref": "refs/tags/v0.1.0", "sha": IDENTITY["sha"]})
            self.tag_exists = True
            result = {"object": {"sha": IDENTITY["sha"]}}
        elif method == "POST" and path == "releases":
            self.assertEqual(json.loads(request.data), {"tag_name": "v0.1.0", "target_commitish": IDENTITY["sha"],
                             "name": "OpenTLV Docs v0.1.0", "body": self.request["notes"], "draft": True,
                             "prerelease": False})
            result = {"id": 17, "tag_name": "v0.1.0", "draft": True}
        elif method == "POST" and path == "releases/17/assets":
            self.assertEqual(parts.netloc, "uploads.github.com")
            asset_id = len(self.uploaded) + 1 if self.asset_id is None else self.asset_id
            self.uploaded[asset_id] = request.data
            result = {"id": asset_id, "state": "uploaded", "name": parse_qs(parts.query)["name"][0], "size": len(request.data),
                      "digest": "sha256:" + ("0" * 64 if self.bad_asset else digest(request.data))}
            if self.digest_mode == "missing":
                del result["digest"]
            elif self.digest_mode == "null":
                result["digest"] = None
            elif self.digest_mode == "malformed":
                result["digest"] = ""
        elif method == "GET" and path.startswith("releases/assets/"):
            self.assertEqual(parts.netloc, "api.github.com")
            self.assertEqual(request.get_header("Accept"), "application/octet-stream")
            self.assertEqual(request.get_header("Authorization"), "Bearer offline-test-token")
            if self.check_redirect:
                redirected = HTTPRedirectHandler().redirect_request(
                    request, None, 302, "Found", {}, "https://release-assets.githubusercontent.com/signed-file")
                self.assertIsNone(redirected.get_header("Authorization"))
                self.assertEqual(redirected.get_header("Accept"), "application/octet-stream")
            raw = self.uploaded[int(path.rsplit("/", 1)[1])]
            if self.download_change == "modified":
                raw = bytes([raw[0] ^ 1]) + raw[1:]
            elif self.download_change == "short":
                raw = raw[:-1]
            elif self.download_change == "long":
                raw += b"extra"
            return io.BytesIO(raw)
        elif method == "PATCH" and path == "releases/17":
            self.release_exists = True
            result = {"id": 17, "tag_name": "v0.1.0", "draft": False}
        else:
            raise AssertionError((method, path))
        return io.BytesIO(json.dumps(result).encode())

    def publish(self):
        with patch.dict(os.environ, self.env), patch("urllib.request.urlopen", side_effect=self.api), \
                redirect_stdout(io.StringIO()):
            exec(self.code, {})

    def mutations(self):
        return [(method, path) for method, path, _ in self.calls if method != "GET"]

    def test_success_creates_exact_tag_then_draft_assets_and_publication(self):
        self.publish()
        self.assertEqual(self.mutations(), [("POST", "git/refs"), ("POST", "releases"),
                         *[("POST", "releases/17/assets")] * 4, ("PATCH", "releases/17")])
        output = self.root / "build/version-release"
        self.assertEqual({p.name for p in output.iterdir()},
                         {"release-manifest.json", "release-notes.md", "full-evidence.json", "SHA256SUMS"})
        record = json.loads((output / "release-manifest.json").read_text())
        self.assertEqual(record["identity"], IDENTITY)
        self.assertEqual(record["core"]["version"], "0.8.0")
        self.assertEqual(record["version"], "0.1.0")
        self.assertEqual(record["pages"]["commit"], "b" * 40)
        for line in (output / "SHA256SUMS").read_text().splitlines():
            sha, name = line.split("  ")
            self.assertEqual(digest((output / name).read_bytes()), sha)

    def test_failed_skipped_cancelled_gates_and_nonmanual_requests_never_tag(self):
        cases = [(key, value) for key in ("FULL", "DEPLOY") for value in ("failure", "skipped", "cancelled", "")]
        cases += [("GITHUB_EVENT_NAME", "repository_dispatch"), ("GITHUB_REF", "refs/heads/feature/test"),
                  ("INPUT_CHANNEL", "development"), ("INPUT_PUBLISH", "false"), ("INPUT_TAG", "v0.2.0"),
                  ("INPUT_CORE_REF", "v0.7.1"), ("PAGES_COMMIT", "d" * 40)]
        for key, value in cases:
            with self.subTest(key=key, value=value), patch.dict(self.env, {key: value}):
                with self.assertRaises(ValueError):
                    self.publish()
                self.assertEqual(self.mutations(), [])

    def test_stale_commit_run_attempt_manifest_and_core_selection_never_tag(self):
        original = copy.deepcopy(self.evidence)
        for key in IDENTITY:
            self.evidence = copy.deepcopy(original)
            self.evidence["identity"][key] = "wrong"
            self.save()
            with self.subTest(key=key), self.assertRaises(ValueError):
                self.publish()
        self.evidence = copy.deepcopy(original)
        self.evidence["manifest_sha256"] = "0" * 64
        self.save()
        with self.assertRaises(ValueError):
            self.publish()
        for key, value in (("channel", "development"), ("revision", "v0.7.1"), ("source", "cli")):
            self.evidence = copy.deepcopy(original)
            self.evidence["selection"][key] = value
            self.save()
            with self.subTest(key=key), self.assertRaises(ValueError):
                self.publish()
        self.assertEqual(self.mutations(), [])

    def test_tampered_or_missing_request_evidence_and_artifacts_never_tag(self):
        for path in (self.request_path, self.candidate / "evidence.json", self.candidate / "site.tar",
                     self.candidate / "history.bundle"):
            raw = path.read_bytes()
            path.write_bytes(b"changed")
            with self.subTest(path=path), self.assertRaises(ValueError):
                self.publish()
            path.unlink()
            with self.assertRaises(FileNotFoundError):
                self.publish()
            path.write_bytes(raw)
        self.assertEqual(self.mutations(), [])

    def test_existing_tag_rejects_publication(self):
        self.tag_exists = True
        with self.assertRaisesRegex(ValueError, "already exists"):
            self.publish()
        self.assertEqual(self.mutations(), [])

    def test_existing_release_without_tag_rejects_publication(self):
        self.release_exists = True
        with self.assertRaisesRegex(ValueError, "already exists"):
            self.publish()
        self.assertEqual(self.mutations(), [])

    def test_existing_draft_on_later_page_rejects_publication(self):
        self.drafts = [{"tag_name": "v9.9.9"}] * 100 + [{"tag_name": "v0.1.0"}]
        with self.assertRaisesRegex(ValueError, "draft already exists"):
            self.publish()
        self.assertEqual(self.mutations(), [])

    def test_api_errors_fail_closed_before_tag_creation(self):
        self.fail = "git/ref/tags/v0.1.0"
        with self.assertRaises(HTTPError):
            self.publish()
        self.assertEqual(self.mutations(), [])

    def test_partial_failure_preserves_tag_and_recovery_record_without_deletion(self):
        self.fail = "releases"
        # Fail release creation, not the prior draft inventory GET.
        original = self.api
        def fail_create(request, **kwargs):
            if request.get_method() == "GET":
                with patch.object(self, "fail", None):
                    return original(request, **kwargs)
            return original(request, **kwargs)
        with patch.object(self, "api", side_effect=fail_create), self.assertRaises(HTTPError):
            self.publish()
        self.assertTrue(self.tag_exists)
        self.assertFalse(self.release_exists)
        self.assertEqual(self.mutations(), [("POST", "git/refs"), ("POST", "releases")])
        self.assertTrue((self.root / "build/version-release/release-manifest.json").is_file())
        self.assertIn("record_ready=true", (self.root / "outputs").read_text())

    def test_wrong_uploaded_bytes_leave_draft_unpublished(self):
        self.bad_asset = True
        with self.assertRaisesRegex(ValueError, "asset digest mismatch"):
            self.publish()
        self.assertTrue(self.tag_exists)
        self.assertNotIn(("PATCH", "releases/17"), self.mutations())
        self.assertFalse(any(path.startswith("releases/assets/") for _, path, _ in self.calls))

    def verify_download_fallback(self):
        self.publish()
        downloads = [(method, path) for method, path, _ in self.calls if path.startswith("releases/assets/")]
        self.assertEqual(downloads, [("GET", f"releases/assets/{i}") for i in range(1, 5)])
        self.assertEqual(self.mutations()[-1], ("PATCH", "releases/17"))
        self.assertTrue(self.release_exists)

    def test_missing_digest_verifies_downloaded_bytes_before_publication(self):
        self.digest_mode = "missing"
        self.verify_download_fallback()

    def test_null_digest_verifies_downloaded_bytes_before_publication(self):
        self.digest_mode = "null"
        self.verify_download_fallback()

    def test_download_redirect_does_not_forward_write_token(self):
        self.digest_mode = "null"
        self.check_redirect = True
        self.verify_download_fallback()

    def test_modified_download_blocks_publication(self):
        self.digest_mode = "null"
        self.download_change = "modified"
        with self.assertRaisesRegex(ValueError, "Downloaded release asset mismatch"):
            self.publish()
        self.assertNotIn(("PATCH", "releases/17"), self.mutations())

    def test_truncated_download_blocks_publication(self):
        self.digest_mode = "missing"
        self.download_change = "short"
        with self.assertRaisesRegex(ValueError, "Downloaded release asset mismatch"):
            self.publish()
        self.assertNotIn(("PATCH", "releases/17"), self.mutations())

    def test_oversized_download_blocks_publication(self):
        self.digest_mode = "null"
        self.download_change = "long"
        with self.assertRaisesRegex(ValueError, "Downloaded release asset mismatch"):
            self.publish()
        self.assertNotIn(("PATCH", "releases/17"), self.mutations())

    def test_failed_asset_download_leaves_draft_for_recovery(self):
        self.digest_mode = "missing"
        self.fail = "releases/assets/1"
        with self.assertRaises(HTTPError):
            self.publish()
        self.assertNotIn(("PATCH", "releases/17"), self.mutations())
        self.assertTrue((self.root / "build/version-release/release-manifest.json").is_file())

    def test_invalid_asset_id_cannot_select_a_download_endpoint(self):
        self.digest_mode = "null"
        self.asset_id = "../other"
        with self.assertRaisesRegex(ValueError, "Invalid uploaded release asset ID"):
            self.publish()
        self.assertFalse(any(path.startswith("releases/assets/") for _, path, _ in self.calls))
        self.assertNotIn(("PATCH", "releases/17"), self.mutations())

    def test_malformed_reported_digest_is_not_treated_as_missing(self):
        self.digest_mode = "malformed"
        with self.assertRaisesRegex(ValueError, "asset digest mismatch"):
            self.publish()
        self.assertFalse(any(path.startswith("releases/assets/") for _, path, _ in self.calls))
        self.assertNotIn(("PATCH", "releases/17"), self.mutations())

    def test_tag_creation_race_cannot_fall_through_to_release_creation(self):
        original = self.api
        def race(request, **kwargs):
            if request.get_method() == "POST" and request.full_url.endswith("/git/refs"):
                raise HTTPError(request.full_url, 422, "reference already exists", {}, None)
            return original(request, **kwargs)
        with patch.object(self, "api", side_effect=race), self.assertRaises(HTTPError):
            self.publish()
        self.assertEqual(self.mutations(), [])
        self.assertFalse(self.release_exists)


class GateTests(unittest.TestCase):
    @unittest.skipIf(os.name == "nt", "Execute the runner's shell gate on Linux")
    def test_gate_requires_version_only_for_explicit_version_publication(self):
        gate = workflow()["jobs"]["gate"]["steps"][0]["run"]
        baseline = {"REQUEST": "success", "FULL": "success", "DEPLOY": "success", "VERSION": "success",
                    "PUBLISH": "true", "MAIN": "true", "VERSIONED": "true"}
        cases = [(baseline, True), (baseline | {"VERSIONED": "false", "VERSION": "skipped"}, True),
                 (baseline | {"VERSIONED": "false", "VERSION": "skipped", "DEPLOY": "skipped",
                              "PUBLISH": "false", "MAIN": "false"}, True)]
        cases += [(baseline | {key: value}, False) for key in ("REQUEST", "FULL", "DEPLOY", "VERSION")
                  for value in ("failure", "cancelled", "skipped")]
        cases += [(baseline | {"MAIN": "false"}, False),
                  (baseline | {"VERSIONED": "false"}, False)]
        for env, success in cases:
            with self.subTest(env=env):
                result = subprocess.run(["bash", "-e", "-c", gate], env=os.environ | env, capture_output=True)
                self.assertEqual(result.returncode == 0, success, result.stderr)

    def test_dependencies_permissions_and_attempt_artifacts_preserve_boundary(self):
        data = workflow()
        jobs = data["jobs"]
        self.assertEqual(jobs["full"]["needs"], ["request"])
        self.assertEqual(jobs["version"]["needs"], ["request", "full", "deploy"])
        self.assertEqual(jobs["gate"]["needs"], ["request", "full", "deploy", "version"])
        self.assertEqual(data["permissions"]["contents"], "read")
        self.assertEqual(jobs["version"]["permissions"], {"contents": "write"})
        self.assertNotIn("required", data["on"]["workflow_dispatch"]["inputs"]["tag"])
        condition = jobs["version"]["if"]
        for requirement in ("github.event_name == 'workflow_dispatch'", "github.ref == 'refs/heads/main'",
                            "inputs.channel == 'release'", "inputs.publish", "needs.full.result == 'success'",
                            "needs.deploy.result == 'success'", "needs.request.outputs.versioned == 'true'"):
            self.assertIn(requirement, condition)
        for step in jobs["version"]["steps"]:
            self.assertNotIn("checkout", step.get("uses", ""))
            self.assertNotIn("tools/docs/", step.get("run", ""))
            if "download-artifact" in step.get("uses", ""):
                self.assertTrue(step["with"]["name"].endswith("-${{ github.run_attempt }}"))


if __name__ == "__main__":
    unittest.main()
