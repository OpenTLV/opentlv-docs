# Bindings

Choose a language interface, then open its overview for setup and documentation.
Availability below describes the sources selected for this portal version;
experimental interfaces do not promise the same coverage as the native APIs. The
[language contracts and capability matrix](../concepts/bindings.md) describe
which operations each binding exposes and the shared C boundary.

| Interface | Purpose | Availability |
| --- | --- | --- |
| [C](c/index.md) | Native engine and public C API | Available in Core |
| [C++](cpp/index.md) | C++ facade over the C engine | Available in Core |
| [Python](python/index.md) | Python objects and iterators | Available; experimental standalone binding |
| [Lua](lua/index.md) | Lua module for scripts and embedded applications | Available; experimental standalone binding |
| [Rust](rust/index.md) | Safe Rust API over the C library | Available; experimental in-tree binding |
| [Go](go/index.md) | Go types, slices and errors | Available; experimental in-tree binding |
| [WebAssembly](wasm/index.md) | JavaScript access to Core in the browser | Available; experimental optional Core build |

C and C++ share the [memory and lifetime contracts](../guides/memory.md),
[diagnostics](../guides/diagnostics.md), [Query](../guides/queries.md),
[Schema](../guides/schemas.md) and [Codec](../guides/codecs.md) guides.
These technical manuals and generated references are maintained by Core.

## Product manuals and versions

Python and Lua maintain their own manuals and release schedules. The manual
links on their overview pages open the exact source selected for this portal version, with
product-specific navigation and a return link to the portal. Independent
publication reserves `/python/` and `/lua/`, relative to the documentation site
root. Those entries are not available yet; use the selected manuals, which
remain accessible without requiring a matching product release.

## Catalog maintenance

Follow the [product registration convention](../development/product-catalogs.md)
to add an interface or update its status. Catalog entries introduce products;
API references, limitations and tutorials remain with their technical owners.
