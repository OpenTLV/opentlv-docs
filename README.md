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
- CMake, a C compiler, and Doxygen 1.9.1 or newer for automatic API generation.
  These tools are not required when consuming verified API artifacts generated
  elsewhere from the same Core sources (instructions below).

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
leave it unset for the sibling default. Normal builds require HEAD to match the
selected revision; local preview can use the current HEAD as described below.
The portal never checks out, fetches, resets, or edits Core on your behalf.

## Generate or consume API references

The MkDocs build automatically configures the selected external Core checkout
and invokes its `cxx-api-docs` target, which depends on `c-api-docs`. Core's
Doxygen declarations, aliases, source comments, and warning-as-error policy
remain authoritative. Generation disables libraries' optional consumers, tests,
and examples; it does not compile the C++ library or any bindings.

The portal owns disposable `build/api/`. A regeneration replaces that directory
to prevent stale CMake settings or HTML from leaking between revisions. Do not
store manually maintained files there. Valid artifacts are reused when their
provenance and checksums match. To force regeneration or prepare artifacts for
another machine, run from the activated documentation environment:

```sh
python tools/docs/api.py
```

Copy the complete `build/api/docs/` directory, including `api-source.json`,
`c-api/`, and `cxx-api/`. Set `OPENTLV_API_DOCS_DIR` to that copied directory to
consume it without invoking CMake or Doxygen. An explicit override must pass all
checks; it never silently falls back to generation. Bare HTML generated directly
by CMake lacks provenance and is rejected. Use the portal command above to
produce the manifest after a successful generation.

The manifest records the effective Core commit, repository, local/dirty status,
Doxygen version, source-content SHA-256, and checksums of both output trees.
The source fingerprint includes tracked and non-ignored untracked files and
detects edits and deletions even when HEAD is unchanged. Git branch, tags and
history used by Core's generated version header are included too. Ignored build
products are excluded. Transfer the same source bytes (including line endings)
and Git metadata when
using artifacts on another machine. Local artifacts cannot enter a normal or
publication build. Checksums detect stale or modified artifacts; this is not
cryptographic authentication of an untrusted producer.

Both references are included under `reference/api/`, retaining the sibling layout
used by C++ links to C declarations. When embedding HTML, the portal translates
Core's expanded guide URLs into relative links to the assembled MkDocs pages.
This also preserves the C reference's link to the C++ overview and works under
local, project, and versioned URL prefixes. Original artifacts remain unchanged.
After rendering, missing local links or anchors between C API, C++ API and guides
fail the build. Navigation within each individual Doxygen reference remains
owned by Doxygen. Unrelated external HTTP destinations are not fetched.

## Build and preview

With the environment activated:

```sh
python -m mkdocs build --strict
python -m mkdocs serve -f mkdocs.local.yml
```

Open `http://127.0.0.1:8000/` for the preview. `mkdocs.local.yml` inherits the portal
configuration and sets only the local URL. Keep the published GitHub Pages URL,
`https://opentlv.github.io/opentlv-docs/`, in `mkdocs.yml` for static builds.
Serving `mkdocs.yml` directly also inherits its `/opentlv-docs/` mount path, so use
the local configuration for the root preview URL. The static site is in `site/`.
Assembly runs before every build, including live rebuilds. Relative checkout
and artifact overrides are resolved from the current working directory.

The build preserves strict navigation, link, and anchor validation, Material
content tabs, search, code highlighting, and the development banner. Missing API
references in explicitly supplied artifacts are errors. Broken source-file links are checked against the external
Core checkout and fail the build. External HTTP destinations are not fetched or
validated by MkDocs.

`source-revision.json` in the assembled output and final site records the selected
repository, configured revision (`revision`), effective checkout HEAD (`commit`),
and local/dirty status. In normal builds, `commit` must resolve from `revision`;
in local preview it may differ. Every page displays the effective Core commit.
Core source and edit links target that commit;
portal-owned asset pages link to this repository.
The `api` field records the corresponding generated-reference provenance and
links to `reference/api/api-source.json`. That manifest describes the original
input artifacts; embedded HTML has its guide links adapted for the site.

