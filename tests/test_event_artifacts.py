# SPDX-License-Identifier: MIT
# Copyright (c) 2026 Marek Cingel

import copy
from email.message import Message
import hashlib
import io
import os
from pathlib import Path
import stat
import sys
import unittest
from unittest.mock import Mock, patch
from urllib.request import HTTPSHandler, build_opener
from urllib.response import addinfourl
import warnings
import zipfile

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "tools/docs"))
import event_artifacts


def zip_bytes(entries):
    result = io.BytesIO()
    with warnings.catch_warnings():
        warnings.simplefilter("ignore", UserWarning)
        with zipfile.ZipFile(result, "w", compression=zipfile.ZIP_DEFLATED) as archive:
            for name, data in entries:
                archive.writestr(name, data)
    return result.getvalue()


class ArtifactTests(unittest.TestCase):
    def setUp(self):
        self.payload = {"source": "python", "repository": "OpenTLV/opentlv-python",
                        "commit": "a" * 40, "ref": "main", "run_id": 123}
        self.item = {"id": "python", "repository": "https://github.com/OpenTLV/opentlv-python",
                     "updates": {"workflow": ".github/workflows/compatibility.yml",
                                 "asset": "compatibility.json", "development_artifact": "compatibility"}}
        self.feed = b'{"schema_version": 1}\n'
        self.raw = zip_bytes([("compatibility.json", self.feed)])
        self.metadata = {"id": 42, "name": "compatibility", "expired": False,
                         "workflow_run": {"id": 123, "head_sha": "a" * 40, "head_branch": "main"}}
        self.evidence(self.raw)
        self.api = Mock(side_effect=lambda _: {"total_count": 1, "artifacts": [self.metadata]})
        self.download = Mock(side_effect=lambda _: self.raw)

    def evidence(self, raw):
        self.raw = raw
        self.metadata.update(size_in_bytes=len(raw), digest="sha256:" + hashlib.sha256(raw).hexdigest())

    def fetch(self):
        return event_artifacts.fetch_feed(self.payload, self.item, self.api, self.download)

    def test_verified_feed_and_fixed_api_paths(self):
        # URL fields in metadata are deliberately not used for fetching.
        self.metadata["archive_download_url"] = "https://attacker.invalid/zip"
        self.assertEqual(self.fetch(), self.feed)
        self.api.assert_called_once_with("OpenTLV/opentlv-python/actions/runs/123/artifacts?per_page=100&page=1")
        self.download.assert_called_once_with("OpenTLV/opentlv-python/actions/artifacts/42/zip")

    def test_pagination_checks_every_page(self):
        others = [{"id": i + 100, "name": "other"} for i in range(100)]
        self.api.side_effect = [{"total_count": 101, "artifacts": others},
                                {"total_count": 101, "artifacts": [self.metadata]}]
        self.assertEqual(self.fetch(), self.feed)
        self.assertEqual([call.args[0] for call in self.api.call_args_list], [
            "OpenTLV/opentlv-python/actions/runs/123/artifacts?per_page=100&page=1",
            "OpenTLV/opentlv-python/actions/runs/123/artifacts?per_page=100&page=2"])

    def test_duplicate_artifact_on_later_page_is_rejected(self):
        self.api.side_effect = [{"total_count": 101, "artifacts": [self.metadata] + [{"name": "other"}] * 99},
                                {"total_count": 101, "artifacts": [self.metadata]}]
        with self.assertRaisesRegex(ValueError, "exactly one"):
            self.fetch()
        self.download.assert_not_called()

    def test_missing_artifact_and_invalid_or_changing_listing(self):
        listings = [None, {}, {"total_count": True, "artifacts": []},
                    {"total_count": 0, "artifacts": []},
                    {"total_count": 1, "artifacts": []},
                    {"total_count": 0, "artifacts": [self.metadata]},
                    {"total_count": 1, "artifacts": [None]},
                    {"total_count": event_artifacts.MAX_ARTIFACTS + 1, "artifacts": []}]
        for listing in listings:
            with self.subTest(listing=listing):
                self.api.side_effect = None
                self.api.return_value = listing
                with self.assertRaises(ValueError):
                    self.fetch()
        self.api.side_effect = [{"total_count": 101, "artifacts": [{"name": "other"}] * 100},
                                {"total_count": 100, "artifacts": []}]
        with self.assertRaisesRegex(ValueError, "changed"):
            self.fetch()
        self.download.assert_not_called()

    def test_rejects_expired_unbound_or_invalid_evidence(self):
        original = copy.deepcopy(self.metadata)
        changes = [{"id": value} for value in (None, True, 0, -1, "42")]
        changes += [{"expired": value} for value in (True, None, 0)]
        changes += [{"digest": value} for value in (None, "", "sha256:bad", "sha512:" + "a" * 64)]
        changes += [{"size_in_bytes": value} for value in (None, True, 0, -1, event_artifacts.MAX_ARCHIVE_BYTES + 1)]
        changes += [{"workflow_run": None}]
        for key, value in (("id", True), ("id", 124), ("head_sha", "b" * 40), ("head_branch", "feature")):
            run = dict(original["workflow_run"], **{key: value})
            changes.append({"workflow_run": run})
        for change in changes:
            with self.subTest(change=change):
                self.metadata = dict(original, **change)
                with self.assertRaisesRegex(ValueError, "evidence"):
                    self.fetch()
        self.download.assert_not_called()

    def test_rejects_repository_and_path_injection(self):
        original = copy.deepcopy(self.payload)
        for change in ({"repository": "attacker/other"}, {"repository": "OpenTLV/opentlv-python/../other"},
                       {"ref": "v1.2.3"}, {"run_id": "123?name=unsafe"}, {"run_id": True}):
            with self.subTest(change=change):
                self.payload = dict(original, **change)
                with self.assertRaises(ValueError):
                    self.fetch()
        self.api.assert_not_called()

    def test_rejects_archive_tamper_and_size_mismatch(self):
        self.raw = self.raw[:-1] + bytes([self.raw[-1] ^ 1])
        with self.assertRaisesRegex(ValueError, "SHA-256"):
            self.fetch()
        self.raw += b"extra"
        with self.assertRaisesRegex(ValueError, "size"):
            self.fetch()

    def test_rejects_empty_duplicate_extra_nested_and_traversing_entries(self):
        for entries in ([], [("compatibility.json", b"{}"), ("compatibility.json", b"{}")],
                        [("compatibility.json", b"{}"), ("script.py", b"print('untrusted')")],
                        [("nested/compatibility.json", b"{}")], [("../compatibility.json", b"{}")],
                        [("/compatibility.json", b"{}")], [("..\\compatibility.json", b"{}")],
                        [("compatibility.json/", b"")]):
            with self.subTest(names=[name for name, _ in entries]):
                self.evidence(zip_bytes(entries))
                with self.assertRaises(ValueError):
                    self.fetch()

    def test_rejects_symbolic_links_and_special_files(self):
        for kind in (stat.S_IFLNK, stat.S_IFDIR, stat.S_IFIFO, stat.S_IFCHR, stat.S_IFSOCK):
            with self.subTest(kind=kind):
                info = zipfile.ZipInfo("compatibility.json")
                info.create_system = 3
                info.external_attr = (kind | 0o644) << 16
                self.evidence(zip_bytes([(info, b"{}")]))
                with self.assertRaisesRegex(ValueError, "unsafe"):
                    self.fetch()

    def test_accepts_regular_unix_file(self):
        info = zipfile.ZipInfo("compatibility.json")
        info.create_system = 3
        info.external_attr = (stat.S_IFREG | 0o644) << 16
        self.evidence(zip_bytes([(info, self.feed)]))
        self.assertEqual(self.fetch(), self.feed)

    def test_accepts_configured_filename_with_leading_underscore_or_dash(self):
        for name in ("_compatibility.json", "-compatibility.json"):
            with self.subTest(name=name):
                self.item["updates"]["asset"] = name
                self.evidence(zip_bytes([(name, self.feed)]))
                self.assertEqual(self.fetch(), self.feed)

    def test_rejects_compressed_bomb_before_decompression(self):
        self.evidence(zip_bytes([("compatibility.json", b"x" * (event_artifacts.MAX_FEED_BYTES + 1))]))
        self.assertLess(len(self.raw), event_artifacts.MAX_ARCHIVE_BYTES)
        with patch.object(zipfile.ZipFile, "open", side_effect=AssertionError("must not decompress")):
            with self.assertRaisesRegex(ValueError, "oversized"):
                self.fetch()

    def test_rejects_invalid_zip_without_extracting_any_files(self):
        self.evidence(b"not a zip archive")
        with self.assertRaisesRegex(ValueError, "intact ZIP"):
            self.fetch()

    def test_injected_download_cannot_bypass_size_bound(self):
        self.raw = b"x" * (event_artifacts.MAX_ARCHIVE_BYTES + 1)
        with self.assertRaisesRegex(ValueError, "size limit"):
            self.fetch()


