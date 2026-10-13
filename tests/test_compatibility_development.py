# SPDX-License-Identifier: MIT
# Copyright (c) 2026 Marek Cingel

"""Development evidence is exact-commit scoped and cannot become a release."""

from copy import deepcopy
import hashlib
import importlib.util
import json
from pathlib import Path
import tempfile
import unittest

from mkdocs.exceptions import PluginError

spec = importlib.util.spec_from_file_location(
    "compatibility", Path(__file__).resolve().parents[1] / "tools/docs/compatibility.py")
compatibility = importlib.util.module_from_spec(spec)
spec.loader.exec_module(compatibility)

COMPONENT = "https://github.com/OpenTLV/opentlv-python"
CORE = "https://github.com/OpenTLV/opentlv"
CORE_SHA = "a" * 40
DEVELOPMENT_SHA = "b" * 40
RELEASE_SHA = "c" * 40
SETTINGS = {"feed": "compatibility/python.json", "sha256": "0" * 64,
            "platform": "linux-x86_64", "configuration": "default"}


def record(channel="development", commit=DEVELOPMENT_SHA, version="main", **changes):
    value = {
        "id": f"run-{commit}", "channel": channel,
        "component": {"repository": COMPONENT, "version": version, "commit": commit},
        "declared_core": ">=0.7.0",
        "core": {"repository": CORE, "version": "main", "commit": CORE_SHA},
        "platform": "linux-x86_64", "configuration": "default", "build": "passed", "test": "passed",
        "evidence": "https://ci.example.invalid/runs/1234", "features": [],
    }
    value.update(changes)
    return value


def select(*records, **options):
    return compatibility.select({"version": 2, "records": list(records)}, SETTINGS,
                                COMPONENT, CORE, CORE_SHA, **options)


