# SPDX-License-Identifier: MIT
# Copyright (c) 2026 Marek Cingel

"""Split Core's onboarding at a reviewed section boundary, without copying sources."""

import re

from mkdocs.exceptions import PluginError

FIRST_PROGRAM = "getting-started/README.md"
CORE_BUILD = "getting-started/core-build.md"
BUILD_SECTIONS = (
    "Install and generate distribution archives",
    "C-only build",
    "Build and run tests",
)
BUILD_FRAGMENTS = frozenset(title.lower().replace(" ", "-") for title in BUILD_SECTIONS)


def split(markdown):
    """Retain every original block; reject changed boundaries before publishing."""
    boundary = "## " + BUILD_SECTIONS[0] + "\n"
    if markdown.count(boundary) != 1:
        raise PluginError("Core onboarding needs one reviewed archive/install section boundary.")
    first, build = markdown.split(boundary)
    build = boundary + build
    if re.findall(r"^## (.+)$", build, re.MULTILINE) != list(BUILD_SECTIONS):
        raise PluginError("Core onboarding build sections changed; review the content split.")
    return first.rstrip() + "\n", "# Core installation and developer builds\n\n" + build


def standalone_go(markdown, selected):
    """Route the transitional Core tutorial to the selected Go owner.

    Keep the canonical Core file intact. The portal must not teach its obsolete
    subtree import while selecting a standalone Go manual and example sources.
    """
    go = next((item for _, item in selected if item["id"] == "go" and item["included"]), None)
    if go is None:
        return markdown
    opening = "/// tab | Go\n"
    if opening in markdown:
        if markdown.count(opening) != 1:
            raise PluginError("Core onboarding needs one reviewed Go tab.")
        before, body = markdown.split(opening)
        end = re.search(r"^///\s*$", body, re.MULTILINE)
        if end is None or re.search(r"^/// tab \|", body[:end.start()], re.MULTILINE):
            raise PluginError("Core onboarding Go tab boundary changed; review the handoff.")
        if "bindings/go/" in body[:end.start()]:
            source = go["repository"] + "/blob/" + go["commit"] + "/examples/quick_start/main.go"
            body = (
                "\nUse the [standalone Go guide](../go/guides/go.md#install-and-integrate) "
                "for setup and the quick-start command, then read the "
                f"[selected runnable source]({source}). "
                "Go owns the current import path and native dependency setup.\n\n"
                "The [executable examples](../guides/examples.md) catalog includes "
                "owner-supplied examples when available at the selected revision.\n\n"
                + body[end.start():]
            )
            markdown = before + opening + body
    return markdown.replace("](../guides/go.md", "](../go/guides/go.md")


def destination(uri, fragment, files):
    """Resolve links to moved sections, never emit old fragments or redirect pages."""
    if (uri == FIRST_PROGRAM and fragment in BUILD_FRAGMENTS
            and files.get_file_from_path(CORE_BUILD) is not None):
        return CORE_BUILD
    return uri
