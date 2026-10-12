# OpenTLV documentation portal

This repository owns the MkDocs Material configuration, navigation, theme,
shared assets, and assembly of the OpenTLV documentation portal. Core owns its
technical Markdown, examples, public headers, and Doxygen configuration in
[`OpenTLV/opentlv`](https://github.com/OpenTLV/opentlv).

Each build reads an external Core checkout and assembles disposable content in
`build/assembled/`. Core documentation is never maintained as a second copy here.
The Core build does not depend on this repository.

## Prerequisites

- Python 3.10 or newer and Git.
- An external Core checkout at the revision selected in `core-source.json`.
- Generated C and C++ Doxygen HTML from that same checkout (instructions below).
  Generation requires CMake, a C compiler, and Doxygen 1.9.1 or newer.

No binding or CLI repository, binding runtime, or Emscripten installation is
required. C++ remains part of Core; generating its reference does not require
building the C++ library, bindings, CLI, examples, or tests.

## Setup

Run commands from this repository's root. In the multi-root workspace the default
Core directory is the sibling `../opentlv`. A separate checkout can be prepared
without changing your development checkout:

```sh
git clone --no-checkout https://github.com/OpenTLV/opentlv.git ../opentlv-docs-core
```

Create an isolated environment; do not install these dependencies into Core's
Python/Conan environment.

PowerShell:

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
python -m pip install -r requirements-docs.txt
$env:OPENTLV_CORE_DIR = (Resolve-Path ../opentlv-docs-core).Path
$coreRevision = (Get-Content core-source.json | ConvertFrom-Json).revision
git -C $env:OPENTLV_CORE_DIR checkout --detach $coreRevision
```

POSIX shell:

```sh
python3 -m venv .venv
. .venv/bin/activate
python -m pip install -r requirements-docs.txt
export OPENTLV_CORE_DIR="$(cd ../opentlv-docs-core && pwd)"
core_revision=$(python -c 'import json; print(json.load(open("core-source.json"))["revision"])')
git -C "$OPENTLV_CORE_DIR" checkout --detach "$core_revision"
```

For an existing workspace checkout, set `OPENTLV_CORE_DIR` to that checkout or
leave it unset for the sibling default. Its HEAD must match the selected revision.
The portal never checks out, fetches, resets, or edits Core on your behalf.

## Generate the API prerequisites

The existing hook requires both HTML reference trees because Core guides link
directly to them. Reuse Core's own targets; Doxygen declarations and configuration
stay in Core. These are manual prerequisites for the initial portal build;
automated generation and artifact provenance belong to
[#2](https://github.com/OpenTLV/opentlv-docs/issues/2).

In PowerShell, using the checkout selected above:

```powershell
cmake -S $env:OPENTLV_CORE_DIR -B build/api -DOPENTLV_BUILD_DOCS=ON -DOPENTLV_BUILD_CXX=OFF -DOPENTLV_BUILD_CLI=OFF -DOPENTLV_BUILD_TESTS=OFF -DOPENTLV_BUILD_EXAMPLES=OFF
cmake --build build/api --target cxx-api-docs
```

In a POSIX shell:

```sh
cmake -S "$OPENTLV_CORE_DIR" -B build/api -DOPENTLV_BUILD_DOCS=ON -DOPENTLV_BUILD_CXX=OFF -DOPENTLV_BUILD_CLI=OFF -DOPENTLV_BUILD_TESTS=OFF -DOPENTLV_BUILD_EXAMPLES=OFF
cmake --build build/api --target cxx-api-docs
```

The C++ target also generates C references. Keep `c-api/html/` and
`cxx-api/html/` as siblings under `build/api/docs/`. To consume references generated
elsewhere, set `OPENTLV_API_DOCS_DIR` to the directory containing those two trees.
Regenerate both whenever the Core revision changes. The initial portal verifies
their presence, not the revision that produced them. Doxygen's existing
API-to-guide URLs remain controlled by Core until #2 adapts that integration.

## Build and preview

With the environment activated:

```sh
python -m mkdocs build --strict
python -m mkdocs serve
```

Open `http://127.0.0.1:8000/opentlv-docs/` for the preview. The static site is in `site/`.
Assembly runs before every build, including live rebuilds. Relative checkout
and artifact overrides are resolved from the current working directory.

The build preserves strict navigation, link, and anchor validation, Material
content tabs, search, code highlighting, and the development banner. Missing API
references are errors. Broken source-file links are checked against the external
Core checkout and fail the build. External HTTP destinations are not fetched or
validated by MkDocs.

`source-revision.json` in the assembled output and final site records the selected
repository, requested revision, resolved commit, and local/dirty status. Every
page displays the Core commit. Core source and edit links target that commit;
portal-owned asset pages link to this repository.

### Revision selection and local changes

`core-source.json` pins the default Core commit. Update it deliberately together
with any required navigation changes. `OPENTLV_CORE_REF` can override it with a
full 40-character commit SHA or a tag name (including annotated tags). Branches
and abbreviated SHAs are rejected. Check out that revision in the external
repository before building; the portal records a tag's resolved SHA. Published
build inputs should be pinned by full SHA.

A normal build rejects tracked changes and non-ignored untracked files in Core.
For an explicit local preview of work based on the selected revision, set:

```powershell
$env:OPENTLV_DOCS_LOCAL = '1'
```

or `export OPENTLV_DOCS_LOCAL=1` in a POSIX shell. This includes local Markdown
changes and non-ignored new files, and displays a local-preview banner. Source
links still show the base commit. Remove the variable to restore clean-checkout
validation. Local preview always uses the development channel.

`OPENTLV_DOCS_CHANNEL` accepts `development` (default) or `release`; it controls
presentation, not deployment. A clean Core source revision is reproducible, but
this initial setup does not claim byte-identical builds across Python package
or Doxygen versions; dependency ranges are retained from the existing portal.

### Transitional component content

The selected Core tree still contains binding/CLI guides and language tabs.
Assembly preserves those existing pages without building their components or
requiring separate repositories. Their documented ownership is unchanged.
Future component extraction will update the selected content and navigation.

The playground assets are preserved. Without optional WASM artifacts it displays
its existing unavailable message. Set `OPENTLV_WASM_DIR` to a directory containing
`opentlv.mjs`, `opentlv-core.js`, and `opentlv-core.wasm` to include them;
`OPENTLV_DOCS_REQUIRE_WASM=1` makes missing artifacts an error.

## Validation and scope

```sh
python -m unittest discover -s tests -v
python -m mkdocs build --strict
git diff --check
```

The tests cover revision selection, dirty-checkout handling, disposable assembly,
source ownership, link rewriting, and required/optional artifacts. Core's
implementation/example inventory checks remain in Core, alongside their inputs.

This is the initial local build for
[#1](https://github.com/OpenTLV/opentlv-docs/issues/1). The configured site URL is
the intended GitHub Pages destination, not a claim that deployment is active.
The existing Core pipeline remains operational during migration. Follow-ups own:

- [#2: Doxygen integration](https://github.com/OpenTLV/opentlv-docs/issues/2).
- [#3: CI and mike publication](https://github.com/OpenTLV/opentlv-docs/issues/3).
- [#4: Versioned multi-repository assembly](https://github.com/OpenTLV/opentlv-docs/issues/4).
- Language example integration, compatibility metadata, and ecosystem updates.

Keep Core Markdown and public API changes in Core. Portal changes belong here.
Removal of the old Core portal configuration and workflow follows validation of
the replacement pipeline; it is not part of this initial build.