class DevelopmentCompatibilityTests(unittest.TestCase):
    def test_release_selection_excludes_development_even_with_stable_version_label(self):
        development = record(version="99.0.0")
        stable = record("release", RELEASE_SHA, "1.2.3")
        for records in ((development, stable), (stable, development)):
            selected = select(*records)
            self.assertEqual(selected["status"], "verified")
            self.assertEqual(selected["record"], stable)
            self.assertEqual(selected["schema_version"], 2)
        self.assertEqual(select(development)["status"], "missing")
        self.assertEqual(select(development, component_commit=DEVELOPMENT_SHA)["status"], "missing")

    def test_development_without_explicit_pin_retains_stable_selection(self):
        development = record()
        stable = record("release", RELEASE_SHA, "1.2.3")
        selected = select(development, stable, channel="development")
        self.assertEqual(selected["record"], stable)
        self.assertEqual(select(development, channel="development")["status"], "missing")

    def test_explicit_development_pin_selects_only_the_exact_component(self):
        pinned = record()
        newer = record(commit="d" * 40, version="next")
        stable = record("release", RELEASE_SHA, "1.2.3")
        for records in ((pinned, newer, stable), (stable, newer, pinned)):
            selected = select(*records, channel="development", component_commit=DEVELOPMENT_SHA)
            self.assertEqual(selected["status"], "verified")
            self.assertEqual(selected["record"], pinned)
        missing = select(newer, stable, channel="development", component_commit=DEVELOPMENT_SHA)
        self.assertEqual(missing["status"], "missing")
        self.assertIsNone(missing["record"])

    def test_exact_pin_can_select_stable_evidence_without_promoting_prerelease(self):
        stable = record("release", RELEASE_SHA, "1.2.3")
        self.assertEqual(select(stable, channel="development", component_commit=RELEASE_SHA)["status"], "verified")
        stable["component"]["version"] = "1.2.3-rc.1"
        self.assertEqual(select(stable, channel="development", component_commit=RELEASE_SHA)["status"], "missing")

    def test_development_requires_exact_core_repository_and_scope(self):
        paths = (("component", "repository", COMPONENT + ".git"),
                 ("core", "repository", CORE + ".git"), ("core", "commit", "d" * 40),
                 (None, "platform", "windows-x64"), (None, "configuration", "debug"))
        for parent, field, value in paths:
            with self.subTest(parent=parent, field=field):
                candidate = record()
                target = candidate[parent] if parent else candidate
                target[field] = value
                result = select(candidate, channel="development", component_commit=DEVELOPMENT_SHA)
                self.assertEqual(result["status"], "missing")

    def test_failed_or_untested_pin_cannot_fall_back_to_another_verified_commit(self):
        stable = record("release", RELEASE_SHA, "1.2.3")
        for outcome in ("failed", "untested"):
            with self.subTest(outcome=outcome):
                selected = select(record(test=outcome), stable, channel="development",
                                  component_commit=DEVELOPMENT_SHA)
                self.assertEqual(selected["status"], outcome)
                self.assertEqual(selected["record"]["component"]["commit"], DEVELOPMENT_SHA)

    def test_development_labels_can_repeat_but_verification_scopes_cannot(self):
        first = record()
        second = record(commit="d" * 40)
        second["core"]["commit"] = "e" * 40
        feed = {"version": 2, "records": [first, second]}
        self.assertEqual(compatibility.validate_feed(feed), feed)
        contradictory = deepcopy(first)
        contradictory.update(id="contradictory-run", test="failed")
        for changes in ({}, {"channel": "release", "component": dict(first["component"], version="1.2.3")}):
            with self.subTest(changes=changes):
                contradictory.update(changes)
                with self.assertRaisesRegex(PluginError, "verification scope"):
                    compatibility.validate_feed({"version": 2, "records": [first, contradictory]})

    def test_release_version_contradictions_remain_invalid_in_v2(self):
        first = record("release", RELEASE_SHA, "1.2.3")
        for second in (record("release", "d" * 40, "v1.2.3+build.2"),
                       record("release", "d" * 40, "1.3.0",
                              core={"repository": CORE, "version": "main", "commit": "e" * 40})):
            with self.subTest(second=second), self.assertRaisesRegex(PluginError, "contradictory"):
                compatibility.validate_feed({"version": 2, "records": [first, second]})

    def test_channel_is_required_only_in_v2_and_unknown_channels_fail(self):
        for channel in (None, True, 1, [], {}, "latest", "Release"):
            with self.subTest(channel=channel), self.assertRaises(PluginError):
                compatibility.validate_feed({"version": 2, "records": [record(channel=channel)]})
        legacy = record("release", RELEASE_SHA, "1.2.3")
        with self.assertRaisesRegex(PluginError, "exactly"):
            compatibility.validate_feed({"version": 1, "records": [legacy]})
        del legacy["channel"]
        with self.assertRaisesRegex(PluginError, "exactly"):
            compatibility.validate_feed({"version": 2, "records": [legacy]})
        selection = compatibility.select({"version": 1, "records": [legacy]}, SETTINGS,
                                         COMPONENT, CORE, CORE_SHA)
        self.assertNotIn("schema_version", selection)
        self.assertEqual(selection["status"], "verified")

    def test_invalid_selection_channels_pins_and_development_identities_fail(self):
        for options in ({"channel": "latest"}, {"channel": None}, {"channel": []},
                        {"channel": "development", "component_commit": "main"},
                        {"channel": "development", "component_commit": "B" * 40}):
            with self.subTest(options=options), self.assertRaises(PluginError):
                select(record(), **options)
        for kind in ("component", "core"):
            for field, value in (("version", ""), ("version", []), ("commit", "main"), ("commit", "B" * 40)):
                with self.subTest(kind=kind, field=field, value=value), self.assertRaises(PluginError):
                    candidate = record()
                    candidate[kind][field] = value
                    compatibility.validate_feed({"version": 2, "records": [candidate]})

    def test_v2_import_checks_pinned_bytes_and_selection_supports_offline_reconstruction(self):
        feed = {"version": 2, "records": [record()]}
        raw = json.dumps(feed).encode("utf-8")
        with tempfile.TemporaryDirectory() as temporary:
            portal = Path(temporary)
            path = portal / SETTINGS["feed"]
            path.parent.mkdir(parents=True)
            path.write_bytes(raw)
            settings = dict(SETTINGS, sha256=hashlib.sha256(raw).hexdigest())
            imported = compatibility.load(portal, settings)
            selected = compatibility.select(imported, settings, COMPONENT, CORE, CORE_SHA,
                                            channel="development", component_commit=DEVELOPMENT_SHA)
            reconstructed = {"version": selected["schema_version"], "records": [selected["record"]]}
            self.assertEqual(selected, compatibility.select(reconstructed, settings, COMPONENT, CORE, CORE_SHA,
                                                           channel="development", component_commit=DEVELOPMENT_SHA))
            selected["record"]["component"]["version"] = "changed"
            self.assertEqual(imported, feed)
            path.write_bytes(b" " + raw)
            with self.assertRaisesRegex(PluginError, "sha256"):
                compatibility.load(portal, settings)


if __name__ == "__main__":
    unittest.main()
