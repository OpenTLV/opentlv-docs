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
| Language repository | Its public API, installation/distribution, supported functionality, examples, tests, versioning and release details. Lua, Python, Rust and Go manuals come from their standalone repositories; in-tree bindings retain Core ownership until their implementation moves. |
| Tool repository | Its commands, configuration, workflows, examples, tests, versions and releases. The CLI manual comes from its standalone repository. |
| Portal | Catalogs, short introductions, contributor entry points, navigation, presentation, source assembly, generated-reference integration, site validation and publication. |
| Workspace | Checkout configuration, bootstrap/setup, editor integration and local cross-repository workflows. Its integration pins describe tested workspace coverage, not another component's current migration or release status. |

Rendered location does not transfer technical ownership. In particular, the
Standards catalog is portal-owned while its detailed guides remain Core-owned;
C/C++ references appear under API but remain Core-owned. Link to the
canonical technical page instead of maintaining a second copy.

A technical change updates documentation and examples in the implementation's
repository. The portal consumes that change through a reviewed source revision;
it does not require a second edit to copied API prose, runtime requirements or
version constants. Catalogs may provide short introductions and routing, while
their detailed capabilities, constraints and instructions remain owner links.

## Source metadata and integration contract

Reuse the existing metadata rather than introducing a second registry:

| Information | Authoritative input and validation |
| --- | --- |
| Documentation identity and selection | `docs-sources.json` registers the repository, documentation root, mount and revision. Source locks record resolved commits and inclusion. Unknown metadata, duplicate registrations and overlapping mounts are rejected before assembly. |
| Page attribution | Assembly derives ownership from the selected repository and source path, including source parts for combined pages. Source/edit links follow those owners; rendered URLs never decide ownership. |
| Component version and examples | Component-owned `docs-examples.json` supplies available example sources and optional version metadata. Declared sources must exist in their owner checkout. Owner versioning guides describe runtime and package metadata. |
| Verified compatibility | The existing compatibility feed selects an exact component/Core combination and scoped example evidence. A successful documentation build does not establish runtime compatibility. |
| Published provenance | `source-revision.json` records exact selected revisions and example/API inputs. Independent product manifests and versions remain distinct from the portal's Core-based version. |

An optional source may be absent only under its declared selection rules.
Missing required registrations, invalid source revisions, absent declared
example files, source collisions and unresolved selected-document links fail
validation. The strict build also checks link anchors and generated-reference
targets. These are integration checks; component behavioral suites remain with
their owners.

Never rewrite an immutable published snapshot to apply ownership corrections.
Merge each correction in its owner repository, update the reviewed portal pin
to that commit, and validate the newly assembled source set. A local preview of
uncommitted corrections is useful review evidence and cannot be published.

The [cross-repository review](https://github.com/OpenTLV/opentlv-docs/blob/main/DOCUMENTATION-OWNERSHIP.md)
records reviewed revisions, corrections and repository dependencies. It is a
dated audit, not a second registry of current component versions or capabilities.

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
paths and owner-specific source/edit links. CLI, Lua, Python, Rust and Go public manuals
retain their own contextual navigation and a return link to the portal.
Selected contributor guides appear in [Development](components.md); migration
and dated validation evidence appear in [Historical records](history.md).

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

The portal already selects standalone CLI, Lua, Python, Rust and Go documentation through
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

The ecosystem-wide ownership corrections in
[#62](https://github.com/OpenTLV/opentlv-docs/issues/62) are merged and selected.
The [content disposition review](https://github.com/OpenTLV/opentlv-docs/blob/main/DOCUMENTATION-CONTENT-REVIEW.md)
records the #61 decisions for every reviewed page and any remaining owner-side
corrections. Historical records retain their original bodies and supporting
files, with archive context and links to current instructions. They are omitted
from normal search and public product menus, but remain accessible through
Development. Current test procedures and planned work remain separate from
completed validation evidence.

The [migration validation record](https://github.com/OpenTLV/opentlv-docs/blob/main/DOCUMENTATION-VALIDATION.md)
for [#50](https://github.com/OpenTLV/opentlv-docs/issues/50) gives the final
disposition of every original page and lists discontinued URLs and remaining
follow-ups. Absolute links into the published site, such as product entry
points, must resolve in the history being deployed.
