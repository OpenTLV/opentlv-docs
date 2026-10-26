# SPDX-License-Identifier: MIT
# Copyright (c) 2026 Marek Cingel

"""Run independent CLI publication through the same sealed Full CI candidate gate."""

import json
import os
import shutil
import unittest
from unittest.mock import patch

import test_cli_release
import test_publication
import quality


class CliCandidateTests(unittest.TestCase):
    def candidate(self, *, portal):
        fixture = test_cli_release.CliPublicationTests()
        fixture.setUp()
        self.addCleanup(fixture.doCleanups)
        if portal:
            # Product snapshots link back to the portal root published by Core.
            test_publication.PublicationTests.prepare(fixture)
            fixture.deploy_bundle()
            fixture.fresh_checkout()
        env = {"GITHUB_REPOSITORY": "OpenTLV/opentlv-docs",
               "GITHUB_SHA": fixture.git("rev-parse", "HEAD"),
               "GITHUB_RUN_ID": "123", "GITHUB_RUN_ATTEMPT": "2",
               "GITHUB_WORKFLOW_REF": "OpenTLV/opentlv-docs/.github/workflows/docs-release.yml@refs/heads/main",
               "PYTHONDONTWRITEBYTECODE": "1"}
        context = patch.dict(os.environ, env)
        context.start()
        self.addCleanup(context.stop)
        quality.baseline(fixture.portal)
        fixture.publish()
        selected = fixture.cli_selection()
        fixture.write("build/selection.json", json.dumps(selected))
        evidence = quality.pack(fixture.portal)
        target = fixture.portal / "build/candidate"
        target.mkdir()
        for name in ("site.tar", "history.bundle", "evidence.json"):
            shutil.copyfile(fixture.portal / "build/publication" / name, target / name)
        return fixture, target, selected, evidence

    def test_cli_snapshot_passes_common_full_evidence_gate_without_core_generation(self):
        fixture, target, selected, evidence = self.candidate(portal=True)
        self.assertEqual(quality.verify(fixture.portal, target), evidence)
        self.assertTrue((target / "site/cli/0.1.0/index.html").is_file())
        self.assertFalse((fixture.portal / "build/sources/core").exists())
        self.assertFalse((fixture.portal / "build/api").exists())
        self.assertEqual(evidence["selection"], selected)
        self.assertIn("cli/0.1.0", evidence["snapshots"])
        self.assertIn("latest", (target / "site/versions.json").read_text(encoding="utf-8"))

    def test_cli_snapshot_requires_its_published_portal_return_link(self):
        fixture, target, _selected, _evidence = self.candidate(portal=False)
        with self.assertRaisesRegex(ValueError, "missing site entry points: https://example.invalid/docs/"):
            quality.verify(fixture.portal, target)


if __name__ == "__main__":
    unittest.main()
