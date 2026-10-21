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


def destination(uri, fragment, files):
    """Resolve links to moved sections, never emit old fragments or redirect pages."""
    if (uri == FIRST_PROGRAM and fragment in BUILD_FRAGMENTS
            and files.get_file_from_path(CORE_BUILD) is not None):
        return CORE_BUILD
    return uri
