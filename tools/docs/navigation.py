# SPDX-License-Identifier: MIT
# Copyright (c) 2026 Marek Cingel

"""Render product manuals separately after MkDocs validates the full inventory."""

import copy

from mkdocs.exceptions import PluginError
from mkdocs.plugins import event_priority
from mkdocs.structure.files import File
from mkdocs.structure.nav import Link, Navigation

# Source names remain repository-owned; only portal output paths change.
# This is a routing table, not a redirect/alias table. No old page is emitted.
PAGE_ROUTES = {
    "formats/overview.md": "standards/index.md",
    "formats/README.md": "api/formats/guide.md",
    "formats/support.md": "api/capabilities.md",
    "api/formats.md": "api/formats/index.md",
    "formats/fixed/configurable.md": "api/formats/fixed/configurable.md",
    "formats/variable.md": "api/formats/variable.md",
    "formats/packed.md": "api/formats/packed.md",
    "formats/escaped.md": "api/formats/escaped.md",
    "formats/custom/README.md": "api/formats/custom/index.md",
    "formats/asn1/ber.md": "standards/asn1/ber.md",
    "formats/asn1/der.md": "standards/asn1/der.md",
    "formats/asn1/cer.md": "standards/asn1/cer.md",
    "formats/bluetooth/README.md": "standards/bluetooth/index.md",
    "formats/nfc/README.md": "standards/nfc/index.md",
    "formats/dhcp/README.md": "standards/dhcp/index.md",
    "formats/lldp/README.md": "standards/lldp/index.md",
    "formats/lldp/conformance.md": "standards/lldp/conformance.md",
    "formats/format-examples.md": "tutorials/formats.md",
    "formats/format-roadmap.md": "development/planning/format-roadmap.md",
    "formats/format-catalogue.md": "development/planning/format-catalogue.md",
    "formats/lldp-review.md": "development/planning/lldp-review.md",
    "getting-started/overview.md": "tutorials/index.md",
    "getting-started/README.md": "tutorials/first-program.md",
    "getting-started/core-build.md": "development/building/core.md",
    "concepts/learning-model.md": "tutorials/concepts/learning-model.md",
    "concepts/core-types.md": "api/concepts/core-types.md",
    "concepts/value.md": "api/concepts/value.md",
    "concepts/length.md": "api/concepts/length.md",
    "concepts/endian.md": "api/concepts/endian.md",
    "guides/processing.md": "tutorials/processing.md",
    "guides/examples.md": "tutorials/examples.md",
    "guides/select-components.md": "api/configuration.md",
    "concepts/field-policies.md": "development/architecture/field-policies.md",
    "concepts/format-capabilities.md": "api/concepts/format-capabilities.md",
    "standards/emv/README.md": "standards/emv/index.md",
    "concepts/bindings.md": "languages/contracts.md",
    "guides/reader.md": "api/guides/reader.md",
    "guides/writer.md": "api/guides/writer.md",
    "guides/document.md": "api/guides/document.md",
    "guides/diagnostics.md": "api/guides/diagnostics.md",
    "guides/queries.md": "api/guides/queries.md",
    "guides/schemas.md": "api/guides/schemas.md",
    "guides/codecs.md": "api/guides/codecs.md",
    "guides/memory.md": "api/guides/memory.md",
    "guides/copy.md": "api/guides/copy.md",
    "guides/cxx-examples.md": "tutorials/cpp-examples.md",
    "concepts/cxx-native-boundary.md": "languages/cpp/concepts/cxx-native-boundary.md",
    "concepts/cxx-formats.md": "languages/cpp/concepts/cxx-formats.md",
    "concepts/cxx-builtins.md": "languages/cpp/concepts/cxx-builtins.md",
    "reference/README.md": "api/reference/index.md",
    "reference/c-api.md": "api/reference/c/index.md",
    "reference/cxx-api.md": "api/reference/cpp/index.md",
    "reference/errors.md": "api/reference/errors.md",
    "concepts/query-language.md": "api/query-language.md",
    "guides/rust.md": "languages/rust/manual/index.md",
    "guides/go.md": "languages/go/manual/index.md",
    "guides/python.md": "languages/python/core-transition.md",
    "guides/lua.md": "languages/lua/core-transition.md",
    "development/webassembly.md": "languages/wasm/development.md",
    "playground/index.md": "tools/playground/index.md",
    "concepts/architecture.md": "development/architecture/architecture.md",
    "concepts/runtime-model.md": "development/architecture/runtime-model.md",
    "concepts/processing-pipeline.md": "development/architecture/processing-pipeline.md",
    "concepts/architectural-rules.md": "development/architecture/architectural-rules.md",
    "concepts/error-model.md": "development/architecture/error-model.md",
    "concepts/format-contract.md": "api/concepts/format-contract.md",
    "concepts/definition-boundaries.md": "development/architecture/definition-boundaries.md",
    "reference/compilers.md": "development/building/compilers.md",
    "development/rust.md": "languages/rust/manual/development.md",
    "development/python.md": "development/bindings/python.md",
    "development/go.md": "languages/go/manual/development.md",
    "development/lua.md": "development/bindings/lua.md",
    "development/documentation-layout.md": "development/documentation/layout.md",
    "development/documentation-ownership.md": "development/documentation/ownership.md",
    "development/documentation-audit.md": "development/documentation/audit-513.md",
    "assets/README.md": "development/documentation/assets.md",
}
PRODUCT_ROUTES = {"cli/": "tools/otlv/manual/", "lua/": "languages/lua/manual/",
                  "python/": "languages/python/manual/"}

