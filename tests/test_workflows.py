# SPDX-License-Identifier: MIT
# Copyright (c) 2026 Marek Cingel

"""CI entry points, required jobs and publishing ownership are repository contracts."""

from pathlib import Path
import unittest

import yaml

ROOT = Path(__file__).resolve().parents[1]


def workflow(name):
    return yaml.load((ROOT / ".github/workflows" / name).read_text(encoding="utf-8"), Loader=yaml.BaseLoader)


class WorkflowTests(unittest.TestCase):
    def test_four_entry_points_and_no_ordinary_push_publication(self):
        expected = {"pr": {"pull_request"}, "main": {"push"},
                    "full": {"workflow_dispatch", "workflow_call"},
                    "release": {"workflow_dispatch", "repository_dispatch"}}
        for stage, triggers in expected.items():
            data = workflow(f"docs-{stage}.yml")
            self.assertEqual(set(data["on"]), triggers)
            self.assertEqual(data["permissions"]["contents"], "read")
        self.assertFalse((ROOT / ".github/workflows/docs.yml").exists())
        for stage in ("pr", "main"):
            text = (ROOT / f".github/workflows/docs-{stage}.yml").read_text()
            self.assertNotIn("docs-full.yml", text)
            self.assertNotIn("deploy-pages", text)
        self.assertNotIn("publish", workflow("docs-full.yml")["on"]["workflow_dispatch"]["inputs"])

    def test_aggregate_gates_require_success_even_when_predecessors_skip(self):
        for stage, predecessor in (("pr", "fast"), ("main", "smoke"), ("full", "prepare")):
            gate = workflow(f"docs-{stage}.yml")["jobs"]["gate"]
            self.assertEqual(gate["if"], "always()")
            self.assertEqual(gate["needs"], [predecessor])
            self.assertEqual(gate["steps"][0]["env"]["RESULT"], "${{ needs." + predecessor + ".result }}")
            self.assertEqual(gate["steps"][0]["run"], 'test "$RESULT" = success')

    def test_publisher_calls_same_commit_full_and_deploys_only_its_artifacts(self):
        jobs = workflow("docs-release.yml")["jobs"]
        self.assertEqual(jobs["full"]["uses"], "./.github/workflows/docs-full.yml")
        deploy = jobs["deploy"]
        self.assertEqual(deploy["needs"], ["full"])
        self.assertIn("needs.full.result == 'success'", deploy["if"])
        self.assertIn("refs/heads/main", deploy["if"])
        commands = "\n".join(step.get("run", "") for step in deploy["steps"])
        self.assertIn('os.environ["EVIDENCE_SHA256"]', commands)
        self.assertNotIn("tools/docs/", commands)
        self.assertNotIn("--force", commands)
        download = next(step for step in deploy["steps"] if "download-artifact@" in step.get("uses", ""))
        self.assertEqual(download["with"]["name"], "docs-candidate-${{ github.run_attempt }}")

    def test_full_builds_once_and_does_not_run_component_behavior(self):
        full = workflow("docs-full.yml")
        steps = full["jobs"]["prepare"]["steps"]
        commands = "\n".join(step.get("run", "") for step in steps)
        self.assertNotIn("mkdocs build", commands)
        self.assertIn("publication.py", commands)
        self.assertIn("cli_release.py", commands)
        self.assertIn("browser_smoke.py", commands)
        source_check = next(i for i, step in enumerate(steps) if step.get("id") == "source")
        wasm = next(i for i, step in enumerate(steps) if "setup-emsdk@" in step.get("uses", ""))
        self.assertLess(source_check, wasm)
        generator = (ROOT / "tools/docs/wasm.py").read_text()
        self.assertIn("-DOPENTLV_BUILD_WASM_TESTS=OFF", generator)
        self.assertNotIn('"ctest"', generator)
        self.assertNotIn("test_doc_inventory.py", (ROOT / "tools/docs/ci.py").read_text())

    def test_updates_serialize_one_branch_per_source_and_auto_merge_is_opt_in(self):
        data = workflow("component-updates.yml")
        self.assertNotIn("client_payload.commit", data["concurrency"]["group"])
        steps = data["jobs"]["propose"]["steps"]
        proposal = next(step for step in steps if step.get("id") == "pull-request")
        self.assertEqual(proposal["with"]["branch"], "automation/component-${{ github.event.client_payload.source }}")
        self.assertIn("changed == 'true'", proposal["if"])
        merge = next(step for step in steps if "auto_merge.py" in step.get("run", ""))
        self.assertIn("vars.DOCS_UPDATES_AUTOMERGE == 'true'", merge["if"])


if __name__ == "__main__":
    unittest.main()
