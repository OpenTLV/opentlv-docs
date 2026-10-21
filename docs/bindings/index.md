# Bindings

Choose a language API, then follow its guides and reference. The
[language contracts and capability matrix](../concepts/bindings.md) describe
which operations each binding exposes and the shared C boundary.

| Language | Start here | Detailed documentation |
| --- | --- | --- |
| C | [Getting started](../getting-started/README.md) | [Reader](../guides/reader.md), [Writer](../guides/writer.md), [Document](../guides/document.md), [C reference](../reference/c-api.md) |
| C++ | [C++ examples](../guides/cxx-examples.md) | [Public/native boundary](../concepts/cxx-native-boundary.md), [C++ reference](../reference/cxx-api.md) |
| Python | [Python manual](../python/guides/python.md) | [Build and contribution guide](../python/development/python.md) |
| Lua | [Lua manual](../lua/api.md) | [Build and installation](../lua/development.md) |

C and C++ share the [memory and lifetime contracts](../guides/memory.md),
[diagnostics](../guides/diagnostics.md), [Query](../guides/queries.md),
[Schema](../guides/schemas.md) and [Codec](../guides/codecs.md) guides.
These technical manuals and generated references are maintained by Core.

## Product manuals and versions

Python and Lua maintain their own manuals and release schedules. The manual
links above open the exact source selected for this portal version, with
product-specific navigation and a return link to the portal. Use the
[Python documentation entry](https://opentlv.github.io/opentlv-docs/python/) or
[Lua documentation entry](https://opentlv.github.io/opentlv-docs/lua/) to browse
independently published versions when available; the selected manuals remain
accessible here without requiring a matching product release.

## In-tree bindings

[Rust](../guides/rust.md), [Go](../guides/go.md) and
[WebAssembly](../development/webassembly.md) have in-tree documentation.
Consult their guides and the capability matrix for experimental status,
integration requirements and limitations.
