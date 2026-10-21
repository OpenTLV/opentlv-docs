# SPDX-License-Identifier: MIT
# Copyright (c) 2026 Marek Cingel

"""Verify format preservation, source ownership and canonical merged links."""

import json
from pathlib import Path
from types import SimpleNamespace
import unittest
from unittest.mock import patch

from mkdocs.exceptions import PluginError
from mkdocs.structure.files import File, Files

import test_portal as fixture

formats = fixture.assembly.formats
navigation = fixture.load_hook("navigation")


def source(name):
    intro = "# Source title\n\nOverview from " + name + ".\n\n"
    for marker, _ in formats.INTRO_SPLITS.get(name, ()):
        intro += marker + "\nPreserved introductory details.\n"
        if marker == "```c\n":
            intro += "```\n"
        intro += "\n"
    return intro + "".join(
        f"## {heading}\n\nPreserved contract: {name}: {heading}.\n\n"
        "```c\n## This is source code, not a section\n"
        "/* [example](../relative.md) */\n```\n\n"
        for heading in formats.PLANS[name]
    )


class FormatTests(unittest.TestCase):
    def test_generic_and_standard_guides_link_their_own_catalogs(self):
        generic = "formats/packed.md"
        standard = "formats/bluetooth/README.md"
        generic_output = formats.render(generic, [(generic, source(generic))])
        standard_output = formats.render(standard, [(standard, source(standard))])
        self.assertIn("[Generic formats](../api/formats.md)", generic_output)
        self.assertNotIn("[Standards catalog]", generic_output)
        self.assertIn("[Standards catalog](../overview.md)", standard_output)
        self.assertNotIn("[Generic formats]", standard_output)

    def test_every_source_body_and_fenced_example_survives_regrouping(self):
        for name in formats.PLANS.keys() - formats.MERGES.keys():
            parts = [name] + [part for part, target in formats.MERGES.items() if target == name]
            output = formats.render(name, [(part, source(part)) for part in parts])
            headings = [line[3:].strip() for line, prose in formats.prose_lines(output)
                        if prose and line.startswith("## ")]
            self.assertEqual(headings, list(formats.SECTIONS))
            for part in parts:
                self.assertIn("Overview from " + part, output)
                for heading in formats.PLANS[part]:
                    self.assertEqual(output.count(f"Preserved contract: {part}: {heading}."), 1)
            count = sum(len(formats.PLANS[part]) for part in parts)
            self.assertEqual(output.count("```c\n## This is source code, not a section\n"
                                          "/* [example](../relative.md) */\n```"), count)

    def test_source_drift_is_rejected_instead_of_losing_sections(self):
        name = "formats/asn1/der.md"
        original = source(name)
        for changed in (original + "\n## New scope\nNew rules.\n",
                        original.replace("## Scope and limits", "## Changed heading"),
                        original + "\n## Scope and limits\nDuplicate.\n"):
            with self.subTest(changed=changed), self.assertRaisesRegex(PluginError, "review the presentation mapping"):
                formats.render(name, [(name, changed)])
        name = "formats/packed.md"
        changed = source(name).replace("```c\n\nPreserved introductory", "```cpp\n\nPreserved introductory")
        with self.assertRaisesRegex(PluginError, "review the presentation mapping"):
            formats.render(name, [(name, changed)])

    def test_assembly_retains_both_core_owners_and_fails_before_replacing_output(self):
        case = fixture.PortalTests(methodName="runTest")
        case.setUp()
        self.addCleanup(case.doCleanups)
        for name in formats.PLANS:
            case.write(case.core / "docs" / name, source(name))
        case.write(case.portal / "docs/formats/overview.md", "# Formats\n")
        with patch.dict("os.environ", {"OPENTLV_DOCS_LOCAL": "1"}):
            config = case.config()
            docs = case.portal / "build/assembled/docs"
            owners = json.loads((docs.parent / "owners.json").read_text())
            self.assertEqual(owners["formats/overview.md"], "portal")
            for old, target in formats.MERGES.items():
                self.assertFalse((docs / old).exists())
                self.assertNotIn(old, owners)
                self.assertEqual(owners[target]["parts"], ["docs/" + target, "docs/" + old])
                self.assertEqual(owners[target]["id"], "core")
                page = SimpleNamespace(file=SimpleNamespace(src_uri=target), meta={})
                fixture.hooks.on_page_markdown((docs / target).read_text(), page, config, Files([]))
                self.assertTrue(page.edit_url.endswith("/docs/" + target))
                for item, name in zip(page.meta["format_sources"], (target, old)):
                    self.assertTrue(item["source"].endswith("/docs/" + name))
                    self.assertTrue(item["edit"].endswith("/docs/" + name))
                self.assertEqual((case.core / "docs" / old).read_text(), source(old))
            before = (docs / "formats/asn1/der.md").read_bytes()
            case.write(case.core / "docs/standards/der/README.md", source("standards/der/README.md") + "\n## New rules\n")
            with self.assertRaisesRegex(PluginError, "review the presentation mapping"):
                fixture.assembly.assemble(case.portal)
            self.assertEqual((docs / "formats/asn1/der.md").read_bytes(), before)

    def test_merge_rebases_local_anchors_and_links_but_never_examples(self):
        markdown = ("[Schema](#schema-aware-validation-and-encoding)\n"
                    "[CER](../cer/README.md#encode)\n"
                    "[External](https://example.invalid/guide)\n"
                    "```md\n[Example](../cer/README.md)\n```\n")
        result = formats.rebase(markdown, "standards/der/README.md", "formats/asn1/der.md")
        self.assertIn("(../../standards/der/README.md#schema-aware-validation-and-encoding)", result)
        self.assertIn("(../../standards/cer/README.md#encode)", result)
        self.assertIn("[External](https://example.invalid/guide)", result)
        self.assertIn("```md\n[Example](../cer/README.md)\n```", result)

    def test_internal_repository_and_generated_api_links_reach_canonical_pages(self):
        files = Files([File(name, ".", "site", True) for name in (
            "formats/overview.md", "formats/README.md", "formats/asn1/der.md", "formats/asn1/cer.md")])
        navigation.on_files(files, SimpleNamespace(use_directory_urls=True))
        page = SimpleNamespace(file=SimpleNamespace(src_uri="formats/support.md", url="api/capabilities/"))
        markdown = "[DER](../standards/der/README.md#encode)"
        result = fixture.hooks.rewrite_source_links(markdown, page, Path("."), {}, "", "", "docs", "formats", files)
        self.assertEqual(result, "[DER](asn1/der.md#encode)")
        # A mounted product's similarly named document is not a Core source.
        self.assertEqual(fixture.hooks.rewrite_source_links(
            markdown, page, Path("."), {"id": "python"}, "", "", "docs", "formats", files), markdown)
        core = {"id": "core", "included": True, "repository": "https://github.com/OpenTLV/opentlv",
                "revision": "a" * 40, "docs_path": "docs", "mount": ""}
        config = SimpleNamespace(extra={"sources": [core]})
        for kind in ("der", "cer"):
            html = f'<a href="{core["repository"]}/blob/{core["revision"]}/docs/standards/{kind}/README.md#encode">Encode</a>'
            result = fixture.hooks.on_page_content(html, page, config, files)
            self.assertIn(f'../../standards/asn1/{kind}/#encode', result)
            result = fixture.hooks.api.adapt_html(
                f'<a href="https://fixture.invalid/docs/standards/{kind}/#encode">Encode</a>',
                "api/reference/c-api/html/index.html", "https://fixture.invalid/docs/", files)
            self.assertIn(f'../../../../standards/asn1/{kind}/index.html#encode', result)
        self.assertEqual(files.get_file_from_path("formats/overview.md").url, "standards/")
        self.assertEqual(files.get_file_from_path("formats/README.md").url, "api/formats/guide/")


if __name__ == "__main__":
    unittest.main()
