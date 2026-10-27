# SPDX-License-Identifier: MIT
# Copyright (c) 2026 Marek Cingel

"""REUSE annotations, license texts and copyright holders are repository contracts."""

from pathlib import Path
import re
import subprocess
import unittest

try:
    import tomllib
except ModuleNotFoundError:  # Python 3.10; CI reads REUSE.toml with 3.12.
    tomllib = None

ROOT = Path(__file__).resolve().parents[1]
HOLDER = "2026 Marek Cingel"
# REUSE-IgnoreStart
# Copyright lines of headers, REUSE metadata and LICENSE files, in any comment syntax.
NOTICE = re.compile(r'^[\s#/*;{-]*(?:Copyright \(c\)|SPDX-FileCopyrightText:?\s*=?)\s*"?(.+)$',
                    re.MULTILINE)
# REUSE-IgnoreEnd
# REUSE does not read examples between these markers as the file's own metadata.
IGNORED = re.compile(rb"REUSE-IgnoreStart.*?REUSE-IgnoreEnd", re.DOTALL)


def tracked():
    return subprocess.run(["git", "ls-files", "--cached", "--others", "--exclude-standard"],
                          cwd=ROOT, check=True, capture_output=True, text=True).stdout.splitlines()


def annotations():
    return tomllib.loads((ROOT / "REUSE.toml").read_text(encoding="utf-8"))["annotations"]


class LicensingTests(unittest.TestCase):
    @unittest.skipIf(tomllib is None, "tomllib requires Python 3.11")
    def test_annotations_list_existing_unheadered_files_explicitly(self):
        files = set(tracked())
        listed = [path for annotation in annotations() for path in annotation["path"]]
        self.assertEqual(len(listed), len(set(listed)))
        for path in listed:
            # A glob would also cover new sources, which must carry their own header.
            self.assertFalse(set("*?[") & set(path), path)
            self.assertIn(path, files)
            data = IGNORED.sub(b"", (ROOT / path).read_bytes())
            self.assertNotIn(b"SPDX-License-Identifier", data, path)
        for annotation in annotations():
            self.assertEqual(annotation["SPDX-FileCopyrightText"], HOLDER)
            self.assertEqual(annotation["SPDX-License-Identifier"], "MIT")

    def test_reuse_license_text_matches_repository_license(self):
        license_text = (ROOT / "LICENSE").read_text(encoding="utf-8")
        template = (ROOT / "LICENSES/MIT.txt").read_text(encoding="utf-8")
        # The texts differ only in the copyright line and their line wrapping.
        # REUSE-IgnoreStart
        license_text = license_text.replace(f"Copyright (c) {HOLDER}", "Copyright (c) <year> <copyright holders>")
        # REUSE-IgnoreEnd
        self.assertEqual(license_text.split(), template.split())
        self.assertEqual(sorted(path.name for path in (ROOT / "LICENSES").iterdir()), ["MIT.txt"])

    def test_organization_is_not_a_copyright_holder(self):
        notices = 0
        for path in tracked():
            data = (ROOT / path).read_bytes()
            if b"\0" in data:
                continue
            for holder in NOTICE.findall(data.decode("utf-8")):
                notices += 1
                self.assertNotIn("OpenTLV", holder, path)
        self.assertGreater(notices, 60)


if __name__ == "__main__":
    unittest.main()
