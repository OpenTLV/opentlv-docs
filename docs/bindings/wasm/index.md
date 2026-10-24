# WebAssembly

The standalone WebAssembly build exposes Core to JavaScript tooling for
parsing, compiled Query, Document editing and contextual Schema validation.

- **Language/environment:** JavaScript with a WebAssembly module built by Emscripten.
- **Status:** experimental standalone binding; private package preparation, no published npm package.
- **Owner:** [OpenTLV JavaScript / WebAssembly](https://github.com/OpenTLV/opentlv-js).

## Installation and first use

Follow the [WebAssembly build guide](../../js/webassembly.md#build)
for the SDK, generated module and browser integration. To explore bytes without
building an application, use the [playground overview](../../tools/playground/overview.md).

## Detailed documentation

The [WebAssembly manual](../../js/webassembly.md) owns build commands,
API usage and constraints. Check the [capability matrix](../../concepts/bindings.md)
for remaining facade gaps. The [private package guide](../../js/packaging.md)
owns the independent JS package version and its distinction from embedded Core.
This manual follows the portal-selected JS commit; no independent JS documentation
release is selected. Node is the validated runtime; browser/worker runtime
coverage is not established by the standalone CI.

[All languages](../index.md)
