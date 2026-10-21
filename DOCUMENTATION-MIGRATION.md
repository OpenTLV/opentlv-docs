# Documentation inventory and migration mapping

Review baseline for [issue #44](https://github.com/OpenTLV/opentlv-docs/issues/44)
and [epic #43](https://github.com/OpenTLV/opentlv-docs/issues/43), prepared
2026-10-21. **Status: proposed; maintainer review pending.** This document does
not authorize or implement structural changes. Approval of its destinations,
ownership transfers and compatibility rules must be recorded in the #44 PR
before #45-#49 begin. #50 verifies the implemented result against the approved
map. A local inventory check is not human review or deployed-site validation.

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
| Formats | `formats/index.md` / `formats/` | Portal catalog and format narrative, reusing all existing format/standard prose; Core headers, tests and support evidence remain authoritative for behavior. |
| Bindings | `bindings/index.md` / `bindings/` | Portal discovery and short overview pages; C/C++ reference and shared contracts stay Core-owned, full Python/Lua manuals stay product-owned. |
| Tools | `tools/index.md` / `tools/` | Portal discovery, CLI overview and playground; CLI commands and release instructions remain CLI-owned. `imtlv` is planned, with no existing manual to migrate. |
| Development | `development/index.md` / `development/` | Portal contributor routing: Architecture, Building from Source, Contributing, Testing and Quality Gates, CI and Release Process. Core/product implementation instructions remain with their owners. |

Targets below are proposed **rendered document paths**, not commands to rename
files in a product repository. Navigation can organize Core-owned sources under
these sections without transferring their technical ownership. Where general
introduction/onboarding/format prose becomes Portal-owned, the follow-up must
coordinate a single canonical source transfer with Core and leave source links
or stubs there; do not maintain two editable manuals. Core API comments, format
behavior, examples, tests and capability evidence do not transfer to Portal.
This updates the earlier ownership policy only after coordinated review.

The catalogs add `bindings/{c,cpp,python,lua}/index.md` and
`tools/{otlv,imtlv}/index.md` as lightweight entry pages. Rust, Go and WASM remain
explicitly experimental/in-tree where documented; their existing manuals are
retained under the corresponding Bindings secondary navigation. No new product
repository or release is assumed. Common C/C++ guides remain shared; C++ and
other overviews link to those guides rather than duplicating their bodies.

## How to read the map and URL policy

Actions are **Keep**, **Move**, **Merge**, **Split**, **Replace**, or **Remove**.
Keep may change navigation grouping without changing the page body or URL.
Move includes a coordinated source-owner transfer even when the rendered URL
stays the same. Merge/Split require a section-by-section preservation check;
Replace requires a named successor. No source is approved for Remove here.

`P/` means `https://opentlv.github.io/opentlv-docs/<portal-version>/`;
for development use `<portal-version> = latest`. Current path cells list the
exact suffix to append. Relative target `.md` paths use normal MkDocs directory
URLs: `README.md` and `index.md` become the directory index, and `x.md` becomes
`x/`. A target starting `/cli/`, `/lua/` or `/python/` instead starts at the
**site root**, outside `P/`. `{version}` means a matching independently
published product version, not the Core version or an invented tag.

| Code | Required compatibility handling |
| --- | --- |
| K | Keep the current rendered URL and existing anchors; no page redirect. |
| R | Keep a compatibility page or supported redirect at the current URL for a changed target. Preserve every old fragment with equivalent section anchors or an explicit fragment map; for Split, route each section to its target. If the page URL stays the same, retain its old anchors there. |
| P | Product boundary: keep the old `P/` route tied to its selected source until a matching independent snapshot is verified. Then use a version-aware compatibility page linking the equivalent product page/sections. Never silently redirect an old pinned manual to moving `stable` or redirect to a missing release. |
| G | GitHub-only source; no published page redirect. Keep its repository path or provide a source stub in a coordinated owner PR. |
| O | Already overridden in assembly; use the Portal row for public URL compatibility and preserve the Core repository hand-off. |

Every R/P row is part of the compatibility work list, including anchors on
otherwise retained routes. For Merge, reconcile conflicting heading IDs and
keep aliases at **both** old entry points. A redirect that loses the requested
fragment is insufficient. Known callers include repository READMEs, changelogs,
source comments, examples, the existing Core ownership/audit tables and issue/PR
links. #50 must enumerate their links at implementation time and verify the
rendered destinations. Existing `link_aliases: ["main"]` is source-link rewriting,
not a public URL redirect mechanism.

Previously published immutable Core and product snapshots retain their bytes,
paths, assets and provenance. Apply this map to new builds and the development
entry only; do not rebuild old releases to install redirects. The site-root
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
| [docs/development/documentation-ownership.md](https://github.com/OpenTLV/opentlv/blob/a5e2453c8cc156122cda01b02d3f91c33580b4f3/docs/development/documentation-ownership.md) | `P/development/documentation-ownership/` | Development | `development/documentation/ownership.md` | Core boundaries; Portal routing | Move | R | Retain extraction history, inventories and source contract. Reconcile format/general prose transfers and completed Python cutover with this map in #49. |
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
| [docs/formats/README.md](https://github.com/OpenTLV/opentlv/blob/a5e2453c8cc156122cda01b02d3f91c33580b4f3/docs/formats/README.md) | `P/formats/` | Formats | `formats/index.md` | Portal prose; Core contracts | Move | K | C library formats; Choose a format; Generic core formats; Built-in standards; Compare formats |
| [docs/formats/asn1/ber.md](https://github.com/OpenTLV/opentlv/blob/a5e2453c8cc156122cda01b02d3f91c33580b4f3/docs/formats/asn1/ber.md) | `P/formats/asn1/ber/` | Formats | `formats/asn1/ber.md` | Portal prose; Core contracts | Move | K | BER-TLV; API and build; Scope and limits; Generic mechanics and ASN.1 rules; Minimal C usage |
| [docs/formats/asn1/cer.md](https://github.com/OpenTLV/opentlv/blob/a5e2453c8cc156122cda01b02d3f91c33580b4f3/docs/formats/asn1/cer.md) | `P/formats/asn1/cer/` | Formats | `formats/asn1/cer.md` | Portal prose; Core contracts | Merge | K | CER-TLV; API and build; Scope and limits; Minimal C usage; Framing and typical use |
| [docs/formats/asn1/der.md](https://github.com/OpenTLV/opentlv/blob/a5e2453c8cc156122cda01b02d3f91c33580b4f3/docs/formats/asn1/der.md) | `P/formats/asn1/der/` | Formats | `formats/asn1/der.md` | Portal prose; Core contracts | Merge | K | DER-TLV; API and build; Scope and limits; Minimal C usage; Framing and typical use |
| [docs/formats/bluetooth/README.md](https://github.com/OpenTLV/opentlv/blob/a5e2453c8cc156122cda01b02d3f91c33580b4f3/docs/formats/bluetooth/README.md) | `P/formats/bluetooth/` | Formats | `formats/bluetooth/README.md` | Portal prose; Core contracts | Move | K | Bluetooth LTV; API and build; Advertising Data Type definitions; Basic Advertising Data value codecs; Advertising Data schema |
| [docs/formats/custom/README.md](https://github.com/OpenTLV/opentlv/blob/a5e2453c8cc156122cda01b02d3f91c33580b4f3/docs/formats/custom/README.md) | `P/formats/custom/` | Formats | `formats/custom/README.md` | Portal prose; Core contracts | Move | K | Application-defined format example; API and build; Scope and limits; C usage; Byte example |
| [docs/formats/dhcp/README.md](https://github.com/OpenTLV/opentlv/blob/a5e2453c8cc156122cda01b02d3f91c33580b4f3/docs/formats/dhcp/README.md) | `P/formats/dhcp/` | Formats | `formats/dhcp/README.md` | Portal prose; Core contracts | Move | K | DHCPv4 option framing; Element and source contracts; Option definitions; Value codecs; Scope and composition |
| [docs/formats/fixed/configurable.md](https://github.com/OpenTLV/opentlv/blob/a5e2453c8cc156122cda01b02d3f91c33580b4f3/docs/formats/fixed/configurable.md) | `P/formats/fixed/configurable/` | Formats | `formats/fixed/configurable.md` | Portal prose; Core contracts | Move | K | Configurable fixed-width TLV; API and build; Standalone Field Encoding; Supported parameters; Wire representation |
| [docs/formats/format-catalogue.md](https://github.com/OpenTLV/opentlv/blob/a5e2453c8cc156122cda01b02d3f91c33580b4f3/docs/formats/format-catalogue.md) | `P/formats/format-catalogue/` | Formats | `formats/format-catalogue.md` | Portal prose; Core contracts | Move | K | Format candidate catalogue; ASN.1 notation (ITU-T X.680 series); Protocols using BER; ASN.1 standards; Smart cards and SIM |
| [docs/formats/format-examples.md](https://github.com/OpenTLV/opentlv/blob/a5e2453c8cc156122cda01b02d3f91c33580b4f3/docs/formats/format-examples.md) | `P/formats/format-examples/` | Formats | `formats/format-examples.md` | Portal prose; Core contracts | Move | K | Format trees and byte examples |
| [docs/formats/format-roadmap.md](https://github.com/OpenTLV/opentlv/blob/a5e2453c8cc156122cda01b02d3f91c33580b4f3/docs/formats/format-roadmap.md) | `P/formats/format-roadmap/` | Formats | `formats/format-roadmap.md` | Portal prose; Core contracts | Move | K | Format expansion candidates; Keep the core generic; Scope principle; How to read this catalogue; Components |
| [docs/formats/lldp-review.md](https://github.com/OpenTLV/opentlv/blob/a5e2453c8cc156122cda01b02d3f91c33580b4f3/docs/formats/lldp-review.md) | `P/formats/lldp-review/` | Formats | `formats/lldp-review.md` | Portal prose; Core contracts | Move | K | LLDP requirements, Format and runtime Layout review; Issue coverage; Evidence and scope; Preliminary wire requirements; Deferred normative verification checklist |
| [docs/formats/lldp/README.md](https://github.com/OpenTLV/opentlv/blob/a5e2453c8cc156122cda01b02d3f91c33580b4f3/docs/formats/lldp/README.md) | `P/formats/lldp/` | Formats | `formats/lldp/README.md` | Portal prose; Core contracts | Move | K | LLDP TLV support; API and build; Wire representation and logical model; Scope and errors; Schema and sequence validation |
| [docs/formats/lldp/conformance.md](https://github.com/OpenTLV/opentlv/blob/a5e2453c8cc156122cda01b02d3f91c33580b4f3/docs/formats/lldp/conformance.md) | `P/formats/lldp/conformance/` | Formats | `formats/lldp/conformance.md` | Portal prose; Core contracts | Move | K | LLDP reference tests and conformance boundary; Evidence; Reference vectors; Remaining normative audit |
| [docs/formats/nfc/README.md](https://github.com/OpenTLV/opentlv/blob/a5e2453c8cc156122cda01b02d3f91c33580b4f3/docs/formats/nfc/README.md) | `P/formats/nfc/` | Formats | `formats/nfc/README.md` | Portal prose; Core contracts | Move | K | NFC Forum Type 2 Tag TLV framing; Length encoding; Input and source ownership; Example; Bindings |
| [docs/formats/packed.md](https://github.com/OpenTLV/opentlv/blob/a5e2453c8cc156122cda01b02d3f91c33580b4f3/docs/formats/packed.md) | `P/formats/packed/` | Formats | `formats/packed.md` | Portal prose; Core contracts | Move | K | Packed Tag/Length configuration; Configuration and lifetime; Length and source ranges; Protocol and binding scope |
| [docs/formats/support.md](https://github.com/OpenTLV/opentlv/blob/a5e2453c8cc156122cda01b02d3f91c33580b4f3/docs/formats/support.md) | `P/formats/support/` | Formats | `formats/support.md` | Portal prose; Core contracts | Move | K | Implemented format and standard capabilities; Native and tool inventory; Semantics beyond framing; Language framing presets |
| [docs/formats/variable.md](https://github.com/OpenTLV/opentlv/blob/a5e2453c8cc156122cda01b02d3f91c33580b4f3/docs/formats/variable.md) | `P/formats/variable/` | Formats | `formats/variable.md` | Portal prose; Core contracts | Move | K | Configurable variable-width TLV; Identifier encoding; Length encoding; Complete format; Declarative policies |
| [docs/getting-started/README.md](https://github.com/OpenTLV/opentlv/blob/a5e2453c8cc156122cda01b02d3f91c33580b4f3/docs/getting-started/README.md) | `P/getting-started/` | Getting Started | `getting-started/index.md + development/building/core.md` | Portal onboarding; Core build | Split | R | Keep first build, C/C++ quick start and consuming Core under Getting Started. Route archive/install packaging, C-only recipes and contributor test builds to Development; preserve old section anchors. |
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
| [docs/standards/cer/README.md](https://github.com/OpenTLV/opentlv/blob/a5e2453c8cc156122cda01b02d3f91c33580b4f3/docs/standards/cer/README.md) | `P/standards/cer/` | Formats | `formats/asn1/cer.md` | Portal prose; Core contracts | Merge | R | Merge with CER framing guide while retaining canonical segmentation, zero-copy segment access, strict value validation and limits. |
| [docs/standards/der/README.md](https://github.com/OpenTLV/opentlv/blob/a5e2453c8cc156122cda01b02d3f91c33580b4f3/docs/standards/der/README.md) | `P/standards/der/` | Formats | `formats/asn1/der.md` | Portal prose; Core contracts | Merge | R | Merge with DER framing guide while retaining strict universal-value checks, schema-aware validation/encoding, traversal limits and errors. |
| [docs/standards/emv/README.md](https://github.com/OpenTLV/opentlv/blob/a5e2453c8cc156122cda01b02d3f91c33580b4f3/docs/standards/emv/README.md) | `P/standards/emv/` | Formats | `formats/emv/index.md` | Portal prose; Core contracts | Move | R | Preserve Book 3 scope, dictionary migration, contexts, DOLs, value representations, structural checks, limits and byte examples. |

## Independent product page mapping

Keep the detailed manuals in their owning repositories and their independent
publication trees. Catalog pages link to the product entry points; they do not
reproduce product navigation inside the central six-section navigation. The
legacy assembled `P/cli`, `P/lua` and `P/python` routes need the P policy even
though the product source action is Keep. Retaining a compatibility rendering
from the same canonical source is not a second editable manual.

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

| Product | Portal discovery target | Detailed documentation / compatibility contract |
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
| Core `guides/python.md` and Python `guides/python.md` describe the same API. The Core copy still installs `./bindings/python/opentlv` and links examples/tests under the old layout; the selected Python source installs `./src`. | Merge into the Python-owned manual after comparing sections, examples and anchors. The obsolete paths are not a reason to discard API, error, lifetime or Query contracts. Preserve `P/guides/python/` through rule P. | #48 |
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
preservation review and compatibility handling added to this map first.

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
| Format/standard byte layouts and trees, especially BER indefinite/EOC, CER nested containers, DER definite framing, Bluetooth LTV, fixed/packed/variable TLV, LLDP, NFC, EMV and candidate wire representations | Portal prose with Core behavior evidence; Formats destinations | Keep annotated bytes, framing boundaries, primitive-versus-constructed distinctions, limitations and citations. Candidate diagrams remain marked as candidates, not supported presets. |
| Reader/Writer/Document/Query/Schema/Codec and diagnostic guide examples; Core `ROADMAP.md` phase diagrams | Core; Bindings guides, Development architecture and repository roadmap | Preserve lifetime/storage diagrams, continuation/error contracts and planned phase relationships. Do not infer new API or release support from reorganization. |
| Portal `docs/assets/{opentlv,opentlv-light,opentlv-dark,logo-mark,favicon}.svg`; Core `docs/assets/opentlv.svg` | Portal assets, Core repository image reference | Keep existing public `P/assets/*.svg` paths; guide moves to Development. Portal overlay remains canonical for the assembled logo. Preserve Core README image links and accessibility descriptions. |
| Portal `docs/playground/playground.js`, `playground.css` and DOM in `playground/index.md` | Portal; `tools/playground/` page | Keep existing `P/playground/*.js` and `*.css` asset URLs and DOM contracts initially. Resolve module/assets from the moved page correctly; do not interpret a page redirect as asset migration. |
| Core `docs/development/ci-baseline.json`; Lua `docs/ci-baseline.json`, `docs/migration/source-inventory.json` | Respective source owners; same source paths | Keep machine-readable evidence and download links at their current assembled suffixes. These are supporting files, not new navigation pages. |
| Python `docs/migration/{original-python.yml,source-inventory.json,validation.json,windows-baseline.log,windows-imported.log}` and `docs/validation/{ci,packaging,standalone-build}.json` | Python; independent migration/validation manuals | Keep exact historical evidence files and relative links alongside their manuals. Do not regenerate old records as part of restructuring. |
| Generated `reference/api/c-api/**` and `reference/api/cxx-api/**` | Core public headers/Doxygen; linked from Bindings | Keep both entire trees, HTML pages, symbol anchors, search data, images and C/C++ cross-links at existing URLs. Generate from the selected Core revision; never maintain generated API prose in Portal. |
| Generated `playground/wasm/{opentlv.mjs,query.mjs,opentlv-core.js,opentlv-core.wasm,wasm-source.json}` | Core WASM bytes; Portal integration | Keep selected-commit identity, all files and integrity metadata. Validate parsing and failure behavior under the new page and compatibility entry without changing the release pipeline. |
| `source-revision.json`, API provenance, source locks, product version metadata and archived snapshots | Portal publication from exact component inputs | Keep provenance and immutable history. A reorganized page cannot replace source identity with a moving branch or treat a local preview as publishable evidence. |

The static non-Markdown docs inventory is 2 Core files, 7 Portal files,
0 CLI files, 2 Lua files and 8 Python files, enumerated above. The Portal logo
overlay makes one Core asset redundant in assembly, not absent from its source
inventory. Generated API/WASM trees are open-ended generated sets: #50 must
compare the full actual output manifest, not only representative index pages.

## Section preservation for merges and splits

| Original page / section group | Destination and review obligation |
| --- | --- |
| Getting Started: Build from a checkout; Quick start (all language tabs); Consume Core from another CMake project (source and installed dependency) | `getting-started/index.md`: keep first-task flow, toolchain prerequisites, static/shared linkage and runtime-loader guidance. First-run examples for every existing language remain available. |
| Getting Started: Install and generate distribution archives; C-only build; Build and run tests | `development/building/core.md`: preserve commands/options and distribution layout; keep old anchors at `P/getting-started/` linking to these sections. Consumer install/consume routing remains in Getting Started. |
| Reference: C and C++ API entry points, generated-reference explanation and lookup-versus-guide distinction | `bindings/reference.md`, linking to the two native reference destinations; preserve existing reference-generation links and source provenance. |
| Reference: supported compilers/build settings and future manual placement rule | Link to `development/building/compilers.md`; replace the placement rule with owner-specific manual links, retaining the useful API lookup guidance. |
| Core Python development: Build; Versioning; Continuous integration; Migration and documentation cutover | Python standalone build, versioning, quality-gate and migration manuals own their details. `development/bindings/python.md` retains only Core coordination and links, including Core's continued Python-interpreter use. |
| Core Python development: Diagnostic vocabulary; shared native adapters, fixtures and cross-language release evidence | `development/bindings/python.md`: retain exact generator commands, output-root constraints, owner/test boundaries and dependency-review requirements. |
| Core Python user guide: Setup and runnable example/test links | Python `guides/python.md`: use the current standalone paths; the original and canonical guide diff establishes obsolete layout links. Preserve old `P/guides/python/` anchors through the version-aware hand-off. |
| Core Python user guide: Reading, Writing, Validating, Definition registries, Codec, Documents, Error handling, C API relationship, tree measurement/materialization, compiled Query and Next step | Python `guides/python.md`: compare each section against its canonical counterpart and retain any unique API/lifetime/diagnostic examples before removing the duplicate body. |
| DER/CER format pages: API/build, scope/limits, minimal C usage, framing and byte examples | Keep these in `formats/asn1/{der,cer}.md` with existing anchors, including explicit `layout-and-typical-use`. Preserve descriptor-only versus recursive/strict semantics. |
| DER standards page: supported scope, tag inspection, traversal/limits, encode, strict universal values, schema-aware validation/encoding, errors/generic I/O | Merge into `formats/asn1/der.md`; retain strict type coverage and unsupported types, calendar/IRI limitations, SET/SET OF rules, schema graph/resource limits and diagnostics. Preserve old `standards/der/` fragments. |
| CER standards page: supported scope, read/traverse, canonical segmentation, zero-copy segments, encode, strict values, errors/offsets/limits | Merge into `formats/asn1/cer.md`; retain segmentation boundaries, borrowed storage, EOC rules and validation limits. Preserve old `standards/cer/` fragments. |

## Review and implementation hand-off

| Follow-up | Input from this map | Evidence required before completion |
| --- | --- | --- |
| [#45 Navigation](https://github.com/OpenTLV/opentlv-docs/issues/45) | Approved six sections, exact target paths and R/P compatibility work list | All landing/secondary navigation targets exist; no silent page omission; old routes and fragments resolve; source ownership transfers are coordinated. |
| [#46 Home and Getting Started](https://github.com/OpenTLV/opentlv-docs/issues/46) | Home, onboarding, model, examples and split build guidance | Retain entry points, all first-task examples, diagrams and consumer integration requirements; check Core README callers. |
| [#47 Formats](https://github.com/OpenTLV/opentlv-docs/issues/47) | All format/standard rows, merge ledger and support/planned distinctions | Preserve every protocol's unique examples, limits and references; review both DER/CER sources and all old fragments. |
| [#48 Bindings and Tools](https://github.com/OpenTLV/opentlv-docs/issues/48) | Catalog entries, native references, product maps, Python duplicate and playground | Validate actual product entry/version URLs, fallback links and return navigation; no copied product manuals; imtlv remains planned. |
| [#49 Development](https://github.com/OpenTLV/opentlv-docs/issues/49) | Architecture, build/contribution/test/release routing, historical evidence and ownership-policy reconciliation | Maintain one technical source of truth per repository and distinguish current instructions from historical validation/planned architecture. |
| [#50 Validation](https://github.com/OpenTLV/opentlv-docs/issues/50) | All 142 original Markdown rows plus assets/generated sets | Compare final destinations with this baseline and newer pin deltas; run existing strict links/anchors, inventory/example, API and browser checks; verify independent publishing and immutable history with hosted evidence. |

Maintainer review should explicitly accept or amend:

- The source-owner transfer for general and format prose, with Core technical
  contracts and executable examples remaining Core-owned.
- Every target, especially DER/CER merges, Python deduplication and build-guide
  splits; no source section may disappear without a recorded disposition.
- R/P compatibility handling, including fragments, product-version matching
  and unavailable-release fallback rather than guessed stable URLs.
- Preservation of historical/planned material and all assets/generated trees.

Record the approving PR/review and any amendments here when available. Until
then this is a reviewable proposal, and the "mapping reviewed before structural
changes" acceptance criterion remains pending. #44 adds no navigation changes,
page moves, technical rewrites, publishing workflow changes or remote release
actions. Local checks establish inventory coverage and document consistency;
they do not establish hosted CI, published URL availability or human approval.
