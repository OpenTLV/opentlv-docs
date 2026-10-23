# Testing and Quality Gates

Each repository owns tests for its own behavior. Integration checks connect
selected components; they do not replace the owners' suites or imply that every
binding exposes every Core feature.

## Quality-gate model

The ecosystem separates four validation purposes. Exact triggers, required jobs,
platform matrices and commands remain in each repository's quality-gate guide.

| Tier | Purpose |
| --- | --- |
| PR | Review feedback and the required gate for a proposed change. |
| Main | Integration validation after changes reach the main branch. A successful Main run is not release approval. |
| Full | Broader verification of the selected revision and configurations, including checks omitted from faster tiers. |
| Release / Publishing | Verification of the release candidate and its required evidence before distributing artifacts or publishing documentation. |

For Docs specifically, PR checks source assembly, strict site generation and
contracts; Main performs documentation smoke checks. Full adds comprehensive
Docs tests, source inventories, API/playground generation, browser checks and
immutable history verification. The Publishing gate verifies evidence from
the required Full run before deployment. A push to Docs `main` does not publish.
The [portal CI guide](https://github.com/OpenTLV/opentlv-docs#ci-and-versioned-publication)
owns exact workflow and evidence requirements.

## Find the owning tests

| Owner | Scope and detailed guidance |
| --- | --- |
| Core | Native contracts and executable examples: [Core quality gates](quality-gates.md), [ABI compatibility](abi-compatibility.md), [fuzzing](fuzzing.md) and [Valgrind](valgrind.md). |
| CLI | Command behavior and dependency integration: [CLI development](../cli/development.md) and [release checks](../cli/releases.md). |
| Lua | Binding API and native dependency: [tests and CI](../lua/testing.md) and [quality gates](../lua/quality-gates.md). |
| Python | Extension, facade and packaging: [Python quality gates](../python/quality-gates.md). |
| Rust | Safe API, FFI layout and native linking: [Rust tests and CI](../rust/quality-gates.md). |
| Go | Public facade, private cgo bridge and external module consumption: [Go tests and CI](../go/development/ci.md). |
| WebAssembly | Tests documented in the Core-hosted [WebAssembly guide](webassembly.md). |
| Portal | Assembly, links, navigation, source provenance, generated-reference integration, browser UI and immutable snapshots: [validation and scope](https://github.com/OpenTLV/opentlv-docs#validation-and-scope). Docs does not run Core CTest or replace component behavioral suites. |
| Workspace | Cross-repository integration smoke and selected dependency provenance: [workspace integration guide](https://github.com/OpenTLV/opentlv-workspace/blob/main/docs/integration.md). Component suites remain with their owners. |

## Performance and recorded evidence

Current Query procedures remain in [adversarial verification](query-adversarial.md)
and the [release checklist](query-release.md). The
[indefinite-boundary follow-up](indefinite-boundary-reuse.md) is a planning document.

The [historical archive](history.md) preserves Reader decode measurements,
C++ facade performance results, the Query phase audit and language migration
validation. Read each record's revision, platform and configuration before using
its results; historical evidence is not a fresh run.

Report local, hosted and release validation separately. For hosted evidence,
identify the repository, tested commit, run and attempt, configuration and
artifacts. An unrun or unsupported check remains explicit; documentation links
and source selection alone are not runtime compatibility evidence.
