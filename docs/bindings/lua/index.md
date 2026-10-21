# Lua

The `opentlv` module provides Lua access to TLV Readers, Writers, tree writing,
Schema, Query and owned Documents. Check the manual for operations that remain
unbound.

- **Language:** Lua and LuaJIT; supported runtimes and build requirements belong
  to the [selected installation guide](../../lua/development.md).
- **Status:** available as an experimental standalone binding, built for the
  Lua runtime that will load it.
- **Owner:** [opentlv-lua](https://github.com/OpenTLV/opentlv-lua).

## Installation and first use

Follow [Lua build and installation](../../lua/development.md), including the
[LuaRocks instructions](../../lua/development.md#luarocks-installation).
The [manual setup](../../lua/api.md#setup) links a runnable quick start and
shows how to load the module.

The [Lua versioning guide](../../lua/versioning.md) owns runtime version
inspection, package metadata and release identity.

## Detailed documentation

Use the [Lua manual](../../lua/api.md) for API contracts and examples and
[implementation notes](../../lua/implementation.md) for ownership and limitations.
These pages are selected from the binding repository and use a separate menu.

Independent Lua releases use `/lua/<version>/`, relative to the documentation
site root, as described by the [owner's release guide](../../lua/releases.md).
The selected manual above remains accessible without a matching published release;
a portal version is not a Lua binding release number.

[All languages](../index.md)
