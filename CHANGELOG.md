# Changelog

All notable changes to this project will be documented in this file.

## [Unreleased]

### Changed

- Route automatic Core and component development updates through reviewed commit pins, reject stale Core pins, and keep release selection independent of development snapshots. (#6)
- Move playground UI ownership into the portal and require verified, matching WASM artifacts and browser validation before publication. (#6)
- Document trusted CI producers, reviewed feed and digest updates, and real binding end-to-end validation as production activation requirements; clarify the schema v1 limit of one example per feature and language and distinguish test fixtures from production integration coverage. (#7)
- Replace `core-source.json` with `docs-sources.json`; validate all component commits and inclusion states when rebuilding a published release. (#4)
- Validate navigation against assembled Markdown without requiring a MkDocs configuration in Core, preserving page coverage after the Core documentation cutover. (OpenTLV/opentlv#608)

### Fixed

- Allow automated source update PRs without compatibility JSON files while staging only the source manifest and available compatibility evidence. (#17)
- Link the documentation header to the main OpenTLV repository while preserving repository-specific page edit and source links. (#6)
- Preserve verified artifact bytes when preparing version history on Windows with Git line-ending conversion enabled. (#6)
- Include `query.mjs` in the playground distribution and reject missing, stale or modified WASM artifacts. (#6)
- Allow local workspace previews at the current Core HEAD while retaining the configured revision in metadata, reject local mode for publication, enforce explicit documentation overrides, and provide a root-URL preview configuration. (#1)

### Added

- Import schema v2 development compatibility records for exact pinned component/Core pairs and propose verified JSON evidence from trusted component workflow artifacts, while retaining schema v1 release selection. (#6)
- Automate reviewed development updates and immutable release documentation from verified Core workflow events, and propose reviewed commit and compatibility feed updates from configured component release producers. (#6)
- Import checksum-pinned compatibility feeds to select the latest verified stable binding release for an exact Core commit, platform and configuration; gate examples on their own evidence and preserve selected results in source locks and published release provenance. (#7)
- Assemble language example tabs from repository-owned catalogs and source files, preserving Core-only documentation and displaying explicit availability, component revisions and supplied verification evidence. (#5)
- Versioned multi-repository documentation assembly with independent source revisions, managed Git checkouts and source locks, workspace overrides, optional components, composed navigation, ownership-aware links, and complete publication provenance. (#4)
- Independent documentation CI with Markdown, Core example/inventory, Doxygen and strict link validation; versioned mike publication to GitHub Pages with manual dry runs, preserved history, and deployment-only write permissions. (#3)
- Generate and verify C/C++ Doxygen references from the selected Core sources, support verified external artifacts, and preserve API/guide links with strict link and anchor checks. (#2)
- Standalone MkDocs Material build consuming an explicitly selected external Core checkout, with strict validation, source revision metadata, shared assets, and an explicit local preview mode. (#1)
