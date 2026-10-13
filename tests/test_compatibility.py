# SPDX-License-Identifier: MIT
# Copyright (c) 2026 Marek Cingel

"""External compatibility contracts, immutable imports and release selection."""

from copy import deepcopy
import hashlib
import importlib.util
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

from mkdocs.exceptions import PluginError

spec = importlib.util.spec_from_file_location(
    "compatibility", Path(__file__).resolve().parents[1] / "tools/docs/compatibility.py")
compatibility = importlib.util.module_from_spec(spec)
spec.loader.exec_module(compatibility)

COMPONENT = "https://github.com/OpenTLV/opentlv-python"
CORE = "https://github.com/OpenTLV/opentlv"
SHA = "a" * 40


def record(version="1.2.3", commit="b" * 40, **changes):
    value = {
        "id": f"run-{version}-{commit}",
        "component": {"repository": COMPONENT, "version": version, "commit": commit},
        "declared_core": ">=0.7.0",
        "core": {"repository": CORE, "version": "0.7.1", "commit": SHA},
        "platform": "linux-x86_64", "configuration": "default", "build": "passed", "test": "passed",
        "evidence": "https://ci.example.invalid/runs/1234",
        "features": [{"id": "fixed.roundtrip", "support": "supported", "examples": [
            {"language": "python", "path": "examples/roundtrip.py", "result": "passed"}]}],
    }
    value.update(changes)
    return value


