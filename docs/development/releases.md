# CI and Release Process

Core, standalone products and the documentation portal have separate release
responsibilities. Start with the owning repository's guide for commands,
version rules, prerequisites and release evidence.

| Owner | Detailed process |
| --- | --- |
| Core | [Core quality gates](quality-gates.md), the repository's [contribution instructions](https://github.com/OpenTLV/opentlv/blob/main/CONTRIBUTING.md), and the feature-specific [Query release checklist](query-release.md). |
| CLI | [Versions and releases](../cli/releases.md). |
| Lua | [Versioning](../lua/versioning.md) and [release quality gate](../lua/releases.md). |
| Python | [Versioning](../python/versioning.md) and [release preparation](../python/releases.md). |
| Go | [Packaging and versioning](../go/packaging.md); independent documentation snapshots are not configured. |
| Rust | [Packaging and versioning](../rust/packaging.md), including the remaining crates.io prerequisites. |
| Portal | [CI and versioned publication](https://github.com/OpenTLV/opentlv-docs#ci-and-versioned-publication), including exact evidence, permissions and recovery. |

## From a component change to documentation

1. The component validates its own change. Where configured, a successful Main
   run can notify Docs to propose a reviewed source-pin update. A documentation
   notification is separate from releasing a component and does not assert
   runtime compatibility.
2. The portal selects explicit component revisions, assembles their manuals and
   integrates matching generated references and examples. Merging a pin update
   runs Docs Main smoke; it does not automatically deploy `latest`.
3. A release notification or controlled manual publication request enters the
   publishing process. The portal requires the appropriate Full validation and
   checks the exact run/attempt, source selection and artifact evidence.
4. A separate deployment job publishes the validated artifacts. Passing local
   checks or preparing a Full candidate alone does not perform deployment.

See [automated ecosystem updates](https://github.com/OpenTLV/opentlv-docs#automated-ecosystem-updates)
for notification policies and [component publication](https://github.com/OpenTLV/opentlv-docs#independent-component-release-publication)
for the independent release flow. These are existing processes, not steps a
documentation contributor must reimplement.

## Versions and preservation

Portal `latest` represents a published development selection. Core release
documentation uses full `X.Y.Z` snapshots; `stable` follows the newest published
release. Existing release snapshots remain immutable when the portal layout or
development sources change.

The Docs repository has its own Git tags and GitHub Releases, independently of
those Core-versioned site paths. A manual Docs Release on `main` with
`channel=release`, `core_ref=v0.8.0`, `tag=v0.1.0` and `publish=true` first verifies
and deploys the portal, then tags the exact verified Docs commit and publishes
its changelog notes and release evidence. The Docs changelog must first be closed
as `[0.1.0]`; automated notifications never create Docs version tags. See the
[versioned release procedure](https://github.com/OpenTLV/opentlv-docs#independent-docs-tag-and-github-release)
for rehearsals, expected assets and partial-failure recovery.

CLI, Lua and Python have independently versioned documentation publication.
Their manuals selected inside a portal version are not proof that the same
independent release is published. Rust manuals are available at the revision
selected for a portal version; independent Rust documentation publication is not
configured. Use the [Languages](../bindings/index.md) and
[Tools](../tools/index.md) overviews for available manual entry points, and the
owner's release guide for its release status.

Record deployment evidence separately from validation. The portal operations
guide owns [Pages setup and recovery](https://github.com/OpenTLV/opentlv-docs#github-pages-setup-and-recovery);
the historical Core documentation archive and existing published snapshots are
preserved independently of new portal content.

## Docs 0.1.0 release preparation

The first Docs release targets `v0.1.0`, with the closed changelog heading
`[0.1.0] - 2026-10-28`. Its Core source is `v0.8.0`, resolved to
`345c77acb29266036df5f27d04ce315bb61853cc`. Docs and Core versions are independent:
the Docs tag identifies the verified portal infrastructure commit, while the new
site snapshot uses `0.8.0/` and the `stable` alias.

The reviewed source baseline in `docs-sources.json` is:

| Component | Release | Exact source commit |
| --- | --- | --- |
| Core | `v0.8.0` | `345c77acb29266036df5f27d04ce315bb61853cc` |
| CLI | `v0.2.0` | `514d76f48485cc7fc602f8287b9f22e4ce015997` |
| Lua | `v0.2.0` | `77abc807bdd59956790497483a9d1fbad4b79019` |
| Python | `v0.1.0` | `52e15f8028da8521ccf64a97b03f7e6e249a0912` |
| Rust | `v0.1.0` | `f297ab3899bafb95716a39a38dfaf7df14e8768d` |
| Go | `v0.1.0` | `247da7863510ebed64030a8c6c01e122ad122a31` |
| JavaScript | `v0.1.0` | `22efa490f25e5d947a7b88f451f68f4aab28b6a9` |

Release preparation and local checks do not establish publication. After merging
the preparation, require Docs Main on the intended release commit and run
Docs Release from `main` with `channel=release`, `core_ref=v0.8.0`, `tag=v0.1.0`
and `publish=false` for the rehearsal. Inspect Full evidence, immutable history,
API generation and browser checks. The publishing operation uses the same inputs
with `publish=true` and performs its own Full verification before Pages deployment
and Docs tag/release creation. Follow the linked procedure above for exact commands
and recovery; do not reuse a different run's evidence or retarget an existing tag.

The expected GitHub Release assets are `release-manifest.json`,
`full-evidence.json`, `release-notes.md` and `SHA256SUMS`. Verify the released
tag's Docs SHA, the recorded Core source and run/attempt, asset checksums and
deployed `0.8.0/` and `stable/` routes before recording completion in
[Docs #135](https://github.com/OpenTLV/opentlv-docs/issues/135) and
[Core #718](https://github.com/OpenTLV/opentlv/issues/718).
