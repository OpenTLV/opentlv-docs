# SPDX-License-Identifier: MIT
# Copyright (c) 2026 Marek Cingel

"""Run independent CLI publication through the same sealed Full CI candidate gate."""

import json
import os
import shutil
import unittest
from unittest.mock import patch

import test_cli_release
import quality


class CliCandidateTests(unittest.TestCase):
    def test_cli_snapshot_passes_common_full_evidence_gate_without_core_generation(self):
        fixture = test_cli_release.CliPublicationTests()
        fixture.setUp()
        self.addCleanup(fixture.doCleanups)
        env = {"GITHUB_REPOSITORY": "OpenTLV/opentlv-docs",
               "GITHUB_SHA": fixture.git("rev-parse", "HEAD"),
               "GITHUB_RUN_ID": "123", "GITHUB_RUN_ATTEMPT": "2",
               "GITHUB_WORKFLOW_REF": "OpenTLV/opentlv-docs/.github/workflows/docs-release.yml@refs/heads/main",
               "PYTHONDONTWRITEBYTECODE": "1"}
        with patch.dict(os.environ, env):
            quality.baseline(fixture.portal)
            fixture.publish()
            selected = fixture.cli_selection()
            fixture.write("build/selection.json", json.dumps(selected))
            evidence = quality.pack(fixture.portal)
            target = fixture.portal / "build/candidate"
            target.mkdir()
            for name in ("site.tar", "history.bundle", "evidence.json"):
                shutil.copyfile(fixture.portal / "build/publication" / name, target / name)
            self.assertEqual(quality.verify(fixture.portal, target), evidence)
            self.assertTrue((target / "site/cli/0.1.0/index.html").is_file())
            self.assertFalse((fixture.portal / "build/sources/core").exists())
            self.assertFalse((fixture.portal / "build/api").exists())
            self.assertEqual(evidence["selection"], selected)
            self.assertIn("cli/0.1.0", evidence["snapshots"])


if __name__ == "__main__":
    unittest.main()