### Revision selection and local changes

`core-source.json` pins the default Core commit. Update it deliberately together
with any required navigation changes. `OPENTLV_CORE_REF` can override it with a
full 40-character commit SHA or a tag name (including annotated tags). Branches
and abbreviated SHAs are rejected. Check out that revision in the external
repository before building; the portal records a tag's resolved SHA. Published
build inputs should be pinned by full SHA.

A normal build rejects tracked changes and non-ignored untracked files in Core.
For an explicit workspace preview using the current Core HEAD, set:

```powershell
$env:OPENTLV_DOCS_LOCAL = '1'
```

or `export OPENTLV_DOCS_LOCAL=1` in a POSIX shell. This includes local Markdown
changes and non-ignored new files, and displays a local-preview banner. HEAD may
differ from the configured revision, which is retained in metadata without
requiring that commit to exist locally. Source links use the actual HEAD; they
cannot show uncommitted changes. No checkout, fetch, or reset is performed.
Remove the variable to restore strict revision and clean-checkout validation.

Local preview is rejected for `OPENTLV_DOCS_CHANNEL=release`, `mkdocs gh-deploy`,
and mike commands. Future publication workflows must also set
`OPENTLV_DOCS_PUBLISH=1`, including development/latest publication and any custom
artifact upload path, so build validation rejects local mode. The portal cannot
prevent manual uploading of an already generated directory; publication must
build with this guard and reject artifacts whose metadata has `local: true`.

`OPENTLV_DOCS_CHANNEL` accepts `development` (default) or `release`; it controls
presentation, not deployment, and release rejects local mode.
A clean Core source revision is reproducible, but
the portal does not claim byte-identical builds across Python package
or Doxygen versions; dependency ranges are retained from the existing portal.

### Transitional component content

Assembly rejects duplicate documentation paths between Core and the portal.
The only intentional overrides are the exact shared presentation paths declared
in `PORTAL_OVERRIDES` in `tools/docs/assembly.py`:

- `assets/README.md`
- `assets/favicon.svg`
- `assets/logo-mark.svg`
- `assets/opentlv.svg`
- `assets/opentlv-light.svg`
- `assets/opentlv-dark.svg`

These portal-owned assets are temporarily still present in Core. New overrides
require an explicit ownership decision and an entry in that list; neither an
entire directory nor arbitrary Core pages may be overwritten. File/directory
conflicts always fail. Input collisions are checked before replacing the previous
assembly, and Core sources remain untouched.

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

Tests require CMake but no C compiler or Doxygen: disposable fixtures exercise
the Core target contract without compiling a library. Full integration validation
also runs the real build against the selected Core checkout and Doxygen.

The tests cover configured/effective revisions, publication guards, dirty-checkout
handling, collision checks, repeatable assembly, source ownership, link rewriting,
the local root preview URL, required/optional artifacts, API generation failures,
artifact provenance and integrity, local source changes, and API links/anchors. Core's
implementation/example inventory checks remain in Core, alongside their inputs.

The standalone build and API integration implement
[#1](https://github.com/OpenTLV/opentlv-docs/issues/1) and
[#2](https://github.com/OpenTLV/opentlv-docs/issues/2). The configured site URL is
the intended GitHub Pages destination, not a claim that deployment is active.
The existing Core pipeline remains operational during migration. Follow-ups own:

- [#3: CI and mike publication](https://github.com/OpenTLV/opentlv-docs/issues/3).
- [#4: Versioned multi-repository assembly](https://github.com/OpenTLV/opentlv-docs/issues/4).
- Language example integration, compatibility metadata, and ecosystem updates.

Keep Core Markdown and public API changes in Core. Portal changes belong here.
Removal of the old Core portal configuration and workflow follows validation of
the replacement pipeline; it is not part of local build or API integration work.