# Presentation notes reconcile old portal instructions without maintaining an
# edited copy of the owner's technical Markdown. Keep the original text intact.
DEVELOPMENT_NOTES = {
    "development/documentation-layout.md": (
        "Core writing conventions remain authoritative for its sources. The portal "
        "hierarchy and combined DER/CER presentation have evolved; the "
        "source directories and former navigation described below are not the "
        "current portal hierarchy."
    ),
    "development/documentation-ownership.md": (
        "Retain this Core ownership inventory and extraction history as source "
        "evidence. CLI, Lua and Python manuals are already selected from their "
        "standalone repositories in this portal. Pending portal-cutover statements "
        "and the old deployment sequence below describe the historical migration."
    ),
    "development/documentation-audit.md": (
        "This is the historical Core #513 audit. Its paths, inventory and validation "
        "describe that review, not the current portal hierarchy or a fresh validation run."
    ),
    "development/python.md": (
        "This portal already selects the standalone Python manual. The pending "
        "portal-cutover statement below is historical. Core still owns the diagnostic "
        "vocabulary generator, native fixtures and dependency coordination; "
        "[Python development](../python/development/python.md) owns standalone build instructions."
    ),
}


@event_priority(50)
def on_files(files, config):
    # Run before API guide-link adaptation. MkDocs resolves source-relative
    # Markdown and HTML links against src_uri and renders them using dest_uri.
    # Keeping src_uri also preserves original edit links and assembly ownership.
    for file in files.documentation_pages():
        target = PAGE_ROUTES.get(file.src_uri)
        if file.src_uri.startswith("bindings/"):
            target = "languages/" + file.src_uri[len("bindings/"):]
        for prefix, destination in PRODUCT_ROUTES.items():
            if file.src_uri.startswith(prefix):
                target = destination + file.src_uri[len(prefix):]
                break
        if target:
            destination = File(target, file.src_dir, file.dest_dir, config.use_directory_urls)
            # Material identifies section indexes by File.name, not URL alone.
            file.name = destination.name
            file.dest_uri = destination.dest_uri
            file.url = destination.url
            file.abs_dest_path = destination.abs_dest_path
    return files


def sequence(pages):
    """Keep previous/next links within one documentation context."""
    for index, page in enumerate(pages):
        page.previous_page = pages[index - 1] if index else None
        page.next_page = pages[index + 1] if index + 1 < len(pages) else None


