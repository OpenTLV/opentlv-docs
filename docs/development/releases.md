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
| Go | [Packaging and versioning](../go/packaging.md); no public module release or independent documentation snapshots yet. |
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

CLI, Lua and Python have independently versioned documentation publication.
Their manuals selected inside a portal version are not proof that the same
independent release is published. Rust manuals are available only at the
revision selected for a portal version until Rust defines releases. Use the [Languages](../bindings/index.md) and
[Tools](../tools/index.md) overviews for available manual entry points, and the
owner's release guide for its release status.

Record deployment evidence separately from validation. The portal operations
guide owns [Pages setup and recovery](https://github.com/OpenTLV/opentlv-docs#github-pages-setup-and-recovery);
the historical Core documentation archive and existing published snapshots are
preserved independently of new portal content.
