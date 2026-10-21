# Changelog

All notable changes to this project will be documented in this file.

## [Unreleased]

### Changed

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
