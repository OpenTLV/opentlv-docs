# Changelog

All notable changes to this project will be documented in this file.

## [Unreleased]

### Changed

- Build the playground from selected standalone JS and Core sources, verify both revisions and fingerprints through publication, and accept Core Main CI documentation notifications. Support removal of the old Core WASM manual and migration records while preserving historical selections and rejecting partial cleanup. (OpenTLV/opentlv#698)
- Register standalone JS/WASM documentation and Main notifications, preserve the historical Core manual, and route JS-owned manuals, examples and version metadata with an exact bootstrap pin. (#93)
- Support Core revisions after the removal of its old Go manuals and baseline, while retaining complete archives for older selected revisions and immutable Git links to the original evidence. Reject partial archive removal through existing strict navigation checks. (OpenTLV/opentlv#686)
- Present Core's retained `development/rust.md` as current Rust ownership guidance at `development/bindings/rust/`, like Python's, instead of archiving it as a superseded copy of the Rust development guide; it now routes builds to `opentlv-rust` and describes the Core inputs the Rust tests read. (OpenTLV/opentlv-rust#7)
- Select the standalone Rust manuals from `opentlv-rust` at an independent pin with Main documentation notifications, render them under Languages with their contributor guide in Development and their migration and validation records in history, and archive Core's superseded Rust guides with links to the current manual. (OpenTLV/opentlv-rust#6)
- Review the assembled content, move contributor manuals and active proposals into Development, and archive migration, performance and validation records with current-guide links while preserving technical sources and evidence. (#61)
- Define the cross-repository documentation ownership contract, route changing component requirements and version details to their owners, and track coordinated Core, Lua and Workspace corrections. (#62)
- Complete the seven-section portal with Tutorials, shared API documentation, Standards and Languages; preserve contributor guidance, component ownership and independent manuals while updating page and generated-reference destinations. (#63)
- Organize Development around architecture, builds, contributing, quality gates and releases, with repository-owned entry points and current portal conventions; distinguish historical migration guidance while preserving Core technical sources. (#49)
- Add Bindings and Tools catalogs with lightweight product overviews, explicit experimental and planned status, links to independently owned manuals, and a documented registration convention; preserve Core ownership of C/C++ references. (#48)
- Add a supported Formats catalog with explicit capabilities and limitations, organize detailed format guides consistently, and combine DER/CER framing and validation pages while preserving Core content, examples and source links. (#47)
- Introduce portal-owned Home and Getting Started learning paths, retain Core first-program and integration examples, and move installation, archive and developer-test guidance into Development with source ownership and internal links preserved. (#46)
- Organize the portal into Home, Getting Started, Formats, Bindings, Tools and Development, with section landings, canonical URLs and separate product manual navigation; retain technical content and update internal links without compatibility redirects for old page URLs. (#45)
- Accept Lua documentation pin notifications from successful Main CI using the same reviewed source-update policy as Python. (#42)
- Accept explicitly configured Python documentation pin notifications from successful Main CI without compatibility claims, and select the normalized Python source layout with its validation page. (OpenTLV/opentlv-python#13)
- Assemble standalone Python manuals with independent source provenance, build and workspace instructions, and Python-owned source and contribution links. (#34)
- Separate PR, Main, Full and Publishing CI with exact-attempt publication evidence, immutable snapshot checks and workflow timings; ordinary main pushes no longer publish. (#31)

- Assemble Lua API, build, test and versioning documentation from the standalone Lua repository with explicit source provenance and cross-repository links, while retaining Core-driven portal versions and existing published snapshots. (#27)
- Route automatic Core and component development updates through reviewed commit pins, reject stale Core pins, and keep release selection independent of development snapshots. (#6)
- Move playground UI ownership into the portal and require verified, matching WASM artifacts and browser validation before publication. (#6)
- Document trusted CI producers, reviewed feed and digest updates, and real binding end-to-end validation as production activation requirements; clarify the schema v1 limit of one example per feature and language and distinguish test fixtures from production integration coverage. (#7)
- Replace `core-source.json` with `docs-sources.json`; validate all component commits and inclusion states when rebuilding a published release. (#4)
- Validate navigation against assembled Markdown without requiring a MkDocs configuration in Core, preserving page coverage after the Core documentation cutover. (OpenTLV/opentlv#608)

### Fixed

- Register Lua's generic Core API coverage guide in contributor navigation so the Lua source-pin update passes complete-documentation checks. (OpenTLV/opentlv-lua#31, #111)
- Pair the Core documentation update with the JS pin already adopted in #103, restoring the WASM binding-contract anchor linked from Core's examples. (#104)
- Adopt the Rust documentation pin proposed by #99 with navigation for Codec/Generator validation and generic Core API coverage; preserve Rust ownership, archive the historical validation record and keep the maintained coverage guide under Development. (#93)
- Include Core's WASM migration baseline in Development history, preserving its source links and evidence while keeping exact Core 0.7.1 navigation compatible. (OpenTLV/opentlv#697)
- Include Core's Go migration baseline in Development history when adopting the Core pin proposed by PR #81. Preserve its source ownership and linked JSON evidence, and keep the exact Core 0.7.1 navigation compatible. (#81)
- Stop archiving Core's Rust user guide, which Core deleted, so updating the Core pin no longer fails the strict build and navigation check on a missing `guides/rust.md`; keep the Core Rust development guide archived. (OpenTLV/opentlv#679)
- Wait up to about three minutes for delayed GitHub job metadata when recording CI timings, retry transient API failures, and measure reruns of failed jobs from the earliest reused job, so a passing documentation check no longer fails its gate on timing evidence. (#74)
- Pin Rust documentation to the merged standalone manuals of OpenTLV/opentlv-rust#15, replacing the pre-integration revision whose Core-relative links failed the strict build. (OpenTLV/opentlv-rust#6)
- Name Marek Cingel instead of OpenTLV as the copyright holder in `LICENSE`, matching the source headers and the Core and Workspace licenses. (#71)
- Reject ambiguous or malformed source registrations before replacing assembled documentation, and resolve generated API links from both original source paths and current portal routes. (#62)
- Correct the migration map to reflect the current epic sub-issues, follow-up order and requirement to complete corrections in owning repositories before closing the ownership review. (#63)
- Pin Python documentation to the merged standalone documentation fixes, resolving the Markdown lint failure and obsolete example links. (#34)
- Support Core 0.7.1 with explicit standalone CLI page ownership and revision-specific navigation, preserving source tags, published snapshots and strict collision checks. (#31)
- Include the updated Core quality-gates page in navigation and keep one monotonic source-update proposal per component, with optional auto-merge requiring the Docs PR gate. (#31)

- Align the pinned Core and Lua documentation revisions with the completed manual migration, restoring standalone Lua pages and navigation. (#27)
- Preserve the original rendered Core release snapshot on repeated publication instead of rebuilding it with the current portal layout. (#21)
- Restore CLI pages from an independently pinned CLI repository after Core extraction, including navigation, cross-repository links and missing-page checks. (#25)
- Allow automated source update PRs without compatibility JSON files while staging only the source manifest and available compatibility evidence. (#17)
- Link the documentation header to the main OpenTLV repository while preserving repository-specific page edit and source links. (#6)
- Preserve verified artifact bytes when preparing version history on Windows with Git line-ending conversion enabled. (#6)
- Include `query.mjs` in the playground distribution and reject missing, stale or modified WASM artifacts. (#6)
- Allow local workspace previews at the current Core HEAD while retaining the configured revision in metadata, reject local mode for publication, enforce explicit documentation overrides, and provide a root-URL preview configuration. (#1)

### Added

- Integrate independently pinned Go manuals, examples and Main documentation updates, with Go-owned links and archived Core migration guides. (OpenTLV/opentlv-go#6)
- Inventory existing documentation and define the proposed six-section migration mapping, preservation requirements and public URL compatibility handling; keep detailed format documentation and C/C++ references Core-owned while Portal owns catalogs, introductions and navigation. (#44)
- Publish verified Lua, Python and configured component releases as independent immutable documentation snapshots through shared publication gates; align the Lua source pin and quality-gate navigation. (#42)
- Publish independently versioned CLI documentation under `cli/<version>/` from verified release-gate notifications, with immutable snapshots, a separate version selector, safe retries and shared serialized Pages deployment. (#21)
- Import schema v2 development compatibility records for exact pinned component/Core pairs and propose verified JSON evidence from trusted component workflow artifacts, while retaining schema v1 release selection. (#6)
- Automate reviewed development updates and immutable release documentation from verified Core workflow events, and propose reviewed commit and compatibility feed updates from configured component release producers. (#6)
- Import checksum-pinned compatibility feeds to select the latest verified stable binding release for an exact Core commit, platform and configuration; gate examples on their own evidence and preserve selected results in source locks and published release provenance. (#7)
- Assemble language example tabs from repository-owned catalogs and source files, preserving Core-only documentation and displaying explicit availability, component revisions and supplied verification evidence. (#5)
- Versioned multi-repository documentation assembly with independent source revisions, managed Git checkouts and source locks, workspace overrides, optional components, composed navigation, ownership-aware links, and complete publication provenance. (#4)
- Independent documentation CI with Markdown, Core example/inventory, Doxygen and strict link validation; versioned mike publication to GitHub Pages with manual dry runs, preserved history, and deployment-only write permissions. (#3)
- Generate and verify C/C++ Doxygen references from the selected Core sources, support verified external artifacts, and preserve API/guide links with strict link and anchor checks. (#2)
- Standalone MkDocs Material build consuming an explicitly selected external Core checkout, with strict validation, source revision metadata, shared assets, and an explicit local preview mode. (#1)
