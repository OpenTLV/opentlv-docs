# WebAssembly

The optional WebAssembly build exposes Core to JavaScript browser tooling for
parsing, compiled Query, Document editing and contextual Schema validation.

- **Language/environment:** JavaScript with a WebAssembly module built by Emscripten.
- **Status:** available as an experimental optional Core build, disabled by default.
- **Owner:** [Core's WebAssembly binding](https://github.com/OpenTLV/opentlv/tree/main/bindings/wasm).

## Installation and first use

Follow the [WebAssembly build guide](../../development/webassembly.md#build)
for the SDK, generated module and browser integration. To explore bytes without
building an application, use the [playground overview](../../tools/playground/overview.md).

## Detailed documentation

The [WebAssembly manual](../../development/webassembly.md) owns build commands,
API usage and constraints. Check the [capability matrix](../../concepts/bindings.md)
for remaining facade gaps. There is no separate product manual version selector
for this in-tree binding.

[All bindings](../index.md)
