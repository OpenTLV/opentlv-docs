# SPDX-License-Identifier: MIT
# Copyright (c) 2026 Marek Cingel

"""Preserve Core onboarding content, provenance and links across its section split."""

import json
from pathlib import Path
from types import SimpleNamespace
import unittest
from unittest.mock import patch

from mkdocs.exceptions import PluginError
from mkdocs.structure.files import File, Files

import test_portal as fixture

onboarding = fixture.assembly.onboarding
navigation = fixture.load_hook("navigation")
SOURCE = """# Getting started

## Build from a checkout

Toolchain, static/shared libraries and loader requirements.

## Quick start

```c
/* Preserve the complete executable example and its expected output. */
```

## Consume Core from another CMake project

Source and installed target requirements.

## Install and generate distribution archives

Archive commands and installation layout.

## C-only build

Feature switches.

## Build and run tests

Test commands and prerequisites.
"""


class OnboardingTests(unittest.TestCase):
    def test_go_handoff_preserves_other_tabs_and_uses_selected_owner(self):
        selected = [(None, {"id": "go", "included": True,
                            "repository": "https://github.com/OpenTLV/opentlv-go", "commit": "a" * 40})]
        native = "/// tab | C\n\n```c\n/* unchanged */\n```\n\n///\n\n"
        legacy = "/// tab | Go\n\nUse bindings/go/examples/quick_start/main.go and the old import.\n\n///\n"
        suffix = "\n[Go](../guides/go.md#install-and-integrate)\n"
        original = native + legacy + suffix
        result = onboarding.standalone_go(original, selected)
        self.assertTrue(result.startswith(native))
        self.assertNotIn("bindings/go/", result)
        self.assertIn("../go/guides/go.md#install-and-integrate", result)
        self.assertIn("/blob/" + "a" * 40 + "/examples/quick_start/main.go", result)
        self.assertEqual(onboarding.standalone_go(original, []), original)
        self.assertEqual(onboarding.standalone_go(result, selected), result)
        for invalid in (native + legacy + legacy, native + legacy.removesuffix("///\n"),
                        native + legacy.replace("\n///\n", "\n/// tab | Python\n///\n")):
            with self.assertRaises(PluginError):
                onboarding.standalone_go(invalid, selected)

    def test_split_retains_every_source_block_and_rejects_changed_boundaries(self):
        first, build = onboarding.split(SOURCE)
        self.assertEqual(first + "\n" + build.split("\n\n", 1)[1], SOURCE)
        self.assertNotIn("## Build and run tests", first)
        self.assertIn("## Consume Core", first)
        for changed in (SOURCE.replace("## Install and generate", "## Generate"),
                        SOURCE + "\n## New developer section\nNeeds review.\n",
                        SOURCE + "\n## Install and generate distribution archives\n"):
            with self.subTest(changed=changed), self.assertRaises(PluginError):
                onboarding.split(changed)

    def test_assembly_transfers_home_and_keeps_split_source_ownership(self):
        case = fixture.PortalTests(methodName="runTest")
        case.setUp()
        self.addCleanup(case.doCleanups)
        case.write(case.core / "docs" / onboarding.FIRST_PROGRAM, SOURCE)
        case.write(case.portal / "docs/index.md", "# Portal introduction\n")
        case.write(case.portal / "docs/getting-started/overview.md", "# Portal learning path\n")
        with patch.dict("os.environ", {"OPENTLV_DOCS_LOCAL": "1"}):
            config = case.config()
            docs = case.portal / "build/assembled/docs"
            self.assertEqual((docs / "index.md").read_text(), "# Portal introduction\n")
            owners = json.loads((docs.parent / "owners.json").read_text())
            self.assertEqual(owners["index.md"], "portal")
            self.assertEqual(owners[onboarding.FIRST_PROGRAM], owners[onboarding.CORE_BUILD])
            self.assertEqual(owners[onboarding.CORE_BUILD]["id"], "core")
            self.assertEqual(owners[onboarding.CORE_BUILD]["path"], "docs/" + onboarding.FIRST_PROGRAM)
            for name, body in zip((onboarding.FIRST_PROGRAM, onboarding.CORE_BUILD), onboarding.split(SOURCE)):
                self.assertEqual((docs / name).read_text(), body)
                page = SimpleNamespace(file=SimpleNamespace(src_uri=name))
                fixture.hooks.on_page_markdown(body, page, config, Files([]))
                self.assertTrue(page.edit_url.endswith("/docs/" + onboarding.FIRST_PROGRAM))
            self.assertEqual((case.core / "docs" / onboarding.FIRST_PROGRAM).read_text(), SOURCE)
            self.assertTrue((case.core / "docs/index.md").read_text().startswith("# Home"))
            before = (docs / onboarding.FIRST_PROGRAM).read_bytes()
            case.write(case.core / "docs" / onboarding.FIRST_PROGRAM, SOURCE + "\n## Unreviewed\n")
            with self.assertRaisesRegex(PluginError, "review the content split"):
                fixture.assembly.assemble(case.portal)
            self.assertEqual((docs / onboarding.FIRST_PROGRAM).read_bytes(), before)
            case.write(case.core / "docs" / onboarding.FIRST_PROGRAM, SOURCE)
            case.write(case.portal / "docs" / onboarding.CORE_BUILD, "# Cannot replace Core\n")
            with self.assertRaisesRegex(PluginError, "collision"):
                fixture.assembly.assemble(case.portal)

    def test_internal_source_and_api_links_reach_moved_sections(self):
        files = Files([File(name, ".", "site", True) for name in (
            onboarding.FIRST_PROGRAM, onboarding.CORE_BUILD, "getting-started/overview.md")])
        navigation.on_files(files, SimpleNamespace(use_directory_urls=True))
        page = SimpleNamespace(file=SimpleNamespace(src_uri="concepts/architecture.md", url="development/architecture/architecture/"))
        original = "[Tests](../getting-started/README.md#build-and-run-tests)"
        markdown = original + "\n```md\n" + original + "\n```\n"
        result = fixture.hooks.rewrite_source_links(markdown, page, Path("."), {}, "", "", "docs", "concepts", files)
        self.assertTrue(result.startswith("[Tests](../getting-started/core-build.md#build-and-run-tests)"))
        self.assertIn("```md\n" + original, result)
        # A similarly named chapter in a mounted product still belongs there.
        self.assertEqual(fixture.hooks.rewrite_source_links(
            markdown, page, Path("."), {"id": "python"}, "", "", "docs", "concepts", files), markdown)
        source = {"id": "core", "included": True, "repository": "https://github.com/OpenTLV/opentlv",
                  "revision": "a" * 40, "docs_path": "docs", "mount": ""}
        config = SimpleNamespace(extra={"sources": [source]})
        link = f'<a href="{source["repository"]}/blob/{source["revision"]}/docs/getting-started/README.md#build-and-run-tests">Tests</a>'
        result = fixture.hooks.on_page_content(link, page, config, files)
        self.assertIn('../../building/core/#build-and-run-tests', result)
        for fragment, destination in (("quick-start", "tutorials/first-program"),
                                      ("build-and-run-tests", "development/building/core")):
            result = fixture.hooks.api.adapt_html(
                f'<a href="https://fixture.invalid/docs/getting-started/#{fragment}">Guide</a>',
                "api/reference/c-api/html/index.html", "https://fixture.invalid/docs/", files)
            self.assertIn(f'../../../../{destination}/index.html#{fragment}', result)
        self.assertEqual(onboarding.destination(onboarding.FIRST_PROGRAM, "quick-start", files), onboarding.FIRST_PROGRAM)
        self.assertEqual(onboarding.destination(onboarding.FIRST_PROGRAM, "build-and-run-tests", Files([])), onboarding.FIRST_PROGRAM)


if __name__ == "__main__":
    unittest.main()
