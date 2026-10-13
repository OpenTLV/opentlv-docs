# SPDX-License-Identifier: MIT
# Copyright (c) 2026 Marek Cingel

"""Exercise the source-update workflow's path selection with real Bash and Git."""

import os
from pathlib import Path
import shutil
import subprocess
import tempfile
import unittest

import yaml


class UpdateStagingTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.git_executable = shutil.which("git")
        if not cls.git_executable:
            raise unittest.SkipTest("Git is required for workflow staging tests")
        if os.name == "nt":
            # Windows' system32/bash.exe is a WSL launcher, not Git Bash.
            git_directory = Path(cls.git_executable).resolve().parent
            candidates = (git_directory / "bash.exe",
                          git_directory.parent / "bin/bash.exe",
                          git_directory.parent / "usr/bin/bash.exe")
            cls.bash = next((str(path) for path in candidates if path.is_file()), None)
        else:
            cls.bash = shutil.which("bash")
        if not cls.bash:
            raise unittest.SkipTest("Bash is required for workflow staging tests")
        workflow = Path(__file__).resolve().parents[1] / ".github/workflows/component-updates.yml"
        cls.steps = yaml.safe_load(workflow.read_text(encoding="utf-8"))["jobs"]["propose"]["steps"]

    def setUp(self):
        temp = tempfile.TemporaryDirectory()
        self.addCleanup(temp.cleanup)
        self.base = Path(temp.name).resolve()
        self.repo = self.base / "repo"
        self.repo.mkdir()
        self.env = {key: value for key, value in os.environ.items()
                    if not key.startswith(("OPENTLV_", "GITHUB_", "GIT_"))}
        self.env.update(GIT_AUTHOR_NAME="Fixture", GIT_AUTHOR_EMAIL="fixture@example.invalid",
                        GIT_COMMITTER_NAME="Fixture", GIT_COMMITTER_EMAIL="fixture@example.invalid",
                        GIT_CONFIG_COUNT="2", GIT_CONFIG_KEY_0="commit.gpgsign", GIT_CONFIG_VALUE_0="false",
                        GIT_CONFIG_KEY_1="core.autocrlf", GIT_CONFIG_VALUE_1="false")
        self.git("init", "-b", "main")
        self.write(".gitignore", "build/\ncompatibility/ignored/\n")
        self.write("docs-sources.json", '{"revision": "old"}\n')
        self.write("README.md", "Fixture\n")
        self.git("add", ".")
        self.git("commit", "-m", "Fixture")

    def run_command(self, args, *, check=True):
        result = subprocess.run(args, cwd=self.repo, env=self.env, capture_output=True, text=True)
        if check:
            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        return result

    def git(self, *args):
        return self.run_command([self.git_executable, *args]).stdout

    def write(self, name, content):
        path = self.repo / name
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content, encoding="utf-8")

    def select_paths(self):
        selection = next(step for step in self.steps if step.get("id") == "update-paths")
        action = next(step for step in self.steps
                      if step.get("uses", "").startswith("peter-evans/create-pull-request@"))
        self.assertEqual(selection["shell"], "bash")
        self.assertEqual(action["with"]["add-paths"], "${{ steps.update-paths.outputs.paths }}")
        script = self.base / "select-paths.sh"
        script.write_text(selection["run"], encoding="utf-8")
        output = self.base / "github-output"
        output.write_text("", encoding="utf-8")
        self.env["GITHUB_OUTPUT"] = output.as_posix()
        self.run_command([self.bash, "--noprofile", "--norc", "-e", "-o", "pipefail", script.as_posix()])
        lines = output.read_text(encoding="utf-8").splitlines()
        self.assertTrue(lines and lines[0].startswith("paths<<"), lines)
        self.assertEqual(lines[-1], lines[0].removeprefix("paths<<"))
        paths = lines[1:-1]
        self.assertIn("docs-sources.json", paths)
        return paths

    def stage_update(self):
        paths = self.select_paths()
        # create-pull-request v7 checks allowed paths, then passes them to Git.
        dirty = self.git("status", "--porcelain", "-unormal", "--", *paths)
        if dirty:
            self.git("add", "--", *paths)
        return set(self.git("diff", "--cached", "--name-only").splitlines())

    def test_original_optional_glob_fails_without_evidence(self):
        self.write("docs-sources.json", '{"revision": "new"}\n')
        result = self.run_command([self.git_executable, "add", "--", "docs-sources.json",
                                   "compatibility/**/*.json"], check=False)
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("pathspec 'compatibility/**/*.json' did not match any files", result.stderr)

    def test_core_update_without_compatibility_directory(self):
        self.write("docs-sources.json", '{"revision": "new"}\n')
        self.assertFalse((self.repo / "compatibility").exists())
        self.assertEqual(self.stage_update(), {"docs-sources.json"})
        self.assertFalse((self.repo / "compatibility").exists())

    def test_directory_without_json_is_optional(self):
        self.write("compatibility/README.md", "No evidence yet\n")
        self.write("docs-sources.json", '{"revision": "new"}\n')
        self.assertEqual(self.stage_update(), {"docs-sources.json"})

    def test_new_nested_and_modified_json_are_staged(self):
        self.write("compatibility/lua/existing.json", '{"version": 1}\n')
        self.git("add", "compatibility/lua/existing.json")
        self.git("commit", "-m", "Existing evidence fixture")
        self.write("compatibility/lua/existing.json", '{"version": 2}\n')
        self.write("compatibility/python/nested/new.json", '{"version": 2}\n')
        self.write("compatibility/root.json", '{"version": 2}\n')
        self.write("docs-sources.json", '{"revision": "new"}\n')
        self.assertEqual(self.stage_update(), {"docs-sources.json", "compatibility/lua/existing.json",
                                              "compatibility/python/nested/new.json", "compatibility/root.json"})

    def test_unrelated_and_ignored_files_remain_unstaged(self):
        self.write("compatibility/lua/helper.py", "old\n")
        self.git("add", "compatibility/lua/helper.py")
        self.git("commit", "-m", "Unrelated fixture")
        self.write("README.md", "Unrelated tracked change\n")
        self.write("compatibility/lua/helper.py", "Unrelated tracked change\n")
        self.write("unrelated.json", "{}\n")
        self.write("compatibility/python/producer.py", "Unrelated producer code\n")
        self.write("compatibility/ignored/evidence.json", "{}\n")
        self.write("build/generated.json", "{}\n")
        self.write("compatibility/python/new.json", '{"version": 2}\n')
        self.write("docs-sources.json", '{"revision": "new"}\n')
        self.assertEqual(self.stage_update(), {"docs-sources.json", "compatibility/python/new.json"})
        self.assertEqual(set(self.git("diff", "--name-only").splitlines()),
                         {"README.md", "compatibility/lua/helper.py"})
        self.assertEqual(set(self.git("ls-files", "--others", "--exclude-standard").splitlines()),
                         {"unrelated.json", "compatibility/python/producer.py"})

    def test_clean_checkout_has_no_update_diff(self):
        original_head = self.git("rev-parse", "HEAD")
        self.assertEqual(self.stage_update(), set())
        self.assertEqual(self.git("rev-parse", "HEAD"), original_head)

    def test_only_unrelated_changes_have_no_update_diff(self):
        self.write("README.md", "Unrelated tracked change\n")
        self.write("compatibility/python/producer.py", "Unrelated producer code\n")
        self.write("compatibility/ignored/evidence.json", "{}\n")
        self.assertEqual(self.stage_update(), set())

    def test_repeated_update_has_no_diff_after_merge(self):
        manifest = '{"revision": "new"}\n'
        evidence = '{"version": 2}\n'
        self.write("docs-sources.json", manifest)
        self.write("compatibility/python/new.json", evidence)
        self.assertEqual(self.stage_update(), {"docs-sources.json", "compatibility/python/new.json"})
        self.git("commit", "-m", "Merged update fixture")
        self.write("docs-sources.json", manifest)
        self.write("compatibility/python/new.json", evidence)
        self.assertEqual(self.stage_update(), set())

    def test_tracked_json_deletion_is_staged(self):
        self.write("compatibility/lua/old.json", '{"version": 1}\n')
        self.git("add", "compatibility/lua/old.json")
        self.git("commit", "-m", "Existing evidence fixture")
        (self.repo / "compatibility/lua/old.json").unlink()
        self.assertEqual(self.stage_update(), {"compatibility/lua/old.json"})


if __name__ == "__main__":
    unittest.main()
