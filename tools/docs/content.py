# SPDX-License-Identifier: MIT
# Copyright (c) 2026 Marek Cingel

"""Reviewed portal presentation; canonical component sources remain unchanged."""

HISTORY_INDEX = "development/history.md"
COMPONENT_INDEX = "development/components.md"

# These records retain their complete source bodies and edit owners. Only the
# combined portal archives them; independent product publications use their
# original navigation and paths.
ARCHIVES = {
    "guides/python.md": ("core", "Python extraction guide", "guides/python.md",
                         "python/guides/python.md", "current Python manual"),
    "development/rust.md": ("core", "Core Rust development guide", "development/rust.md",
                            "rust/development/rust.md", "current Rust development guide"),
    "development/documentation-audit.md": (
        "core", "Documentation audit (#513)", "documentation-audit.md",
        "development/documentation.md", "current documentation conventions"),
    "development/query-phase-audit.md": (
        "core", "Query phase implementation audit", "query-phase-audit.md",
        "development/query-adversarial.md", "current query verification guide"),
    "development/reader-decode-performance.md": (
        "core", "Reader decode performance report", "reader-decode-performance.md",
        "development/testing.md", "current testing entry points"),
    "development/cxx-facade-performance.md": (
        "core", "C++ facade performance report", "cxx-facade-performance.md",
        "development/testing.md", "current testing entry points"),
    "lua/migration.md": ("lua", "Lua migration provenance", "migration.md",
                         "lua/development.md", "current Lua build guide"),
    "python/migration.md": ("python", "Python migration provenance", "migration.md",
                            "python/development/python.md", "current Python development guide"),
    "python/validation/standalone-build.md": (
        "python", "Python standalone build validation", "validation/standalone-build.md",
        "python/development/python.md", "current Python build guide"),
    "python/validation/ci.md": (
        "python", "Python CI validation", "validation/ci.md",
        "python/quality-gates.md", "current Python quality gates"),
    "python/validation/packaging.md": (
        "python", "Python packaging validation", "validation/packaging.md",
        "python/releases.md", "current Python release guide"),
    "python/validation/layout.md": (
        "python", "Python source layout validation", "validation/layout.md",
        "python/development/python.md", "current Python development guide"),
    "rust/migration.md": ("rust", "Rust migration provenance", "migration.md",
                          "rust/development/rust.md", "current Rust development guide"),
    "rust/validation/standalone-build.md": (
        "rust", "Rust standalone build validation", "validation/standalone-build.md",
        "rust/development/rust.md", "current Rust build guide"),
    "rust/validation/ci.md": (
        "rust", "Rust CI validation", "validation/ci.md",
        "rust/quality-gates.md", "current Rust quality gates"),
    "rust/validation/packaging.md": (
        "rust", "Rust packaging validation", "validation/packaging.md",
        "rust/packaging.md", "current Rust packaging guide"),
    "rust/validation/layout.md": (
        "rust", "Rust source layout validation", "validation/layout.md",
        "rust/development/rust.md", "current Rust development guide"),
}

COMPONENT_GUIDES = {
    "cli/development.md": ("cli", "CLI development"),
    "cli/releases.md": ("cli", "CLI versions and releases"),
    "lua/testing.md": ("lua", "Lua tests and CI"),
    "lua/quality-gates.md": ("lua", "Lua quality gates"),
    "lua/implementation.md": ("lua", "Lua implementation and ownership"),
    "lua/releases.md": ("lua", "Lua release quality gate"),
    "python/quality-gates.md": ("python", "Python tests and CI"),
    "python/releases.md": ("python", "Python release preparation"),
    "rust/quality-gates.md": ("rust", "Rust tests and CI"),
}


def route(name, history=False, components=False):
    if history and name in ARCHIVES:
        owner, _title, path, _current, _label = ARCHIVES[name]
        return f"development/history/{owner}/{path}"
    if components and name in COMPONENT_GUIDES:
        return "development/components/" + name
    return None


def group(items, overview):
    """Find the explicit portal destination, never invent a missing section."""
    for entry in items:
        if not isinstance(entry, dict):
            continue
        for value in entry.values():
            if isinstance(value, list):
                if any(isinstance(child, dict) and overview in child.values() for child in value):
                    return value
                found = group(value, overview)
                if found is not None:
                    return found
    return None


def relocate(items, base):
    """Move reviewed, present product entries into the portal's Development nav.

    Unknown entries are retained so full-inventory validation still detects new
    or missing sources. The source registration remains the independent manual's
    complete inventory.
    """
    destinations = [(ARCHIVES, group(base, HISTORY_INDEX)),
                    (COMPONENT_GUIDES, group(base, COMPONENT_INDEX))]

    def visit(entries):
        result = []
        for entry in entries:
            if isinstance(entry, str):
                for records, destination in destinations:
                    if destination is not None and entry in records:
                        destination.append({records[entry][1]: entry})
                        break
                else:
                    result.append(entry)
                continue
            for title, value in entry.items():
                if isinstance(value, list):
                    children = visit(value)
                    if children:
                        result.append({title: children})
                else:
                    for records, destination in destinations:
                        if destination is not None and value in records:
                            destination.append({records[value][1]: value})
                            break
                    else:
                        result.append({title: value})
        return result

    return visit(items)
