# SPDX-License-Identifier: MIT
# Copyright (c) 2026 OpenTLV
"""Exact bootstrap compatibility for the standalone JS documentation handoff."""

BOOTSTRAP_COMMIT = "037fde09d3caf26f32071911ebc78c63cb84f2e0"
MANUAL = "js/webassembly.md"


def bootstrap(source):
    # The reviewed layout baseline predates the manual transfer. Never hide a
    # missing manual for arbitrary later pins or for an uncommitted preview.
    return (source.get("id") == "js"
            and source.get("repository") == "https://github.com/OpenTLV/opentlv-js"
            and source.get("commit") == BOOTSTRAP_COMMIT
            and not source.get("local"))


def ready(sources):
    return any(item["id"] == "js" and item["included"] and not bootstrap(item)
               for item in sources)