def on_page_markdown(markdown, page, config, files):
    # The new contributor landing also supports the exact historical Core
    # revision accepted by assembly; do not hide missing pages in other builds.
    core = config.extra.get("core_source", {})
    if (page.file.src_uri in {"development/index.md", "development/testing.md",
                             "development/releases.md", "development/documentation.md"}
            and core.get("repository") == "https://github.com/OpenTLV/opentlv"
            and core.get("commit") == "e12a52ff69a64468eecab084795a0530c273efea"):
        markdown = markdown.replace("[quality gates](quality-gates.md)",
                                    "[development workflow](workflow.md)")
        markdown = markdown.replace("[Core quality gates](quality-gates.md)",
                                    "[Core development workflow](workflow.md)")
        markdown = markdown.replace("[ownership guide](documentation-ownership.md)",
                                    "[documentation audit](documentation-audit.md)")
        markdown = markdown.replace("[ownership inventory](documentation-ownership.md)",
                                    "[documentation audit](documentation-audit.md)")
        markdown += ("\nThis historical Core version predates the separate quality-gates and\n"
                     "documentation-ownership pages; the links above use its workflow and audit.\n")
    note = DEVELOPMENT_NOTES.get(page.file.src_uri)
    if note and files.get_file_from_path("development/documentation.md") is not None:
        # A component's independent manual has no portal guidance page. Add notes
        # only in an assembled portal and retain its original source/edit owner.
        title, separator, body = markdown.partition("\n")
        markdown = (title + '\n\n!!! note "Portal context"\n\n    ' + note
                    + " See [current portal conventions](documentation.md) for "
                    "hierarchy, ownership and publication entry points.\n"
                    + separator + body)
    return markdown


def on_nav(nav, config, files):
    destinations = {}
    for file in files:
        key = file.dest_uri.casefold()
        if key in destinations:
            raise PluginError(f"Portal output collision: {destinations[key]} and {file.src_uri}")
        destinations[key] = file.src_uri
    # Assembly includes all manuals in the inventory. Only their presentation
    # is separated: no excluded technical content or guessed release redirects.
    products = {}
    for source in config.extra.get("sources", []):
        if source["id"] == "core" or not source["included"]:
            continue
        definition = source["navigation"]
        if definition["section"]:
            raise PluginError("Product navigation must be separate from portal sections.")
        sections = [item for item in nav.items
                    if item.is_section and item.title == definition["title"]]
        if len(sections) != 1:
            raise PluginError(f"Missing or ambiguous product navigation: {source['id']}")
        section = sections[0]
        prefix = source["mount"].rstrip("/") + "/"
        pages = [page for page in nav.pages if page.file.src_uri.startswith(prefix)]
        for item in section.children:
            item.parent = None
        product = Navigation([Link("OpenTLV portal", nav.homepage.url), *section.children], pages)
        product.homepage = nav.homepage
        sequence(pages)
        for page in pages:
            products[page.file.src_uri] = (product, source)
        nav.items.remove(section)
        nav.pages = [page for page in nav.pages if page not in pages]
    sequence(nav.pages)
    config.extra["product_navigation"] = products
    return nav


def on_page_context(context, page, config, nav):
    selected = config.extra.get("product_navigation", {}).get(page.file.src_uri)
    if selected is None:
        return context
    product, source = selected
    context["nav"] = product
    context["product_source"] = source
    # A page-local configuration keeps Material's desktop sidebar and mobile
    # drawer, without treating manual chapters as global tabs. These manuals
    # are pinned to the portal snapshot; its version selector is not a product
    # release selector. Independent publication keeps its own configuration.
    presentation = copy.copy(config)
    presentation.theme = copy.deepcopy(config.theme)
    presentation.theme["features"] = [feature for feature in config.theme["features"]
                                      if feature not in ("navigation.tabs", "navigation.sections")]
    presentation.extra = dict(config.extra)
    presentation.extra.pop("version", None)
    context["config"] = presentation
    return context
