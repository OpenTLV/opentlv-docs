# SPDX-License-Identifier: MIT
# Copyright (c) 2026 Marek Cingel

"""Present complete Core-owned format blocks in a consistent reading order."""

import posixpath
import re
from urllib.parse import urlsplit, urlunsplit

from mkdocs.exceptions import PluginError

SECTIONS = ("Overview", "Format structure", "Encoding rules", "Supported capabilities",
            "Examples", "Limitations", "References")
MERGES = {f"standards/{kind}/README.md": f"formats/asn1/{kind}.md" for kind in ("der", "cer")}

# These older introductions embed wire tables/examples before their first H2.
# Move complete tails at reviewed boundaries; do not copy their technical text.
INTRO_SPLITS = {
    "formats/packed.md": (("It is always built, independently of\n", 3), ("```c\n", 4)),
    "formats/nfc/README.md": (("| Identifier | Name | Framing |\n", 1),),
    "formats/dhcp/README.md": (("The descriptor implements the option framing in\n", 1),
                              ("For example, `35 01 01`", 4)),
}

# Explicit source headings make source changes reviewable: no unmatched block
# can silently disappear. Values are positions in the common section sequence.
PLANS = {
    "formats/fixed/configurable.md": {
        "API and build": 3, "Standalone Field Encoding": 2, "Supported parameters": 3,
        "Wire representation": 1, "Errors": 5, "Example (C)": 4, "Example (C++)": 4,
        "Example (C++, runtime-configurable)": 4,
    },
    "formats/variable.md": {
        "Identifier encoding": 1, "Length encoding": 2, "Complete format": 4,
        "Declarative policies": 3, "Concrete rules and terminated framing": 5,
    },
    "formats/packed.md": {
        "Configuration and lifetime": 1, "Length and source ranges": 2,
        "Protocol and binding scope": 5,
    },
    "formats/bluetooth/README.md": {
        "API and build": 3, "Advertising Data Type definitions": 3,
        "Basic Advertising Data value codecs": 3, "Advertising Data schema": 3,
        "Advertising Data containers and padding": 3, "Wire representation and logical model": 1,
        "Length semantics": 2, "Differences from conventional TLV": 1, "Parsing": 4,
        "UUID values and lists": 3, "Service Data": 3,
        "Manufacturer Specific Data and Company Identifiers": 3, "Encoding": 2,
        "Unknown types": 5, "Malformed input": 5, "Limitations": 5,
        "Byte example": 4, "How it fits the format architecture": 6,
    },
    "formats/nfc/README.md": {
        "Length encoding": 2, "Input and source ownership": 5, "Example": 4,
        "Bindings": 3, "Generic composition": 1,
    },
    "formats/dhcp/README.md": {
        "Element and source contracts": 2, "Option definitions": 3,
        "Value codecs": 4, "Scope and composition": 5,
    },
    "formats/lldp/README.md": {
        "API and build": 3, "Wire representation and logical model": 1,
        "Scope and errors": 5, "Schema and sequence validation": 3,
        "Value codecs": 2, "Coverage of #362 and #363": 3, "Presets in bindings": 4,
    },
    "formats/asn1/ber.md": {
        "API and build": 3, "Scope and limits": 5, "Generic mechanics and ASN.1 rules": 2,
        "Minimal C usage": 4, "Framing and typical use": 1, "Byte example": 4,
        "Shared ASN.1 mechanisms": 6,
    },
    "formats/asn1/der.md": {
        "API and build": 3, "Scope and limits": 5, "Minimal C usage": 4,
        "Framing and typical use": 1, "Byte example": 4,
    },
    "formats/asn1/cer.md": {
        "API and build": 3, "Scope and limits": 5, "Minimal C usage": 4,
        "Framing and typical use": 1, "Byte example: nested indefinite-length containers": 4,
    },
    "standards/der/README.md": {
        "Supported scope": 3, "Read and inspect a tag": 4, "Traverse and limit work": 5,
        "Encode": 2, "Strict universal value validation": 3,
        "Schema-aware validation and encoding": 3, "Errors and generic I/O": 5,
    },
    "standards/cer/README.md": {
        "Supported scope": 3, "Read and traverse": 4, "Canonical string segmentation": 2,
        "Zero-copy access to segments": 4, "Encode": 2,
        "Strict universal value validation": 3, "Errors, offsets and limits": 5,
    },
    "standards/emv/README.md": {
        "Migration from the X-macro dictionary (#381)": 6, "Framing and lookup": 1,
        "Contexts": 3, "Value representations": 2, "Diagnostics and tooling": 3,
        "Validation limits": 5, "Structural validation": 3,
        "Data Object Lists (PDOL/CDOL/DDOL)": 3, "Byte example": 4, "Example": 4,
    },
}

