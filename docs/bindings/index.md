# Languages

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
| [Rust](rust/index.md) | Safe Rust API over the C library | Available; experimental standalone binding |
| [Go](go/index.md) | Go types, slices and errors | Available; experimental standalone binding |
| [WebAssembly](wasm/index.md) | JavaScript access to Core in the browser | Available; experimental optional Core build |

C and C++ share the [memory and lifetime contracts](../guides/memory.md),
[diagnostics](../guides/diagnostics.md), [Query](../guides/queries.md),
[Schema](../guides/schemas.md) and [Codec](../guides/codecs.md) guides.
These shared contracts and the [C/C++ native references](../reference/README.md)
are available through [API](../api/index.md) and remain maintained by Core.
Language overviews own setup routing and language-specific usage guidance.

## Product manuals and versions

Python, Lua, Rust and Go maintain their own manuals. The manual links on their
overview pages open the exact source selected for this portal version, with
product-specific navigation and a return link to the portal. Python and Lua
also have their own release schedules; independent publication reserves
`/python/` and `/lua/`, relative to the documentation site root. Publication and
release availability are described by the owners'
[Python release guide](../python/releases.md) and [Lua release guide](../lua/releases.md).
Rust has no independent documentation releases yet; see its
[packaging and versioning](../rust/packaging.md) guide.
Go likewise follows the portal-selected source revision; its
[packaging policy](../go/packaging.md) describes the independent binding version.
The selected manuals remain accessible without requiring a matching product release.

Contributor tests, implementation notes and release procedures are collected in
[Development](../development/components.md). Migration provenance and dated
validation remain available through [Historical records](../development/history.md).

## Catalog maintenance

Follow the [product registration convention](../development/product-catalogs.md)
to add an interface or update its status. Catalog entries introduce products;
API references, limitations and tutorials remain with their technical owners.
