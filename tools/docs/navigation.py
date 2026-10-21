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
    "concepts/learning-model.md": "getting-started/concepts/learning-model.md",
    "concepts/core-types.md": "getting-started/concepts/core-types.md",
    "concepts/value.md": "getting-started/concepts/value.md",
    "concepts/length.md": "getting-started/concepts/length.md",
    "concepts/endian.md": "getting-started/concepts/endian.md",
    "guides/processing.md": "getting-started/processing.md",
    "guides/examples.md": "getting-started/examples.md",
    "guides/select-components.md": "getting-started/select-components.md",
    "concepts/field-policies.md": "formats/concepts/field-policies.md",
    "concepts/format-capabilities.md": "formats/concepts/capabilities.md",
    "standards/emv/README.md": "formats/emv/index.md",
    "standards/der/README.md": "formats/asn1/der-validation.md",
    "standards/cer/README.md": "formats/asn1/cer-validation.md",
    "concepts/bindings.md": "bindings/contracts.md",
    "guides/reader.md": "bindings/c/guides/reader.md",
    "guides/writer.md": "bindings/c/guides/writer.md",
    "guides/document.md": "bindings/c/guides/document.md",
    "guides/diagnostics.md": "bindings/c/guides/diagnostics.md",
    "guides/queries.md": "bindings/c/guides/queries.md",
    "guides/schemas.md": "bindings/c/guides/schemas.md",
    "guides/codecs.md": "bindings/c/guides/codecs.md",
    "guides/memory.md": "bindings/c/guides/memory.md",
    "guides/copy.md": "bindings/c/guides/copy.md",
    "guides/cxx-examples.md": "bindings/cpp/examples.md",
    "concepts/cxx-native-boundary.md": "bindings/cpp/concepts/cxx-native-boundary.md",
    "concepts/cxx-formats.md": "bindings/cpp/concepts/cxx-formats.md",
    "concepts/cxx-builtins.md": "bindings/cpp/concepts/cxx-builtins.md",
    "reference/README.md": "bindings/reference.md",
    "reference/c-api.md": "bindings/c/reference/index.md",
    "reference/cxx-api.md": "bindings/cpp/reference/index.md",
    "reference/errors.md": "bindings/c/reference/errors.md",
    "concepts/query-language.md": "bindings/c/reference/query-language.md",
    "guides/rust.md": "bindings/rust/manual/index.md",
    "guides/go.md": "bindings/go/manual/index.md",
    "guides/python.md": "bindings/python/core-transition.md",
    "guides/lua.md": "bindings/lua/core-transition.md",
    "development/webassembly.md": "bindings/wasm/development.md",
    "playground/index.md": "tools/playground/index.md",
    "concepts/architecture.md": "development/architecture/architecture.md",
    "concepts/runtime-model.md": "development/architecture/runtime-model.md",
    "concepts/processing-pipeline.md": "development/architecture/processing-pipeline.md",
    "concepts/architectural-rules.md": "development/architecture/architectural-rules.md",
    "concepts/error-model.md": "development/architecture/error-model.md",
    "concepts/format-contract.md": "development/architecture/format-contract.md",
    "concepts/definition-boundaries.md": "development/architecture/definition-boundaries.md",
    "reference/compilers.md": "development/building/compilers.md",
    "development/rust.md": "bindings/rust/manual/development.md",
    "development/python.md": "development/bindings/python.md",
    "development/go.md": "bindings/go/manual/development.md",
    "development/lua.md": "development/bindings/lua.md",
    "development/documentation-layout.md": "development/documentation/layout.md",
    "development/documentation-ownership.md": "development/documentation/ownership.md",
    "development/documentation-audit.md": "development/documentation/audit-513.md",
    "assets/README.md": "development/documentation/assets.md",
}
PRODUCT_ROUTES = {"cli/": "tools/otlv/manual/", "lua/": "bindings/lua/manual/",
                  "python/": "bindings/python/manual/"}


@event_priority(50)
def on_files(files, config):
    # Run before API guide-link adaptation. MkDocs resolves source-relative
    # Markdown and HTML links against src_uri and renders them using dest_uri.
    # Keeping src_uri also preserves original edit links and assembly ownership.
    for file in files.documentation_pages():
        target = PAGE_ROUTES.get(file.src_uri)
        for prefix, destination in PRODUCT_ROUTES.items():
            if file.src_uri.startswith(prefix):
                target = destination + file.src_uri[len(prefix):]
                break
        if target:
            destination = File(target, file.src_dir, file.dest_dir, config.use_directory_urls)
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
    if (page.file.src_uri == "development/index.md"
            and core.get("repository") == "https://github.com/OpenTLV/opentlv"
            and core.get("commit") == "e12a52ff69a64468eecab084795a0530c273efea"):
        markdown = markdown.replace("[quality gates](quality-gates.md)",
                                    "[development workflow](workflow.md)")
        markdown = markdown.replace("[Core quality gates](quality-gates.md)",
                                    "[Core development workflow](workflow.md)")
        markdown = markdown.replace("[ownership guide](documentation-ownership.md)",
                                    "[documentation audit](documentation-audit.md)")
        markdown += ("\nThis historical Core version predates the separate quality-gates and\n"
                     "documentation-ownership pages; the links above use its workflow and audit.\n")
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
