# Lua

The `opentlv` module provides Lua access to TLV Readers, Writers, tree writing,
Schema, Query and owned Documents. Check the manual for operations that remain
unbound.

- **Language:** Lua 5.1–5.4 and LuaJIT.
- **Status:** available as an experimental standalone binding, built for the
  Lua runtime that will load it.
- **Owner:** [opentlv-lua](https://github.com/OpenTLV/opentlv-lua).

## Installation and first use

Follow [Lua build and installation](../../lua/development.md), including the
[LuaRocks instructions](../../lua/development.md#luarocks-installation).
The [manual setup](../../lua/api.md#setup) links a runnable quick start and
shows how to load the module.

After installation, check the binding version:

```lua
local opentlv = require("opentlv")

print(opentlv.version())
```

## Detailed documentation

Use the [Lua manual](../../lua/api.md) for API contracts and examples and
[implementation notes](../../lua/implementation.md) for ownership and limitations.
These pages are selected from the binding repository and use a separate menu.

Independent Lua documentation at `/lua/`, relative to the documentation site
root, is not available yet. Use the selected manual above without requiring a
matching release; a portal version is not a Lua binding release number.

[All bindings](../index.md)
