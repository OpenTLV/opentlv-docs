# Register a binding or tool

The portal owns product discovery. Each product repository owns its detailed
API, tutorials, build instructions and release documentation. C, C++ and the
in-tree bindings retain Core ownership even when reached through Languages.

## Add a catalog entry

1. Verify the implementation and documentation in the selected source revision.
   Record whether the product is available, experimental or planned. Do not
   infer a package-registry release from a source checkout or a manual.
2. Create `docs/bindings/<slug>/index.md` or `docs/tools/<slug>/index.md`.
   Use a stable lowercase slug, a product-name heading, a short description,
   status, technical owner, installation/access link and detailed documentation
   link. Language entries identify the language/runtime and link its owner-maintained
   requirements; tools introduce their purpose and link supported commands and
   capabilities. Link to an owned first example and versioning guide instead of
   copying executable examples, runtime minimums or version constants. Avoid
   maintaining another tutorial here. If an existing application already
   occupies the directory URL, use `overview.md`, as with the playground.
   `docs/bindings/` remains a source directory; the portal renders its catalog
   and overviews under `languages/`.
3. Add one linked row to the corresponding catalog and register the overview
   in `mkdocs.yml`. Keep product manual chapters out of the central menu.
   Put shared public contracts and C/C++ references in API; keep language-specific
   setup and usage guidance in Languages. C/C++ technical sources remain
   Core-owned; other language manuals retain their component owners.
4. For a separately maintained manual, follow the
   [source registration instructions](https://github.com/OpenTLV/opentlv-docs#multi-repository-assembly).
   Keep its navigation in `docs-sources.json` with an empty `section`, and use
   the routing convention in `tools/docs/navigation.py` for its selected manual.
   Do not copy its Markdown into Portal. Registering a catalog entry does not
   require changing release workflows or adding hosting infrastructure.
5. Use source-relative Markdown links to the selected manual so MkDocs validates
   and routes them within the portal version. Link independent published versions
   separately through the product entry URL, such as `/cli/`, only after checking
   that it is available. Check aliases such as `/cli/stable/` as well. For an
   unpublished entry, state its reserved path as text rather than linking a 404.
   Keep the selected manual accessible when no independent snapshot exists.
6. Run the strict site build and navigation checks documented in the
   [portal operations guide](https://github.com/OpenTLV/opentlv-docs#portal-navigation).
   Check catalog-to-overview-to-manual navigation, source/edit ownership and
   return links on desktop and mobile. Update the changelog and migration map.

## Planned products and status changes

A planned entry names the product and states that installation and documentation
are unavailable. State unknown purpose or capabilities explicitly; do not invent
commands, repositories, downloads or manual links. Update the overview and catalog
together when an implementation becomes available, citing the owning documentation.
An experimental implementation is available source, not a promise of feature parity
or a published package.

Catalogs describe the selected documentation snapshot. Product versions and
release status belong to their owners; portal versions must not be presented as
binding or tool release numbers. Existing immutable published snapshots retain
their original catalogs and manuals.
