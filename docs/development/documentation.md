# Documentation ownership and portal conventions

This page owns the current portal hierarchy and contributor routing. Core's
[ownership inventory](documentation-ownership.md) retains technical boundaries
and extraction history; its [layout guide](documentation-layout.md) retains
source-writing conventions. Their historical portal navigation and cutover
instructions must be read alongside the current rules here.

## One technical source per owner

| Owner | Maintain here |
| --- | --- |
| Core | Architecture, shared semantics, detailed format rules and limitations, C/C++ APIs and Doxygen inputs, native examples and their correctness, Core builds and tests. |
| Binding or tool | Its API or commands, installation, dependency requirements, examples, tests, packaging and release details. CLI, Lua and Python manuals come from their standalone repositories. |
| Portal | Catalogs, short introductions, contributor entry points, navigation, presentation, source assembly, generated-reference integration, site validation and publication. |
| Workspace | Shared editor setup, bootstrap and cross-repository integration orchestration. |

Rendered location does not transfer technical ownership. In particular, the
Standards catalog is portal-owned while its detailed guides remain Core-owned;
C/C++ references appear under API but remain Core-owned. Link to the
canonical technical page instead of maintaining a second copy.

## Portal hierarchy

The current site uses the seven-section hierarchy from
[epic #43](https://github.com/OpenTLV/opentlv-docs/issues/43), implemented by
[#63](https://github.com/OpenTLV/opentlv-docs/issues/63):

| Section | Reader's task |
| --- | --- |
| Home | Discover OpenTLV and choose a starting point. |
| Tutorials | Learn the basic model, run a first program and follow practical examples. |
| API | Use shared public contracts, Reader/Writer, Document, Query, Schema, Codec, diagnostics, generic formats and C/C++ reference. |
| Standards | Discover implemented protocol presets, capabilities and limitations, then read the owner-maintained technical guides. |
| Languages | Choose a language and reach its installation, usage guidance and manual. C/C++ overviews link to the references in API. |
| Tools | Find CLI and playground documentation and identify planned tools. |
| Development | Change OpenTLV: architecture, builds, contributing, tests, CI and releases. Documentation conventions are supporting contributor guidance. |

Generic format configurations belong in API; protocol-specific wire rules,
supported subsets and examples belong in Standards. Tutorials links to existing
task examples, and Languages retains language-specific setup and usage guidance.
Development remains contributor-oriented and links to public contracts without
maintaining another explanation of them. Architecture, implementation design,
planned work and historical audits remain separate from available public API
contracts. The Development entry points introduced by #49 remain in use.

Source directories such as `concepts/`, `guides/`, `formats/`, `bindings/` and `reference/` still describe
the owning repository's source layout. They are not additional top-level portal
sections. The portal assigns rendered paths while retaining original source
paths and owner-specific source/edit links. CLI, Lua and Python manuals retain
their own contextual navigation and a return link to the portal.

## Write and validate a documentation change

Preserve the Core layout guide's progressive learning, executable examples,
language tabs, diagrams, contracts and explicit limitations. The portal combines
DER/CER framing and validation for presentation; Core retains both technical
sources. Source layout need not mirror the rendered hierarchy.

Add portal introductions to the appropriate section and link to selected manuals
using source-relative Markdown links. Follow [Register a binding or tool](product-catalogs.md)
for catalog changes. Update navigation and the
[migration mapping](https://github.com/OpenTLV/opentlv-docs/blob/main/DOCUMENTATION-MIGRATION.md)
when changing the hierarchy. The current reorganization replaces old page URLs
without redirects or compatibility aliases; published immutable snapshots are
not rewritten.

Run the owner's source/example checks and the portal's
[validation commands](https://github.com/OpenTLV/opentlv-docs#validation-and-scope).
Check the strict build, links and anchors, source/edit attribution and desktop/mobile
navigation. Keep generated references and site output as build artifacts.

## Migration records and current sources

The portal already selects standalone CLI, Lua and Python documentation through
its [source manifest](https://github.com/OpenTLV/opentlv-docs/blob/main/docs-sources.json).
The retained [Core Python coordination page](python.md) owns the diagnostic
vocabulary generator, native fixtures and dependency coordination; Python's
[standalone guide](../python/development/python.md) owns its build and contributor
instructions. Earlier statements that the portal Python cutover is pending
describe the historical migration, not the current portal selection.

Core's [documentation audit for #513](documentation-audit.md) and the cutover
sequence in its ownership inventory are retained evidence. Their old paths,
source-manifest names and deployment prerequisites describe that migration;
they are not instructions to repeat it. Use the portal's
[current operations guide](https://github.com/OpenTLV/opentlv-docs#ci-and-versioned-publication)
for publication and recovery. A retained historical validation record does not
prove the current deployment or a newly selected component combination.

The ecosystem-wide ownership review and repository-specific corrections are
tracked in [#62](https://github.com/OpenTLV/opentlv-docs/issues/62).
The subsequent content disposition review in
[#61](https://github.com/OpenTLV/opentlv-docs/issues/61) decides what to keep,
relocate, archive or remove. Context notes here preserve evidence while those
reviews remain open; they do not claim that the original sources are corrected.
