# Contributing

Start in the repository that owns the behavior or documentation you want to
change. The [documentation ownership and portal conventions](documentation.md)
explain where a change belongs; the [architecture entry point](architecture/index.md)
links the shared contracts that contributors must preserve.

## Repository entry points

| Repository | Contribution guidance |
| --- | --- |
| Core | [CONTRIBUTING](https://github.com/OpenTLV/opentlv/blob/main/CONTRIBUTING.md), [repository instructions](https://github.com/OpenTLV/opentlv/blob/main/AGENTS.md), and the selected [development workflow](workflow.md). Includes native API documentation, examples, source conventions and Core validation. |
| CLI | [CONTRIBUTING](https://github.com/OpenTLV/opentlv-cli/blob/main/CONTRIBUTING.md) and [CLI development](../cli/development.md). |
| Lua | [Implementation and ownership](../lua/implementation.md), [development](../lua/development.md), and [tests](../lua/testing.md). |
| Python | [CONTRIBUTING](https://github.com/OpenTLV/opentlv-python/blob/main/CONTRIBUTING.md) and the [build, workspace and contribution guide](../python/development/python.md). |
| Go | [Issues](https://github.com/OpenTLV/opentlv-go/issues) and the [standalone development guide](../go/development/go.md). |
| Rust | [Issues](https://github.com/OpenTLV/opentlv-rust/issues) and the [build, features and contribution guide](../rust/development/rust.md#contributing). |
| Portal | The [portal README](https://github.com/OpenTLV/opentlv-docs#readme) owns site setup, validation and operations. Follow the [portal documentation conventions](documentation.md) and [product registration convention](product-catalogs.md). |
| Workspace | The [workspace repository](https://github.com/OpenTLV/opentlv-workspace) owns shared editor configuration, bootstrap and integration orchestration. |

Repository policy links above target current development on `main`. Manuals
assembled into this portal describe the selected source revisions; consult the
target branch's policies when preparing a contribution.

## Prepare a change

1. Read the owning repository's contribution rules and relevant technical
   contract. WebAssembly changes follow Core's rules as well as its component
   guide; Go changes follow the standalone Go repository's rules.
2. Change implementation, examples and technical documentation together in the
   owning repository. Keep Core C/C++ API comments and Doxygen inputs in Core;
   the portal integrates their generated output.
3. Run the owner's relevant tests and checks. For changes spanning repositories,
   record dependency revisions and validate the integration separately.
4. Describe what changed and the actual validation scope in the pull request.
   Follow the owner's changelog and review conventions. A local pass does not
   establish hosted CI or release readiness.

Use [Testing and Quality Gates](testing.md) to choose validation and
[CI and Release Process](releases.md) to understand the later publication steps.
