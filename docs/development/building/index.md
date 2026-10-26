# Building from Source

Choose the repository you want to develop. Each owner maintains its prerequisites,
commands and supported configurations; building one component does not require
building the complete ecosystem.

| Target | Start here |
| --- | --- |
| Core C/C++ | [First build and CMake integration](../../getting-started/README.md), then [Core installation and developer builds](../../getting-started/core-build.md) for archives, C-only builds and tests. Check [compiler support](../../reference/compilers.md) and [component selection](../../guides/select-components.md). |
| otlv CLI | [CLI development](../../cli/development.md) owns the standalone executable's build and selected Core dependency. |
| Lua | [Lua build and installation](../../lua/development.md) owns Lua/LuaJIT setup and the native dependency. |
| Python | [Python build and workspace guide](../../python/development/python.md) owns extension builds, packaging and contributor setup. |
| Rust | [Rust build, features and contribution guide](../../rust/development/rust.md) owns Cargo builds, the pinned Core dependency and local workspace development. |
| Go | [Go development](../../go/development/go.md) owns standalone builds, cgo linking and the pinned native Core dependency. |
| JavaScript | The [JavaScript build guide](../../bindings/javascript/index.md) covers the standalone binding and its Emscripten toolchain. [Playground builds](https://github.com/OpenTLV/opentlv-docs#playground-builds) describes its integration into the portal UI. |
| Documentation portal | The portal README owns [prerequisites](https://github.com/OpenTLV/opentlv-docs#prerequisites), [setup](https://github.com/OpenTLV/opentlv-docs#setup), [build and preview](https://github.com/OpenTLV/opentlv-docs#build-and-preview), and [API reference generation](https://github.com/OpenTLV/opentlv-docs#generate-or-consume-api-references). |

The optional [multi-repository workspace](https://github.com/OpenTLV/opentlv-workspace)
provides editor and checkout coordination. Repository-owned instructions above
remain authoritative for each component's build.

## Select dependencies deliberately

Follow the component's dependency-selection instructions and keep the selected
Core revision and configuration visible in validation results. A local sibling
checkout can differ from a reviewed dependency pin.

The documentation portal assembles the revisions selected in its source
manifest. Its [local preview mode](https://github.com/OpenTLV/opentlv-docs#revision-selection-and-local-changes)
can include workspace changes, but is not a reproducible release build and cannot
authorize publication. Continue with [Testing and Quality Gates](../testing.md)
after building the component you changed.
