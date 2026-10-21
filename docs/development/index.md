# Development

Start with the documentation owned by the component you want to change.
The portal organizes the entry points; each repository maintains its technical
contracts, build instructions and release evidence.

## Architecture

Read the [architecture overview](../concepts/architecture.md),
[processing pipeline](../concepts/processing-pipeline.md) and
[architectural rules](../concepts/architectural-rules.md) before changing Core.
The [runtime model](../concepts/runtime-model.md) distinguishes planned work
from the existing implementation.

## Building from source

Use [Core installation and developer builds](../getting-started/core-build.md)
for distribution archives, C-only builds and tests. The
[first-program guide](../getting-started/README.md) covers the initial build
and consuming the library. Check [compiler support](../reference/compilers.md)
and [component selection](../guides/select-components.md) for build constraints.
Use the owner-maintained [CLI](../cli/development.md),
[Lua](../lua/development.md) and [Python](../python/development/python.md)
guides for those products.

## Contributing

Follow the [Core development workflow](workflow.md) and the contribution
instructions in the relevant product guide. The
[documentation layout](documentation-layout.md) and
[ownership guide](documentation-ownership.md) describe where technical sources
belong. The [portal repository](https://github.com/OpenTLV/opentlv-docs) owns
site assembly, navigation and presentation.
Follow [Register a binding or tool](product-catalogs.md) when adding product
overviews or changing catalog availability.

## Testing and quality gates

Core's [quality gates](quality-gates.md), [ABI checks](abi-compatibility.md),
[fuzzing](fuzzing.md) and [Valgrind guide](valgrind.md) cover native validation.
The [Lua](../lua/quality-gates.md) and [Python](../python/quality-gates.md)
manuals define their own test scope and evidence.

## CI and release process

Use the [Core quality gates](quality-gates.md) and
[Query release checklist](query-release.md) for Core work. Product release
instructions remain in the [CLI](../cli/releases.md),
[Lua](../lua/releases.md) and [Python](../python/releases.md) manuals.
The [portal operations guide](https://github.com/OpenTLV/opentlv-docs#readme)
describes documentation CI and publication.