REFERENCES = {
    "asn1": "[ITU-T X.690](https://www.itu.int/rec/T-REC-X.690-202102-I/en)",
    "bluetooth": "[Bluetooth Core GAP](https://www.bluetooth.com/wp-content/uploads/Files/Specification/HTML/Core-60/out/en/host/generic-access-profile.html) and [Core Specification Supplement](https://www.bluetooth.com/wp-content/uploads/Files/Specification/HTML/CSS_v12/out/en/supplement-to-the-bluetooth-core-specification/data-types-specification.html)",
    "dhcp": "[RFC 2132](https://www.rfc-editor.org/rfc/rfc2132.html#section-2)",
    "nfc": "[NFC Forum Type 2 Tag Operation Specification 1.1, section 2.3](https://community.nxp.com/pwmxy87654/attachments/pwmxy87654/nfc/3252/1/NFCForum-Type-2-Tag_1.1%20Specification.pdf)",
    "lldp": "[IEEE 802.1AB-2016 publication record](https://standards.ieee.org/ieee/802.1AB/6047/) and [conformance boundary](conformance.md)",
    "emv": "[EMVCo Book 3 v4.4](https://www.emvco.com/specifications/book-3-application-specification-2/)",
}


def prose_lines(markdown):
    """Yield lines with a flag; fenced examples must remain byte-for-byte intact."""
    fence = None
    for line in markdown.splitlines(keepends=True):
        match = re.match(r"^ {0,3}(`{3,}|~{3,})(.*)$", line.rstrip("\r\n"))
        if fence:
            if match and match[1][0] == fence[0] and len(match[1]) >= len(fence) and not match[2].strip():
                fence = None
            yield line, False
        elif match:
            fence = match[1]
            yield line, False
        else:
            yield line, True


def blocks(markdown):
    """Separate only top-level Markdown sections, retaining every body line."""
    title, separator, rest = markdown.partition("\n")
    if not separator or not title.startswith("# "):
        raise PluginError("Format source needs a single leading title.")
    result = [(None, [])]
    for line, prose in prose_lines(rest):
        if prose and line.startswith("## "):
            result.append((line[3:].strip(), [line]))
        else:
            result[-1][1].append(line)
    return title, [(heading, "".join(lines)) for heading, lines in result]


def rebase(markdown, source, target):
    """Keep links relative to their original Core document when joining pages."""
    if source == target:
        return markdown

    def link(match):
        prefix, url, suffix = match.groups()
        parts = urlsplit(url)
        if parts.scheme or parts.netloc or parts.path.startswith("/"):
            return match[0]
        resolved = posixpath.normpath(posixpath.join(posixpath.dirname(source), parts.path)) if parts.path else source
        relative = posixpath.relpath(resolved, posixpath.dirname(target))
        return prefix + urlunsplit(("", "", relative, parts.query, parts.fragment)) + suffix

    pattern = re.compile(r"(\[[^\]]*\]\()([^\s)]+)(\))")
    return "".join(pattern.sub(link, line) if prose else line for line, prose in prose_lines(markdown))


def demote(markdown):
    return "".join("#" + line if prose and re.match(r"^#{2,5} ", line) else line
                   for line, prose in prose_lines(markdown))


def introduction(source, markdown):
    parts = []
    index = 0
    for marker, next_index in INTRO_SPLITS.get(source, ()):
        if markdown.count(marker) != 1:
            raise PluginError(f"Format introduction changed in {source}; review the presentation mapping.")
        before, after = markdown.split(marker)
        parts.append((index, before.strip()))
        index, markdown = next_index, marker + after
    parts.append((index, markdown.strip()))
    return parts


def render(target, documents):
    """Regroup reviewed sections without maintaining technical prose in Portal."""
    groups = [[] for _ in SECTIONS]
    title = None
    for source, markdown in documents:
        source_title, sections = blocks(rebase(markdown, source, target))
        title = title or source_title
        headings = [heading for heading, _ in sections if heading is not None]
        if len(headings) != len(set(headings)) or set(headings) != set(PLANS[source]):
            raise PluginError(f"Format sections changed in {source}; review the presentation mapping.")
        for index, intro in introduction(source, sections[0][1]):
            if source != target:
                intro = "### Validation overview\n\n" + intro
            groups[index].append(intro)
        for heading, body in sections[1:]:
            index = PLANS[source][heading]
            # An existing heading matching the common section gets that same ID.
            if heading == SECTIONS[index]:
                body = body.split("\n", 1)[1]
            else:
                body = demote(body)
            groups[index].append(body.strip())
    family = target.split("/")[1]
    reference = REFERENCES.get(family, "The OpenTLV configuration contract on this page (no external protocol standard).")
    base = posixpath.dirname(target)
    shared = posixpath.relpath("concepts/format-capabilities.md", base)
    generic = target in {"formats/fixed/configurable.md", "formats/variable.md", "formats/packed.md"}
    catalog = posixpath.relpath("api/formats.md" if generic else "formats/overview.md", base)
    label = "Generic formats" if generic else "Standards catalog"
    groups[6].append(f"{reference}\n\n[Shared Format concepts]({shared}) · [{label}]({catalog})")
    # Some source pages combine structure/examples with their introduction.
    # Do not invent duplicate technical text merely to fill an empty section.
    return title + "\n\n" + "\n\n".join(
        "## " + section + "\n\n" + "\n\n".join(parts)
        for section, parts in zip(SECTIONS, groups) if parts
    ) + "\n"


def destination(uri, files):
    target = MERGES.get(uri)
    if target and files.get_file_from_path(uri) is None and files.get_file_from_path(target) is not None:
        return target
    return uri
