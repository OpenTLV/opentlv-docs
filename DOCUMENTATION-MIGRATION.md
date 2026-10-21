# Documentation inventory and migration mapping

Review baseline for [issue #44](https://github.com/OpenTLV/opentlv-docs/issues/44)
and [epic #43](https://github.com/OpenTLV/opentlv-docs/issues/43), prepared
2026-10-21. **Baseline merged in [PR #56](https://github.com/OpenTLV/opentlv-docs/pull/56);
issue #44 closed as completed.** The maintainer's subsequent #45 implementation request
authorizes the navigation phase below. #50 verifies the completed migrations
against this map. A local inventory check is not deployed-site validation.

## Updated epic scope (2026-10-21)

The updated [epic #43](https://github.com/OpenTLV/opentlv-docs/issues/43) and
[#63](https://github.com/OpenTLV/opentlv-docs/issues/63) establish the final target:
**Home, Tutorials, API, Standards, Languages, Tools, Development**.
The original six-section mapping records the completed foundation; the #63
section below records its implemented seven-section successor. Issues #44–#49
and the example repair #51 are closed. Issue #63 is implemented locally;
ownership review #62, content disposition #61 and final published validation #50
remain separate follow-ups.

| Follow-up | Responsibility |
| --- | --- |
| #49 | Contributor entry points in Development; retain owner-maintained architecture, build, contribution, test and release details. |
| #63 | Implement seven sections; move shared public contracts, generic formats and C/C++ references into API; reorganize Tutorials, Standards and Languages while reusing Development. |
| #62 | Review cross-repository ownership and stale component information, track corrections in owning repositories and extend integration validation. |
| #61 | Review content against the final hierarchy; record Keep, Relocate, Archive or Remove with destinations and justification. |
| #50 | Final content, navigation, product-version and published integration verification after the preceding work. |

Issue #63 also coordinates with #19 (Home wire explorer) and #20 (visual identity).
They are related issues, not direct children in the current epic's sub-issue list.
The current #50 text still names six sections and the original URL compatibility
requirements. Its final audit must use #63's approved seven-section target and
the maintainer's no-redirect amendment below; the old wording is not evidence
that either decision was reversed. This records the discrepancy without changing
remote issues or claiming final epic acceptance.

## Seven-section implementation (#63)

The current navigation is **Home, Tutorials, API, Standards, Languages, Tools,
Development**, with landing paths `/`, `tutorials/`, `api/`, `standards/`,
`languages/`, `tools/` and `development/` relative to the selected portal version.
This section supersedes earlier target-location cells for moved pages; those
cells remain the historical inventory and preservation evidence from #44–#49.

API now contains shared public concepts, Reader/Writer, Document, Query, Schema,
Codec, diagnostics, configuration, generic format mechanisms and native reference
entry points. Standards contains the existing supported protocol presets. The
original Portal generic-configuration introduction and table move from the old
Formats catalog to `docs/api/formats.md`; the standards table stays in its source
page. Both catalogs retain capabilities, limits and links to canonical Core
guides. A new Portal `docs/api/index.md` routes readers to public contracts.

Tutorials retains the first program and adds task routing to existing examples;
C++ and format examples join its navigation. Languages retains product discovery
and language-specific material, linking shared contracts and native references
in API. The architecture and contributor entry points from #49 remain in
Development. Public Format/Element/source-layout contracts move to API; internal
design notes, format candidates and the LLDP requirements review remain accessible
through Development. No existing technical page is removed, archived or copied
into maintained Portal sources. The wider disposition review remains #61.

`navigation.py` changes rendered URLs while preserving source paths and technical
owners. Independent CLI, Lua and Python source mounts and publication namespaces
remain unchanged; selected Lua/Python manuals now render under `languages/`.
The exact Core 0.7.1 compatibility branch recognizes Languages and still includes
its historical Lua pages. Onboarding splits and DER/CER assembly retain their
reviewed source boundaries and source/edit attribution.

Generated C/C++ reference files move from `reference/api/` to `api/reference/`,
retaining sibling `c-api/html/` and `cxx-api/html/` trees. Core-authored links keep
their original source paths and resolve to the new generated targets in the
assembled site. Source metadata records the new manifest destination. The old
output is not emitted as a redirect or alias. Existing immutable release trees
with the old namespace remain readable and reusable without rebuilding them.

The preservation audit accounts for **129 navigable pages** (127 from #49 plus
two Portal introductions) and all **113 imported component files**. Of those,
102 are byte-identical to the #49 assembly; the only change in the remaining 11
is the Portal-injected catalog backlink, now Generic formats or Standards catalog.
Every original technical block, example and diagram remains. All four source
pins are unchanged. Every page retains its owner/edit attribution and appears
at its current path in search. Local evidence is recorded in
`build/issue63-validation.json`; hosted CI, release deployment and #50 acceptance
remain separate evidence.

### Current route dispositions

The table lists every changed page destination and both added pages relative to
the #49 assembly. All unlisted existing source pages keep their previous output
and owner. Existing published immutable snapshots retain their original routes.

| Source path | Previous output | Current output | Owner | Action |
| --- | --- | --- | --- | --- |
| `api/formats.md` | `new` | `api/formats/` | Portal | Add |
| `api/index.md` | `new` | `api/` | Portal | Add |
| `bindings/index.md` | `bindings/` | `languages/` | Portal | Move |
| `bindings/c/index.md` | `bindings/c/` | `languages/c/` | Portal | Move |
| `bindings/cpp/index.md` | `bindings/cpp/` | `languages/cpp/` | Portal | Move |
| `bindings/go/index.md` | `bindings/go/` | `languages/go/` | Portal | Move |
| `bindings/lua/index.md` | `bindings/lua/` | `languages/lua/` | Portal | Move |
| `bindings/python/index.md` | `bindings/python/` | `languages/python/` | Portal | Move |
| `bindings/rust/index.md` | `bindings/rust/` | `languages/rust/` | Portal | Move |
| `bindings/wasm/index.md` | `bindings/wasm/` | `languages/wasm/` | Portal | Move |
| `concepts/bindings.md` | `bindings/contracts/` | `languages/contracts/` | core | Move |
| `concepts/core-types.md` | `getting-started/concepts/core-types/` | `api/concepts/core-types/` | core | Move |
| `concepts/cxx-builtins.md` | `bindings/cpp/concepts/cxx-builtins/` | `languages/cpp/concepts/cxx-builtins/` | core | Move |
| `concepts/cxx-formats.md` | `bindings/cpp/concepts/cxx-formats/` | `languages/cpp/concepts/cxx-formats/` | core | Move |
| `concepts/cxx-native-boundary.md` | `bindings/cpp/concepts/cxx-native-boundary/` | `languages/cpp/concepts/cxx-native-boundary/` | core | Move |
| `concepts/endian.md` | `getting-started/concepts/endian/` | `api/concepts/endian/` | core | Move |
| `concepts/field-policies.md` | `formats/concepts/field-policies/` | `development/architecture/field-policies/` | core | Move |
| `concepts/format-capabilities.md` | `formats/concepts/capabilities/` | `api/concepts/format-capabilities/` | core | Move |
| `concepts/format-contract.md` | `development/architecture/format-contract/` | `api/concepts/format-contract/` | core | Move |
| `concepts/learning-model.md` | `getting-started/concepts/learning-model/` | `tutorials/concepts/learning-model/` | core | Move |
| `concepts/length.md` | `getting-started/concepts/length/` | `api/concepts/length/` | core | Move |
| `concepts/query-language.md` | `bindings/c/reference/query-language/` | `api/query-language/` | core | Move |
| `concepts/value.md` | `getting-started/concepts/value/` | `api/concepts/value/` | core | Move |
| `development/go.md` | `bindings/go/manual/development/` | `languages/go/manual/development/` | core | Move |
| `development/rust.md` | `bindings/rust/manual/development/` | `languages/rust/manual/development/` | core | Move |
| `development/webassembly.md` | `bindings/wasm/development/` | `languages/wasm/development/` | core | Move |
| `formats/escaped.md` | `formats/escaped/` | `api/formats/escaped/` | Portal | Move |
| `formats/format-catalogue.md` | `formats/format-catalogue/` | `development/planning/format-catalogue/` | core | Move |
| `formats/format-examples.md` | `formats/format-examples/` | `tutorials/formats/` | core | Move |
| `formats/format-roadmap.md` | `formats/format-roadmap/` | `development/planning/format-roadmap/` | core | Move |
| `formats/lldp-review.md` | `formats/lldp-review/` | `development/planning/lldp-review/` | core | Move |
| `formats/overview.md` | `formats/` | `standards/` | Portal | Move |
| `formats/packed.md` | `formats/packed/` | `api/formats/packed/` | core | Move |
| `formats/README.md` | `formats/guide/` | `api/formats/guide/` | core | Move |
| `formats/support.md` | `formats/support/` | `api/capabilities/` | core | Move |
| `formats/variable.md` | `formats/variable/` | `api/formats/variable/` | core | Move |
| `formats/asn1/ber.md` | `formats/asn1/ber/` | `standards/asn1/ber/` | core | Move |
| `formats/asn1/cer.md` | `formats/asn1/cer/` | `standards/asn1/cer/` | core | Move |
| `formats/asn1/der.md` | `formats/asn1/der/` | `standards/asn1/der/` | core | Move |
| `formats/bluetooth/README.md` | `formats/bluetooth/` | `standards/bluetooth/` | core | Move |
| `formats/custom/README.md` | `formats/custom/` | `api/formats/custom/` | core | Move |
| `formats/dhcp/README.md` | `formats/dhcp/` | `standards/dhcp/` | core | Move |
| `formats/fixed/configurable.md` | `formats/fixed/configurable/` | `api/formats/fixed/configurable/` | core | Move |
| `formats/lldp/conformance.md` | `formats/lldp/conformance/` | `standards/lldp/conformance/` | core | Move |
| `formats/lldp/README.md` | `formats/lldp/` | `standards/lldp/` | core | Move |
| `formats/nfc/README.md` | `formats/nfc/` | `standards/nfc/` | core | Move |
| `getting-started/overview.md` | `getting-started/` | `tutorials/` | Portal | Move |
| `getting-started/README.md` | `getting-started/first-program/` | `tutorials/first-program/` | core | Move |
| `guides/codecs.md` | `bindings/c/guides/codecs/` | `api/guides/codecs/` | core | Move |
| `guides/copy.md` | `bindings/c/guides/copy/` | `api/guides/copy/` | core | Move |
| `guides/cxx-examples.md` | `bindings/cpp/examples/` | `tutorials/cpp-examples/` | core | Move |
| `guides/diagnostics.md` | `bindings/c/guides/diagnostics/` | `api/guides/diagnostics/` | core | Move |
| `guides/document.md` | `bindings/c/guides/document/` | `api/guides/document/` | core | Move |
| `guides/examples.md` | `getting-started/examples/` | `tutorials/examples/` | core | Move |
| `guides/go.md` | `bindings/go/manual/` | `languages/go/manual/` | core | Move |
| `guides/memory.md` | `bindings/c/guides/memory/` | `api/guides/memory/` | core | Move |
| `guides/processing.md` | `getting-started/processing/` | `tutorials/processing/` | core | Move |
| `guides/python.md` | `bindings/python/core-transition/` | `languages/python/core-transition/` | core | Move |
| `guides/queries.md` | `bindings/c/guides/queries/` | `api/guides/queries/` | core | Move |
| `guides/reader.md` | `bindings/c/guides/reader/` | `api/guides/reader/` | core | Move |
| `guides/rust.md` | `bindings/rust/manual/` | `languages/rust/manual/` | core | Move |
| `guides/schemas.md` | `bindings/c/guides/schemas/` | `api/guides/schemas/` | core | Move |
| `guides/select-components.md` | `getting-started/select-components/` | `api/configuration/` | core | Move |
| `guides/writer.md` | `bindings/c/guides/writer/` | `api/guides/writer/` | core | Move |
| `lua/api.md` | `bindings/lua/manual/api/` | `languages/lua/manual/api/` | lua | Move |
| `lua/development.md` | `bindings/lua/manual/development/` | `languages/lua/manual/development/` | lua | Move |
| `lua/implementation.md` | `bindings/lua/manual/implementation/` | `languages/lua/manual/implementation/` | lua | Move |
| `lua/migration.md` | `bindings/lua/manual/migration/` | `languages/lua/manual/migration/` | lua | Move |
| `lua/quality-gates.md` | `bindings/lua/manual/quality-gates/` | `languages/lua/manual/quality-gates/` | lua | Move |
| `lua/releases.md` | `bindings/lua/manual/releases/` | `languages/lua/manual/releases/` | lua | Move |
| `lua/testing.md` | `bindings/lua/manual/testing/` | `languages/lua/manual/testing/` | lua | Move |
| `lua/versioning.md` | `bindings/lua/manual/versioning/` | `languages/lua/manual/versioning/` | lua | Move |
| `python/migration.md` | `bindings/python/manual/migration/` | `languages/python/manual/migration/` | python | Move |
| `python/quality-gates.md` | `bindings/python/manual/quality-gates/` | `languages/python/manual/quality-gates/` | python | Move |
| `python/releases.md` | `bindings/python/manual/releases/` | `languages/python/manual/releases/` | python | Move |
| `python/versioning.md` | `bindings/python/manual/versioning/` | `languages/python/manual/versioning/` | python | Move |
| `python/development/python.md` | `bindings/python/manual/development/python/` | `languages/python/manual/development/python/` | python | Move |
| `python/guides/python.md` | `bindings/python/manual/guides/python/` | `languages/python/manual/guides/python/` | python | Move |
| `python/validation/ci.md` | `bindings/python/manual/validation/ci/` | `languages/python/manual/validation/ci/` | python | Move |
| `python/validation/layout.md` | `bindings/python/manual/validation/layout/` | `languages/python/manual/validation/layout/` | python | Move |
| `python/validation/packaging.md` | `bindings/python/manual/validation/packaging/` | `languages/python/manual/validation/packaging/` | python | Move |
| `python/validation/standalone-build.md` | `bindings/python/manual/validation/standalone-build/` | `languages/python/manual/validation/standalone-build/` | python | Move |
| `reference/c-api.md` | `bindings/c/reference/` | `api/reference/c/` | core | Move |
| `reference/cxx-api.md` | `bindings/cpp/reference/` | `api/reference/cpp/` | core | Move |
| `reference/errors.md` | `bindings/c/reference/errors/` | `api/reference/errors/` | core | Move |
| `reference/README.md` | `bindings/reference/` | `api/reference/` | core | Move |
| `standards/emv/README.md` | `formats/emv/` | `standards/emv/` | core | Move |

## Development phase (#49)

Six new portal-owned pages provide five contributor entry points plus current
documentation conventions:

| Source / rendered destination | Disposition and ownership |
| --- | --- |
| `development/index.md` / `development/` | Keep the Portal landing; replace its inline routing with links to the five entry points. All original destinations remain reachable through them. |
| `development/architecture/index.md` / `development/architecture/` | Add Portal routing to Core's canonical architecture and relevant component contracts, with planned work identified. |
| `development/building/index.md` / `development/building/` | Add Portal build entry points; reuse the Core build split from #46 and repository-owned commands. |
| `development/contributing.md` / `development/contributing/` | Add Portal contribution-policy and ownership routing. |
| `development/testing.md` / `development/testing/` | Add Portal quality-tier overview and owner-specific validation links; retain performance and audit evidence with its scope. |
| `development/releases.md` / `development/releases/` | Add Portal release/publication overview and links to the existing detailed processes. |
| `development/documentation.md` / `development/documentation/` | Add current Portal conventions, distinguish the implemented six-section foundation from #63's seven-section target, and link #61/#62 follow-ups. |

The Core layout, ownership, Python coordination and #513 audit pages retain all
original text. `navigation.py` adds visibly labeled Portal context during
rendering, pointing to current conventions and standalone Python guidance.
The notes do not replace Core's source/edit attribution or rewrite its technical
instructions. The original generator commands, shared fixtures, examples,
diagrams, historical inventories and migration evidence are retained.
Core source corrections and later archive/removal decisions remain with #62/#61.

No existing component page is removed or rerouted by #49, and all four source
pins remain unchanged. The expected inventory is 127 navigable pages (121 from
issue #48 plus six Portal pages). Local build and navigation evidence belongs to
`build/issue49-validation.json`; hosted CI, publication and final #50 validation
are separate evidence and are not implied by a local pass.

## Navigation phase (#45)

Source pins still match the four source revisions inventoried below. The six
sections now group every existing page by its mapped destination. Home,
Getting Started and Formats reuse their existing landings; Bindings, Tools and
Development add portal-owned routing pages. Both MkDocs `README.md` and
`index.md` yield directory URLs, so all six target landing URLs are available
without replacing Core-owned technical content.

The original 105 navigable pages remain in the assembled inventory, with three
new landings. CLI, Lua and Python use contextual product menus, with links back
to the current portal version, rather than extending the six global sections.
Their selected-source manuals now render under `tools/otlv/manual/`,
`bindings/lua/manual/` and `bindings/python/manual/`. No matching independent
release is assumed. Independently published product snapshots and publication
rules are unchanged.

**Maintainer amendment during #45: this reorganization does not preserve URL
compatibility.** New output paths replace old page URLs without redirects,
aliases or fragment compatibility stubs. This supersedes the baseline's R/P
compatibility requirements throughout this document; the URL rules below now
describe direct routing, while old URL cells remain inventory annotations.
Existing published immutable snapshots are not rewritten.

`tools/docs/navigation.py` defines the canonical rendered paths for the Move
rows while preserving repository-owned source paths. MkDocs resolves internal
links and generated API guide links to those destinations. The #47 format
presentation and #48 catalogs are described below. Development restructuring
for #49 is recorded above. The full reference overview renders at `bindings/reference.md`,
and Core's Python transition manual remains at
`bindings/python/core-transition.md` until its unique content is merged. No
row's technical content is removed by #45.

## Home and Getting Started phase (#46)

Home is now portal-owned and routes all previous audiences through Getting
Started, Formats, Bindings, Tools and Development. The portal's new Getting
Started landing introduces TLV, the first element, owned Document parsing,
format choice, language setup and CLI inspection. It links to the existing
component examples and manuals rather than duplicating their tutorials.

Assembly splits Core `docs/getting-started/README.md` at the reviewed
`Install and generate distribution archives` heading. Everything before it
(first build, every language tab, wire bytes/output and CMake consumption)
renders at `getting-started/first-program/`. The three remaining sections
(installation/archives, C-only build, tests) render at
`development/building/core/`. Every original text block remains, with the same
Core source/edit target; `tools/docs/onboarding.py` rejects a changed boundary
or unexpected developer section. The virtual build page shares the original
source directory for link resolution. Internal and generated API links target
the moved sections directly; no compatibility fragments are retained.

The inventory now contains 110 navigable pages: the 108 pages from #45, a new
Getting Started landing and one additional rendered part of the Core guide.
Home replaces its previous routing content. Core README quick-start callers
still target the retained source section; immutable repository files and
already-published snapshots are unchanged. The original Home audiences,
reference, compiler/component, roadmap and project-policy routes remain
reachable from Home or its linked catalogs. Concept diagrams and executable
examples remain Core/product-owned and unchanged.

## Supported Formats phase (#47)

The portal catalog at `formats/` lists Fixed, Variable, Packed and Escaped
configurations and BER, DER, CER, EMV, Bluetooth, LLDP, DHCPv4 and NFC Type 2.
Each entry links to a dedicated page and names its specification, implemented
scope and limits. Escaped was already implemented and documented in Core's NFC
composition section; its new portal entry links to that explanation and the
Core declarations. Custom callbacks are an extension point; candidate and
roadmap entries are explicitly separate from implemented support.

Core's complete original Formats index, including every technical comparison,
example and generic interface explanation, renders at `formats/guide/`.
The new `docs/formats/overview.md` owns discovery. Existing technical content
is retained even where the former index also included discovery tables.

The reviewed heading map in `tools/docs/formats.py` groups whole Core sections
under Overview, Format structure, Encoding rules, Supported capabilities,
Examples, Limitations and References where applicable. It retains code fences,
diagrams, tables, subheadings and body text; missing, duplicate or unknown
headings fail assembly for review. Empty categories are omitted rather than
filled with duplicated technical explanations.

DER/CER consolidation is implemented as a presentation merge of the two
original Core documents, not an authored technical copy in Portal. This refines
the baseline's proposed physical Core source merge: technical edits still
belong in Core, while Portal only regroups the selected immutable blocks.
Both original paths are recorded in assembly ownership and linked with source
and edit actions on each combined page. Relative links in imported validation
blocks retain their original meaning. Internal, repository and generated API
links resolve to `formats/asn1/{der,cer}/`; the separate validation outputs and
their search entries disappear without redirects or fragment stubs.

The inventory remains 110 navigable pages: two new portal pages (catalog and
Escaped entry) replace the two separately rendered validation pages. All four
source pins and published snapshots remain unchanged. No parser, encoder,
binding API or format capability is changed by this presentation work.

## Bindings and Tools phase (#48)

The catalogs now link lightweight portal-owned overviews for C, C++, Python,
Lua, Rust, Go and WebAssembly, and for otlv, the playground and planned imtlv.
Each available product identifies its purpose, runtime or capabilities,
availability, technical owner, installation/access and detailed documentation.
Experimental in-tree interfaces are distinguished from native APIs and
standalone bindings; imtlv has no asserted implementation, download or manual.

The existing CLI, Lua and Python selected-source manuals retain their paths,
source/edit ownership, separate menus and return links. The live CLI entry and
`/cli/stable/` manual remain linked. The reserved `/python/` and `/lua/` entries
returned HTTP 404 during #48 validation, so the catalogs describe those paths
without dead links and direct users to the selected manuals. C/C++ references
and technical guides remain Core-owned.
The playground application retains `tools/playground/`; its new introduction
uses `tools/playground/overview/` to avoid replacing the application URL.

The inventory grows from 110 to 121 navigable pages: ten product overviews and
one [registration convention](docs/development/product-catalogs.md). No existing
technical page is removed or copied into portal maintenance. In particular,
the Core reference overview and Python transition guide retain their unique
content; consolidating those technical sources is outside the catalog task.
All four source pins and independent publication workflows remain unchanged.

## Baseline and inventory method

The baseline is the portal commit below and the exact four source revisions in
its `docs-sources.json`, not sibling working-tree HEADs or a live deployment.
Source links in every row address those immutable revisions. Enumerate tracked
Markdown with `git ls-tree -r --name-only <revision>`, read it with
`git show <revision>:<path>`, then compare `docs/` with `mkdocs.yml`, source
mounts/navigation and `tools/docs/assembly.py` overrides. Inspect headings,
examples, diagrams, cross-references and the full source for merge/split cases.
The content column identifies review topics; the disposition covers the entire
page, including all sections not repeated in that column.

| Source | Repository | Exact revision | Markdown under docs/ | Other Markdown |
| --- | --- | --- | ---: | ---: |
| portal | [opentlv-docs](https://github.com/OpenTLV/opentlv-docs) | `882d8eeb366129adf15e50748fc1affe57c83be9` | 2 | 2 |
| core | [opentlv](https://github.com/OpenTLV/opentlv) | `a5e2453c8cc156122cda01b02d3f91c33580b4f3` | 84 | 17 |
| cli | [opentlv-cli](https://github.com/OpenTLV/opentlv-cli) | `abd2bce09a9f25071a41d7c1f3249fd48e8a0b20` | 4 | 7 |
| lua | [opentlv-lua](https://github.com/OpenTLV/opentlv-lua) | `6f610f5552a64efa21aeeb863ad161c91154dbc8` | 8 | 3 |
| python | [opentlv-python](https://github.com/OpenTLV/opentlv-python) | `d846b4ff7f2c74fbf0571a065da1d83698b6f40c` | 10 | 5 |

There are **142 source Markdown files: 108 under docs/ and 34 outside it**.
Core contributes 84 docs sources, two of which (`assets/README.md` and
`playground/index.md`) are already replaced by the Portal overlay. This leaves
106 assembled Markdown files; excluding the Core GitHub-only `docs/README.md`
leaves **105 navigable pages**. Overridden sources are still inventoried below.
Generated API HTML is inventoried by its two complete output trees separately.
Build output, caches and generated copies are not additional authored pages.
This new mapping is a repository review artifact outside `docs/`, so it neither
adds a navigation item nor changes the assembled site.

Refresh the inventory against the new pinned revisions before each migration
PR. Add dispositions for new pages and account for changed sections rather than
silently treating this frozen baseline as a live inventory. The historical Core
audit is supporting evidence, not a substitute for this multi-repository scan.

## Six-section destinations and ownership

| Section | Landing page / URL inside a portal version | Responsibility and detailed destinations |
| --- | --- | --- |
| Home | `index.md` / `/` | Portal introduction, ecosystem entry points and project status; reuse the Core homepage and repository entry material. |
| Getting Started | `getting-started/index.md` / `getting-started/` | Portal learning path, install/consume entry and first task; Core remains authoritative for shared semantics, code examples and CMake contracts. |
| Formats | `formats/index.md` / `formats/` | Portal owns the catalog, short introductions and navigation. Core owns detailed format rules, implementation limitations, technical examples and their correctness, including the source Markdown displayed under this section. |
| Bindings | `bindings/index.md` / `bindings/` | Portal discovery and short overview pages; C/C++ reference and shared contracts stay Core-owned, full Python/Lua manuals stay product-owned. |
| Tools | `tools/index.md` / `tools/` | Portal discovery, CLI overview and playground; CLI commands and release instructions remain CLI-owned. `imtlv` is planned, with no existing manual to migrate. |
| Development | `development/index.md` / `development/` | Portal contributor routing: Architecture, Building from Source, Contributing, Testing and Quality Gates, CI and Release Process. Core/product implementation instructions remain with their owners. |

Targets below are proposed **rendered document paths**, not commands to rename
files in a product repository. Navigation can organize Core-owned sources under
these sections without transferring their technical ownership. Portal owns
general introductions, onboarding/discovery pages and navigation. Core remains
the source of truth for detailed format documentation: rules, implementation
limitations, technical examples and their correctness. Its source Markdown can
be assembled under `/formats/` without moving ownership to Portal. Format and
standard technical content, including DER/CER, must be maintained in Core.
Portal consumes the canonical sources rather than maintaining edited copies;
the #47 presentation merge above preserves both original Core documents.

The same boundary applies to C/C++: access through Bindings changes discovery,
not ownership of the technical manuals, reference Markdown, public API comments
or generated Doxygen output. Those remain Core-owned. Any transfer of general
introductory material must be explicit and coordinated; it does not include
technical sections embedded in the original page. The Formats landing-page
split below records that distinction for the existing mixed-purpose index.

The catalogs add `bindings/{c,cpp,python,lua}/index.md` and
`tools/{otlv,imtlv}/index.md` as lightweight entry pages. Rust, Go and WASM remain
explicitly experimental/in-tree where documented; their existing manuals are
retained under the corresponding Bindings secondary navigation. No new product
repository or release is assumed. Common C/C++ guides remain shared; C++ and
other overviews link to those guides rather than duplicating their bodies.

## How to read the map and URL policy

Following the #45 maintainer amendment, the implementation requires canonical
new paths and valid internal links, not old-URL compatibility.

Actions are **Keep**, **Move**, **Merge**, **Split**, **Replace**, or **Remove**.
Keep may change navigation grouping without changing the page body or URL.
Move changes a rendered location or an explicitly identified source location;
it does not imply a source-owner transfer. Merge/Split require a
section-by-section preservation and ownership check;
Replace requires a named successor. No source is approved for Remove here.

`P/` means `https://opentlv.github.io/opentlv-docs/<portal-version>/`;
for development use `<portal-version> = latest`. Current path cells list the
exact suffix to append. Relative target `.md` paths use normal MkDocs directory
URLs: `README.md` and `index.md` become the directory index, and `x.md` becomes
`x/`. A target starting `/cli/`, `/lua/` or `/python/` instead starts at the
**site root**, outside `P/`. `{version}` means a matching independently
published product version, not the Core version or an invented tag.

| Code | URL handling |
| --- | --- |
| K | Keep the current rendered path where it remains the canonical destination. |
| R | Render at the new canonical destination and update internal links. Do not emit an old-URL redirect, alias or fragment stub. |
| P | Product boundary: keep independently versioned publication separate. Selected-source manuals render under the new Bindings/Tools manual paths; do not redirect them to an unverified or moving product release. |
| G | GitHub-only source; no published page redirect. Keep its repository path or provide a source stub in a coordinated owner PR. |
| O | Already overridden in assembly; use the Portal row for the canonical rendered path and preserve source ownership. |

For Merge, reconcile conflicting heading IDs and retain unique technical
content. Internal links, navigation, search results and generated API guide
links must resolve to canonical destinations. External callers of old page URLs
are not covered by compatibility guarantees. Existing
`link_aliases: ["main"]` resolves repository source links against the selected
commit; it is not a public URL redirect mechanism.

Previously published immutable Core and product snapshots retain their bytes,
paths, assets and provenance. Apply this map to new builds and the development
entry only; do not rebuild old releases to change their layout. The site-root
default/version selectors and `stable` aliases retain their current publication
semantics. The legacy `https://opentlv.github.io/opentlv/` site and its archived
`latest/playground/` remain outside this migration; preserve existing hand-offs.
These are source/configuration-derived URLs, not claims that every route was
checked on the live deployment.

## Portal-owned page mapping

| Current source | Current URL | Section | Target | Owner after migration | Action | URL rule | Content to preserve |
| --- | --- | --- | --- | --- | --- | --- | --- |
| [docs/assets/README.md](https://github.com/OpenTLV/opentlv-docs/blob/882d8eeb366129adf15e50748fc1affe57c83be9/docs/assets/README.md) | `P/assets/` | Development | `development/documentation/assets.md` | Portal | Move | R | Logo meaning, variants, dimensions, accessibility, license and all five SVG links. |
| [docs/playground/index.md](https://github.com/OpenTLV/opentlv-docs/blob/882d8eeb366129adf15e50748fc1affe57c83be9/docs/playground/index.md) | `P/playground/` | Tools | `tools/playground/index.md` | Portal UI; Core WASM | Move | R | Preserve controls, fixed TLV/LTV options, Tree/Hex/JSON views, Bluetooth padding, CER limitations, local-only parsing and 65,536-element / 64-level limits. |

## Core page mapping

Core owns the source of every row in this table at the baseline.

| Current source | Current URL | Section | Target | Owner after migration | Action | URL rule | Content to preserve |
| --- | --- | --- | --- | --- | --- | --- | --- |
| [docs/README.md](https://github.com/OpenTLV/opentlv/blob/a5e2453c8cc156122cda01b02d3f91c33580b4f3/docs/README.md) | `Not published` | Home | `Core:docs/README.md` | Core | Keep | G | GitHub documentation index, explicitly excluded from the site; continue linking to the canonical Home and contributor entry points. |
| [docs/assets/README.md](https://github.com/OpenTLV/opentlv/blob/a5e2453c8cc156122cda01b02d3f91c33580b4f3/docs/assets/README.md) | `P/assets/` | Development | `development/documentation/assets.md` | Portal | Replace | O | Core copy is already overridden by Portal; retain its GitHub source link until coordinated cleanup. Use the portal asset guide, including all logo variants. |
| [docs/concepts/architectural-rules.md](https://github.com/OpenTLV/opentlv/blob/a5e2453c8cc156122cda01b02d3f91c33580b4f3/docs/concepts/architectural-rules.md) | `P/concepts/architectural-rules/` | Development | `development/architecture/architectural-rules.md` | Core | Move | R | Core architectural rules; 1. Generic core first; 2. Stable conceptual model; Definition; Format |
| [docs/concepts/architecture.md](https://github.com/OpenTLV/opentlv/blob/a5e2453c8cc156122cda01b02d3f91c33580b4f3/docs/concepts/architecture.md) | `P/concepts/architecture/` | Development | `development/architecture/architecture.md` | Core | Move | R | Layered OpenTLV architecture (#65, #279, #280, #281, #327); Conceptual model; Planned runtime and compiled models; Responsibilities and dependency direction; Repository layout |
| [docs/concepts/bindings.md](https://github.com/OpenTLV/opentlv/blob/a5e2453c8cc156122cda01b02d3f91c33580b4f3/docs/concepts/bindings.md) | `P/concepts/bindings/` | Bindings | `bindings/contracts.md` | Core | Move | R | Canonical C boundary, per-language capability matrix, ownership and parity limitations. Portal catalog links here without copying the matrix. |
| [docs/concepts/core-types.md](https://github.com/OpenTLV/opentlv/blob/a5e2453c8cc156122cda01b02d3f91c33580b4f3/docs/concepts/core-types.md) | `P/concepts/core-types/` | Getting Started | `getting-started/concepts/core-types.md` | Core | Move | R | C core types; Tags are borrowed; Tag comparison; Other tag operations; Constructing tags |
| [docs/concepts/cxx-builtins.md](https://github.com/OpenTLV/opentlv/blob/a5e2453c8cc156122cda01b02d3f91c33580b4f3/docs/concepts/cxx-builtins.md) | `P/concepts/cxx-builtins/` | Bindings | `bindings/cpp/concepts/cxx-builtins.md` | Core / C++ | Move | R | C++ built-in standards; Framing entry points; Value codecs and fields |
| [docs/concepts/cxx-formats.md](https://github.com/OpenTLV/opentlv/blob/a5e2453c8cc156122cda01b02d3f91c33580b4f3/docs/concepts/cxx-formats.md) | `P/concepts/cxx-formats/` | Bindings | `bindings/cpp/concepts/cxx-formats.md` | Core / C++ | Move | R | C++ Format customization; Operations; Generic consumers and built-ins; Measurement and diagnostics; Shared invariants and lifetime |
| [docs/concepts/cxx-native-boundary.md](https://github.com/OpenTLV/opentlv/blob/a5e2453c8cc156122cda01b02d3f91c33580b4f3/docs/concepts/cxx-native-boundary.md) | `P/concepts/cxx-native-boundary/` | Bindings | `bindings/cpp/concepts/cxx-native-boundary.md` | Core / C++ | Move | R | C++ public and native boundary; Public facade; Ownership, allocation and errors; Exception policy; Node validity and allocation costs |
| [docs/concepts/definition-boundaries.md](https://github.com/OpenTLV/opentlv/blob/a5e2453c8cc156122cda01b02d3f91c33580b4f3/docs/concepts/definition-boundaries.md) | `P/concepts/definition-boundaries/` | Development | `development/architecture/definition-boundaries.md` | Core | Move | R | Definition boundary audit (#381); Decision: minimal Definition, optional domain dictionaries; Evidence across standards; Separate decision: logical identity and identifier mapping; Native and future runtime modules |
| [docs/concepts/endian.md](https://github.com/OpenTLV/opentlv/blob/a5e2453c8cc156122cda01b02d3f91c33580b4f3/docs/concepts/endian.md) | `P/concepts/endian/` | Getting Started | `getting-started/concepts/endian.md` | Core | Move | R | Integer byte-order conversions; Checked variable-width integers; Next step |
| [docs/concepts/error-model.md](https://github.com/OpenTLV/opentlv/blob/a5e2453c8cc156122cda01b02d3f91c33580b4f3/docs/concepts/error-model.md) | `P/concepts/error-model/` | Development | `development/architecture/error-model.md` | Core | Move | R | Failure model; One failure, four questions; Result taxonomy; Admission rule; Results |
| [docs/concepts/field-policies.md](https://github.com/OpenTLV/opentlv/blob/a5e2453c8cc156122cda01b02d3f91c33580b4f3/docs/concepts/field-policies.md) | `P/concepts/field-policies/` | Formats | `formats/concepts/field-policies.md` | Core | Move | R | Generic field-policy contracts, borrowed context/storage, encoding/error behavior and builtin adoption. |
| [docs/concepts/format-capabilities.md](https://github.com/OpenTLV/opentlv/blob/a5e2453c8cc156122cda01b02d3f91c33580b4f3/docs/concepts/format-capabilities.md) | `P/concepts/format-capabilities/` | Formats | `formats/concepts/capabilities.md` | Core | Move | R | Independent wire dimensions, capability matrix, representative protocols and architecture stress tests. |
| [docs/concepts/format-contract.md](https://github.com/OpenTLV/opentlv/blob/a5e2453c8cc156122cda01b02d3f91c33580b4f3/docs/concepts/format-contract.md) | `P/concepts/format-contract/` | Development | `development/architecture/format-contract.md` | Core | Move | R | Format and Element contract; Semantic content and source; Encoding and preservation; Field ordering and length scope; Field Encoding and Format composition |
| [docs/concepts/learning-model.md](https://github.com/OpenTLV/opentlv/blob/a5e2453c8cc156122cda01b02d3f91c33580b4f3/docs/concepts/learning-model.md) | `P/concepts/learning-model/` | Getting Started | `getting-started/concepts/learning-model.md` | Core | Move | R | Element, Reader/Writer, Document and optional Query/Schema/Codec; preserve the learning sequence and diagrams. |
| [docs/concepts/length.md](https://github.com/OpenTLV/opentlv/blob/a5e2453c8cc156122cda01b02d3f91c33580b4f3/docs/concepts/length.md) | `P/concepts/length/` | Getting Started | `getting-started/concepts/length.md` | Core | Move | R | Logical TLV value lengths; x86 and x64; Next step |
| [docs/concepts/processing-pipeline.md](https://github.com/OpenTLV/opentlv/blob/a5e2453c8cc156122cda01b02d3f91c33580b4f3/docs/concepts/processing-pipeline.md) | `P/concepts/processing-pipeline/` | Development | `development/architecture/processing-pipeline.md` | Core | Move | R | Canonical processing pipeline; Canonical structural events (#402); Continuation, borrowing and subtree skipping; Consumers and projections; Removed superseded interfaces |
| [docs/concepts/query-language.md](https://github.com/OpenTLV/opentlv/blob/a5e2453c8cc156122cda01b02d3f91c33580b4f3/docs/concepts/query-language.md) | `P/concepts/query-language/` | Bindings | `bindings/c/reference/query-language.md` | Core | Move | R | V1/F2 language grammar, ordering, metadata, providers and execution storage; shared contract for all bindings. |
| [docs/concepts/runtime-model.md](https://github.com/OpenTLV/opentlv/blob/a5e2453c8cc156122cda01b02d3f91c33580b4f3/docs/concepts/runtime-model.md) | `P/concepts/runtime-model/` | Development | `development/architecture/runtime-model.md` | Core | Move | R | Phase 2 runtime model and canonical IR; Future model construction and inference; From source to execution; AST and semantic analysis; Canonical IR |
| [docs/concepts/value.md](https://github.com/OpenTLV/opentlv/blob/a5e2453c8cc156122cda01b02d3f91c33580b4f3/docs/concepts/value.md) | `P/concepts/value/` | Getting Started | `getting-started/concepts/value.md` | Core | Move | R | Borrowed TLV values; Comparing, slicing and copying values; Relationship to tlv_element_t; Next step |
| [docs/development/abi-compatibility.md](https://github.com/OpenTLV/opentlv/blob/a5e2453c8cc156122cda01b02d3f91c33580b4f3/docs/development/abi-compatibility.md) | `P/development/abi-compatibility/` | Development | `development/abi-compatibility.md` | Core | Keep | K | C ABI compatibility; Baseline; What breaks the ABI; CI behavior; Intentional breaking changes |
| [docs/development/cxx-facade-performance.md](https://github.com/OpenTLV/opentlv/blob/a5e2453c8cc156122cda01b02d3f91c33580b4f3/docs/development/cxx-facade-performance.md) | `P/development/cxx-facade-performance/` | Development | `development/cxx-facade-performance.md` | Core | Keep | K | C++ Reader and Document performance; Implementation boundary; Workloads; Measurement method; Results |
| [docs/development/documentation-audit.md](https://github.com/OpenTLV/opentlv/blob/a5e2453c8cc156122cda01b02d3f91c33580b4f3/docs/development/documentation-audit.md) | `P/development/documentation-audit/` | Development | `development/documentation/audit-513.md` | Core | Move | R | Historical #513 audit: retain evidence and page inventory; label dated scope and link to this migration map rather than treating old paths as current guidance. |
| [docs/development/documentation-layout.md](https://github.com/OpenTLV/opentlv/blob/a5e2453c8cc156122cda01b02d3f91c33580b4f3/docs/development/documentation-layout.md) | `P/development/documentation-layout/` | Development | `development/documentation/layout.md` | Core conventions; Portal hierarchy | Move | R | Preserve progressive-learning, examples, language tabs and validation rules. Reconcile old section names with the approved six sections during #49. |
| [docs/development/documentation-ownership.md](https://github.com/OpenTLV/opentlv/blob/a5e2453c8cc156122cda01b02d3f91c33580b4f3/docs/development/documentation-ownership.md) | `P/development/documentation-ownership/` | Development | `development/documentation/ownership.md` | Core boundaries; Portal routing | Move | R | Retain extraction history, inventories and source contract. Reconcile Portal discovery with retained Core technical ownership and the completed Python cutover in #49. |
| [docs/development/fuzzing.md](https://github.com/OpenTLV/opentlv/blob/a5e2453c8cc156122cda01b02d3f91c33580b4f3/docs/development/fuzzing.md) | `P/development/fuzzing/` | Development | `development/fuzzing.md` | Core | Keep | K | Fuzzing the C API; Targets and contracts; Seed corpus; Run locally; Reproduce and minimize a finding |
| [docs/development/go.md](https://github.com/OpenTLV/opentlv/blob/a5e2453c8cc156122cda01b02d3f91c33580b4f3/docs/development/go.md) | `P/development/go/` | Bindings | `bindings/go/manual/development.md` | Core / go (until extraction) | Move | R | Go binding development |
| [docs/development/indefinite-boundary-reuse.md](https://github.com/OpenTLV/opentlv/blob/a5e2453c8cc156122cda01b02d3f91c33580b4f3/docs/development/indefinite-boundary-reuse.md) | `P/development/indefinite-boundary-reuse/` | Development | `development/indefinite-boundary-reuse.md` | Core | Keep | K | Follow-up: reuse indefinite element boundaries; Motivation and existing behavior; Contracts to preserve; Acceptance criteria for a separate implementation |
| [docs/development/python.md](https://github.com/OpenTLV/opentlv/blob/a5e2453c8cc156122cda01b02d3f91c33580b4f3/docs/development/python.md) | `P/development/python/` | Development | `development/bindings/python.md + /python/{version}/development/python/` | Core coordination; Python build | Split | P | Keep Core diagnostic-vocabulary generation, shared fixtures and native-CI responsibilities in Core. Delegate standalone setup, versioning and Python CI to Python; this page is not wholly obsolete. |
| [docs/development/quality-gates.md](https://github.com/OpenTLV/opentlv/blob/a5e2453c8cc156122cda01b02d3f91c33580b4f3/docs/development/quality-gates.md) | `P/development/quality-gates/` | Development | `development/quality-gates.md` | Core | Keep | K | Core quality gates; Entry points; Release artifacts; Repository settings and publication boundary; Release performance verification |
| [docs/development/query-adversarial.md](https://github.com/OpenTLV/opentlv/blob/a5e2453c8cc156122cda01b02d3f91c33580b4f3/docs/development/query-adversarial.md) | `P/development/query-adversarial/` | Development | `development/query-adversarial.md` | Core | Keep | K | Query adversarial verification; Lifecycle oracle; Storage relationships; Callbacks and Document revision; Plan equivalence and frontend-free builds |
| [docs/development/query-phase-audit.md](https://github.com/OpenTLV/opentlv/blob/a5e2453c8cc156122cda01b02d3f91c33580b4f3/docs/development/query-phase-audit.md) | `P/development/query-phase-audit/` | Development | `development/query-phase-audit.md` | Core | Keep | K | Query F1-F6 implementation audit; Phase status; Completed follow-up and remaining candidate verification; Findings fixed during this follow-up; Original work-package coverage |
| [docs/development/query-release.md](https://github.com/OpenTLV/opentlv/blob/a5e2453c8cc156122cda01b02d3f91c33580b4f3/docs/development/query-release.md) | `P/development/query-release/` | Development | `development/query-release.md` | Core | Keep | K | Query hardening and release checklist; Resource and validation boundaries; Public-facade evidence and candidate requirements |
| [docs/development/reader-decode-performance.md](https://github.com/OpenTLV/opentlv/blob/a5e2453c8cc156122cda01b02d3f91c33580b4f3/docs/development/reader-decode-performance.md) | `P/development/reader-decode-performance/` | Development | `development/reader-decode-performance.md` | Core | Keep | K | Reader decode measurements; Scope and decisions; Workloads and measurement method; Recorded Release results; Document allocator experiment |
| [docs/development/rust.md](https://github.com/OpenTLV/opentlv/blob/a5e2453c8cc156122cda01b02d3f91c33580b4f3/docs/development/rust.md) | `P/development/rust/` | Bindings | `bindings/rust/manual/development.md` | Core / rust (until extraction) | Move | R | Rust bindings (experimental); Core types; Reader; Writer; Schemas |
| [docs/development/valgrind.md](https://github.com/OpenTLV/opentlv/blob/a5e2453c8cc156122cda01b02d3f91c33580b4f3/docs/development/valgrind.md) | `P/development/valgrind/` | Development | `development/valgrind.md` | Core | Keep | K | Valgrind memory and performance checks; Run locally; Memcheck CI scope; Read a report; Suppressions and exclusions |
| [docs/development/webassembly.md](https://github.com/OpenTLV/opentlv/blob/a5e2453c8cc156122cda01b02d3f91c33580b4f3/docs/development/webassembly.md) | `P/development/webassembly/` | Bindings | `bindings/wasm/development.md` | Core / WASM | Move | R | Keep experimental status, build, JavaScript use, Query/Document, parse tooling and tests. Tools/playground links here for implementation details. |
| [docs/development/workflow.md](https://github.com/OpenTLV/opentlv/blob/a5e2453c8cc156122cda01b02d3f91c33580b4f3/docs/development/workflow.md) | `P/development/workflow/` | Development | `development/workflow.md` | Core | Keep | K | Development workflow |
| [docs/formats/README.md](https://github.com/OpenTLV/opentlv/blob/a5e2453c8cc156122cda01b02d3f91c33580b4f3/docs/formats/README.md) | `P/formats/` | Formats | `formats/index.md + formats/guide.md` | Portal catalog; Core technical guide | Split | R | Keep catalog and short introductions in Portal; retain all technical capability tables, read/write/traversal examples, generic interface and length-before-tag rules in Core-owned Markdown. Retain the technical sections at their canonical destinations. |
| [docs/formats/asn1/ber.md](https://github.com/OpenTLV/opentlv/blob/a5e2453c8cc156122cda01b02d3f91c33580b4f3/docs/formats/asn1/ber.md) | `P/formats/asn1/ber/` | Formats | `formats/asn1/ber.md` | Core | Keep | K | BER-TLV; API and build; Scope and limits; Generic mechanics and ASN.1 rules; Minimal C usage |
| [docs/formats/asn1/cer.md](https://github.com/OpenTLV/opentlv/blob/a5e2453c8cc156122cda01b02d3f91c33580b4f3/docs/formats/asn1/cer.md) | `P/formats/asn1/cer/` | Formats | `formats/asn1/cer.md` | Core | Merge | K | CER-TLV; API and build; Scope and limits; Minimal C usage; Framing and typical use |
| [docs/formats/asn1/der.md](https://github.com/OpenTLV/opentlv/blob/a5e2453c8cc156122cda01b02d3f91c33580b4f3/docs/formats/asn1/der.md) | `P/formats/asn1/der/` | Formats | `formats/asn1/der.md` | Core | Merge | K | DER-TLV; API and build; Scope and limits; Minimal C usage; Framing and typical use |
| [docs/formats/bluetooth/README.md](https://github.com/OpenTLV/opentlv/blob/a5e2453c8cc156122cda01b02d3f91c33580b4f3/docs/formats/bluetooth/README.md) | `P/formats/bluetooth/` | Formats | `formats/bluetooth/README.md` | Core | Keep | K | Bluetooth LTV; API and build; Advertising Data Type definitions; Basic Advertising Data value codecs; Advertising Data schema |
| [docs/formats/custom/README.md](https://github.com/OpenTLV/opentlv/blob/a5e2453c8cc156122cda01b02d3f91c33580b4f3/docs/formats/custom/README.md) | `P/formats/custom/` | Formats | `formats/custom/README.md` | Core | Keep | K | Application-defined format example; API and build; Scope and limits; C usage; Byte example |
| [docs/formats/dhcp/README.md](https://github.com/OpenTLV/opentlv/blob/a5e2453c8cc156122cda01b02d3f91c33580b4f3/docs/formats/dhcp/README.md) | `P/formats/dhcp/` | Formats | `formats/dhcp/README.md` | Core | Keep | K | DHCPv4 option framing; Element and source contracts; Option definitions; Value codecs; Scope and composition |
| [docs/formats/fixed/configurable.md](https://github.com/OpenTLV/opentlv/blob/a5e2453c8cc156122cda01b02d3f91c33580b4f3/docs/formats/fixed/configurable.md) | `P/formats/fixed/configurable/` | Formats | `formats/fixed/configurable.md` | Core | Keep | K | Configurable fixed-width TLV; API and build; Standalone Field Encoding; Supported parameters; Wire representation |
| [docs/formats/format-catalogue.md](https://github.com/OpenTLV/opentlv/blob/a5e2453c8cc156122cda01b02d3f91c33580b4f3/docs/formats/format-catalogue.md) | `P/formats/format-catalogue/` | Formats | `formats/format-catalogue.md` | Core | Keep | K | Format candidate catalogue; ASN.1 notation (ITU-T X.680 series); Protocols using BER; ASN.1 standards; Smart cards and SIM |
| [docs/formats/format-examples.md](https://github.com/OpenTLV/opentlv/blob/a5e2453c8cc156122cda01b02d3f91c33580b4f3/docs/formats/format-examples.md) | `P/formats/format-examples/` | Formats | `formats/format-examples.md` | Core | Keep | K | Format trees and byte examples |
| [docs/formats/format-roadmap.md](https://github.com/OpenTLV/opentlv/blob/a5e2453c8cc156122cda01b02d3f91c33580b4f3/docs/formats/format-roadmap.md) | `P/formats/format-roadmap/` | Formats | `formats/format-roadmap.md` | Core | Keep | K | Format expansion candidates; Keep the core generic; Scope principle; How to read this catalogue; Components |
| [docs/formats/lldp-review.md](https://github.com/OpenTLV/opentlv/blob/a5e2453c8cc156122cda01b02d3f91c33580b4f3/docs/formats/lldp-review.md) | `P/formats/lldp-review/` | Formats | `formats/lldp-review.md` | Core | Keep | K | LLDP requirements, Format and runtime Layout review; Issue coverage; Evidence and scope; Preliminary wire requirements; Deferred normative verification checklist |
| [docs/formats/lldp/README.md](https://github.com/OpenTLV/opentlv/blob/a5e2453c8cc156122cda01b02d3f91c33580b4f3/docs/formats/lldp/README.md) | `P/formats/lldp/` | Formats | `formats/lldp/README.md` | Core | Keep | K | LLDP TLV support; API and build; Wire representation and logical model; Scope and errors; Schema and sequence validation |
| [docs/formats/lldp/conformance.md](https://github.com/OpenTLV/opentlv/blob/a5e2453c8cc156122cda01b02d3f91c33580b4f3/docs/formats/lldp/conformance.md) | `P/formats/lldp/conformance/` | Formats | `formats/lldp/conformance.md` | Core | Keep | K | LLDP reference tests and conformance boundary; Evidence; Reference vectors; Remaining normative audit |
| [docs/formats/nfc/README.md](https://github.com/OpenTLV/opentlv/blob/a5e2453c8cc156122cda01b02d3f91c33580b4f3/docs/formats/nfc/README.md) | `P/formats/nfc/` | Formats | `formats/nfc/README.md` | Core | Keep | K | NFC Forum Type 2 Tag TLV framing; Length encoding; Input and source ownership; Example; Bindings |
| [docs/formats/packed.md](https://github.com/OpenTLV/opentlv/blob/a5e2453c8cc156122cda01b02d3f91c33580b4f3/docs/formats/packed.md) | `P/formats/packed/` | Formats | `formats/packed.md` | Core | Keep | K | Packed Tag/Length configuration; Configuration and lifetime; Length and source ranges; Protocol and binding scope |
| [docs/formats/support.md](https://github.com/OpenTLV/opentlv/blob/a5e2453c8cc156122cda01b02d3f91c33580b4f3/docs/formats/support.md) | `P/formats/support/` | Formats | `formats/support.md` | Core | Keep | K | Implemented format and standard capabilities; Native and tool inventory; Semantics beyond framing; Language framing presets |
| [docs/formats/variable.md](https://github.com/OpenTLV/opentlv/blob/a5e2453c8cc156122cda01b02d3f91c33580b4f3/docs/formats/variable.md) | `P/formats/variable/` | Formats | `formats/variable.md` | Core | Keep | K | Configurable variable-width TLV; Identifier encoding; Length encoding; Complete format; Declarative policies |
| [docs/getting-started/README.md](https://github.com/OpenTLV/opentlv/blob/a5e2453c8cc156122cda01b02d3f91c33580b4f3/docs/getting-started/README.md) | `P/getting-started/` | Getting Started | `getting-started/first-program.md + development/building/core.md`, linked from `getting-started/index.md` | Core technical content; Portal onboarding | Split | R | Implemented in #46: first build, all language quick starts and consuming Core stay under Getting Started. Archive/install packaging, C-only recipes and contributor test builds move to Development; every original block is retained. |
| [docs/guides/codecs.md](https://github.com/OpenTLV/opentlv/blob/a5e2453c8cc156122cda01b02d3f91c33580b4f3/docs/guides/codecs.md) | `P/guides/codecs/` | Bindings | `bindings/c/guides/codecs.md` | Core | Move | R | C value codecs; C++11 typed fields and Value codecs; ASN.1 universal-type codecs; Complete object mappings; Other languages |
| [docs/guides/copy.md](https://github.com/OpenTLV/opentlv/blob/a5e2453c8cc156122cda01b02d3f91c33580b4f3/docs/guides/copy.md) | `P/guides/copy/` | Bindings | `bindings/c/guides/copy.md` | Core | Move | R | Explicit TLV copies |
| [docs/guides/cxx-examples.md](https://github.com/OpenTLV/opentlv/blob/a5e2453c8cc156122cda01b02d3f91c33580b4f3/docs/guides/cxx-examples.md) | `P/guides/cxx-examples/` | Bindings | `bindings/cpp/examples.md` | Core / C++ | Move | R | C++ examples; Borrowed parsing and sequential iteration; Nested writing and traversal; Owning Document and Query; Typed Values and custom Formats |
| [docs/guides/diagnostics.md](https://github.com/OpenTLV/opentlv/blob/a5e2453c8cc156122cda01b02d3f91c33580b4f3/docs/guides/diagnostics.md) | `P/guides/diagnostics/` | Bindings | `bindings/c/guides/diagnostics.md` | Core | Move | R | Diagnostics; Evidence locations; Layering context; Reader diagnostics; Writer diagnostics |
| [docs/guides/document.md](https://github.com/OpenTLV/opentlv/blob/a5e2453c8cc156122cda01b02d3f91c33580b4f3/docs/guides/document.md) | `P/guides/document/` | Bindings | `bindings/c/guides/document.md` | Core | Move | R | Mutable documents; Original source locations; Formats; Building from a Tree Reader; Materializing a selected subtree |
| [docs/guides/examples.md](https://github.com/OpenTLV/opentlv/blob/a5e2453c8cc156122cda01b02d3f91c33580b4f3/docs/guides/examples.md) | `P/guides/examples/` | Getting Started | `getting-started/examples.md` | Core examples; Portal discovery | Move | R | Preserve workflow/language coverage and executable source inventory; link to each owning repository instead of copying examples. |
| [docs/guides/go.md](https://github.com/OpenTLV/opentlv/blob/a5e2453c8cc156122cda01b02d3f91c33580b4f3/docs/guides/go.md) | `P/guides/go/` | Bindings | `bindings/go/manual/index.md` | Core / go (until extraction) | Move | R | Using OpenTLV from Go; Install and integrate; Format and Element; Reader and input windows; Writer and nested construction |
| [docs/guides/memory.md](https://github.com/OpenTLV/opentlv/blob/a5e2453c8cc156122cda01b02d3f91c33580b4f3/docs/guides/memory.md) | `P/guides/memory/` | Bindings | `bindings/c/guides/memory.md` | Core | Move | R | Memory ownership and lifetime; Reading; Tags; Writing; Format context ownership and lifetime |
| [docs/guides/processing.md](https://github.com/OpenTLV/opentlv/blob/a5e2453c8cc156122cda01b02d3f91c33580b4f3/docs/guides/processing.md) | `P/guides/processing/` | Getting Started | `getting-started/processing.md` | Core | Move | R | Borrowed reading/selection versus owned editing; writing versus regeneration decision table. |
| [docs/guides/python.md](https://github.com/OpenTLV/opentlv/blob/a5e2453c8cc156122cda01b02d3f91c33580b4f3/docs/guides/python.md) | `P/guides/python/` | Bindings | `/python/{version}/guides/python/` | Python | Merge | P | Merge any unique content into the Python-owned guide before retiring this duplicate. Update obsolete bindings/python/opentlv installation/example paths; retain Reader, Writer, Schema, Codec, Document, Query and diagnostic examples. |
| [docs/guides/queries.md](https://github.com/OpenTLV/opentlv/blob/a5e2453c8cc156122cda01b02d3f91c33580b4f3/docs/guides/queries.md) | `P/guides/queries/` | Bindings | `bindings/c/guides/queries.md` | Core | Move | R | Path queries; Syntax; Static C plans and frontend-free execution; C++11 constexpr plans; Full programs and integration |
| [docs/guides/reader.md](https://github.com/OpenTLV/opentlv/blob/a5e2453c8cc156122cda01b02d3f91c33580b4f3/docs/guides/reader.md) | `P/guides/reader/` | Bindings | `bindings/c/guides/reader.md` | Core | Move | R | Pull-based Reader; Outcomes and state; Incremental input windows; Source and diagnostics; C++ iteration and parsing ranges |
| [docs/guides/rust.md](https://github.com/OpenTLV/opentlv/blob/a5e2453c8cc156122cda01b02d3f91c33580b4f3/docs/guides/rust.md) | `P/guides/rust/` | Bindings | `bindings/rust/manual/index.md` | Core / rust (until extraction) | Move | R | Using OpenTLV from Rust; Cargo setup; Reading; Writing; Error handling |
| [docs/guides/schemas.md](https://github.com/OpenTLV/opentlv/blob/a5e2453c8cc156122cda01b02d3f91c33580b4f3/docs/guides/schemas.md) | `P/guides/schemas/` | Bindings | `bindings/c/guides/schemas.md` | Core | Move | R | Optional C schemas; What a tag is, what a format allows and what a schema requires; Complete structure validation; Ordered, unordered and CHOICE-like structures; Value constraints on decoded values |
| [docs/guides/select-components.md](https://github.com/OpenTLV/opentlv/blob/a5e2453c8cc156122cda01b02d3f91c33580b4f3/docs/guides/select-components.md) | `P/guides/select-components/` | Getting Started | `getting-started/select-components.md` | Core | Move | R | Consumer-facing capability profiles and component recipes; Development links here for shared configuration details. |
| [docs/guides/writer.md](https://github.com/OpenTLV/opentlv/blob/a5e2453c8cc156122cda01b02d3f91c33580b4f3/docs/guides/writer.md) | `P/guides/writer/` | Bindings | `bindings/c/guides/writer.md` | Core | Move | R | Writer and scoped construction; Typed C++ writing; Workspace and scoped errors; Exact size measurement; Complete C++ example |
| [docs/index.md](https://github.com/OpenTLV/opentlv/blob/a5e2453c8cc156122cda01b02d3f91c33580b4f3/docs/index.md) | `P/` | Home | `index.md` | Portal | Move | K | Transfer the ecosystem introduction and progressive entry links from Core to Portal; preserve all audience routes. |
| [docs/playground/index.md](https://github.com/OpenTLV/opentlv/blob/a5e2453c8cc156122cda01b02d3f91c33580b4f3/docs/playground/index.md) | `P/playground/` | Tools | `tools/playground/index.md` | Portal UI; Core WASM | Replace | O | Core is already a hand-off stub. Portal supplies the actual UI; keep Core WASM build/test ownership and the archived playground link. |
| [docs/reference/README.md](https://github.com/OpenTLV/opentlv/blob/a5e2453c8cc156122cda01b02d3f91c33580b4f3/docs/reference/README.md) | `P/reference/` | Bindings | `bindings/reference.md + development/building/compilers.md` | Core reference; Portal discovery | Split | R | Keep C/C++ API entry links in Bindings; send compiler/build lookup to Development. Replace the old all-language-reference placement rule with links to product owners. |
| [docs/reference/c-api.md](https://github.com/OpenTLV/opentlv/blob/a5e2453c8cc156122cda01b02d3f91c33580b4f3/docs/reference/c-api.md) | `P/reference/c-api/` | Bindings | `bindings/c/reference/index.md` | Core | Move | R | Keep every API-area entry, including wire generation, traversal, diagnostics, schemas and codecs. Generated reference/api/c-api/** URLs stay unchanged. |
| [docs/reference/compilers.md](https://github.com/OpenTLV/opentlv/blob/a5e2453c8cc156122cda01b02d3f91c33580b4f3/docs/reference/compilers.md) | `P/reference/compilers/` | Development | `development/building/compilers.md` | Core | Move | R | Compiler support and Clang configuration; preserve supported minimums and platform constraints. |
| [docs/reference/cxx-api.md](https://github.com/OpenTLV/opentlv/blob/a5e2453c8cc156122cda01b02d3f91c33580b4f3/docs/reference/cxx-api.md) | `P/reference/cxx-api/` | Bindings | `bindings/cpp/reference/index.md` | Core | Move | R | Keep C++ reference entry and links to underlying C declarations. Generated reference/api/cxx-api/** URLs stay unchanged. |
| [docs/reference/errors.md](https://github.com/OpenTLV/opentlv/blob/a5e2453c8cc156122cda01b02d3f91c33580b4f3/docs/reference/errors.md) | `P/reference/errors/` | Bindings | `bindings/c/reference/errors.md` | Core | Move | R | Error codes; Result and diagnostic invariant; Query result and kind pairs; Regression enforcement; Diagnostic field ownership |
| [docs/standards/cer/README.md](https://github.com/OpenTLV/opentlv/blob/a5e2453c8cc156122cda01b02d3f91c33580b4f3/docs/standards/cer/README.md) | `P/standards/cer/` | Formats | `formats/asn1/cer.md` | Core | Merge | R | Merge with CER framing guide while retaining canonical segmentation, zero-copy segment access, strict value validation and limits. |
| [docs/standards/der/README.md](https://github.com/OpenTLV/opentlv/blob/a5e2453c8cc156122cda01b02d3f91c33580b4f3/docs/standards/der/README.md) | `P/standards/der/` | Formats | `formats/asn1/der.md` | Core | Merge | R | Merge with DER framing guide while retaining strict universal-value checks, schema-aware validation/encoding, traversal limits and errors. |
| [docs/standards/emv/README.md](https://github.com/OpenTLV/opentlv/blob/a5e2453c8cc156122cda01b02d3f91c33580b4f3/docs/standards/emv/README.md) | `P/standards/emv/` | Formats | `formats/emv/index.md` | Core | Move | R | Preserve Book 3 scope, dictionary migration, contexts, DOLs, value representations, structural checks, limits and byte examples. |

## Independent product page mapping

Keep the detailed manuals in their owning repositories and their independent
publication trees. Catalog pages link to the product entry points; they do not
reproduce product navigation inside the central six-section navigation. The
selected-source manuals render under the new Bindings/Tools manual paths
described above; the old `P/cli`, `P/lua` and `P/python` page URLs are not kept.
The table's site-root destinations describe independent product publication,
not a redirect from a portal-selected source to a different product revision.

| Current source | Current URL | Section | Target | Owner after migration | Action | URL rule | Content to preserve |
| --- | --- | --- | --- | --- | --- | --- | --- |
| [docs/README.md](https://github.com/OpenTLV/opentlv-cli/blob/abd2bce09a9f25071a41d7c1f3249fd48e8a0b20/docs/README.md) | `P/cli/` | Tools | `/cli/{version}/` | Cli | Keep | P | Command-line tool; First inspection; Build and install; Commands; Output |
| [docs/development.md](https://github.com/OpenTLV/opentlv-cli/blob/abd2bce09a9f25071a41d7c1f3249fd48e8a0b20/docs/development.md) | `P/cli/development/` | Tools | `/cli/{version}/development/` | Cli | Keep | P | CLI development; Requirements; Standalone build; Local workspace; Presets and build configurations |
| [docs/json-schema.md](https://github.com/OpenTLV/opentlv-cli/blob/abd2bce09a9f25071a41d7c1f3249fd48e8a0b20/docs/json-schema.md) | `P/cli/json-schema/` | Tools | `/cli/{version}/json-schema/` | Cli | Keep | P | TLV JSON document; Document; Elements; Round trip; Format constraints |
| [docs/releases.md](https://github.com/OpenTLV/opentlv-cli/blob/abd2bce09a9f25071a41d7c1f3249fd48e8a0b20/docs/releases.md) | `P/cli/releases/` | Tools | `/cli/{version}/releases/` | Cli | Keep | P | CLI versions and releases; Version reporting; Development checks; Request a release; Release evidence |
| [docs/api.md](https://github.com/OpenTLV/opentlv-lua/blob/6f610f5552a64efa21aeeb863ad161c91154dbc8/docs/api.md) | `P/lua/api/` | Bindings | `/lua/{version}/api/` | Lua | Keep | P | Using OpenTLV from Lua; Setup; Reading; Visitor and tree traversal; Error handling |
| [docs/development.md](https://github.com/OpenTLV/opentlv-lua/blob/6f610f5552a64efa21aeeb863ad161c91154dbc8/docs/development.md) | `P/lua/development/` | Bindings | `/lua/{version}/development/` | Lua | Keep | P | Development; Requirements; Local workspace Core; Installed Core; Pinned remote Core |
| [docs/implementation.md](https://github.com/OpenTLV/opentlv-lua/blob/6f610f5552a64efa21aeeb863ad161c91154dbc8/docs/implementation.md) | `P/lua/implementation/` | Bindings | `/lua/{version}/implementation/` | Lua | Keep | P | Lua bindings (experimental); Build; Versioning; Continuous integration; Codec implementation |
| [docs/migration.md](https://github.com/OpenTLV/opentlv-lua/blob/6f610f5552a64efa21aeeb863ad161c91154dbc8/docs/migration.md) | `P/lua/migration/` | Bindings | `/lua/{version}/migration/` | Lua | Keep | P | Lua source migration; Provenance; Source inventory; Preserved contracts; Verification and remaining validation |
| [docs/quality-gates.md](https://github.com/OpenTLV/opentlv-lua/blob/6f610f5552a64efa21aeeb863ad161c91154dbc8/docs/quality-gates.md) | `P/lua/quality-gates/` | Bindings | `/lua/{version}/quality-gates/` | Lua | Keep | P | Lua quality gates; Entry points; Core verification; Module artifacts; Timings and acceptance |
| [docs/releases.md](https://github.com/OpenTLV/opentlv-lua/blob/6f610f5552a64efa21aeeb863ad161c91154dbc8/docs/releases.md) | `P/lua/releases/` | Bindings | `/lua/{version}/releases/` | Lua | Keep | P | Lua releases; Preparation; Verification and publication |
| [docs/testing.md](https://github.com/OpenTLV/opentlv-lua/blob/6f610f5552a64efa21aeeb863ad161c91154dbc8/docs/testing.md) | `P/lua/testing/` | Bindings | `/lua/{version}/testing/` | Lua | Keep | P | Lua tests and CI; Ownership and migration baseline; CI selection and ownership; Historical migration validation; Comparing with Core |
| [docs/versioning.md](https://github.com/OpenTLV/opentlv-lua/blob/6f610f5552a64efa21aeeb863ad161c91154dbc8/docs/versioning.md) | `P/lua/versioning/` | Bindings | `/lua/{version}/versioning/` | Lua | Keep | P | Lua binding versioning; Version metadata; First standalone release baseline |
| [docs/development/python.md](https://github.com/OpenTLV/opentlv-python/blob/d846b4ff7f2c74fbf0571a065da1d83698b6f40c/docs/development/python.md) | `P/python/development/python/` | Bindings | `/python/{version}/development/python/` | Python | Keep | P | Python development; Build; Core selection; Local workspace development; Supported Python versions |
| [docs/guides/python.md](https://github.com/OpenTLV/opentlv-python/blob/d846b4ff7f2c74fbf0571a065da1d83698b6f40c/docs/guides/python.md) | `P/python/guides/python/` | Bindings | `/python/{version}/guides/python/` | Python | Keep | P | Using OpenTLV from Python; Setup; Activate the virtual environment for your shell before installing.; Reading; Writing |
| [docs/migration.md](https://github.com/OpenTLV/opentlv-python/blob/d846b4ff7f2c74fbf0571a065da1d83698b6f40c/docs/migration.md) | `P/python/migration/` | Bindings | `/python/{version}/migration/` | Python | Keep | P | Python source migration; Provenance; Source inventory; Preserved contracts; Supported versions and configurations at the baseline |
| [docs/quality-gates.md](https://github.com/OpenTLV/opentlv-python/blob/d846b4ff7f2c74fbf0571a065da1d83698b6f40c/docs/quality-gates.md) | `P/python/quality-gates/` | Bindings | `/python/{version}/quality-gates/` | Python | Keep | P | Python quality gates; Documentation portal notifications; Supported configurations; Test ownership and quality; Dependency verification |
| [docs/releases.md](https://github.com/OpenTLV/opentlv-python/blob/d846b4ff7f2c74fbf0571a065da1d83698b6f40c/docs/releases.md) | `P/python/releases/` | Bindings | `/python/{version}/releases/` | Python | Keep | P | Python release preparation; Prepare a candidate; GitHub release and documentation publication; Future PyPI publication (separate approval and issue) |
| [docs/validation/ci.md](https://github.com/OpenTLV/opentlv-python/blob/d846b4ff7f2c74fbf0571a065da1d83698b6f40c/docs/validation/ci.md) | `P/python/validation/ci/` | Bindings | `/python/{version}/validation/ci/` | Python | Keep | P | Python CI validation; Scope; Completed local checks; Diagnostics resolved during validation; Hosted Full follow-up and shell correction (2026-10-21) |
| [docs/validation/layout.md](https://github.com/OpenTLV/opentlv-python/blob/d846b4ff7f2c74fbf0571a065da1d83698b6f40c/docs/validation/layout.md) | `P/python/validation/layout/` | Bindings | `/python/{version}/validation/layout/` | Python | Keep | P | Source layout validation |
| [docs/validation/packaging.md](https://github.com/OpenTLV/opentlv-python/blob/d846b4ff7f2c74fbf0571a065da1d83698b6f40c/docs/validation/packaging.md) | `P/python/validation/packaging/` | Bindings | `/python/{version}/validation/packaging/` | Python | Keep | P | Independent packaging validation (#4); Scope; Completed checks; Local environment notes; Remaining hosted and release evidence |
| [docs/validation/standalone-build.md](https://github.com/OpenTLV/opentlv-python/blob/d846b4ff7f2c74fbf0571a065da1d83698b6f40c/docs/validation/standalone-build.md) | `P/python/validation/standalone-build/` | Bindings | `/python/{version}/validation/standalone-build/` | Python | Keep | P | Standalone Python build validation; Dependency and implementation; Completed checks; Verification tests; Local evidence and limitations |
| [docs/versioning.md](https://github.com/OpenTLV/opentlv-python/blob/d846b4ff7f2c74fbf0571a065da1d83698b6f40c/docs/versioning.md) | `P/python/versioning/` | Bindings | `/python/{version}/versioning/` | Python | Keep | P | Python binding versioning |

### Product entry points

All root-relative URLs in this table are below
`https://opentlv.github.io/opentlv-docs/`, not below a Core version.

| Product | Portal discovery target | Detailed documentation / product boundary |
| --- | --- | --- |
| C | `bindings/c/` | Core-owned guide and C API landing targets above; preserve `P/reference/api/c-api/**` and symbol fragments. |
| C++ | `bindings/cpp/` | Core-owned C++ examples/reference and shared C contracts; preserve `P/reference/api/cxx-api/**` and C cross-links. |
| CLI | `tools/otlv/` | Retain `/cli/`, `/cli/stable/` and `/cli/{version}/`, including `json-schema/`, `development/` and `releases/`. |
| Lua | `bindings/lua/` | Retain `/lua/`, `/lua/stable/` and `/lua/{version}/`; API entry is `api/` inside the product snapshot. |
| Python | `bindings/python/` | Retain `/python/`, `/python/stable/` and `/python/{version}/`; API entry is `guides/python/` inside the product snapshot. |
| Rust / Go | `bindings/rust/`, `bindings/go/` | Current in-tree Core manuals map above; keep their experimental status and repository links. Extraction/publication is not part of #44. |
| WASM | `bindings/wasm/` | Core owns module/build/test documentation; Portal owns the playground UI at `tools/playground/`. |
| imtlv | `tools/imtlv/` | Planned entry only in #48; no existing source, download or release documentation is asserted. |

Root product routes are publication contracts from the existing configuration,
not evidence that a first Lua/Python release is already deployed. Before a
catalog links a stable manual, verify that entry and page exist; otherwise link
the owning repository manual and mark release documentation unavailable.
Keep product versions independent and retain a return link to the portal.

## Repository-only Markdown and entry material

These 34 files are not mounted pages. Every row keeps its existing source URL
(G: no portal redirect), owner and complete content. The target is the unchanged
repository path; the Section column identifies where a portal overview should
link to it. Reuse introductory material through links or a reviewed source
transfer, not by importing entire README, release history or test manuals.
Internal templates/instructions remain repository guidance, not public nav.

| Owner | Current source | Section | Target | Action / URL rule | Content / role |
| --- | --- | --- | --- | --- | --- |
| portal | [CHANGELOG.md](https://github.com/OpenTLV/opentlv-docs/blob/882d8eeb366129adf15e50748fc1affe57c83be9/CHANGELOG.md) | Development | `portal:CHANGELOG.md` | Keep / G | Changelog; [Unreleased]; Changed; Fixed; Added |
| portal | [README.md](https://github.com/OpenTLV/opentlv-docs/blob/882d8eeb366129adf15e50748fc1affe57c83be9/README.md) | Home | `portal:README.md` | Keep / G | OpenTLV documentation portal; Prerequisites; Setup; CLI documentation source; Lua documentation source |
| core | [.github/PULL_REQUEST_TEMPLATE.md](https://github.com/OpenTLV/opentlv/blob/a5e2453c8cc156122cda01b02d3f91c33580b4f3/.github/PULL_REQUEST_TEMPLATE.md) | Development | `core:.github/PULL_REQUEST_TEMPLATE.md` | Keep / G | Description; Related Issue; Type of Change; Testing; API / Compatibility Impact |
| core | [AGENTS.md](https://github.com/OpenTLV/opentlv/blob/a5e2453c8cc156122cda01b02d3f91c33580b4f3/AGENTS.md) | Development | `core:AGENTS.md` | Keep / G | Repository instructions; Architecture; Changelog; Public API documentation |
| core | [CHANGELOG.md](https://github.com/OpenTLV/opentlv/blob/a5e2453c8cc156122cda01b02d3f91c33580b4f3/CHANGELOG.md) | Development | `core:CHANGELOG.md` | Keep / G | Changelog; [Unreleased]; Fixed; Changed; Added |
| core | [CODE_OF_CONDUCT.md](https://github.com/OpenTLV/opentlv/blob/a5e2453c8cc156122cda01b02d3f91c33580b4f3/CODE_OF_CONDUCT.md) | Development | `core:CODE_OF_CONDUCT.md` | Keep / G | Contributor Covenant Code of Conduct; Our Pledge; Our Standards; Enforcement Responsibilities; Scope |
| core | [CONTRIBUTING.md](https://github.com/OpenTLV/opentlv/blob/a5e2453c8cc156122cda01b02d3f91c33580b4f3/CONTRIBUTING.md) | Development | `core:CONTRIBUTING.md` | Keep / G | Contributing to OpenTLV; Source license headers; Public API documentation; Deterministic property tests; Generate the C API reference |
| core | [README.md](https://github.com/OpenTLV/opentlv/blob/a5e2453c8cc156122cda01b02d3f91c33580b4f3/README.md) | Home | `core:README.md` | Keep / G | Why OpenTLV?; What you can do; Quick start; Build and integrate; Documentation |
| core | [ROADMAP.md](https://github.com/OpenTLV/opentlv/blob/a5e2453c8cc156122cda01b02d3f91c33580b4f3/ROADMAP.md) | Development | `core:ROADMAP.md` | Keep / G | Roadmap; Phase 1 — Execution Foundation; Phase 2 — Runtime Model & OTLV; Phase 3 — Protocol Inference; Phase 4 — Compilation |
| core | [SECURITY.md](https://github.com/OpenTLV/opentlv/blob/a5e2453c8cc156122cda01b02d3f91c33580b4f3/SECURITY.md) | Development | `core:SECURITY.md` | Keep / G | Security Policy; Supported versions; Reporting a vulnerability; What to include; What to expect |
| core | [benchmarks/README.md](https://github.com/OpenTLV/opentlv/blob/a5e2453c8cc156122cda01b02d3f91c33580b4f3/benchmarks/README.md) | Development | `core:benchmarks/README.md` | Keep / G | Local benchmarks; Schema definition checking and input processing; Public C++ Reader and Document; Wait until other builds and tests have stopped before collecting timings. |
| core | [benchmarks/baselines/README.md](https://github.com/OpenTLV/opentlv/blob/a5e2453c8cc156122cda01b02d3f91c33580b4f3/benchmarks/baselines/README.md) | Development | `core:benchmarks/baselines/README.md` | Keep / G | Benchmark baselines |
| core | [bindings/go/README.md](https://github.com/OpenTLV/opentlv/blob/a5e2453c8cc156122cda01b02d3f91c33580b4f3/bindings/go/README.md) | Bindings | `core:bindings/go/README.md` | Keep / G | Go binding (experimental); Package boundary; Ownership and lifetime; User documentation; Build and run |
| core | [examples/nfc/type2/README.md](https://github.com/OpenTLV/opentlv/blob/a5e2453c8cc156122cda01b02d3f91c33580b4f3/examples/nfc/type2/README.md) | Getting Started | `core:examples/nfc/type2/README.md` | Keep / G | NFC Type 2 validation corpus; Decode and encode the sample; Positive vectors; Invalid vectors; Run validation |
| core | [examples/tlv++/src/README.md](https://github.com/OpenTLV/opentlv/blob/a5e2453c8cc156122cda01b02d3f91c33580b4f3/examples/tlv++/src/README.md) | Getting Started | `core:examples/tlv++/src/README.md` | Keep / G | C++ examples; Common operations; Advanced control |
| core | [examples/tlv/src/README.md](https://github.com/OpenTLV/opentlv/blob/a5e2453c8cc156122cda01b02d3f91c33580b4f3/examples/tlv/src/README.md) | Getting Started | `core:examples/tlv/src/README.md` | Keep / G | C examples; Use cases; API tour; Formats; Builtins |
| core | [tests/README.md](https://github.com/OpenTLV/opentlv/blob/a5e2453c8cc156122cda01b02d3f91c33580b4f3/tests/README.md) | Development | `core:tests/README.md` | Keep / G | Test layout |
| core | [tests/property/README.md](https://github.com/OpenTLV/opentlv/blob/a5e2453c8cc156122cda01b02d3f91c33580b4f3/tests/property/README.md) | Development | `core:tests/property/README.md` | Keep / G | Deterministic property suite; Build and run; Corpus contract; Wire property and coverage; Failure evidence and reproduction |
| core | [tests/query/README.md](https://github.com/OpenTLV/opentlv/blob/a5e2453c8cc156122cda01b02d3f91c33580b4f3/tests/query/README.md) | Development | `core:tests/query/README.md` | Keep / G | Query conformance; F2 completion evidence (#520); F3 completion evidence (#521); Adversarial API verification |
| cli | [.github/PULL_REQUEST_TEMPLATE.md](https://github.com/OpenTLV/opentlv-cli/blob/abd2bce09a9f25071a41d7c1f3249fd48e8a0b20/.github/PULL_REQUEST_TEMPLATE.md) | Development | `cli:.github/PULL_REQUEST_TEMPLATE.md` | Keep / G | Description; Related Issue; Type; Testing; Checklist |
| cli | [CHANGELOG.md](https://github.com/OpenTLV/opentlv-cli/blob/abd2bce09a9f25071a41d7c1f3249fd48e8a0b20/CHANGELOG.md) | Development | `cli:CHANGELOG.md` | Keep / G | Changelog; [Unreleased]; Changed; Added |
| cli | [CONTRIBUTING.md](https://github.com/OpenTLV/opentlv-cli/blob/abd2bce09a9f25071a41d7c1f3249fd48e8a0b20/CONTRIBUTING.md) | Development | `cli:CONTRIBUTING.md` | Keep / G | Contributing to OpenTLV CLI; Development; Contributor tools; License and provenance; Changelog |
| cli | [README.md](https://github.com/OpenTLV/opentlv-cli/blob/abd2bce09a9f25071a41d7c1f3249fd48e8a0b20/README.md) | Tools | `cli:README.md` | Keep / G | OpenTLV CLI; Current status; Requirements; Standalone build; Local workspace and offline use |
| cli | [src/README.md](https://github.com/OpenTLV/opentlv-cli/blob/abd2bce09a9f25071a41d7c1f3249fd48e8a0b20/src/README.md) | Tools | `cli:src/README.md` | Keep / G | CLI implementation |
| cli | [tests/README.md](https://github.com/OpenTLV/opentlv-cli/blob/abd2bce09a9f25071a41d7c1f3249fd48e8a0b20/tests/README.md) | Development | `cli:tests/README.md` | Keep / G | CLI tests; Run the regression suites; Frozen behavior comparison; Core dependency integration; Fixture ownership and provenance |
| cli | [tests/baseline/README.md](https://github.com/OpenTLV/opentlv-cli/blob/abd2bce09a9f25071a41d7c1f3249fd48e8a0b20/tests/baseline/README.md) | Development | `cli:tests/baseline/README.md` | Keep / G | CLI migration regression baseline; Origin and scope; Existing regression tests and fixture inventory; Commands and arguments; Process and diagnostic contract |
| lua | [CHANGELOG.md](https://github.com/OpenTLV/opentlv-lua/blob/6f610f5552a64efa21aeeb863ad161c91154dbc8/CHANGELOG.md) | Development | `lua:CHANGELOG.md` | Keep / G | Changelog; [Unreleased]; Changed; Fixed; Added |
| lua | [README.md](https://github.com/OpenTLV/opentlv-lua/blob/6f610f5552a64efa21aeeb863ad161c91154dbc8/README.md) | Bindings | `lua:README.md` | Keep / G | opentlv-lua; Build; LuaRocks; Migration status; Repository layout |
| lua | [provenance/original-readme.md](https://github.com/OpenTLV/opentlv-lua/blob/6f610f5552a64efa21aeeb863ad161c91154dbc8/provenance/original-readme.md) | Development | `lua:provenance/original-readme.md` | Keep / G | opentlv (Lua, experimental); Build; Test; Writing; Schema validation |
| python | [CHANGELOG.md](https://github.com/OpenTLV/opentlv-python/blob/d846b4ff7f2c74fbf0571a065da1d83698b6f40c/CHANGELOG.md) | Development | `python:CHANGELOG.md` | Keep / G | Changelog; [Unreleased]; Changed; Fixed; Added |
| python | [CONTRIBUTING.md](https://github.com/OpenTLV/opentlv-python/blob/d846b4ff7f2c74fbf0571a065da1d83698b6f40c/CONTRIBUTING.md) | Development | `python:CONTRIBUTING.md` | Keep / G | Contributing to opentlv-python |
| python | [README.md](https://github.com/OpenTLV/opentlv-python/blob/d846b4ff7f2c74fbf0571a065da1d83698b6f40c/README.md) | Bindings | `python:README.md` | Keep / G | opentlv-python; Install from source; Activate the virtual environment for your shell.; Dependency assurance; Layout and validation |
| python | [native/README.md](https://github.com/OpenTLV/opentlv-python/blob/d846b4ff7f2c74fbf0571a065da1d83698b6f40c/native/README.md) | Bindings | `python:native/README.md` | Keep / G | opentlv-core (experimental) |
| python | [src/README.md](https://github.com/OpenTLV/opentlv-python/blob/d846b4ff7f2c74fbf0571a065da1d83698b6f40c/src/README.md) | Bindings | `python:src/README.md` | Keep / G | opentlv (experimental) |

## Duplicates, obsolete guidance and deliberate retention

| Finding at the pinned baseline | Disposition and preservation requirement | Follow-up |
| --- | --- | --- |
| Core `guides/python.md` and Python `guides/python.md` describe the same API. The Core copy still installs `./bindings/python/opentlv` and links examples/tests under the old layout; the selected Python source installs `./src`. | Merge into the Python-owned manual after comparing sections, examples and anchors. The obsolete paths are not a reason to discard API, error, lifetime or Query contracts. Use the new canonical Python destinations under rule P. | #48 |
| Core `development/python.md` describes the pre-cutover hand-off as still pending, while Python is already a required portal source. | Split: update the stale cutover statement later; retain Core-owned vocabulary-generator commands, shared test fixtures, native CI boundaries and dependency coordination. Link Python build/CI/versioning details to their owner. | #49 |
| Core and Portal both track the logo guide and playground page. Assembly already overrides the Core pages. | Replace the two assembled Core copies with the existing Portal owners. Core's playground stub and historical link remain useful repository entry points; this issue does not delete them. | #45, #48, #49 |
| DER/CER each have a framing page under `formats/asn1/` and a deeper validation page under `standards/`. | Merge paired pages into the corresponding format destination. These are overlapping subjects, not interchangeable content: retain generic framing versus recursive/strict validation boundaries, schema rules, code, diagrams, limits and references. | #47 |
| `formats/support.md`, `concepts/bindings.md` and `formats/format-roadmap.md` are related catalogs. | Keep separate facts: implemented native/tool support, language capability parity, and planned expansion. Catalogs link to these sources; they must not flatten partial/planned support into a claim of implementation. | #47, #48 |
| Core `docs/index.md`, root `README.md`, `docs/README.md` and `reference/README.md` overlap as entry lists. | Transfer the portal Home introduction, retain compact repository entry points, split the reference routing, and link to canonical detailed pages. Preserve existing README quick-start anchors. | #46, #48 |
| Core `documentation-audit.md`, `documentation-layout.md` and `documentation-ownership.md` retain older inventories, section names and extraction guidance. | Keep dated audit evidence; reconcile current policy and links in a coordinated change. Do not call a historical inventory a current complete page list or replace technical ownership with portal navigation ownership. | #49 |
| Core format roadmap/candidate catalogue, LLDP review/conformance notes, runtime model and indefinite-boundary follow-up describe planned work or incomplete verification. | Keep with their explicit status. Historical/planned content is not obsolete merely because it is not implemented. Preserve normative-audit gaps and the distinction between local results and release evidence. | #47, #49 |
| Lua `provenance/original-readme.md`, Lua/Python migration manuals and validation records contain old layouts and historical commands. | Keep as immutable provenance/history with dates and links to current setup. Do not promote the original README to the current installation guide or rewrite old validation results as new evidence. | #48, #49 |

No whole technical page has been established as safe to delete. Consequently,
there are **no Remove dispositions**. Any later deletion needs an explicit
justification, a named replacement (or evidence of irrelevance), section-level
preservation review and canonical routing added to this map first.

## Examples, diagrams, assets and generated material

All inline code, byte dumps, ASCII trees, tables, explicit anchors and diagrams
travel with their page disposition. A heading-only rewrite is not preservation.
For each merge/split, compare the original source at the recorded commit with
the target and account for every block; preserve expected output, negative
examples, resource limits, ownership conditions and normative references.

| Existing material | Owner and destination | Action and validation obligation |
| --- | --- | --- |
| Core `docs/getting-started/README.md` language tabs and `<!-- example: ... -->` inclusions | Core/product executable sources; Getting Started quick start | Keep every existing language and round-trip example, including expected wire bytes/output. Route setup to product owners. Reuse existing example validation; do not create portal-owned copies of executables. |
| Core `docs/guides/examples.md`, `guides/cxx-examples.md`, `examples/tlv/src/`, `examples/tlv++/src/`, `examples/nfc/type2/` and in-tree binding examples | Core; Getting Started discovery and Bindings detail | Keep source inventory, workflow coverage, NFC positive/negative vectors and C++ examples. Source links remain pinned or resolve through the owning repository. |
| CLI manual command samples and `tests/`; Lua `examples/` and tests; Python `examples/`, `tests/python/` and Query runner | CLI/Lua/Python; independent manuals | Keep examples with their product contract and tests. Fix only confirmed stale source links during migration; preserve outputs, diagnostics and feature prerequisites. Portal validates integration, not duplicate component test suites. |
| Core concept diagrams in `architecture`, `architectural-rules`, `definition-boundaries`, `format-contract`, `format-capabilities`, `processing-pipeline`, `runtime-model`, `learning-model`, `core-types`, `value`, `length`, `endian` and `bindings` | Core; destinations in the page table | Keep conceptual trees, dependency direction, wire/logical distinctions and planned-phase labels; preserve text diagrams as well as any rendered visuals. |
| Format/standard byte layouts and trees, especially BER indefinite/EOC, CER nested containers, DER definite framing, Bluetooth LTV, fixed/packed/variable TLV, LLDP, NFC, EMV and candidate wire representations | Core-owned technical Markdown and examples; displayed under Formats | Keep annotated bytes, framing boundaries, primitive-versus-constructed distinctions, limitations and citations. Candidate diagrams remain marked as candidates, not supported presets. |
| Reader/Writer/Document/Query/Schema/Codec and diagnostic guide examples; Core `ROADMAP.md` phase diagrams | Core; Bindings guides, Development architecture and repository roadmap | Preserve lifetime/storage diagrams, continuation/error contracts and planned phase relationships. Do not infer new API or release support from reorganization. |
| Portal `docs/assets/{opentlv,opentlv-light,opentlv-dark,logo-mark,favicon}.svg`; Core `docs/assets/opentlv.svg` | Portal assets, Core repository image reference | Keep existing public `P/assets/*.svg` paths; guide moves to Development. Portal overlay remains canonical for the assembled logo. Preserve Core README image links and accessibility descriptions. |
| Portal `docs/playground/playground.js`, `playground.css` and DOM in `playground/index.md` | Portal; `tools/playground/` page | Keep existing `P/playground/*.js` and `*.css` asset URLs and DOM contracts initially. Resolve module/assets from the moved page correctly; do not interpret a page redirect as asset migration. |
| Core `docs/development/ci-baseline.json`; Lua `docs/ci-baseline.json`, `docs/migration/source-inventory.json` | Respective source owners; same source paths | Keep machine-readable evidence and download links at their current assembled suffixes. These are supporting files, not new navigation pages. |
| Python `docs/migration/{original-python.yml,source-inventory.json,validation.json,windows-baseline.log,windows-imported.log}` and `docs/validation/{ci,packaging,standalone-build}.json` | Python; independent migration/validation manuals | Keep exact historical evidence files and relative links alongside their manuals. Do not regenerate old records as part of restructuring. |
| Generated `reference/api/c-api/**` and `reference/api/cxx-api/**` | Core public headers/Doxygen; linked from Bindings | Keep both entire trees, HTML pages, symbol anchors, search data, images and C/C++ cross-links at existing URLs. Generate from the selected Core revision; never maintain generated API prose in Portal. |
| Generated `playground/wasm/{opentlv.mjs,query.mjs,opentlv-core.js,opentlv-core.wasm,wasm-source.json}` | Core WASM bytes; Portal integration | Keep selected-commit identity, all files and integrity metadata. Validate parsing and failure behavior under the new page without changing the release pipeline. |
| `source-revision.json`, API provenance, source locks, product version metadata and archived snapshots | Portal publication from exact component inputs | Keep provenance and immutable history. A reorganized page cannot replace source identity with a moving branch or treat a local preview as publishable evidence. |

The static non-Markdown docs inventory is 2 Core files, 7 Portal files,
0 CLI files, 2 Lua files and 8 Python files, enumerated above. The Portal logo
overlay makes one Core asset redundant in assembly, not absent from its source
inventory. Generated API/WASM trees are open-ended generated sets: #50 must
compare the full actual output manifest, not only representative index pages.

## Section preservation for merges and splits

| Original page / section group | Destination and review obligation |
| --- | --- |
| Core Formats index: Choose a format; overview lists and discovery links | Portal-owned `formats/index.md`: retain the catalog and short introductions, linking to Core-owned detailed pages and support evidence. Keep the existing `P/formats/` entry. |
| Core Formats index: Compare formats, technical capability tables, Reading one element, Traversing multiple elements, Writing one element, Generic interface, Nested traversal and Formats whose length precedes the tag | Core-owned source rendered at `formats/guide.md`: preserve every technical table, rule, example and limitation. Link to the new destinations; no technical source ownership transfers to Portal. |
| Getting Started: Build from a checkout; Quick start (all language tabs); Consume Core from another CMake project (source and installed dependency) | `getting-started/first-program.md`, linked from the portal `getting-started/index.md`: retains every block, toolchain prerequisite, static/shared linkage and runtime-loader guidance. First-run examples for every existing language remain available. |
| Getting Started: Install and generate distribution archives; C-only build; Build and run tests | `development/building/core.md`: retains commands/options and distribution layout. Internal links target these sections directly, with no old anchors at `P/getting-started/`. Consumer install/consume routing remains in Getting Started. |
| Reference: C and C++ API entry points, generated-reference explanation and lookup-versus-guide distinction | `bindings/reference.md`, linking to the two native reference destinations; preserve existing reference-generation links and source provenance. |
| Reference: supported compilers/build settings and future manual placement rule | Link to `development/building/compilers.md`; replace the placement rule with owner-specific manual links, retaining the useful API lookup guidance. |
| Core Python development: Build; Versioning; Continuous integration; Migration and documentation cutover | Python standalone build, versioning, quality-gate and migration manuals own their details. `development/bindings/python.md` retains only Core coordination and links, including Core's continued Python-interpreter use. |
| Core Python development: Diagnostic vocabulary; shared native adapters, fixtures and cross-language release evidence | `development/bindings/python.md`: retain exact generator commands, output-root constraints, owner/test boundaries and dependency-review requirements. |
| Core Python user guide: Setup and runnable example/test links | Python `guides/python.md`: use the current standalone paths; the original and canonical guide diff establishes obsolete layout links. Retain unique content during the owner-maintained merge; no old-URL hand-off is required. |
| Core Python user guide: Reading, Writing, Validating, Definition registries, Codec, Documents, Error handling, C API relationship, tree measurement/materialization, compiled Query and Next step | Python `guides/python.md`: compare each section against its canonical counterpart and retain any unique API/lifetime/diagnostic examples before removing the duplicate body. |
| DER/CER format pages: API/build, scope/limits, minimal C usage, framing and byte examples | Keep these in `formats/asn1/{der,cer}.md` with existing anchors, including explicit `layout-and-typical-use`. Preserve descriptor-only versus recursive/strict semantics. |
| DER standards page: supported scope, tag inspection, traversal/limits, encode, strict universal values, schema-aware validation/encoding, errors/generic I/O | Merge into `formats/asn1/der.md`; retain strict type coverage and unsupported types, calendar/IRI limitations, SET/SET OF rules, schema graph/resource limits and diagnostics. Update internal links to the merged canonical sections. |
| CER standards page: supported scope, read/traverse, canonical segmentation, zero-copy segments, encode, strict values, errors/offsets/limits | Merge into `formats/asn1/cer.md`; retain segmentation boundaries, borrowed storage, EOC rules and validation limits. Update internal links to the merged canonical sections. |

## Review and implementation hand-off

| Follow-up | Input from this map | Evidence required before completion |
| --- | --- | --- |
| [#45 Navigation](https://github.com/OpenTLV/opentlv-docs/issues/45) | Six sections, canonical target paths and the revised R/P routing policy | All landing/secondary navigation targets exist; no silent content omission; internal links resolve to new paths without old-URL aliases; source ownership remains explicit. |
| [#46 Home and Getting Started](https://github.com/OpenTLV/opentlv-docs/issues/46) | Implemented: portal Home/onboarding and split Core build guidance | All first-task blocks, diagrams and consumer integration requirements retained; existing Core README source callers still resolve. |
| [#47 Formats](https://github.com/OpenTLV/opentlv-docs/issues/47) | All format/standard rows, merge ledger and support/planned distinctions | Keep detailed format sources and DER/CER merges in Core; Portal owns only discovery. Preserve every protocol's unique examples, limits and references; review both DER/CER sources and the new internal links. |
| [#48 Bindings and Tools](https://github.com/OpenTLV/opentlv-docs/issues/48) | Catalog entries, native references, product maps, Python duplicate and playground | Validate actual product entry/version URLs, fallback links and return navigation; no copied product manuals; imtlv remains planned. |
| [#49 Development](https://github.com/OpenTLV/opentlv-docs/issues/49) | Architecture, build/contribution/test/release routing, historical evidence and ownership-policy reconciliation | Maintain one technical source of truth per repository and distinguish current instructions from historical validation/planned architecture. |
| [#50 Validation](https://github.com/OpenTLV/opentlv-docs/issues/50) | All 142 original Markdown rows plus assets/generated sets | Compare final destinations with this baseline and newer pin deltas; run existing strict links/anchors, inventory/example, API and browser checks; verify independent publishing and immutable history with hosted evidence. |

Maintainer review should explicitly accept or amend:

- Portal ownership of catalogs, short introductions and navigation, with Core
  ownership of detailed format Markdown, rules, limitations, technical examples
  and their correctness. C/C++ technical manuals and references also remain Core-owned.
- Every target, especially DER/CER merges, Python deduplication and build-guide
  splits; no source section may disappear without a recorded disposition.
- R/P canonical routing and product-version separation, without old-URL
  compatibility or guessed stable release targets.
- Preservation of historical/planned material and all assets/generated trees.

PR #56 merged the baseline, and #44 was closed as completed before the
maintainer requested implementation of #45. The navigation-phase amendment at
the top records which parts are implemented and which remain assigned to later
issues. #44 itself added no navigation changes, page moves, technical rewrites,
publishing workflow changes or remote release actions. Local checks establish
inventory coverage and document consistency; they do not establish hosted CI
or published URL availability.
