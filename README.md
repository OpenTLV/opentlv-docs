# OpenTLV documentation portal

This repository owns the MkDocs Material configuration, navigation, theme,
shared assets, and assembly of the OpenTLV documentation portal. Core owns its
technical Markdown, examples, public headers, and Doxygen configuration in
[`OpenTLV/opentlv`](https://github.com/OpenTLV/opentlv).

Each build reads independently selected repository checkouts and assembles
disposable content in `build/assembled/`. Component documentation is never
maintained as a second copy here.
The Core build does not depend on this repository.

## Prerequisites

- Python 3.10 or newer and Git.
- An external Core checkout at the revision selected in `docs-sources.json`.
- CMake, a C compiler, and Doxygen 1.9.1 or newer for automatic API generation.
  These tools are not required when consuming verified API artifacts generated
  elsewhere from the same Core sources (instructions below).

The default manifest requires no binding or CLI repository, binding runtime,
or Emscripten installation. C++ remains part of Core; generating its reference does not require
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
$coreRevision = ((Get-Content docs-sources.json | ConvertFrom-Json).sources | Where-Object id -eq core).revision
git -C $env:OPENTLV_CORE_DIR checkout --detach $coreRevision
```

POSIX shell:

```sh
python3 -m venv .venv
. .venv/bin/activate
python -m pip install -r requirements-docs.txt
export OPENTLV_CORE_DIR="$(cd ../opentlv-docs-core && pwd)"
core_revision=$(python -c 'import json; print(next(s["revision"] for s in json.load(open("docs-sources.json"))["sources"] if s["id"] == "core"))')
git -C "$OPENTLV_CORE_DIR" checkout --detach "$core_revision"
```

For an existing workspace checkout, set `OPENTLV_CORE_DIR` to that checkout or
leave it unset for the sibling default. Normal builds require HEAD to match the
selected revision; local preview can use the current HEAD as described below.
MkDocs never checks out, fetches, resets, or edits workspace sources.
The explicit `ci.py fetch` command creates separate managed checkouts as described below.

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
in local preview it may differ. Every page displays the included component commits; the `sources` list records
all components, including omitted optional repositories and their omission reason.
Core source and edit links target that commit;
portal-owned asset pages link to this repository.
The `api` field records the corresponding generated-reference provenance and
links to `reference/api/api-source.json`. That manifest describes the original
input artifacts; embedded HTML has its guide links adapted for the site.

### Revision selection and local changes

`docs-sources.json` pins every component independently, including the default Core commit. Update it deliberately together
with any required navigation changes. `OPENTLV_CORE_REF` can override it with a
full 40-character commit SHA or a tag name (including annotated tags). Branches
and abbreviated SHAs are rejected. Check out that revision in the external
repository before building; the portal records a tag's resolved SHA. Published
build inputs should be pinned by full SHA.

A normal build rejects tracked changes and non-ignored untracked files in every included source.
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
and mike commands. The publication workflow sets
`OPENTLV_DOCS_PUBLISH=1`, including development/latest publication and any custom
artifact upload path, so build validation rejects local mode. Any additional
publication workflow must set this guard too. The portal cannot
prevent manual uploading of an already generated directory; publication must
build with this guard and reject artifacts whose metadata has `local: true`.

`OPENTLV_DOCS_CHANNEL` accepts `development` (default) or `release`; it controls
presentation, not deployment, and release rejects local mode.
A clean Core source revision is reproducible, but
the portal does not claim byte-identical builds across Python package
or Doxygen versions; dependency ranges are retained from the existing portal.

### Multi-repository assembly

`docs-sources.json` is the single source manifest (schema version `1`). Core is
required and retains its existing root URLs and Doxygen integration. Additional
components choose their own tags or full commit SHAs; they do not need matching
Core version numbers. The published portal version still follows the selected
Core release tag, while its metadata records the independently selected inputs.

Add a component entry to `sources`, for example (replace the example repository
and tag with an existing component release):

```json
{
  "id": "python",
  "repository": "https://github.com/OpenTLV/opentlv-python",
  "revision": "v2.3.0",
  "docs_path": "docs",
  "mount": "bindings/python",
  "required": false,
  "navigation": {
    "title": "Python",
    "section": ["Language APIs"],
    "items": [
      {"Overview": "index.md"},
      {"Examples": "examples.md"}
    ]
  }
}
```

`id` is unique, lowercase, and uses letters, digits or underscores, starting with
a letter. `docs_path` and `mount` are contained POSIX paths. Only Core uses an
empty mount. `navigation.items` uses standard MkDocs nested lists and titles,
with Markdown paths relative to the component's documentation directory.
`section` is a sequence of parent navigation titles; an empty list adds a
section at the top level. Duplicate section titles at the insertion destination
are errors. Every assembled Markdown page must appear in the resulting
navigation, except Core's root GitHub `README.md`.

Navigation configuration belongs to the portal. Component Markdown and assets
remain in their owning repositories; no component needs a MkDocs configuration,
portal dependency, or synchronized build/release. Assembly copies tracked files
only, plus non-ignored additions in explicit local preview. It rejects path
escapes, file/directory conflicts, case-insensitive collisions and collisions
with generated API output before replacing the previous assembly.

By default, each checkout is a sibling directory named after its repository.
`OPENTLV_PYTHON_DIR` overrides the example component checkout, just as
`OPENTLV_CORE_DIR` overrides Core. `OPENTLV_DOCS_SOURCE_ROOT` instead selects a
parent directory containing checkouts named by source ID. Per-component directory
overrides take precedence. An explicitly supplied missing override is an error.
Local preview applies to all components and cannot be published.

A missing optional workspace checkout is omitted. During explicit fetching, an
optional repository that Git cannot contact is recorded as unavailable; Git
cannot reliably distinguish a missing private repository from an access or
transport failure. Required repositories always fail in that case. Once a
repository is available, invalid tags, wrong HEADs, missing documentation and
dirty checkouts are errors even when the component is optional. Omitted
components contribute neither files nor navigation. Their status remains in
`source-revision.json` and in the page footer.

For reproducible managed inputs, run from the portal in a fresh build directory:

```powershell
python tools/docs/ci.py select
python tools/docs/ci.py fetch
$env:OPENTLV_DOCS_SOURCE_ROOT = (Resolve-Path build/sources).Path
$env:OPENTLV_DOCS_LOCK = (Resolve-Path build/sources.lock.json).Path
python tools/docs/ci.py check
python -m mkdocs build --strict
```

In POSIX shells, use `export OPENTLV_DOCS_SOURCE_ROOT="$PWD/build/sources"` and
`export OPENTLV_DOCS_LOCK="$PWD/build/sources.lock.json"` after fetching. Unset any
per-component directory overrides when using the managed checkouts. `select`
accepts `INPUT_CHANNEL` and `INPUT_CORE_REF`, matching the CI manual inputs.

Fetching uses standard `git clone --no-checkout` and detached checkout of the
resolved SHA. It refuses existing managed checkout directories; it never resets
or deletes them. The lock records the manifest, exact selected commits and
omitted components. All later build steps use the lock and reject changed
configuration or checkout HEADs. Preserve the lock and the published
`source-revision.json` when auditing a build. Unset `OPENTLV_DOCS_LOCK` before
switching to local preview. No byte-identical rendering across different Python
or Doxygen versions is claimed.

### Links between components

Relative links within component documentation retain their original layout.
Relative source links leaving that documentation directory target the owning
repository at its actual commit, and edit links use the original source path.

For cross-repository documentation links, use ordinary GitHub URLs of the form
`https://github.com/OWNER/REPO/blob/REVISION/DOCS_PATH/page.md#anchor`, with the
manifest's selected tag or resolved SHA. Links to included sources are converted
to local site links and their destination pages and anchors are validated.
Reference-style Markdown links and HTML links are supported too. This keeps the
original Markdown usable on GitHub without portal-specific link syntax.
Links to omitted optional components remain external, so Core can still build;
external HTTP availability is not checked. Links to other revisions remain
external rather than silently pointing at different content.

### Integration mechanism decision

We evaluated the existing
[mkdocs-multirepo-plugin](https://github.com/jdoiro3/mkdocs-multirepo-plugin) and
[mkdocs-monorepo-plugin](https://github.com/backstage/mkdocs-monorepo-plugin).
Multirepo supplies remote imports, branch/tag selection and navigation imports;
its `nav_repos` mode also supports portal-owned navigation. Its README marks the
project as inactive. Monorepo merges local documentation through included MkDocs
configurations and does not supply the required Git revision selection.

The portal uses standard Git, MkDocs navigation and its existing assembly hooks.
This preserves workspace checkout ownership and the Core cutover contract
without requiring MkDocs configurations in component repositories. The custom
layer is limited to manifest validation, source locks, assembly, navigation and
link/provenance integration. Neither plugin replaces the required immutable
source-set validation, publication guards and Core API artifact verification.
No additional MkDocs plugin dependency is introduced.

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

These portal-owned assets may still be present in older Core revisions; after
Core cleanup only its README logo and attribution page remain. New overrides
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
python tools/docs/ci.py check
python -m mkdocs build --strict
git diff --check
```

Tests require CMake but no C compiler or Doxygen: disposable fixtures exercise
the Core target contract without compiling a library. Full integration validation
also runs the real build against the selected Core checkout and Doxygen.

The tests cover configured/effective revisions, publication guards, dirty-checkout
handling, collision checks, repeatable assembly, source ownership, link rewriting,
the local root preview URL, required/optional artifacts, API generation failures,
artifact provenance and integrity, local source changes, and API links/anchors.
Publication tests run real mike builds and Git transfers between disposable local
repositories, covering preserved history, failed builds, metadata rejection, and
concurrent publication conflicts. They do not contact GitHub.

`tools/docs/ci.py check` invokes the selected Core's example synchronization,
inventory tests, and inventory validator alongside their original inputs. It
assembles Markdown and checks navigation against every assembled Markdown page
except the root GitHub `README.md`. It does not read or require a Core
`mkdocs.yml`; nested README pages still require navigation entries. These checks inspect source files without
building or running Core examples, bindings, or CLI. Strict MkDocs validation
checks the resulting navigation, links and anchors.

CI uses `markdownlint-cli@0.45.0` with `.markdownlint.json`, without automatic
fixes, on portal Markdown, Core's README, and assembled documentation. With Node
22 available, the same lint can be run after `ci.py check`:

```sh
npx --yes markdownlint-cli@0.45.0 --config .markdownlint.json \
  README.md CHANGELOG.md 'docs/**/*.md' \
  "$OPENTLV_CORE_DIR/README.md" 'build/assembled/docs/**/*.md'
```

Set `OPENTLV_CORE_DIR` explicitly for this command (use `../opentlv` for the
default sibling checkout).

## CI and versioned publication

`.github/workflows/docs.yml` validates every PR targeting `main`, pushes to
`main`, and manual runs. Validation has only `contents: read`. It checks out the
sources from `docs-sources.json` (with an optional Core override) with full history
and tags. It resolves all revisions once into `build/sources.lock.json`; validation,
API generation and both MkDocs/mike builds use that exact selection. Doxygen, source validation, linting, tests and strict builds must all pass.

The read-only job also runs mike against a local `gh-pages` branch, including a
strict build under the version's actual URL prefix. It checks site/API metadata
and prepares both a Git bundle and the complete versioned Pages artifact. Mike
aliases use copies so assets and JSON work through `stable/` without symlinks.
Only the separate deployment job can write: it imports the validated bundle,
pushes the prepared history once without force, and deploys the prepared artifact
with the official GitHub Pages Actions. It does not run Core or build scripts.

| Trigger | Result |
| --- | --- |
| Pull request to `main` | Validate and prepare artifacts; never publish. |
| Push to `main` | Validate and publish `latest` using all manifest revisions. |
| Manual run, `publish: false` | Validate and prepare artifacts for the selected channel; no remote changes. |
| Manual run on `main`, `publish: true` | Validate and publish the selected channel. |
| Manual run on another branch | Validate only, regardless of `publish`. |

Manual inputs are `channel` (`development` or `release`), `core_ref` (empty uses
the manifest), and `publish` (defaults to false). Development accepts a full SHA
or tag. Release requires a Core tag `X.Y.Z` or `vX.Y.Z`; branches, bare SHAs and
prerelease tags cannot label a stable release. The resolved Core SHA is recorded
in each version's `source-revision.json`. Release directories use the full
`X.Y.Z`, retaining patch releases independently. Rebuilding the same version is
allowed only for the same complete source set: repositories, revisions, SHAs,
mounts, navigation and optional inclusion state. A moved component tag or a
newly available optional repository cannot silently replace a published release.
Older publications without multi-source metadata cannot be overwritten by the
new assembler; publish a new version instead.

The newest published release owns `stable`; publishing an older release does
not move that alias backwards. The site root redirects to `stable` once a release
exists, otherwise to `latest`. Later development builds preserve that default
and all release directories. Core tags do not trigger this repository directly;
automated cross-repository release events remain a follow-up.

### GitHub Pages setup and recovery

Before the first publication, a repository administrator must select **Settings
→ Pages → Build and deployment → Source: GitHub Actions**. Configure the
`github-pages` environment to allow deployments from `main`. No personal access
token is required. `gh-pages` stores mike history; Pages serves the uploaded
artifact, rather than relying on a bot push to trigger a branch-based Pages build.
See GitHub's [custom Pages workflow documentation](https://docs.github.com/en/pages/getting-started-with-github-pages/using-custom-workflows-with-github-pages).

All non-PR runs share one concurrency group and do not cancel active publication.
GitHub may replace a pending run with a newer pending run; dispatch a particular
release again if it was superseded. A failed validation or preparation cannot
change the published site or remote history. A conflicting remote history update
rejects the normal fast-forward push and blocks Pages deployment.

The history push and Pages deployment are two separate services, not a single
transaction. If Pages deployment fails after the push, the previous live site
remains available, while `gh-pages` already contains the prepared version. Rerun
the failed deployment job while its artifact is available, or dispatch a fresh
run from `main` with the same Core revision and channel. Prefer a fresh run if
another publication has since succeeded. Successful publication replaces the
whole site, including the preserved historical versions.

For a release rehearsal, dispatch with `channel: release`, a Core release tag,
and `publish: false`. Inspect the logs and artifacts, then dispatch on `main` with
the same inputs and `publish: true`. `tools/docs/publication.py` is intended for
disposable CI checkouts: it creates local mike commits but never pushes itself.

The existing Core publication workflow remains in place until the replacement
has passed hosted validation and a real Pages deployment. Local checks cannot
verify repository Pages settings, environment protection, or hosted deployment.
WASM remains optional; this workflow does not compile the playground or download
unverified artifacts. Playground integration belongs to #6.

The standalone build, API integration, and CI/publication infrastructure implement
[#1](https://github.com/OpenTLV/opentlv-docs/issues/1),
[#2](https://github.com/OpenTLV/opentlv-docs/issues/2),
[#3](https://github.com/OpenTLV/opentlv-docs/issues/3), and
[#4](https://github.com/OpenTLV/opentlv-docs/issues/4). The configured site URL is
the intended GitHub Pages destination; deployment still requires the setup above.
The existing Core pipeline remains operational during migration. Follow-ups own:

- Language example integration, compatibility metadata, and ecosystem updates.

Keep Core Markdown and public API changes in Core. Portal changes belong here.
Removal of the old Core portal configuration and workflow follows validation of
the replacement pipeline; it is not part of this migration step.

### Core cutover (#608)

The navigation check supports Core before and after removal of its MkDocs
configuration. Merge this portal change first, keeping the current Core pin.
After Core cleanup is merged, update `docs-sources.json` to that actual full
commit SHA and publish again. Local integration with uncommitted Core changes
uses `OPENTLV_DOCS_LOCAL=1` and is not deployment evidence.

Follow the [Core cutover procedure](https://github.com/OpenTLV/opentlv/blob/main/docs/development/documentation-ownership.md#cutover-for-issue-608)
before removing the old publisher: a real successful Pages deployment and
content checks are prerequisites. Preserve the old Core `gh-pages` site and its
historical versions; the new portal does not import, relabel or delete them.
The original workflow must be disabled and pending publishers cancelled.

The portal's publication workflow still does not supply WASM artifacts. Keep
the historical playground available until #6 supplies verified artifacts and
transfers its UI sources. The Core playground page links to the archive and
states its version limitation; a successful Markdown/API build alone does not
prove equivalent interactive behavior.
