# Changelog

All notable changes to this project will be documented in this file.

## [Unreleased]

### Fixed

- Allow local workspace previews at the current Core HEAD while retaining the configured revision in metadata, reject local mode for publication, enforce explicit documentation overrides, and provide a root-URL preview configuration. (#1)

### Added

- Generate and verify C/C++ Doxygen references from the selected Core sources, support verified external artifacts, and preserve API/guide links with strict link and anchor checks. (#2)
- Standalone MkDocs Material build consuming an explicitly selected external Core checkout, with strict validation, source revision metadata, shared assets, and an explicit local preview mode. (#1)
