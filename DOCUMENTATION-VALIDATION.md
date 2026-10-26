# Documentation migration validation

Final validation record for [issue #50](https://github.com/OpenTLV/opentlv-docs/issues/50)
and [epic #43](https://github.com/OpenTLV/opentlv-docs/issues/43), prepared
2026-10-26 against Docs `566031c782f58d8aff13f67a2cbee8b96d2b1f29` and the source
pins below. It compares the current portal with the
[migration mapping](DOCUMENTATION-MIGRATION.md) and the
[content disposition review](DOCUMENTATION-CONTENT-REVIEW.md). It does not
replace their dated evidence.

The approved target is the seven-section hierarchy from
[#63](https://github.com/OpenTLV/opentlv-docs/issues/63): Home, Tutorials, API,
Standards, Languages, Tools and Development. It also follows the #45 maintainer
amendment, under which moved page URLs have no redirects or aliases. The six
sections and URL compatibility options in the #50 text describe the earlier
target, which the mapping records as superseded. They are validated here as the
seven sections and documented discontinued URLs.

## Validated selection

| Source | Selected pin | Deployed `latest` (gh-pages `350104a`) |
| --- | --- | --- |
| core | `4cd674fe87d7d4af1695f6bcd224bbca6344c4cb` | `1043bdccb0b5d3b519c5dd05cfc69bcdab511530` |
| cli | `abd2bce09a9f25071a41d7c1f3249fd48e8a0b20` | same |
| lua | `e2b65d515852748b80d1e4506c4b3a306d30a2f4` | same |
| python | `74d7ed756229ab11544d5eba38568ae6f2bfddb0` | same |
| rust | `ee2d1f4eae24321f9dbd62d35fdeaf79e344bfbe` | same |
| go | `bc73a5100ef6109e8e5634add62785eb21352254` | same |
| js | `42687fb3fc7552aed887badab9ea1ac0651748be` | `72338d82aad22c1620b75e0f8f190de11982a74a` |

The deployed `latest` was built from Docs `3696ae3` by the manual Docs Release
run [40293924482](https://github.com/OpenTLV/opentlv-docs/actions/runs/40293924482).
Later Core and JS pin updates (#121–#123) are merged and pass Docs PR/Main, but
are not yet published. The local checks below use the exact current pins and a
clean managed checkout of each source.

## Acceptance summary

| Criterion | Result | Evidence |
| --- | --- | --- |
| Every original page is accounted for | Pass | All 142 baseline Markdown rows have a final disposition in the [ledger](#baseline-ledger). |
| Relevant technical information is preserved | Pass | 100 rows render from their owner. 37 are retained as repository files or Portal overlays. 5 were removed by owner extractions and have standalone successors. |
| Seven top-level sections work | Pass | Desktop (1440 px) and mobile (390 px) browser smoke; live landing URLs return HTTP 200. |
| Internal links are valid | Pass | Strict MkDocs build with link, anchor and navigation validation set to warn, so strict mode fails on them. |
| Public URLs preserved or handling documented | Pass, one owner correction | 8 page URLs and the root are unchanged. 92 are discontinued by policy. One Core reference to a moved route is tracked below. |
| Existing examples remain accessible and valid | Pass | Core example and inventory validators pass at the selected pin. Example tabs come from repository-owned catalogs. |
| CLI, Python, Lua and Core integration | Pass | See [product integration](#product-documentation-integration). |
| Independently versioned documentation intact | Pass | `cli/0.1.0` keeps the same tree in every gh-pages commit since its publication. |
| Stable documentation URLs accessible | Pass | `/cli/`, `/cli/stable/`, `/cli/0.1.0/` and the legacy `opentlv.github.io/opentlv/` site return HTTP 200. |
| Previously published versions unchanged | Pass | Full gate snapshot comparison; history inspection below. |
| Documentation builds successfully | Pass | Local strict build at the exact pins; hosted Docs Main succeeded for `566031c`. |
| Publishing workflows complete successfully | Pass for the deployed revision, pending for current main | Docs Release run 40293924482 succeeded. Publishing current main needs a maintainer-approved release run. |
| No unrelated product implementation changes | Pass | This validation changes only Portal checks and documentation. |
| Remaining issues are tracked | Pass | See [remaining work](#remaining-work). |

## Content preservation

The #44 baseline contains 142 source Markdown files from the Portal, Core, CLI,
Lua and Python revisions recorded in the mapping. The ledger at the end resolves
each row against the selected pin and the actual built site. A row counts as
rendered only if a built page exposes that owner path as its edit action. The
combined DER/CER pages and the split Core first-program guide expose all of
their original sources this way.

| Final disposition | Rows |
| --- | ---: |
| Rendered from the owning source | 100 |
| Repository-only file retained at the selected pin (G) | 33 |
| Core source retained, presentation replaced by a Portal page or excluded GitHub index | 4 |
| Removed by the owner after extraction, with a standalone successor | 5 |

Core removed these five sources in the binding extractions of Core #679, #686
and #698; this migration removed none of them. Their successors are the Rust, Go and JS manuals
now selected from `opentlv-rust`, `opentlv-go` and `opentlv-js`. Older selected
Core revisions still render the archived originals, and immutable Git revisions
retain the evidence. No Portal decision removed a technical page.

The current assembly has 149 Markdown files. Excluding Core's GitHub-only index
leaves 148 navigable pages: Core 75, Portal 30, Rust 11, Python 10, Lua 9, Go 5,
CLI 4 and JS 4. The navigation check requires every assembled page in the
navigation, and every built page has an owner edit link. The 17 historical
records at the current pins keep their bodies, anchors and owner links under
`development/history/`.

The dated #61 review lists 129 pages. 124 are at their recorded destinations.
The remaining five rows, the Core Go, Rust and WebAssembly manuals, were later
superseded by the standalone manuals above. The review notes this change for
WebAssembly only. Rust's retained Core development guide now renders at
`development/bindings/rust/` (OpenTLV/opentlv-rust#7).

The generated C and C++ reference trees contain the same files as the Doxygen
output of the selected Core revision: 441 and 651 files. The deployed trees
(451 and 661 files) come from the older Core revision and the hosted Doxygen
version. Full CI regenerates both. The playground WebAssembly distribution is
built only in Full CI, where its browser smoke must pass before publication.

## Navigation

The existing `tools/docs/navigation_smoke.py` passed against the strictly built
site under the `/opentlv-docs/latest/` prefix. It covers:

- the seven tabs on desktop and the seven-item mobile drawer, opening each
  landing through its control without horizontal overflow;
- the CLI, Lua, Python and Rust manual menus, which hide the portal tabs,
  exclude archive and contributor chapters and return to the portal root;
- format, catalog, contributor and archive routes, including archive-to-current
  links.

The live deployment serves all seven landings below `/opentlv-docs/latest/`.
Breadcrumbs are not enabled in the current Material configuration. Section tabs,
section indexes and the active navigation path show the reader's location.
Adding breadcrumbs would be a presentation change and is out of this issue's
scope.

## URL compatibility

Following the no-redirect policy, the built site emits no page at a
discontinued baseline URL. The site root is the only old path still served,
and it remains Home. Of the 100 rendered baseline pages, 8 keep their URL:
seven Core contributor pages under `development/` and `standards/emv/`. The other
92 render only at the destinations in the ledger. Their baseline URLs are
intentionally discontinued, including the old `getting-started/`, `formats/`
and `bindings/` landings, which now return HTTP 404 on the live site.

These public entry points are preserved: the site root and `/latest/`,
`P/assets/*.svg`, `P/playground/playground.{js,css}`, the CLI publication
namespace and the legacy `https://opentlv.github.io/opentlv/` site. Previously
published immutable snapshots keep their own layout.

Known references were checked on the `main` branch of every repository in the
workspace:

| Reference | Target | Result |
| --- | --- | --- |
| Core `README.md`, `CONTRIBUTING.md`, `docs/README.md`, `docs/index.md`, ownership guide | `/opentlv-docs/` | HTTP 200 |
| Core `cmake/doxygen.cmake` | `/opentlv-docs/latest/` | HTTP 200 |
| Go `README.md` | `/opentlv-docs/latest/languages/go/` | HTTP 200 |
| CLI `docs/releases.md` | `/opentlv-docs/cli/<version>/` pattern | `/cli/0.1.0/` HTTP 200 |
| Portal catalogs and CLI overview | `/opentlv-docs/cli/`, `/opentlv-docs/cli/stable/` | HTTP 200 |
| Core `docs/playground/index.md` and ownership guide | `/opentlv/` and `/opentlv/latest/playground/` | HTTP 200 |
| Core `docs/playground/index.md` | `/opentlv-docs/latest/playground/` | HTTP 404; moved to `tools/playground/` |

The Core playground stub is a GitHub-only page that the Portal overrides. Its
link must be corrected in Core; see [remaining work](#remaining-work).
External sites, release notes and closed issue comments cannot be enumerated
completely. They follow the documented no-redirect policy.

## Product documentation integration

| Product | Portal entry | Selected manual and ownership | Independent publication |
| --- | --- | --- | --- |
| Core | Home, Tutorials, API, Standards, Development | 75 pages with Core edit links at the selected pin; C/C++ references under `api/reference/` | Core releases publish portal versions; none is published yet. `latest` is development. |
| CLI | `tools/otlv/` | `tools/otlv/manual/` and two contributor pages, CLI edit links, product menu with a return link | `/cli/0.1.0/` (`stable`), unchanged since 2026-10-18, with a portal return link |
| Python | `languages/python/` | `languages/python/manual/`, contributor and history pages, Python edit links | `/python/` is reserved; no release is published, and catalogs do not link it |
| Lua | `languages/lua/` | `languages/lua/manual/`, contributor and history pages, Lua edit links | `/lua/` is reserved; no release is published, and catalogs do not link it |

Rust, Go and JavaScript follow the same pattern from their own repositories.
Portal-owned pages are the 30 catalogs, introductions and contributor entry
points. Detailed manuals keep their owner's source and edit links and are not
copied into Portal sources.

## Documentation examples

`tools/docs/ci.py check` ran the selected Core revision's
`check_doc_examples.py` and `check_doc_inventory.py`; both passed. Language
example tabs are assembled from repository-owned catalogs and source files, as
in #5. The Getting Started example regression was fixed in #51. Components keep
their own executable example tests; the Portal does not duplicate them.

## Build and publishing

| Check | Scope | Result |
| --- | --- | --- |
| `ci.py select`, `ci.py check`, `mkdocs build --strict` | Exact pins, clean managed checkouts | Pass; `source-revision.json` records each pin as clean and non-local |
| Versioned candidate build | `site_url` under `latest/`, placed into the published gh-pages history | Pass, including the new entry-point check |
| `navigation_smoke.py` | Built site, Chromium | Pass |
| Docs Main for `566031c` | Hosted | Run [40357862020](https://github.com/OpenTLV/opentlv-docs/actions/runs/40357862020) succeeded |
| Documentation source updates | Hosted repository dispatch | Recent runs succeeded and produced reviewed pin PRs #122 and #123 |
| Docs Release for `3696ae3` | Hosted Full CI and deployment | Run 40293924482 succeeded; gh-pages `350104a` |

Product publication is separate from portal publication. The `cli/` namespace
has its own `versions.json` and `stable` alias. The `cli/0.1.0` tree
`89f60142989a6c0091a04f790067a21ec3c7971c` is identical in all 12 gh-pages
commits since its publication. Full CI records every immutable snapshot tree
before generation and rejects changed trees before deployment. Release and
publishing workflows were not modified.

## Regression prevention

| Risk | Existing or added check | Runs in |
| --- | --- | --- |
| Broken internal links and anchors | Strict MkDocs link and anchor validation | PR, Main, Full |
| Missing referenced pages | Strict validation and the assembled-page navigation check in `ci.py` | PR, Main, Full |
| Invalid navigation entries | Stale and omitted navigation entries fail `ci.py`; navigation contract tests | PR, Main, Full |
| Missing documentation assets | Strict validation of Markdown asset links and generated API references; WASM manifests and checksums | PR, Main, Full (WASM in Full) |
| Invalid product entry points | **Added:** absolute links from the new version into `site_url` must resolve in the prepared history | Full gate |
| Lost or rerouted pages, menus and archives | Navigation, onboarding and format contract tests; browser navigation smoke | PR, Full |
| Changed published snapshots | Immutable tree comparison in `quality.py` | Full gate |

MkDocs does not validate absolute URLs. It therefore accepted links to the
separately published CLI entry points and product return links without checking
them. `quality.py verify` now checks them against the exact history being
deployed. The check covers only the new version's HTML, not older snapshots.
A missing product publication or a moved portal route fails before deployment.

## Remaining work

| Item | Owner | Tracking |
| --- | --- | --- |
| Correct the Core playground stub link from `latest/playground/` to `latest/tools/playground/`, then adopt the Core pin | Core, then Portal pin update | Core follow-up issue |
| Publish current main and confirm the live seven-section site with the selected Core and JS pins | Maintainer-approved Docs Release run | #50 completion |
| First Lua and Python releases before `/lua/` and `/python/` can be linked | Lua and Python release processes | Existing component release flows |
| Visual identity and the Home wire explorer | Portal | #20, #19 |

## Baseline ledger

Destinations are relative to a portal version (`P/`). `G` marks repository-only
files that remain at their source path. Rows follow the mapping's table order.

| Owner | Source | Baseline URL | Final destination |
| --- | --- | --- | --- |
| portal | `docs/assets/README.md` | `P/assets/` | `development/documentation/assets/` |
| portal | `docs/playground/index.md` | `P/playground/` | `tools/playground/` |
| core | `docs/README.md` | `Not published` | Retained GitHub index; excluded from the site (G) |
| core | `docs/assets/README.md` | `P/assets/` | Replaced by Portal `development/documentation/assets/`; Core source retained (G) |
| core | `docs/concepts/architectural-rules.md` | `P/concepts/architectural-rules/` | `development/architecture/architectural-rules/` |
| core | `docs/concepts/architecture.md` | `P/concepts/architecture/` | `development/architecture/architecture/` |
| core | `docs/concepts/bindings.md` | `P/concepts/bindings/` | `languages/contracts/` |
| core | `docs/concepts/core-types.md` | `P/concepts/core-types/` | `api/concepts/core-types/` |
| core | `docs/concepts/cxx-builtins.md` | `P/concepts/cxx-builtins/` | `languages/cpp/concepts/cxx-builtins/` |
| core | `docs/concepts/cxx-formats.md` | `P/concepts/cxx-formats/` | `languages/cpp/concepts/cxx-formats/` |
| core | `docs/concepts/cxx-native-boundary.md` | `P/concepts/cxx-native-boundary/` | `languages/cpp/concepts/cxx-native-boundary/` |
| core | `docs/concepts/definition-boundaries.md` | `P/concepts/definition-boundaries/` | `development/architecture/definition-boundaries/` |
| core | `docs/concepts/endian.md` | `P/concepts/endian/` | `api/concepts/endian/` |
| core | `docs/concepts/error-model.md` | `P/concepts/error-model/` | `development/architecture/error-model/` |
| core | `docs/concepts/field-policies.md` | `P/concepts/field-policies/` | `development/architecture/field-policies/` |
| core | `docs/concepts/format-capabilities.md` | `P/concepts/format-capabilities/` | `api/concepts/format-capabilities/` |
| core | `docs/concepts/format-contract.md` | `P/concepts/format-contract/` | `api/concepts/format-contract/` |
| core | `docs/concepts/learning-model.md` | `P/concepts/learning-model/` | `tutorials/concepts/learning-model/` |
| core | `docs/concepts/length.md` | `P/concepts/length/` | `api/concepts/length/` |
| core | `docs/concepts/processing-pipeline.md` | `P/concepts/processing-pipeline/` | `development/architecture/processing-pipeline/` |
| core | `docs/concepts/query-language.md` | `P/concepts/query-language/` | `api/query-language/` |
| core | `docs/concepts/runtime-model.md` | `P/concepts/runtime-model/` | `development/planning/runtime-model/` |
| core | `docs/concepts/value.md` | `P/concepts/value/` | `api/concepts/value/` |
| core | `docs/development/abi-compatibility.md` | `P/development/abi-compatibility/` | `development/abi-compatibility/` |
| core | `docs/development/cxx-facade-performance.md` | `P/development/cxx-facade-performance/` | `development/history/core/cxx-facade-performance/` |
| core | `docs/development/documentation-audit.md` | `P/development/documentation-audit/` | `development/history/core/documentation-audit/` |
| core | `docs/development/documentation-layout.md` | `P/development/documentation-layout/` | `development/documentation/layout/` |
| core | `docs/development/documentation-ownership.md` | `P/development/documentation-ownership/` | `development/documentation/ownership/` |
| core | `docs/development/fuzzing.md` | `P/development/fuzzing/` | `development/fuzzing/` |
| core | `docs/development/go.md` | `P/development/go/` | Removed by Core #686; successor `languages/go/manual/development/go/` (opentlv-go) |
| core | `docs/development/indefinite-boundary-reuse.md` | `P/development/indefinite-boundary-reuse/` | `development/planning/indefinite-boundary-reuse/` |
| core | `docs/development/python.md` | `P/development/python/` | `development/bindings/python/` |
| core | `docs/development/quality-gates.md` | `P/development/quality-gates/` | `development/quality-gates/` |
| core | `docs/development/query-adversarial.md` | `P/development/query-adversarial/` | `development/query-adversarial/` |
| core | `docs/development/query-phase-audit.md` | `P/development/query-phase-audit/` | `development/history/core/query-phase-audit/` |
| core | `docs/development/query-release.md` | `P/development/query-release/` | `development/query-release/` |
| core | `docs/development/reader-decode-performance.md` | `P/development/reader-decode-performance/` | `development/history/core/reader-decode-performance/` |
| core | `docs/development/rust.md` | `P/development/rust/` | `development/bindings/rust/` |
| core | `docs/development/valgrind.md` | `P/development/valgrind/` | `development/valgrind/` |
| core | `docs/development/webassembly.md` | `P/development/webassembly/` | Removed by Core #698; successor `languages/javascript/manual/webassembly/` (opentlv-js) |
| core | `docs/development/workflow.md` | `P/development/workflow/` | `development/workflow/` |
| core | `docs/formats/README.md` | `P/formats/` | `api/formats/guide/` |
| core | `docs/formats/asn1/ber.md` | `P/formats/asn1/ber/` | `standards/asn1/ber/` |
| core | `docs/formats/asn1/cer.md` | `P/formats/asn1/cer/` | `standards/asn1/cer/` |
| core | `docs/formats/asn1/der.md` | `P/formats/asn1/der/` | `standards/asn1/der/` |
| core | `docs/formats/bluetooth/README.md` | `P/formats/bluetooth/` | `standards/bluetooth/` |
| core | `docs/formats/custom/README.md` | `P/formats/custom/` | `api/formats/custom/` |
| core | `docs/formats/dhcp/README.md` | `P/formats/dhcp/` | `standards/dhcp/` |
| core | `docs/formats/fixed/configurable.md` | `P/formats/fixed/configurable/` | `api/formats/fixed/configurable/` |
| core | `docs/formats/format-catalogue.md` | `P/formats/format-catalogue/` | `development/planning/format-catalogue/` |
| core | `docs/formats/format-examples.md` | `P/formats/format-examples/` | `tutorials/formats/` |
| core | `docs/formats/format-roadmap.md` | `P/formats/format-roadmap/` | `development/planning/format-roadmap/` |
| core | `docs/formats/lldp-review.md` | `P/formats/lldp-review/` | `development/planning/lldp-review/` |
| core | `docs/formats/lldp/README.md` | `P/formats/lldp/` | `standards/lldp/` |
| core | `docs/formats/lldp/conformance.md` | `P/formats/lldp/conformance/` | `standards/lldp/conformance/` |
| core | `docs/formats/nfc/README.md` | `P/formats/nfc/` | `standards/nfc/` |
| core | `docs/formats/packed.md` | `P/formats/packed/` | `api/formats/packed/` |
| core | `docs/formats/support.md` | `P/formats/support/` | `api/capabilities/` |
| core | `docs/formats/variable.md` | `P/formats/variable/` | `api/formats/variable/` |
| core | `docs/getting-started/README.md` | `P/getting-started/` | `development/building/core/`, `tutorials/first-program/` |
| core | `docs/guides/codecs.md` | `P/guides/codecs/` | `api/guides/codecs/` |
| core | `docs/guides/copy.md` | `P/guides/copy/` | `api/guides/copy/` |
| core | `docs/guides/cxx-examples.md` | `P/guides/cxx-examples/` | `tutorials/cpp-examples/` |
| core | `docs/guides/diagnostics.md` | `P/guides/diagnostics/` | `api/guides/diagnostics/` |
| core | `docs/guides/document.md` | `P/guides/document/` | `api/guides/document/` |
| core | `docs/guides/examples.md` | `P/guides/examples/` | `tutorials/examples/` |
| core | `docs/guides/go.md` | `P/guides/go/` | Removed by Core #686; successor `languages/go/manual/guides/go/` (opentlv-go) |
| core | `docs/guides/memory.md` | `P/guides/memory/` | `api/guides/memory/` |
| core | `docs/guides/processing.md` | `P/guides/processing/` | `tutorials/processing/` |
| core | `docs/guides/python.md` | `P/guides/python/` | `development/history/core/guides/python/` |
| core | `docs/guides/queries.md` | `P/guides/queries/` | `api/guides/queries/` |
| core | `docs/guides/reader.md` | `P/guides/reader/` | `api/guides/reader/` |
| core | `docs/guides/rust.md` | `P/guides/rust/` | Removed by Core #679; successor `languages/rust/manual/guides/rust/` (opentlv-rust) |
| core | `docs/guides/schemas.md` | `P/guides/schemas/` | `api/guides/schemas/` |
| core | `docs/guides/select-components.md` | `P/guides/select-components/` | `api/configuration/` |
| core | `docs/guides/writer.md` | `P/guides/writer/` | `api/guides/writer/` |
| core | `docs/index.md` | `P/` | Replaced by Portal Home `/` (#46); Core source retained (G) |
| core | `docs/playground/index.md` | `P/playground/` | Replaced by Portal `tools/playground/`; Core stub retained (G) |
| core | `docs/reference/README.md` | `P/reference/` | `api/reference/` |
| core | `docs/reference/c-api.md` | `P/reference/c-api/` | `api/reference/c/` |
| core | `docs/reference/compilers.md` | `P/reference/compilers/` | `development/building/compilers/` |
| core | `docs/reference/cxx-api.md` | `P/reference/cxx-api/` | `api/reference/cpp/` |
| core | `docs/reference/errors.md` | `P/reference/errors/` | `api/reference/errors/` |
| core | `docs/standards/cer/README.md` | `P/standards/cer/` | `standards/asn1/cer/` |
| core | `docs/standards/der/README.md` | `P/standards/der/` | `standards/asn1/der/` |
| core | `docs/standards/emv/README.md` | `P/standards/emv/` | `standards/emv/` |
| cli | `docs/README.md` | `P/cli/` | `tools/otlv/manual/` |
| cli | `docs/development.md` | `P/cli/development/` | `development/components/cli/development/` |
| cli | `docs/json-schema.md` | `P/cli/json-schema/` | `tools/otlv/manual/json-schema/` |
| cli | `docs/releases.md` | `P/cli/releases/` | `development/components/cli/releases/` |
| lua | `docs/api.md` | `P/lua/api/` | `languages/lua/manual/api/` |
| lua | `docs/development.md` | `P/lua/development/` | `languages/lua/manual/development/` |
| lua | `docs/implementation.md` | `P/lua/implementation/` | `development/components/lua/implementation/` |
| lua | `docs/migration.md` | `P/lua/migration/` | `development/history/lua/migration/` |
| lua | `docs/quality-gates.md` | `P/lua/quality-gates/` | `development/components/lua/quality-gates/` |
| lua | `docs/releases.md` | `P/lua/releases/` | `development/components/lua/releases/` |
| lua | `docs/testing.md` | `P/lua/testing/` | `development/components/lua/testing/` |
| lua | `docs/versioning.md` | `P/lua/versioning/` | `languages/lua/manual/versioning/` |
| python | `docs/development/python.md` | `P/python/development/python/` | `languages/python/manual/development/python/` |
| python | `docs/guides/python.md` | `P/python/guides/python/` | `languages/python/manual/guides/python/` |
| python | `docs/migration.md` | `P/python/migration/` | `development/history/python/migration/` |
| python | `docs/quality-gates.md` | `P/python/quality-gates/` | `development/components/python/quality-gates/` |
| python | `docs/releases.md` | `P/python/releases/` | `development/components/python/releases/` |
| python | `docs/validation/ci.md` | `P/python/validation/ci/` | `development/history/python/validation/ci/` |
| python | `docs/validation/layout.md` | `P/python/validation/layout/` | `development/history/python/validation/layout/` |
| python | `docs/validation/packaging.md` | `P/python/validation/packaging/` | `development/history/python/validation/packaging/` |
| python | `docs/validation/standalone-build.md` | `P/python/validation/standalone-build/` | `development/history/python/validation/standalone-build/` |
| python | `docs/versioning.md` | `P/python/versioning/` | `languages/python/manual/versioning/` |
| portal | `CHANGELOG.md` | — | Repository file retained at the selected pin (G) |
| portal | `README.md` | — | Repository file retained at the selected pin (G) |
| core | `.github/PULL_REQUEST_TEMPLATE.md` | — | Repository file retained at the selected pin (G) |
| core | `AGENTS.md` | — | Repository file retained at the selected pin (G) |
| core | `CHANGELOG.md` | — | Repository file retained at the selected pin (G) |
| core | `CODE_OF_CONDUCT.md` | — | Repository file retained at the selected pin (G) |
| core | `CONTRIBUTING.md` | — | Repository file retained at the selected pin (G) |
| core | `README.md` | — | Repository file retained at the selected pin (G) |
| core | `ROADMAP.md` | — | Repository file retained at the selected pin (G) |
| core | `SECURITY.md` | — | Repository file retained at the selected pin (G) |
| core | `benchmarks/README.md` | — | Repository file retained at the selected pin (G) |
| core | `benchmarks/baselines/README.md` | — | Repository file retained at the selected pin (G) |
| core | `bindings/go/README.md` | — | Removed by Core #686; successor `go:README.md` (G) |
| core | `examples/nfc/type2/README.md` | — | Repository file retained at the selected pin (G) |
| core | `examples/tlv++/src/README.md` | — | Repository file retained at the selected pin (G) |
| core | `examples/tlv/src/README.md` | — | Repository file retained at the selected pin (G) |
| core | `tests/README.md` | — | Repository file retained at the selected pin (G) |
| core | `tests/property/README.md` | — | Repository file retained at the selected pin (G) |
| core | `tests/query/README.md` | — | Repository file retained at the selected pin (G) |
| cli | `.github/PULL_REQUEST_TEMPLATE.md` | — | Repository file retained at the selected pin (G) |
| cli | `CHANGELOG.md` | — | Repository file retained at the selected pin (G) |
| cli | `CONTRIBUTING.md` | — | Repository file retained at the selected pin (G) |
| cli | `README.md` | — | Repository file retained at the selected pin (G) |
| cli | `src/README.md` | — | Repository file retained at the selected pin (G) |
| cli | `tests/README.md` | — | Repository file retained at the selected pin (G) |
| cli | `tests/baseline/README.md` | — | Repository file retained at the selected pin (G) |
| lua | `CHANGELOG.md` | — | Repository file retained at the selected pin (G) |
| lua | `README.md` | — | Repository file retained at the selected pin (G) |
| lua | `provenance/original-readme.md` | — | Repository file retained at the selected pin (G) |
| python | `CHANGELOG.md` | — | Repository file retained at the selected pin (G) |
| python | `CONTRIBUTING.md` | — | Repository file retained at the selected pin (G) |
| python | `README.md` | — | Repository file retained at the selected pin (G) |
| python | `native/README.md` | — | Repository file retained at the selected pin (G) |
| python | `src/README.md` | — | Repository file retained at the selected pin (G) |