class CompatibilityTests(unittest.TestCase):
    def setUp(self):
        temporary = tempfile.TemporaryDirectory()
        self.addCleanup(temporary.cleanup)
        self.portal = Path(temporary.name).resolve()
        self.settings = {"feed": "compatibility/python.json", "sha256": "0" * 64,
                         "platform": "linux-x86_64", "configuration": "default"}

    def feed(self, *records):
        return {"version": 1, "records": list(records)}

    def save(self, feed):
        raw = json.dumps(feed).encode("utf-8")
        path = self.portal / self.settings["feed"]
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(raw)
        self.settings["sha256"] = hashlib.sha256(raw).hexdigest()
        return raw

    def select(self, *records):
        return compatibility.select(self.feed(*records), self.settings, COMPONENT, CORE, SHA)

    def test_latest_numeric_stable_passed_release_and_deterministic_order(self):
        records = [record("v1.9.0", "b" * 40), record("1.10.0", "c" * 40),
                   record("2.0.0", "d" * 40, test="failed"), record("3.0.0-rc.1", "e" * 40)]
        selected = self.select(*records)
        self.assertEqual(selected["status"], "verified")
        self.assertEqual(selected["record"]["component"]["version"], "1.10.0")
        self.assertEqual(selected, self.select(*reversed(records)))
        self.assertEqual(selected["feed"], {"source": self.settings["feed"], "sha256": "0" * 64})
        self.assertEqual(selected["core"], {"repository": CORE, "commit": SHA, "version": "0.7.1"})
        selected["record"]["features"].clear()
        self.assertTrue(records[1]["features"], "selection must not alias mutable input records")

    def test_failure_untested_missing_have_no_verified_selection(self):
        failed = self.select(record("1.0.0", test="failed"),
                             record("2.0.0", "c" * 40, build="failed", test="untested"))
        self.assertEqual(failed["status"], "failed")
        self.assertEqual(failed["record"]["component"]["version"], "2.0.0")
        untested = self.select(record(build="untested", test="untested", features=[]))
        self.assertEqual(untested["status"], "untested")
        missing = self.select(record("4.0.0-beta.1"))
        self.assertEqual(missing["status"], "missing")
        self.assertIsNone(missing["record"])
        self.assertIsNone(missing["core"]["version"])

    def test_exact_repositories_commits_and_scope_are_required(self):
        for field, value in (("platform", "windows-x64"), ("configuration", "debug")):
            with self.subTest(field=field):
                self.assertEqual(self.select(record(**{field: value}))["status"], "missing")
        for kind, field, value in (("component", "repository", COMPONENT + ".git"),
                                   ("core", "repository", CORE + ".git"),
                                   ("core", "commit", "c" * 40)):
            with self.subTest(kind=kind, field=field):
                candidate = record()
                candidate[kind][field] = value
                self.assertEqual(self.select(candidate)["status"], "missing")

    def test_declared_range_and_example_results_do_not_implicitly_select_or_verify(self):
        candidate = record(declared_core="<0.1.0", features=[])
        self.assertEqual(self.select(candidate)["status"], "verified")
        candidate["test"] = "untested"
        candidate["declared_core"] = ">=0.7.0"
        self.assertEqual(self.select(candidate)["status"], "untested")
        candidate["features"] = record()["features"]
        self.assertEqual(self.select(candidate)["status"], "untested")

    def test_local_import_hashes_exact_bytes_and_never_downloads(self):
        feed = self.feed(record())
        self.save(feed)
        with patch.object(compatibility, "_download", side_effect=AssertionError("unexpected network")):
            self.assertEqual(compatibility.load(self.portal, self.settings), feed)
            (self.portal / self.settings["feed"]).write_bytes(b" " + json.dumps(feed).encode())
            with self.assertRaisesRegex(PluginError, "sha256"):
                compatibility.load(self.portal, self.settings, allow_download=True)

    def test_remote_import_requires_explicit_fetch_then_build_uses_cache(self):
        feed = self.feed(record())
        raw = json.dumps(feed).encode()
        self.settings.update(feed="https://ci.example.invalid/results.json", sha256=hashlib.sha256(raw).hexdigest())
        with patch.object(compatibility, "_download", return_value=raw) as download:
            with self.assertRaisesRegex(PluginError, "fetch sources"):
                compatibility.load(self.portal, self.settings)
            download.assert_not_called()
            self.assertEqual(compatibility.load(self.portal, self.settings, allow_download=True), feed)
            self.assertEqual(compatibility.load(self.portal, self.settings), feed)
            download.assert_called_once_with(self.settings["feed"])
        path = self.portal / "build/compatibility" / f"{self.settings['sha256']}.json"
        self.assertEqual(path.read_bytes(), raw)
        path.write_bytes(b"tampered")
        with patch.object(compatibility, "_download", side_effect=AssertionError("must not refresh bad cache")):
            with self.assertRaisesRegex(PluginError, "sha256"):
                compatibility.load(self.portal, self.settings, allow_download=True)

    def test_bad_digest_and_bad_schema_are_never_cached(self):
        for raw, digest in ((b"{}", "0" * 64), (b"{}", hashlib.sha256(b"{}").hexdigest())):
            with self.subTest(digest=digest):
                self.settings.update(feed="https://ci.example.invalid/results.json", sha256=digest)
                with patch.object(compatibility, "_download", return_value=raw):
                    with self.assertRaises(PluginError):
                        compatibility.load(self.portal, self.settings, allow_download=True)
                self.assertFalse((self.portal / "build/compatibility" / f"{digest}.json").exists())

    def test_duplicate_json_keys_invalid_utf8_and_oversize_rejected(self):
        for raw in (b'{"version":1,"version":1,"records":[]}', b"\xff", b"[", b" " * 129):
            with self.subTest(raw=raw[:30]):
                self.settings.update(feed="https://ci.example.invalid/results.json",
                                     sha256=hashlib.sha256(raw).hexdigest())
                with patch.object(compatibility, "_download", return_value=raw), patch.object(compatibility, "MAX_BYTES", 128):
                    with self.assertRaises(PluginError):
                        compatibility.load(self.portal, self.settings, allow_download=True)

    def test_unsafe_source_settings_and_redirects_are_rejected(self):
        for source in ("../feed.json", "/feed.json", "C:/feed.json", "a\\feed.json", "a//feed.json",
                       "http://ci.example.invalid/feed", "https://user:secret@ci.example.invalid/feed",
                       "https://ci.example.invalid:99999/feed", "https:///feed"):
            with self.subTest(source=source):
                with self.assertRaises(PluginError):
                    compatibility.validate_settings(dict(self.settings, feed=source))
        for changes in ({"sha256": "A" * 64}, {"platform": []}, {"extra": True}):
            with self.subTest(changes=changes), self.assertRaises(PluginError):
                compatibility.validate_settings(dict(self.settings, **changes))
        with self.assertRaisesRegex(PluginError, "HTTPS"):
            compatibility._HTTPSRedirect().redirect_request(None, None, 302, "Found", {}, "http://example.invalid/feed")

    def test_symlink_feed_cannot_escape_portal(self):
        target = self.portal / "target.json"
        raw = json.dumps(self.feed(record())).encode()
        target.write_bytes(raw)
        link = self.portal / "feed.json"
        try:
            link.symlink_to(target)
        except OSError:
            self.skipTest("symlink creation unavailable")
        self.settings.update(feed="feed.json", sha256=hashlib.sha256(raw).hexdigest())
        with self.assertRaisesRegex(PluginError, "symlinks"):
            compatibility.load(self.portal, self.settings)

    def test_duplicate_and_contradictory_records_fail(self):
        first = record()
        conflicting_scope = record(id="another-run", test="failed")
        conflicting_version = record(commit="c" * 40)
        alias_version = record("v1.2.3+build.2", "c" * 40)
        contradictory_core = record("1.3.0", "c" * 40)
        contradictory_core["core"]["commit"] = "d" * 40
        for second in (first, conflicting_scope, conflicting_version, alias_version, contradictory_core):
            with self.subTest(second=second["id"]), self.assertRaises(PluginError):
                compatibility.validate_feed(self.feed(first, second))

    def test_schema_types_versions_and_contradictory_outcomes_fail(self):
        bad_records = [record(build="failed"), record(test=True), record(features={}), record(id=""),
                       record(component={}), record("1.2"), record("01.2.3"), record("1.2.3-01"),
                       record(evidence="https://user@ci.example.invalid/run")]
        for field in ("component", "core"):
            candidate = record()
            candidate[field]["commit"] = "A" * 40
            bad_records.append(candidate)
        unsupported = record()
        unsupported["features"][0]["support"] = "unsupported"
        bad_records.append(unsupported)
        duplicate_feature = record()
        duplicate_feature["features"] *= 2
        bad_records.append(duplicate_feature)
        duplicate_example = record()
        duplicate_example["features"][0]["examples"] *= 2
        bad_records.append(duplicate_example)
        unsafe_example = record()
        unsafe_example["features"][0]["examples"][0]["path"] = "../example.py"
        bad_records.append(unsafe_example)
        for candidate in bad_records:
            with self.subTest(candidate=candidate), self.assertRaises(PluginError):
                compatibility.validate_feed(self.feed(candidate))
        for malformed in ({"version": True, "records": []}, {"version": 3, "records": []},
                          {"version": 1, "records": {}}, {"version": 1, "records": [], "extra": True}):
            with self.subTest(feed=malformed), self.assertRaises(PluginError):
                compatibility.validate_feed(malformed)

    def test_partial_feature_support_and_build_metadata_are_valid(self):
        candidate = record("1.2.3+build.7")
        candidate["features"] += [
            {"id": "query.plan", "support": "unsupported", "examples": []},
            {"id": "der.decode", "support": "unknown", "examples": [
                {"language": "python", "path": "examples/der.py", "result": "untested"}]},
        ]
        selected = self.select(candidate)
        self.assertEqual(selected["status"], "verified")
        self.assertEqual(selected["record"]["features"], candidate["features"])
        copy = deepcopy(candidate)
        copy["platform"] = "windows-x64"
        copy["id"] = "windows-run"
        self.assertEqual(self.select(candidate, copy)["record"], candidate)

    def test_malformed_nested_field_types_report_contract_errors(self):
        paths = [
            ("id",), ("component",), ("component", "repository"), ("component", "version"),
            ("component", "commit"), ("core",), ("core", "version"), ("declared_core",),
            ("platform",), ("configuration",), ("build",), ("test",), ("evidence",),
            ("features", 0, "id"), ("features", 0, "support"),
            ("features", 0, "examples", 0, "language"), ("features", 0, "examples", 0, "path"),
            ("features", 0, "examples", 0, "result"),
        ]
        for path in paths:
            for malformed in (None, True, 1, [], {}):
                with self.subTest(path=path, value=malformed):
                    candidate = record()
                    target = candidate
                    for part in path[:-1]:
                        target = target[part]
                    target[path[-1]] = malformed
                    with self.assertRaises(PluginError):
                        compatibility.validate_feed(self.feed(candidate))


if __name__ == "__main__":
    unittest.main()