class DownloadTests(unittest.TestCase):
    def opener(self, transport):
        return lambda *handlers: build_opener(*handlers, transport)

    def test_authenticated_api_download_strips_credentials_at_storage_redirect(self):
        requests = []

        class Transport(HTTPSHandler):
            def https_open(self, request):
                requests.append(request)
                headers = Message()
                if len(requests) == 1:
                    headers["Location"] = "https://signed.storage.invalid/object?signature=value"
                    response = addinfourl(io.BytesIO(b""), headers, request.full_url, code=302)
                    response.msg = "Found"
                    return response
                response = addinfourl(io.BytesIO(b"zip bytes"), headers, request.full_url, code=200)
                response.msg = "OK"
                return response

        with patch.dict(os.environ, {"GH_TOKEN": "unit-test-token"}), \
                patch.object(event_artifacts, "build_opener", self.opener(Transport())):
            result = event_artifacts._download("OpenTLV/opentlv-python/actions/artifacts/42/zip")
        self.assertEqual(result, b"zip bytes")
        self.assertEqual(len(requests), 2)
        self.assertEqual(requests[0].full_url, "https://api.github.com/repos/OpenTLV/opentlv-python/actions/artifacts/42/zip")
        self.assertEqual(requests[0].get_header("Authorization"), "Bearer unit-test-token")
        self.assertIsNone(requests[1].get_header("Authorization"))

    def test_insecure_or_embedded_credential_redirect_is_rejected(self):
        for target in ("http://storage.invalid/feed.zip", "https://user:secret@storage.invalid/feed.zip"):
            class Transport(HTTPSHandler):
                def https_open(self, request):
                    headers = Message()
                    headers["Location"] = target
                    response = addinfourl(io.BytesIO(b""), headers, request.full_url, code=302)
                    response.msg = "Found"
                    return response

            with self.subTest(target=target), \
                    patch.object(event_artifacts, "build_opener", self.opener(Transport())):
                with self.assertRaisesRegex(ValueError, "HTTPS"):
                    event_artifacts._download("OpenTLV/opentlv-python/actions/artifacts/42/zip")

    def test_download_enforces_actual_and_declared_body_limits(self):
        for length, content in (("33", b""), ("invalid", b""), ("-1", b""), (None, b"x" * 33)):
            class Transport(HTTPSHandler):
                def https_open(self, request):
                    headers = Message()
                    if length is not None:
                        headers["Content-Length"] = length
                    response = addinfourl(io.BytesIO(content), headers, request.full_url, code=200)
                    response.msg = "OK"
                    return response

            with self.subTest(length=length), patch.object(event_artifacts, "MAX_ARCHIVE_BYTES", 32), \
                    patch.object(event_artifacts, "build_opener", self.opener(Transport())):
                with self.assertRaisesRegex(ValueError, "size limit"):
                    event_artifacts._download("OpenTLV/opentlv-python/actions/artifacts/42/zip")


if __name__ == "__main__":
    unittest.main()
