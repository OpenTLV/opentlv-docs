# OpenTLV documentation portal

This repository owns the MkDocs Material configuration, navigation, theme,
shared assets, and assembly of the OpenTLV documentation portal. Core owns its
technical Markdown, examples, public headers, and Doxygen configuration in
[`OpenTLV/opentlv`](https://github.com/OpenTLV/opentlv).

Each build reads independently selected repository checkouts and assembles
disposable content in `build/assembled/`. Component documentation is never
maintained as a second copy here.
The Core build does not depend on this repository.

The [documentation inventory and migration mapping](DOCUMENTATION-MIGRATION.md)
records the pinned source baseline, current seven-section destinations, content
ownership and the no-redirect URL policy. Earlier migration stages remain
documented there as historical evidence.

The [cross-repository ownership audit](DOCUMENTATION-OWNERSHIP.md) records the
review and correction chain completed in #62. Core, Lua and Workspace corrections
are merged, and the portal selects the corrected Core and Lua revisions.
Follow the [documentation contribution contract](docs/development/documentation.md)
for canonical sources, metadata and validation responsibilities.

The [content disposition review](DOCUMENTATION-CONTENT-REVIEW.md) accounts for
every reviewed page and records the changes for #61. Historical evidence is
archived separately from current manuals, and contributor material is grouped
under Development. The remaining Core planning corrections must merge in Core
and be adopted through reviewed portal pins before #61 can close. A local preview
does not update the selected source set or establish publication readiness.

## Portal navigation

The central portal implements the seven sections defined by
[epic #43](https://github.com/OpenTLV/opentlv-docs/issues/43) and
[#63](https://github.com/OpenTLV/opentlv-docs/issues/63): Home, Tutorials, API,
Standards, Languages, Tools and Development. Their landing URLs are `/`,
`/tutorials/`, `/api/`, `/standards/`, `/languages/`, `/tools/` and `/development/`, relative to the selected
portal version (for example `/opentlv-docs/latest/`). MkDocs maps both `README.md`
and `index.md` to a directory index. The entry pages are portal-owned introductions;
technical contracts and detailed format documentation remain Core-owned.

Material's tabs expose the seven sections on desktop; its mobile drawer exposes
the same hierarchy. Section indexes and grouped secondary navigation keep
technical details within the appropriate section. API groups shared public
concepts, processing guides, generic format mechanisms, configuration and native
references. Standards contains actual protocols and their supported subsets.
Languages retains language-specific discovery and manuals; Tutorials provides
practical task entry points. Development retains #49's contributor guidance,
component contributor manuals, internal design notes, planning and a clearly
identified archive of historical evidence.

`docs-sources.json` retains the complete product navigation for inventory checks
and independent publication. The assembly navigation includes every page;
`tools/docs/content.py` assigns reviewed historical and contributor pages to
Development; `tools/docs/navigation.py` separates the remaining CLI, Lua and
Python manuals into contextual menus after MkDocs validates the complete
inventory. Product source links retain their owners; ordinary manual menus and
previous/next links stay within the product, with a return link to the current
portal version. They do not show the
portal version selector as if it selected a product release. Independently
published product snapshots retain their own selectors and portal return link.

The routing introduced in #45 now assigns pages to the seven sections. The routing
tables in `tools/docs/navigation.py` and `tools/docs/content.py` change MkDocs destinations while keeping original
source paths for ownership, inventory and link resolution. Internal links,
search results and generated API guide links use the new destinations.
**Old page URLs are intentionally not supported:** there are no redirects or
compatibility aliases. Product manuals selected for a portal version live under
`tools/otlv/manual/`, `languages/lua/manual/` and `languages/python/manual/`.
Independent product publication remains separate from these selected manuals.

Issue #46 transferred Home to the portal and added the practical learning
path through TLV concepts, a first element, Document, formats, languages and CLI.
It reuses the selected manuals and examples. The landing source is `docs/getting-started/overview.md`
(rendered as the section index), avoiding MkDocs' source-level `index.md`/`README.md`
collision. During assembly, `tools/docs/onboarding.py` splits
Core's existing guide at the archive/install heading: first
build, all language examples and consumer integration render at
`tutorials/first-program/`; installation/archives, C-only builds and tests
render at `development/building/core/`. Both retain their original Core source
and edit links. No technical source is copied into portal maintenance. A changed
split boundary or unexpected developer section fails assembly for review.
Internal links to moved sections use the new destination without old fragments.

Issue #47 introduced the format catalog and consistent technical presentation.
Issue #63 separates its generic configurations into `api/formats/` and actual
protocols into `standards/`, preserving both catalog tables and their limitations.
Core's complete former Formats index renders at `api/formats/guide/`, preserving
all comparison tables and shared processing examples. `tools/docs/formats.py`
groups the existing format blocks under Overview, Format structure, Encoding
rules, Supported capabilities, Examples, Limitations and References where
applicable. Empty sections are omitted; existing examples stay with their
technical explanations. No binding API manual is copied into the catalog.

DER and CER each combine their Core framing and validation sources into one
rendered page at `standards/asn1/{der,cer}/`. The assembly preserves every source
body and fenced example, rebases links, and records both source paths in
`owners.json`. Each combined page exposes both original source/edit links.
Unknown, missing or duplicate source headings fail assembly before replacing
output. The Core files and source pins are unchanged. No separate validation
pages or compatibility redirects are emitted; internal and API links resolve
directly to the combined pages.

Issue #48 adds lightweight overviews for C, C++, Python, Lua, Rust, Go and
WebAssembly, plus otlv, the playground and planned imtlv. Catalogs state source
availability separately from experimental status and independent publication.
Overviews link setup and first examples in the owning manuals; they do not
maintain copies of API tutorials. C/C++ technical ownership remains with Core.
The playground application keeps `tools/playground/`; its introduction uses
`tools/playground/overview/`. Independent product release URLs remain unchanged;
selected Lua/Python usage, setup and versioning chapters render under Languages.
Follow [Register a binding or tool](docs/development/product-catalogs.md) when
adding an entry or changing its availability.

The [historical records index](docs/development/history.md) collects 11 retained
migration, validation, performance and audit pages under
`development/history/{owner}/`. This includes Core's Python transition guide,
the Lua/Python migration records and the dated Python validation reports.
Each page retains its technical body, anchors, evidence and owner edit link,
with a visible historical note and links to current instructions. Archived
records are omitted from normal search results; the archive index remains
searchable and linked from Development.

Eight current CLI/Lua/Python contributor pages render under
`development/components/`, linked by the
[component contributor index](docs/development/components.md). Build instructions
needed by Lua/Python users and their public versioning contracts remain in the
language manuals. The planned runtime model and indefinite-boundary proposal
belong to Development planning. Existing published snapshots and independently
published component manuals keep their own content, navigation and URLs.

Check the navigation contract with
`python -B -m unittest discover -s tests -p test_navigation.py -v`.
Check onboarding preservation, ownership and link routing with
`python -B -m unittest discover -s tests -p test_onboarding.py -v`.
Check format preservation, merged source ownership and canonical links with
`python -B -m unittest discover -s tests -p test_formats.py -v`.
After building the site and installing `requirements-browser.txt` plus
Playwright Chromium, run `python -B tools/docs/navigation_smoke.py site` for
desktop/mobile navigation, archive-to-current links and component contributor
routes without requiring WASM. The publishing browser smoke
also runs these checks under the prepared version and project prefixes.

Issue #49 adds contributor entry points for Architecture, Building from Source,
Contributing, Testing and Quality Gates, and CI and Release Process. A portal
conventions page describes the implemented seven-section hierarchy and
routes contributors to their source owners. Short, explicitly portal-authored
context notes accompany Core's layout, ownership and Python cutover pages;
the completed #513 audit now uses the historical archive note. Original content
and source/edit links are retained. Repository-wide ownership corrections are
complete in #62; #61 tracks content disposition and its remaining owner-source
corrections, and #50 tracks final published validation. These notes do not correct the
upstream technical sources or establish current release/deployment evidence.

## Prerequisites

- Python 3.10 or newer and Git.
- External Core, CLI, Lua and Python checkouts at the revisions selected in `docs-sources.json`.
- CMake, a C compiler, and Doxygen 1.9.1 or newer for automatic API generation.
  These tools are not required when consuming verified API artifacts generated
  elsewhere from the same Core sources (instructions below).

Local documentation previews require the CLI, Lua and Python documentation sources but do not
build their executables or native modules, or require binding runtimes,
or Emscripten. Publishing the playground requires the additional
[WASM and browser tools](#playground-builds). C++ remains part of Core; generating its reference does not require
building the C++ library, bindings, CLI, examples, or tests.

## Setup

Run commands from this repository's root. In the multi-root workspace the default
Core, CLI, Lua and Python directories are the siblings `../opentlv`,
`../opentlv-cli`, `../opentlv-lua` and `../opentlv-python`.
Separate checkouts can be prepared without changing your development checkouts:

```sh
git clone --no-checkout https://github.com/OpenTLV/opentlv.git ../opentlv-docs-core
git clone --no-checkout https://github.com/OpenTLV/opentlv-cli.git ../opentlv-docs-cli
git clone --no-checkout https://github.com/OpenTLV/opentlv-lua.git ../opentlv-docs-lua
git clone --no-checkout https://github.com/OpenTLV/opentlv-python.git ../opentlv-docs-python
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
$env:OPENTLV_CLI_DIR = (Resolve-Path ../opentlv-docs-cli).Path
$cliRevision = ((Get-Content docs-sources.json | ConvertFrom-Json).sources | Where-Object id -eq cli).revision
git -C $env:OPENTLV_CLI_DIR checkout --detach $cliRevision
$env:OPENTLV_LUA_DIR = (Resolve-Path ../opentlv-docs-lua).Path
$luaRevision = ((Get-Content docs-sources.json | ConvertFrom-Json).sources | Where-Object id -eq lua).revision
git -C $env:OPENTLV_LUA_DIR checkout --detach $luaRevision
$env:OPENTLV_PYTHON_DIR = (Resolve-Path ../opentlv-docs-python).Path
$pythonRevision = ((Get-Content docs-sources.json | ConvertFrom-Json).sources | Where-Object id -eq python).revision
git -C $env:OPENTLV_PYTHON_DIR checkout --detach $pythonRevision
```

POSIX shell:

```sh
python3 -m venv .venv
. .venv/bin/activate
python -m pip install -r requirements-docs.txt
export OPENTLV_CORE_DIR="$(cd ../opentlv-docs-core && pwd)"
core_revision=$(python -c 'import json; print(next(s["revision"] for s in json.load(open("docs-sources.json"))["sources"] if s["id"] == "core"))')
git -C "$OPENTLV_CORE_DIR" checkout --detach "$core_revision"
export OPENTLV_CLI_DIR="$(cd ../opentlv-docs-cli && pwd)"
cli_revision=$(python -c 'import json; print(next(s["revision"] for s in json.load(open("docs-sources.json"))["sources"] if s["id"] == "cli"))')
git -C "$OPENTLV_CLI_DIR" checkout --detach "$cli_revision"
export OPENTLV_LUA_DIR="$(cd ../opentlv-docs-lua && pwd)"
lua_revision=$(python -c 'import json; print(next(s["revision"] for s in json.load(open("docs-sources.json"))["sources"] if s["id"] == "lua"))')
git -C "$OPENTLV_LUA_DIR" checkout --detach "$lua_revision"
export OPENTLV_PYTHON_DIR="$(cd ../opentlv-docs-python && pwd)"
python_revision=$(python -c 'import json; print(next(s["revision"] for s in json.load(open("docs-sources.json"))["sources"] if s["id"] == "python"))')
git -C "$OPENTLV_PYTHON_DIR" checkout --detach "$python_revision"
```

For existing workspace checkouts, set `OPENTLV_CORE_DIR`, `OPENTLV_CLI_DIR`,
`OPENTLV_LUA_DIR` and `OPENTLV_PYTHON_DIR`
or leave them unset for the sibling defaults. Normal builds require HEAD to match the
selected revision; local preview can use the current HEAD as described below.
MkDocs never checks out, fetches, resets, or edits workspace sources.
The explicit `ci.py fetch` command creates separate managed checkouts as described below.

### CLI documentation source

The required `cli` source in `docs-sources.json` mounts the standalone CLI's
`docs/` directory at `cli/`. Its manifest navigation owns the command guide,
JSON schema, development guide and release guide. The command and JSON guides
render under `tools/otlv/manual/`; contributor development and release guides
render under `development/components/cli/`. These pages do not depend on Core's removed `docs/cli/`.
Core and CLI are independently pinned, recorded in the source lock and shown
in published provenance. No CLI compilation or dependency download is needed
to assemble these Markdown sources.

When selecting a historical Core such as `0.7.1`, the standalone CLI owns the
two extracted pages `cli/README.md` and `cli/json-schema.md`. Assembly explicitly
replaces Core's `docs/cli/` copies with the matching CLI `docs/` files, recording
CLI ownership and its pinned revision before portal URL routing. This rule is
limited to those exact paths and source owners; every other collision fails.
Core tags and source files remain untouched. Existing published
versions retain their original content and source set. Updating `latest` does
not rebuild those versions. The CLI pin includes the standalone development
guide from CLI #5; update it deliberately alongside documentation validation.

Core `0.7.1` also uses an explicit navigation adjustment keyed to its immutable
commit `e12a52ff69a64468eecab084795a0530c273efea`: it retains the two historical
Core Lua guides and omits the two development pages introduced later.
Other revisions use the current navigation. Missing and unlisted pages remain
errors; assembly never prunes navigation based on which files happen to exist.

The optional `link_aliases` source field lists named Git refs used only to
recognize documentation links. CLI opts in to `["main"]` because Core's
repository-readable guides link to `opentlv-cli/blob/main/docs/...`. The portal
maps those links to the selected CLI pages, preserving query strings and
anchors. It never fetches or builds the alias ref: `revision` still selects the
immutable source. Other repositories, unlisted refs, historical commit links,
links outside the mounted docs directory, and code examples remain unchanged.
Aliases are validated, included in source locks and published metadata, and
require matching assembled pages and anchors under strict validation.

### Lua documentation source

The required `lua` source mounts `opentlv-lua/docs/` at the source path `lua/`
and renders its usage, setup and versioning manual under `languages/lua/manual/`,
linked from Languages. Contributor chapters render under
`development/components/lua/`, and migration provenance under
`development/history/lua/`. Lua owns the API guide, implementation
notes, build and LuaRocks instructions, tests, versioning and migration history.
The original import README remains a historical artifact outside the mounted
docs directory; it is linked from the provenance guide, not presented as setup.

Core and Lua both declare `link_aliases: ["main"]` so repository-readable
cross-references resolve to the selected immutable pages in either direction.
Source and example links outside `docs/` point to their owning repository at
the selected commit. This does not verify runtime compatibility or select a
Lua release automatically.

The Lua manual handoff is complete in the selected sources: Core no longer
supplies the manuals, and Lua supplies `docs/api.md` and
`docs/implementation.md`. Future corrections merge in their owning repositories
before reviewed portal pins select the available commits. A local preview can
validate coordinated working trees before those commits exist; it cannot be
published.

The central portal's version follows Core; independently published Lua manuals
use the [component release publication flow](#independent-component-release-publication)
and Lua's own release identity. Existing published snapshots keep their original
bytes and source set. Their old Lua URLs remain part of those snapshots; current
integrated navigation and links use `languages/lua/manual/api/` and
`development/components/lua/implementation/`.

### Python documentation source

The required `python` source mounts `opentlv-python/docs/` at the source path
`python/` and renders its usage, setup and versioning manual under
`languages/python/manual/`, linked from Languages. Contributor quality and release
guides render under `development/components/python/`; migration and dated
validation records render under `development/history/python/`.
Python owns the user guide, standalone build and installation,
workspace development, supported Python versions, contribution instructions,
quality gates, versioning, release preparation and validation records.
The portal consumes these manuals without compiling or installing the binding.
Core remains the source of truth for shared architecture and TLV semantics.

Python is pinned independently of Core. `OPENTLV_PYTHON_DIR` selects an explicit
checkout; its default is the workspace sibling `../opentlv-python`.
`OPENTLV_DOCS_LOCAL=1` previews working-tree documentation; normal builds require
the selected clean commit and publication rejects local mode. This portal
variable selects documentation only. Building the Python extension against a
local Core uses the separate `OPENTLV_PYTHON_CORE_SOURCE` setting documented in
the [Python build guide](https://github.com/OpenTLV/opentlv-python/blob/main/docs/development/python.md).
The portal's Python requirement applies to documentation tooling; the binding's
runtime requirements belong to its own build guide.

Repository-relative source and example links and page edit links resolve to
`OpenTLV/opentlv-python` at its selected commit. The explicit `main` link alias
maps cross-repository documentation links to the assembled pages. Historical
commit links remain historical. Python bugs and contributions belong to the
[Python repository](https://github.com/OpenTLV/opentlv-python/issues); portal
presentation belongs here. Do not create a second maintained Python manual in
this repository.

The current Core pin includes the Python implementation removal and standalone
repository references. Its retained `guides/python.md` renders in the historical
archive at `development/history/core/guides/python/`; `development/python.md`
remains current Core ownership guidance at `development/bindings/python/`.
The Python section consumes the
canonical standalone manuals. Removing those transitional Core files requires
a coordinated Core change and navigation update; missing pages still fail.

When updating Python manuals, merge the component change first and then select
its available full commit in `docs-sources.json`. Validate the exact pins as
well as any local preview. The central portal's version follows Core;
[independent Python manuals](#independent-component-release-publication) follow
Python releases. Documentation assembly neither publishes Python packages nor
asserts verified runtime compatibility. Existing published snapshots keep their
original source set.

## Independent component release publication

Lua, Python and future explicitly configured components use the shared
component snapshot renderer and the existing Full/Publishing gates. CLI retains
its established evidence contract and uses the same renderer. Component releases
are independent of the Core documentation version and the reviewed development
pins in `docs-sources.json`.

Lua/Python publishers create `component-release-<attempt>` with one `release.json`
receipt only after the GitHub release succeeds. Their separate read-only
notifiers send `component-release-published` with `source`, `repository`, `commit`,
`ref`, `run_id` and `run_attempt`. Bare tags and Python preparation-only artifacts
do not authorize publication. Python's `publish_release` input defaults to false;
enabling it creates a GitHub release after Full verification, with no PyPI upload.

Each source explicitly configures its trusted producer:

```json
"publication": {
  "workflow": ".github/workflows/python-release.yml",
  "artifact": "component-release-{attempt}",
  "asset": "release.json"
}
```

The schema-1 receipt has `kind: component-release`, `status: published`, source
and repository identities, `tag`, `version`, `commit`, `workflow_commit`, numeric
`run_id`, `run_attempt` and `release_id`. Docs verifies the successful main
workflow-dispatch run, its current attempt, artifact size/digest and exact
receipt identity. It independently resolves the tag, verifies workflow ancestry
and requires the same published GitHub release ID and prerelease status.
Unconfigured sources, forks, failed runs, stale attempts, expired artifacts,
moved tags and candidate-only evidence fail closed.

Publication creates `<source>/<version>/`, `<source>/versions.json` and a stable
alias for stable releases. Prereleases never replace stable; delayed releases
cannot move it backwards. Sources without a root index get a portal-generated
overview from their reviewed navigation. Markdown and source links belong to
the component's exact release commit; no component runtime tests, Core generation
or WASM build are repeated for a component-only publication.

All components share the existing serialized deployment. Repeated notifications
verify and reuse immutable snapshots; another commit at the same version fails.
Full evidence tracks every published namespace, including historical components
no longer configured. Core/other component snapshots, catalogs, aliases and
development pins are preserved. Normal main updates still propose source PRs
and do not trigger publication.

Merge Docs before enabling the producer workflows. Configure
`OPENTLV_COMPONENT_READ_TOKEN` in Docs with Contents and Actions read access to
the configured component repositories; keep the existing CLI credential.
Each producer uses `OPENTLV_DOCS_DISPATCH_TOKEN` with Contents write permission
restricted to Docs, available only to the notifier's final step. Missing or
insufficient credentials fail visibly. Rerun a failed notifier while its receipt
is retained. After a Docs deployment failure, rerun all Docs Release jobs so the
new attempt gets fresh gate evidence while historical snapshots reuse their bytes.
Expired receipts require newly verified producer evidence; preparation artifacts
cannot substitute for it. Partial producer tag/release failures require manual
inspection and recovery; producers never overwrite existing releases.

Onboarding another component requires a reviewed source/navigation entry with
this publication policy, a successful release producer emitting the same receipt,
and a notifier using the same event. Include contract and snapshot regressions,
then verify the hosted chain and served URLs. Local fixtures do not establish
hosted publication. Component package-registry publication remains separately owned.

## Independent CLI release publication

CLI release documentation is published at `cli/<version>/`, for example
`cli/0.1.0/` or `cli/0.2.0-rc.1/`. Its version comes exclusively from the CLI
tag `v<version>`. The CLI header and version selector identify the displayed
release; `cli/versions.json` is independent of Core's root `versions.json`.
The Tools catalog links to `cli/`, whose default is `cli/stable/` once a
stable CLI release exists. Prereleases are selectable but never replace stable.
Out-of-order stable releases cannot move stable backwards. Before the first
stable release, the first published prerelease remains the default.

The selected CLI manual in `latest` continues to use the reviewed CLI commit
in `docs-sources.json`. Publishing a CLI release does not change that pin,
Core's `latest`/`stable`, existing Core snapshots, or the Docs version.
CLI-only publication fetches CLI Markdown and assets, without building CLI,
fetching Core, generating Doxygen, or building WASM. CLI source remains owned
by `opentlv-cli`; the portal owns presentation and publication.

After **CLI release gate** completes successfully, CLI's separate
`docs-notify.yml` workflow sends `cli-docs-released` to this repository:

```json
{
  "source": "cli",
  "repository": "OpenTLV/opentlv-cli",
  "commit": "<full CLI commit SHA>",
  "ref": "v0.1.0",
  "run_id": 123,
  "run_attempt": 1
}
```

Docs checks the configured repository, the completed successful
`.github/workflows/release.yml` run on `main`, and its current attempt.
It downloads the digest-verified `release-result-<attempt>` artifact and
requires its request to match the notified tag, CLI SHA, workflow SHA and run
identity. The CLI candidate may precede the workflow commit; Docs verifies
that ancestry and resolves the tag independently. Failed jobs, stale attempts,
expired/missing evidence, moved tags and invalid versions fail closed. This
flow consumes CLI release evidence, not binding compatibility feeds.

Each CLI snapshot records the tag, CLI commit, producer identity, evidence
digest, Docs infrastructure commit and rendered-file SHA-256 digests in
`source-revision.json`. Repeating publication of the same release verifies
and reuses the archived snapshot, without fetching sources or rebuilding it.
A different commit at the same version is rejected. Core release retries
also reuse their original snapshot after validating their selected source set.
Changing current navigation, theme or renderer never rebuilds historical
release directories. Version catalogs and moving aliases are intentionally
mutable; the release directories remain unchanged.

Core and CLI publications share the workflow's `docs-publication` concurrency
group and deployment job. Validation prepares a complete site and Git bundle
without remote writes. Deployment uses a normal fast-forward push and then
Pages deployment. A failed build leaves both remote history and the served
site untouched; a concurrent external history update rejects the push.
If Pages deployment fails after the history push, the served site remains at
the last successful deployment. Rerun all Docs Release jobs to produce verified
evidence for the new attempt; release snapshots reuse their archived bytes.
Rerunning only deployment cannot reuse another attempt's artifacts.
Never force-push publication history.

### Activation and retry

1. Merge the Docs receiver and CLI notifier workflows onto their respective
   `main` branches before releasing a CLI revision.
2. Configure `OPENTLV_DOCS_DISPATCH_TOKEN` in `opentlv-cli` with permission to
   [dispatch events](https://docs.github.com/en/rest/repos/repos#create-a-repository-dispatch-event)
   to `OpenTLV/opentlv-docs` (fine-grained token: target repository Contents
   write). CLI's ordinary token reads its release evidence;
   the cross-repository token is used only by the notification step.
3. Configure `OPENTLV_CLI_READ_TOKEN` in `opentlv-docs`, scoped to
   `OpenTLV/opentlv-cli` with Actions read and Contents read. It verifies the
   gate, tag and [release artifact](https://docs.github.com/en/rest/actions/artifacts#download-an-artifact).
   The Docs repository's ordinary token is scoped to Docs and is not the
   cross-repository artifact credential. The read token cannot publish Pages.
4. Run a real CLI release gate and check the notifier, Docs validation and
   Pages deployment separately. Confirm `cli/<version>/source-revision.json`
   and the CLI selector, and compare pre-existing Core and CLI snapshot bytes.

If notification fails, rerun **Notify CLI documentation portal** for the same
successful gate. Do not rerun the release gate just to resend a notification:
the gate intentionally refuses an existing tag. A failed Docs run can be
rerun while the original release evidence remains available. Keep release
evidence available under the repository's artifact retention policy; expired
evidence is rejected even when a snapshot already exists.

The first CLI release creates the `cli/` entry point. Until then, use the
selected CLI manual linked from Tools in development documentation. Local synthetic tests do
not prove the dispatch credential, hosted gate or production Pages deployment.

## Language example integration

Core pages can contain a feature slot with ordinary Markdown fallback content:

```markdown
<!-- opentlv-examples: fixed.roundtrip -->
See the native executable sources linked here when reading outside the portal.
<!-- /opentlv-examples -->
```

Use paired, standalone markers outside code fences. Feature IDs are stable
lowercase identifiers such as `fixed.roundtrip`; they identify one operation
and input contract shared by every language in that group. Do not derive them
from page filenames, line numbers or API spellings. Core owns the shared
explanation and fallback; each component owns its executable example. Nested,
malformed or unclosed slots fail assembly. Literal markers inside fenced code
are preserved.

Each selected checkout may supply a root `docs-examples.json`:

```json
{
  "version": 1,
  "component_version": "2.3.0",
  "examples": [
    {
      "feature": "fixed.roundtrip",
      "language": "python",
      "status": "supported",
      "path": "examples/quick_start.py"
    },
    {
      "feature": "schema.validate",
      "language": "python",
      "status": "unsupported",
      "reason": "This release does not expose this operation."
    }
  ]
}
```

`component_version` is the owner's version label; if omitted, the selected tag
or full commit is displayed instead. The source link always includes the exact
resolved commit, independently of that label. A `supported` entry requires a
UTF-8 source file relative to the repository root. An `unsupported` entry
requires a reason and must not reference code. A missing entry says only that
no example was supplied; it does not imply lack of API support. Supported
languages, in tab order, are `c`, `cpp`, `rust`, `python`, `lua` and `go`.
Labels stay `C`, `C++`, `Rust`, `Python`, `Lua` and `Go` so Material's existing
`content.tabs.link` preference works across pages.

To customize discovery, add an `examples` object to the component's entry in
`docs-sources.json`:

```json
"examples": {
  "manifest": "docs-examples.json",
  "languages": ["python"],
  "results": []
}
```

An explicit manifest is required to exist when its repository is included;
otherwise the conventional root manifest is optional, preserving older Core
revisions. Explicit `languages` also lets the portal display an unavailable
optional repository or a missing example. Without that list, languages are
discovered from its catalog. Configure at most one provider per language.
Duplicate feature/language entries, escaping paths, symlinks, ignored inputs
and missing declared files fail before replacing the previous assembly.
Local preview also permits non-ignored new files. Assembly reads complete
source files directly; no example code is maintained in this repository.
`source-revision.json` records catalog and source checksums in `example_inputs`.
Live preview watches those source files as well as Markdown.

### Verification displayed with examples

Catalog availability is independent of compatibility evidence. By default, a
supported example is shown with **Verified Core: not established**. A selected
Core commit, a declared dependency, a version label, or successful documentation
generation does not prove a test pass.

For explicitly pinned components, the optional `examples.results` list is a
narrow input for already selected external results. Each object contains exactly
these fields (replace the illustrative commits and evidence URL with the actual
test record):

```json
{
  "feature": "fixed.roundtrip",
  "language": "python",
  "component_commit": "1111111111111111111111111111111111111111",
  "core_commit": "2222222222222222222222222222222222222222",
  "core_version": "0.7.1",
  "result": "passed",
  "evidence": "https://example.invalid/results/immutable-result-id",
  "platform": "linux-x86_64",
  "configuration": "default"
}
```

A passed record is displayed as verified only when both full SHAs match the
selected checkouts and local preview is disabled. The tab shows the verified
Core version and commit, platform, configuration and evidence link. Matching
`failed` or `untested` records withhold code and explain the result. Missing or
stale records leave code explicitly unverified; unsupported entries never show
code. Select one result per feature/language, including one explicit platform
and configuration; the portal does not aggregate results into a broader claim.
These records are included in the existing source lock and release source-set
comparison. An existing release cannot silently acquire different evidence.

The portal validates and presents supplied evidence; it does not authenticate
the producer, fetch the evidence URL, or execute binding tests. Use immutable
published test records. For automatic release selection and stricter example
verification, configure a [compatibility feed](#compatibility-based-release-selection).
Keep executable-source tests in the owning repositories and reuse their existing example checks.
Core's native quick starts already participate in its source synchronization
and build/execution checks.

### Enabling the first native slot

Core's companion change adds `fixed.roundtrip` to its catalog and example guide.
Preview it with the sibling Core checkout and `OPENTLV_DOCS_LOCAL=1`. After that
change is committed and merged, update the Core pin in `docs-sources.json` to
the actual merged SHA. The current immutable pin is deliberately retained until
then; older selected Core revisions still build normally. Bindings can opt in
independently by adding their catalog and a portal source entry. Without binding
repositories, Core examples and ordinary documentation remain usable.

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

Both references are included under `api/reference/`, retaining the sibling layout
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
The header links to the main product repository, `OpenTLV/opentlv`, and mike
versions follow Core. Page edit and source links follow each page's owner and
selected commit. Portal-owned pages use `extra.portal_repository` from
`mkdocs.yml` to link to `OpenTLV/opentlv-docs`, independently of the header.
The `api` field records the corresponding generated-reference provenance and
links to `api/reference/api-source.json`. That manifest describes the original
input artifacts; embedded HTML has its guide links adapted for the site.

### Revision selection and local changes

`docs-sources.json` selects every component independently, including the explicitly
pinned Core commit. Components use either an explicit revision or the
[compatibility selection](#compatibility-based-release-selection) described below.
Update the manifest deliberately together with any required navigation changes.
`OPENTLV_CORE_REF` can override the Core revision with a
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
presentation and compatibility selection, not deployment. Release rejects local
mode and excludes development compatibility records.
A clean Core source revision is reproducible, but
the portal does not claim byte-identical builds across Python package
or Doxygen versions; dependency ranges are retained from the existing portal.

### Multi-repository assembly

`docs-sources.json` is the single source manifest (schema version `1`). Core is
required and retains its source ownership and Doxygen integration; the portal
assigns canonical rendered URLs through `tools/docs/navigation.py`. Additional
components choose their own tags or full commit SHAs, select a verified
release from a compatibility feed, or pin a development commit with exact-pair
compatibility evidence; they do not need matching
Core version numbers. The published portal version still follows the selected
Core release tag, while its metadata records the independently selected inputs.

Manifest validation requires integer `version: 1` and rejects unknown keys,
duplicate JSON keys, duplicate source IDs, duplicate repository/documentation-root
registrations and overlapping non-Core mounts. These checks protect ownership
before source selection or assembly; an unused or empty source directory does
not make an ambiguous registration valid.

Add a component entry to `sources`. The illustrative entry below shows the
schema, not the active Python configuration: Python is already required at
`python/` in the checked-in manifest. Do not append a duplicate `python` entry;
use an existing component release and its actual documentation paths:

```json
{
  "id": "python",
  "repository": "https://github.com/OpenTLV/opentlv-python",
  "revision": "v2.3.0",
  "docs_path": "docs",
  "mount": "python",
  "required": false,
  "navigation": {
    "title": "Python",
    "section": [],
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
`section` is a sequence of parent navigation titles in the source schema.
The central portal requires an empty list for product manuals: assembly adds
their inventory sections at the top level, and the navigation hook separates
them into contextual menus before rendering. Duplicate section titles are
errors. Every assembled Markdown page must appear in the inventory, except
Core's root GitHub `README.md`. Add explicit output routing for a new component
in `tools/docs/navigation.py` and a link from the appropriate catalog.

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
or deletes them. The lock records the manifest, exact selected commits, imported
compatibility results and omitted components. All later build steps use the lock
and reject changed configuration or checkout HEADs. Preserve the lock and the published
`source-revision.json` when auditing a build. Unset `OPENTLV_DOCS_LOCK` before
switching to local preview. No byte-identical rendering across different Python
or Doxygen versions is claimed.

### Compatibility-based release selection

A non-Core source can replace `revision` with `compatibility`, or combine a full
commit `revision` with `compatibility` to verify that exact development input.
Core always has an explicit revision; the importer resolves it before selecting any binding.
The default manifest pins Core, CLI, Lua and Python documentation explicitly.
It does not enable a compatibility-feed producer or claim runtime compatibility
for those component/Core pairs.

For example, replace the explicit Python source entry with a compatibility
selection only after activation, using a real catalog, navigation and feed
digest in place of the illustrative values:

```json
{
  "id": "python",
  "repository": "https://github.com/OpenTLV/opentlv-python",
  "compatibility": {
    "feed": "compatibility/python.json",
    "sha256": "0000000000000000000000000000000000000000000000000000000000000000",
    "platform": "linux-x86_64",
    "configuration": "default"
  },
  "examples": {
    "manifest": "docs-examples.json",
    "languages": ["python"]
  },
  "docs_path": "docs",
  "mount": "python",
  "required": false,
  "navigation": {
    "title": "Python",
    "section": [],
    "items": [{"Overview": "index.md"}]
  }
}
```

When both `revision` and `compatibility` are present, `revision` must be a full
lowercase commit SHA. Development builds require a passed record for that exact
component/Core pair and configured scope; they cannot fall back to another
component commit. Without the pin, development builds retain stable release
selection. Release builds ignore this development pin and choose a verified
stable release from the feed, excluding development records. A feed containing
only development records cannot provide a release component.

Compatibility selection requires a nonempty explicit `examples.languages` list and forbids inline
`examples.results`. Its `feed` is either an HTTPS URL or a contained POSIX path
relative to this portal, such as the local JSON file above. The file must be
UTF-8 JSON, at most 16 MiB, without symlinks. `sha256` is the lowercase digest of
the exact feed bytes, including whitespace and line endings. Calculate it after
writing the local copy:

```powershell
(Get-FileHash compatibility/python.json -Algorithm SHA256).Hash.ToLowerInvariant()
```

or `sha256sum compatibility/python.json` in a POSIX shell. Copy that digest into
the manifest; the all-zero value in the example is only a placeholder.

The external producer supplies schema version `1`:

```json
{
  "version": 1,
  "records": [
    {
      "id": "python-2.3.0-core-0.7.1-linux-default-run-42",
      "component": {
        "repository": "https://github.com/OpenTLV/opentlv-python",
        "version": "2.3.0",
        "commit": "1111111111111111111111111111111111111111"
      },
      "declared_core": ">=0.7.0 <0.8.0",
      "core": {
        "repository": "https://github.com/OpenTLV/opentlv",
        "version": "0.7.1",
        "commit": "2222222222222222222222222222222222222222"
      },
      "platform": "linux-x86_64",
      "configuration": "default",
      "build": "passed",
      "test": "passed",
      "evidence": "https://example.invalid/results/immutable-run-42",
      "features": [
        {
          "id": "fixed.roundtrip",
          "support": "supported",
          "examples": [
            {
              "language": "python",
              "path": "examples/quick_start.py",
              "result": "passed"
            }
          ]
        }
      ]
    }
  ]
}
```

Every object has exactly the fields shown. `records`, `features` and `examples`
may be empty. Record IDs are unique immutable identifiers. Commits are full
lowercase SHAs; repository URLs identify the tested owners, independently of
the version labels. The producer publishes records for component releases:
`component.version` identifies a released version, not a projected version from
a development branch. The importer consumes that release identity without
querying a package registry or GitHub release status.
`declared_core` records the component's declared dependency
as text. The importer does not evaluate that range or use it as proof of
compatibility. `core` records what was actually tested. `platform` and
`configuration` are exact, case-sensitive scope labels shared with the manifest.
`evidence` is an HTTPS URL identifying the producer's result.

`build`, `test` and each example's `result` accept `passed`, `failed` or
`untested`. Passed tests require a passed build. Feature `support` accepts
`supported`, `unsupported` or `unknown`; passed examples require a supported
feature. A feature ID matches the Core slot and component catalog, and the
example path is relative to the component repository root. Missing feature or
example entries establish neither support nor verification. Duplicate scopes,
contradictory release commits, duplicate fields and invalid records fail import,
including for optional components.

Both schema versions permit at most one example per language within each feature.
A second entry with the same language is rejected even when its path differs.
This matches the owner catalog's feature/language identity. Multiple examples
of one feature in the same language would require extending both contracts and
the portal's selection rules; changing only the duplicate check is insufficient.

#### Development compatibility records

Schema version `2` adds a required `channel` field to every record. All other
fields and exact repository/commit/scope requirements are unchanged. A `release`
record follows the version `1` release rules; a `development` record is eligible
only for a development build with an explicit component commit pin:

```json
{
  "version": 2,
  "records": [
    {
      "id": "python-main-core-main-linux-default-run-43",
      "channel": "development",
      "component": {
        "repository": "https://github.com/OpenTLV/opentlv-python",
        "version": "2.4.0-dev",
        "commit": "3333333333333333333333333333333333333333"
      },
      "declared_core": ">=0.7.0 <0.8.0",
      "core": {
        "repository": "https://github.com/OpenTLV/opentlv",
        "version": "main",
        "commit": "4444444444444444444444444444444444444444"
      },
      "platform": "linux-x86_64",
      "configuration": "default",
      "build": "passed",
      "test": "passed",
      "evidence": "https://example.invalid/results/immutable-run-43",
      "features": []
    }
  ]
}
```

Development version labels are display text and may repeat across commits.
They do not establish release identity or ordering; the two full SHAs identify
what was tested. A stable-looking version label on a development record never
makes that record eligible for a release build. A pinned development build can
also use a stable release record for the same exact commit. Duplicate evidence
for the same component/Core pair and scope remains invalid across both channels.

A version `2` feed may retain earlier `release` records alongside development
snapshots, allowing release builds to select stable evidence independently of
the development pin. Version `1` retains its original release-only contract and
cannot contain `channel`. Source locks and published metadata preserve the
selected record and the schema version, so offline replay applies the same rules.
Generated source locks also preserve the documentation channel. Offline consumers
inherit that channel when none is specified and reject a conflicting explicit channel.

#### Selection and imported evidence

Stable selection first matches the component repository, actual Core repository and
commit, platform and configuration. It then chooses the greatest stable
component version whose build and tests both passed. Versions are compared as
numeric `X.Y.Z`, so `2.10.0` sorts after `2.9.0`; an optional `v` prefix and SemVer
build metadata are accepted, while prereleases are excluded. Build metadata
does not change precedence. Different commits claiming the same release are
rejected. If a newer release failed or was not tested, an older verified release
can be selected. This chooses one binding commit for the entire build, before
its checkout, documentation or examples are loaded. If the selected owner catalog
declares `component_version`, it must agree with the feed's selected version
(with or without a leading `v`); a mismatch fails strict assembly. Local preview
can display an edited catalog version alongside the feed-selected release,
while withholding its example code and verified claim.

An optional binding with no verified release is omitted, with its unavailable
status and verification scope retained in metadata and example tabs. A required
binding with no verified release fails preparation. No matching result, an
untested combination and a failed verification remain distinct states. A
successful general build/test record allows selecting the binding, but its
example code is shown only when the feature is explicitly supported and that
language and exact catalog path have their own passed result. Missing evidence,
failed or untested examples, unknown support and unsupported features withhold
code and explain why. The tab identifies the selected binding release and commit,
declared Core dependency, actually verified Core version and commit, platform,
configuration and evidence. Local preview never presents verified code from an
automatically selected binding. Explicitly pinned sources without `compatibility` retain the
[manual evidence behavior](#verification-displayed-with-examples) described above.

Use the `ci.py select`, `ci.py fetch`, `OPENTLV_DOCS_SOURCE_ROOT` and
`OPENTLV_DOCS_LOCK` workflow from [multi-repository assembly](#multi-repository-assembly)
after configuring the feed. `fetch` imports compatibility data before checking
out the selected binding commit. HTTPS feeds are downloaded only by this
explicit preparation command and cached at `build/compatibility/<sha256>.json`.
An unlocked build reads the local feed or verified cache; it never downloads a
feed itself. A locked build uses the recorded selection without needing the
original feed or cache. Remote cache bytes are checked against the pinned digest
when imported, and a changed manifest requires a new selection and lock.

The lock and `source-revision.json` retain the feed identity, digest, full selected
record and selection scope in `compatibility_result`, including the reason when
no verified release is available. Preserve these with published artifacts.
Updating a feed, its digest, selected binding or verification result cannot
silently replace an existing Core documentation release. Rebuild it from the
preserved manifest, lock and checkouts; use a new release for changed inputs.

Checksums establish input integrity, not producer authenticity. The importer does
not authenticate the producer, follow evidence links, run an ecosystem test
suite or update component dependencies. The automated update receiver additionally
verifies the configured producer workflow and its GitHub run before preparing a
proposal. Producing correct records belongs to the owning test infrastructure;
no ecosystem test runner is introduced here.

#### Production feed activation

Use results published by a trusted CI workflow maintained by the component or
ecosystem owners. Review the producing workflow and its run evidence before
trusting a feed. Add or update the feed location and SHA-256 digest through a
reviewed pull request in this repository, linking the producing CI run and its
immutable result artifact. Documentation builds must not automatically refresh
the digest from a moving feed URL. These are operational requirements; the
importer does not enforce producer trust or pull-request review.

Before enabling the first production binding source, validate the complete
flow with an actual released binding and its published compatibility results:

1. Review the producer, exact component and Core commits, platform,
   configuration, feature coverage and individual example results.
2. In a fresh checkout, import the pinned feed with `ci.py fetch` and run the
   source checks and strict build using the generated source lock.
3. Check the selected release, displayed versions, evidence links and example
   availability against the CI record, including missing, failed or untested
   results where available.
4. Rebuild with the preserved lock without access to the original feed and
   confirm that the same component and evidence remain selected. Record the
   outcome in the activation pull request before publishing the binding source.

The automated integration tests use controlled feeds and disposable Git
repositories. They exercise import, selection, rendering, lock replay and
publication behavior, but do not establish that a production binding's CI
producer emits correct records. The strict portal build validates documentation
assembly and links. A production feed and real binding end-to-end validation
are still required before activating that integration.

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
The portal presentation overrides are the exact shared paths declared
in `PORTAL_OVERRIDES` in `tools/docs/assembly.py`:

- `index.md` (portal introduction transferred from Core in #46)
- `assets/README.md`
- `assets/favicon.svg`
- `assets/logo-mark.svg`
- `assets/opentlv.svg`
- `assets/opentlv-light.svg`
- `assets/opentlv-dark.svg`
- `playground/index.md`
- `playground/playground.js`
- `playground/playground.css`

These portal-owned presentation files may still be present in selected Core
revisions. Home ownership transferred in #46; technical pages remain Core-owned. New overrides
require an explicit ownership decision and an entry in that list; neither an
entire directory nor arbitrary Core pages may be overwritten. File/directory
conflicts always fail. Input collisions are checked before replacing the previous
assembly, and Core sources remain untouched.

`CLI_MIGRATED_PAGES` additionally transfers `cli/README.md` and
`cli/json-schema.md` from historical Core to the selected standalone CLI.
It requires the exact original source paths and keeps CLI ownership regardless
of source order. Without a selected CLI replacement, Core's pages remain.
If CLI is selected but lacks a migrated page, assembly fails instead of falling
back to historical Core content.

The selected Core tree still contains binding guides and language tabs.
Assembly preserves those existing pages without building their components or
requiring their runtimes. CLI, Lua and canonical Python manuals come from their
required independent sources. Core's former Python usage guide retains its
technical content in the historical archive, while its current Python ownership
guide remains in Development. The #62 owner corrections are merged and selected.
The [content review](DOCUMENTATION-CONTENT-REVIEW.md) records retained pages,
archive and contributor destinations, and remaining #61 owner-source corrections.
Moving retained pages requires a coordinated navigation update. Other binding
extraction will update the selected content and navigation.

The portal owns the playground UI. Exact-path overlays also support old Core
revisions that still contain its page, JavaScript and stylesheet. The component
continues to own the WASM implementation, CMake target and native smoke tests.
See [Playground builds](#playground-builds) for verified artifacts and preview.

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

`tools/docs/ci.py check` invokes the selected Core's example synchronization
and inventory validators alongside their original inputs. It
assembles Markdown and checks navigation against every assembled Markdown page
except the root GitHub `README.md`. It does not read or require a Core
`mkdocs.yml`; nested README pages still require navigation entries. These checks inspect source files without
building or running Core examples, bindings, or CLI. Strict MkDocs validation
checks the resulting navigation, links and anchors.

CI uses `markdownlint-cli@0.45.0` with `.markdownlint.json`, without automatic
fixes, on portal Markdown, Core's README, and assembled documentation. With Node
24 available, the same lint can be run after `ci.py check`:

```sh
npx --yes markdownlint-cli@0.45.0 --config .markdownlint.json \
  README.md CHANGELOG.md 'docs/**/*.md' \
  "$OPENTLV_CORE_DIR/README.md" 'build/assembled/docs/**/*.md'
```

Set `OPENTLV_CORE_DIR` explicitly for this command (use `../opentlv` for the
default sibling checkout).

## CI and versioned publication

Four entry points separate fast feedback from comprehensive publication checks:

| Workflow | Trigger | Required work |
| --- | --- | --- |
| `docs-pr.yml` / Docs PR | PR to `main` | Exact source assembly, strict MkDocs/Doxygen build, links, navigation, Markdown and workflow/evidence contract regressions; `Docs PR gate`. |
| `docs-main.yml` / Docs Main | Push to `main` | Pinned source assembly, navigation and strict site generation smoke; `Docs Main gate`. |
| `docs-full.yml` / Docs Full | Manual or called by Publishing Gate | All Docs tests, source inventories, formatting, API and playground generation, browser checks, versioned build and immutable history verification; `Docs Full gate`. |
| `docs-release.yml` / Docs Release | Release dispatch or controlled manual request | Same-commit Full CI, exact attempt evidence verification and optional deployment; `Docs Publishing gate`. |

Require **Docs PR gate** in branch protection or a ruleset. Aggregate gates reject
failed, cancelled, missing and unexpectedly skipped prerequisites. Main does not
dispatch Full CI or publish. PR/Main skip Emscripten, browser installation,
publication preparation and publication regression suites. Main also skips the
PR formatting and contract suites.

Full resolves all revisions once into `build/sources.lock.json`; source checks,
API generation and the single strict mike build use that selection. The existing
API cache is reused only after source fingerprints and file checksums match.
Full builds the playground distribution but does not run Core CTest or any
component behavioral suites. Its browser smoke validates the published UI.
Core retains native tests, ABI, fuzzing and performance; CLI and bindings retain
their executable/API tests. Docs owns generation, navigation, links and snapshots.

Full has read-only repository permissions. It runs mike against a local
`gh-pages` branch, under the version's actual URL prefix, checks site/API/WASM
metadata and prepares a Git bundle plus the complete versioned Pages artifact. Mike
aliases use copies so assets and JSON work through `stable/` without symlinks.
Only the separate deployment job can write: it imports the validated bundle,
pushes the prepared history once without force, and deploys the prepared artifact
with the official GitHub Pages Actions. It does not run Core or build scripts.

`docs-candidate-<attempt>` contains the bundle, site archive and `evidence.json`.
Evidence records the repository, infrastructure SHA, workflow ref, run ID,
attempt, exact source selection, source-manifest digest, artifact digests and
immutable historical tree IDs. The Full gate downloads only its own attempt,
verifies the bundle, source metadata, archive paths and unchanged historical
trees, then uploads `docs-pages-<attempt>`. Deployment checks the gate's evidence
digest and identity again before a fast-forward history push.
Missing or mismatched evidence fails closed; no unrelated run can authorize
deployment. Core version policy and the independent CLI release flow are retained.

Every aggregate gate uploads `docs-<stage>-timings-<attempt>`. Timing JSON separates
elapsed workflow time through the named predecessor jobs from summed runner job
time, excluding the collecting gate. The collector paginates the exact attempt
and retries delayed job metadata six times before failing. For PRs it records
both the API's head SHA and the tested merge SHA. Compare like-for-like successful
scenarios; a failed old monolithic run is diagnostic evidence, not a speedup baseline.
After pushing this change, collect hosted PR, Main and manual Full artifacts.
Local tests do not establish hosted success or production deployment.

| Trigger | Result |
| --- | --- |
| Pull request to `main` | Fast documentation verification; never prepare publication or publish. |
| Push to `main` | Documentation integration smoke only; never Full CI or publication. |
| Verified Core main notification | Open a reviewed PR updating the explicit Core commit in `docs-sources.json`. |
| Verified Core stable-tag notification | Validate and publish the immutable release version. |
| Verified component release notification | Open a reviewed PR pinning the component commit and release feed digest. |
| Verified component main notification | With development opt-in, open a reviewed PR pinning the component commit and verified exact-pair evidence. |
| Verified documentation-only main notification | With explicit documentation opt-in, propose a source commit pin without runtime compatibility claims. |
| Manual run, `publish: false` | Validate and prepare artifacts for the selected channel; no remote changes. |
| Manual run on `main`, `publish: true` | Validate and publish the selected channel. |
| Manual Full run | Complete verification and prepared artifacts; no deployment. |
| Manual Release run on another branch, `publish: true` | Deployment is refused and the Publishing gate fails. |

Manual inputs are `channel` (`development` or `release`), `core_ref` (empty uses
the manifest), and `publish` (defaults to false). Development accepts a full SHA
or tag. Release requires a Core tag `X.Y.Z` or `vX.Y.Z`; branches, bare SHAs and
prerelease tags cannot label a stable release. The resolved Core SHA is recorded
in each version's `source-revision.json`. Release directories use the full
`X.Y.Z`, retaining patch releases independently. Rebuilding the same version is
allowed only for the same complete source set: repositories, revisions, SHAs,
mounts, navigation, compatibility evidence and optional inclusion state. A moved
component tag, changed feed or newly available optional repository cannot silently
replace a published release.
Older publications without multi-source metadata cannot be overwritten by the
new assembler; publish a new version instead.

The newest published release owns `stable`; publishing an older release does
not move that alias backwards. The site root redirects to `stable` once a release
exists, otherwise to `latest`. Later development builds preserve that default
and all release directories. Successful Core WASM workflows notify this
repository through the event contract below.

### GitHub Pages setup and recovery

Before the first publication, a repository administrator must select **Settings
→ Pages → Build and deployment → Source: GitHub Actions**. Configure the
`github-pages` environment to allow deployments from `main`. Pages publication
itself needs no personal access token; cross-repository notifications and update
PRs use the tokens described below. `gh-pages` stores mike history; Pages serves the uploaded
artifact, rather than relying on a bot push to trigger a branch-based Pages build.
See GitHub's [custom Pages workflow documentation](https://docs.github.com/en/pages/getting-started-with-github-pages/using-custom-workflows-with-github-pages).

Publication runs share one concurrency group and do not cancel active publication.
Development notifications only propose source updates and use separate groups.
GitHub may replace a pending run with a newer pending run; dispatch a particular
release again if it was superseded. A failed validation or preparation cannot
change the published site or remote history. A conflicting remote history update
rejects the normal fast-forward push and blocks Pages deployment.

The history push and Pages deployment are two separate services, not a single
transaction. If Pages deployment fails after the push, the previous live site
remains available, while `gh-pages` already contains the prepared version. Rerun
all Docs Release jobs, or dispatch a fresh run from `main` with the same Core
revision and channel. Each attempt must produce and verify its own evidence.
Successful publication replaces the
whole site, including the preserved historical versions.

For a release rehearsal, dispatch with `channel: release`, a Core release tag,
and `publish: false`. Inspect the logs and artifacts, then dispatch on `main` with
the same inputs and `publish: true`. `tools/docs/publication.py` is intended for
disposable CI checkouts: it creates local mike commits but never pushes itself.

Docs owns the current portal publication workflow. Core supplies technical
documentation and verified artifacts; its historical portal publisher is no
longer the current publication path. Local checks cannot verify repository Pages
settings, environment protection, or hosted deployment.
Publication builds the selected Core WASM target, verifies provenance, and
exercises the prepared playground in Chromium. PR/Main builds and local previews
may omit WASM; Full and publication require the verified playground.

The standalone build, API integration, and CI/publication infrastructure implement
[#1](https://github.com/OpenTLV/opentlv-docs/issues/1),
[#2](https://github.com/OpenTLV/opentlv-docs/issues/2),
[#3](https://github.com/OpenTLV/opentlv-docs/issues/3), and
[#4](https://github.com/OpenTLV/opentlv-docs/issues/4). Language example rendering
implements [#5](https://github.com/OpenTLV/opentlv-docs/issues/5), with the native
slot activation described above. External compatibility import and verified
binding release selection implement [#7](https://github.com/OpenTLV/opentlv-docs/issues/7).
The configured site URL is the GitHub Pages destination; a new deployment still
requires the repository setup and hosted validation above. Remaining integration
work includes:

- External compatibility test producers and production binding feed activation.

Keep Core Markdown and public API changes in Core. Portal changes belong here.
The Core portal configuration and publisher cutover are historical work;
the completed ownership corrections are recorded in the
[ownership audit](DOCUMENTATION-OWNERSHIP.md). Content review and remaining
planning-source corrections are tracked in the
[content disposition review](DOCUMENTATION-CONTENT-REVIEW.md).

### Core cutover (#608)

The following procedure records the original portal/Core publication cutover,
including the subsequent playground UI handoff. These sequencing requirements
describe that migration, not pending prerequisites for current development.
For current contribution and source-update instructions, use the
[documentation contract](docs/development/documentation.md) and
[multi-repository assembly](#multi-repository-assembly) above. Historical sites
and already published release snapshots remain preserved.

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

Merge and validate #6 in this repository before merging the companion Core UI
removal. Preserve the historical playground; the new portal does not overwrite
its versions. Browser validation runs against the actual prepared site before
upload and deployment, separately from Markdown/API validation.

## Automated ecosystem updates

Core's `docs-notify.yml` runs after a successful `WebAssembly Build` push run.
It sends `core-docs-updated` to this repository using `repository_dispatch`.
The receiver verifies the configured repository, successful completed push run,
workflow path `.github/workflows/wasm.yml`, SHA and main/tag reference through
GitHub's API. Fork/PR runs, unknown sources, prereleases and moved tags fail.
Tags may be lightweight or annotated. A main notification prepares a reviewed
manifest pin update; it does not publish directly. A stable-tag notification
starts release validation, where sources are resolved once and the fetched
Core commit must match the verified event before building.

Example payload (use actual producer evidence):

```json
{
  "event_type": "core-docs-updated",
  "client_payload": {
    "source": "core",
    "repository": "OpenTLV/opentlv",
    "commit": "1111111111111111111111111111111111111111",
    "ref": "main",
    "run_id": 123456
  }
}
```

`ref` is `main` or a stable `X.Y.Z`/`vX.Y.Z` tag. The sender sends no commands,
checkout URLs, artifact paths or deployment instructions. Development proposals
persist a full Core commit SHA in `docs-sources.json`. Repeated notifications
update one `automation/component-<source>` proposal per source; an older
notification cannot undo a newer merged or pending pin. Portal checks use the reviewed manifest selection and reject a
Core revision older than the published `latest`, rather than silently selecting
a different revision. Manual development publications apply the same regression
guard. Diverged Core histories fail for maintainer review. PR validation uses
the proposed manifest pin. Published releases keep their
complete source set and compatibility evidence frozen; changed inputs fail
rather than replace an existing release.

Automated proposals stage only `docs-sources.json` and JSON evidence under
`compatibility/`. The workflow resolves matching Git paths before creating the
PR, so Core-only updates work without a compatibility directory or JSON files.
Unrelated files remain excluded, and no new PR is created when these selected
files have no changes relative to the base branch.

Configure `OPENTLV_DOCS_DISPATCH_TOKEN` in Core as a fine-grained PAT
with Contents write access to `OpenTLV/opentlv-docs`, sufficient
for repository dispatch. Core's own `GITHUB_TOKEN` cannot write across repositories.
The notification job performs no checkout. Install the receiver on docs `main`
before enabling the sender on Core `main`. A missing token fails notification
visibly; it does not change the successful producer result or publish anything.

Configure `DOCS_UPDATES_TOKEN` in this repository with Contents and Pull requests
write permissions for Core and component proposals. Use a PAT or an externally
refreshed App token so the created PR triggers normal documentation validation.
Enable Actions PR creation in repository settings. Proposals require review by
default. To opt in to auto-merge, enable GitHub repository auto-merge, require
`Docs PR gate` on `main` with an up-to-date branch requirement, and set the
repository variable `DOCS_UPDATES_AUTOMERGE=true`. The update token needs read
access to the applicable rules/protection metadata as well as PR write access.
The helper refuses auto-merge without that required gate and binds its request
to the generated PR head SHA; it never bypasses protection or failing checks.
The helper reads active [branch rules](https://docs.github.com/en/rest/repos/rules#get-rules-for-a-branch)
or classic [required-check protection](https://docs.github.com/en/rest/branches/branch-protection#get-status-checks-protection)
to verify these prerequisites.
Remove the variable to stop enabling auto-merge on subsequent proposals; disable
auto-merge separately on any already queued PRs.

Source updates do not invent navigation entries. A new Core page still requires
a reviewed change to `mkdocs.yml`; keep that check strict. For example, the
superseded #32/#33 pin proposals failed because `development/quality-gates.md`
was missing from portal navigation. #31 incorporates the newer #33 pin and its
navigation entry. One proposal per source prevents a new PR accumulating for
each subsequent commit while such an integration fix is pending.
The successful Core build and release do not
depend on the separate notification or portal workflows.

### Component releases and reviewed evidence

Opt in an existing compatibility source with:

```json
"updates": {
  "workflow": ".github/workflows/compatibility.yml",
  "asset": "compatibility.json"
}
```

The trusted producer must complete successfully on a stable tag push and publish
a stable GitHub release containing the configured JSON asset. After that run
completes, its notification workflow sends the same five payload fields using
`event_type: component-docs-released`, the configured source ID/repository, tag,
exact commit and successful run ID. Use the Core notification workflow as the
sender pattern, with the component's workflow name and event type.

The portal verifies the producer, tag and release asset and prepares a PR changing
that source's full commit pin, feed URL and GitHub-reported SHA-256 digest. It
preserves the platform/configuration, other sources and navigation. The branch
is keyed by source and commit, so repeated notifications update the same proposal.
PR validation imports the feed and checks the notified component commit against
the selected Core. Missing verification omits an optional component or fails a
required component; a successful producer alone is not proof of that pair.
Merge only after the production activation checks above and normal documentation
validation.

### Lua and Python documentation pin notifications

Lua and Python use the existing `component-docs-updated` event with the five
fields `source`, `repository`, `commit`, `ref`, and `run_id`. Each source entry
opts in explicitly; for example, Python uses:

```json
"updates": {
  "mode": "documentation",
  "workflow": ".github/workflows/python-main.yml"
}
```

Lua uses the same mode with `.github/workflows/lua-main.yml`. This mode is
restricted to non-Core sources with explicit revisions and no
`compatibility` configuration. It accepts only `main` development events from
a successful, completed push run in the configured source repository and
workflow. The run's exact SHA must remain on current `main` history. Release
events, forks, PR runs and unconfigured sources are rejected. Compatibility
sources retain their existing artifact/feed requirements; documentation-only
updates do not claim that the component and selected Core passed behavioral tests.

The receiver changes only the notifying source's revision, opens or updates
`automation/component-lua` or `automation/component-python`, and rejects stale or divergent updates. Replays
matching a pending or merged pin are no-ops. Docs PR checks validate the proposed
assembly; new pages need matching navigation. These Main notifications do not start
Docs Full or Pages publication. Each component continues to own its binding tests.

Merge the source policy before enabling the corresponding notifier.
Each producer's `OPENTLV_DOCS_DISPATCH_TOKEN` must be a fine-grained token restricted to
this repository with Contents write permission. `DOCS_UPDATES_TOKEN` retains
the existing Contents/Pull requests write permissions needed to create a PR
that starts normal checks; `DOCS_SOURCE_READ_TOKEN` is optional for reading the
public producer run. Auto-merge remains separately opt-in and guarded by the
Docs PR gate.

Each sender checks documentation changes after successful Main CI and
uses an attempt-specific JSON artifact. Its privileged notifier performs no
checkout and sends the producer SHA, not the notifier's current default-branch
SHA. Retry a failed notifier while its artifact is retained; duplicate delivery
does not create another proposal. HTTP acceptance is distinct from successful
receiver processing, PR validation, merge and publication. Local contract tests
mock the GitHub API; hosted delivery must be verified after both changes merge.

Lua compares manuals, examples and notification infrastructure against the
previous successful Main commit, covering intervening cancelled or failed pushes.
Unrelated source-only changes do not dispatch. Its release notifier remains
separate and requires an actual verified GitHub release.

### Component development notifications

To accept main-branch updates, additionally configure the trusted producer's
Actions artifact name:

```json
"updates": {
  "workflow": ".github/workflows/compatibility.yml",
  "asset": "compatibility.json",
  "development_artifact": "documentation-compatibility"
}
```

The configured workflow must finish successfully for a push to the component's
`main`, upload that artifact containing exactly the configured regular JSON file
at its root, and notify the
portal with `event_type: component-docs-updated`. Use the same five payload fields
as the Core example with the component source ID, repository, exact commit,
`ref: main` and producer run ID. The receiver verifies main ancestry and the
trusted run before inspecting the artifact. The artifact must belong to that
run and have a GitHub SHA-256 digest; expired, ambiguous, modified or malformed
artifacts fail. Archive paths cannot select files to write in the portal.

The imported feed must verify the exact notified component commit, the currently
pinned Core commit, and the configured platform/configuration. Version `2`
development records support this evidence; an existing stable record for the
exact pair is also accepted. Failed, untested or missing evidence prevents the
proposal. The receiver stores only verified JSON at
`compatibility/<source>/<sha256>.json` and proposes that file plus the updated
`docs-sources.json` pin and digest. It never executes producer code or tests.
Review and PR documentation checks run before merge. Publishing `latest` then
requires an explicit Docs Release request and successful Full verification.

If the default token cannot read the producer's Actions artifacts, configure
`DOCS_SOURCE_READ_TOKEN` with `Actions: read` and `Contents: read` access in the
configured repositories. This read token is separate from the token used to
create update PRs. Optional sources without `development_artifact` remain
release-only for automatic updates.

No production binding compatibility producer is configured in the default manifest.
New feeds must still pass the importer checksum/schema/selection checks and real
binding validation. Core events never refresh a moving feed digest automatically.

### Acceptance criteria for issue #6

1. Verified Core and opted-in component main notifications prepare reviewed
   updates with explicit full commit pins in `docs-sources.json`. Repeated events
   target the same proposal; delayed events cannot revert a newer merged main pin.
2. Every compatibility-selected component has passed evidence for the actual
   Core/component pair and requested scope. A development pin is not permission
   to publish an unverified combination. Version `1` feeds retain the #7 contract.
3. Release selection excludes development snapshots and freezes the complete
   source set, compatibility evidence and WASM provenance. A changed source or
   artifact cannot replace an existing release.
4. Failed event verification, source validation, build or browser checks preserve
   the previous successful publication. Publication uses a normal fast-forward
   history push and never force-pushes over concurrent history.
5. Every published playground contains all four WASM distribution files from
   the selected exact Core commit, passes provenance and integrity checks, and
   passes browser checks under the prepared version and applicable aliases.
6. Notification and proposal failures remain independent of Core build/release
   success. Integration tests cover event rejection and replay, pin selection,
   development/release separation and failed or conflicting publication.

These contracts are exercised locally with controlled feeds and Git repositories.
Hosted completion still requires the first real producer notification, proposal
validation and Pages deployment; production binding activation additionally
requires a trusted live feed and actual binding validation as described above.

### Recovery

Publication events share the existing serialized publication group. Source
proposals serialize per source and update one branch, so newer notifications
replace superseded pending updates for that source. Each
proposal starts from the current portal `main` manifest. GitHub may replace a pending publication run;
an active publication is never cancelled. Re-send a missed notification after
its producer succeeds, or use the existing manual
workflow with an exact Core ref and `publish: false` for a rehearsal. A release
notification can be replayed provided its entire selected source set is unchanged.
If a merged proposal is stale relative to the published Core, update the manifest
through a new reviewed proposal; publication will not silently substitute a pin.
For an expired token, restore the appropriate repository secret and rerun the
notification. If a development evidence artifact has expired, run the trusted
producer again and notify with the new successful run ID. Failed checks leave
the previous deployed site intact.

## Playground builds

Install Emscripten **4.0.10**, Ninja and Node.js **24** in addition to the normal
documentation tools, then run from the activated portal environment:

```sh
python tools/docs/wasm.py
python -m mkdocs serve -f mkdocs.local.yml
```

The command invokes the selected Core's `opentlv-wasm` CMake target with component
tests disabled. It records repository, exact commit, local/dirty state,
source fingerprint, toolchain and SHA-256 hashes in `wasm-source.json` next to
`opentlv.mjs`, `query.mjs`, `opentlv-core.js` and `opentlv-core.wasm` in
`build/wasm/bindings/wasm/dist/`. Local source changes invalidate old artifacts.
Build with `OPENTLV_DOCS_LOCAL=1` when previewing an uncommitted Core checkout.

Alternatively set `OPENTLV_WASM_DIR` to a complete previously generated directory
including its manifest. Explicit missing, stale, modified or unproven artifacts
fail; they never silently fall back. Transferred source bytes and Git metadata
must match the selected checkout, as with API artifacts. Checksums establish
integrity, not authentication of an arbitrary external producer.

Ordinary previews may omit artifacts and display the unavailable message.
Full CI sets `OPENTLV_DOCS_REQUIRE_WASM=1`, generates playground assets, and verifies
its provenance again in both the site and versioned publication. Metadata is
included in `source-revision.json` and `playground/wasm/wasm-source.json`.
Existing archived versions are preserved; they are not rebuilt by a new event.

Browser validation uses an optional isolated dependency set:

```sh
python -m pip install -r requirements-browser.txt
python -m playwright install chromium
python tools/docs/browser_smoke.py build/publication/site --version latest
```

It serves the prepared output under the project URL prefix and checks module
loading, successful BER parsing and a truncated-input error. It checks the
selected version and its aliases, including `stable` when publishing the newest
release. A browser failure prevents artifact upload and deployment. CI installs
Chromium OS dependencies with `playwright install --with-deps chromium`.
