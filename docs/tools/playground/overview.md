# TLV playground

The playground is an interactive browser interface for exploring TLV bytes.

- **Capabilities:** parse and inspect input using the Core WebAssembly engine;
  the interface exposes the operations available in its matching module.
- **Status:** the interface is available in the portal. Parsing requires the
  matching WebAssembly assets; the application reports when they are unavailable.
- **Owner:** the portal maintains the interface; Core maintains the WebAssembly API.

## Access and documentation

[Open the TLV playground](../../playground/index.md). No native installation is
needed to use a deployed build with its WebAssembly module. Local documentation
previews may lack that module.

The [Standards catalog](../../formats/overview.md) describes protocol scope;
[generic configurations](../../api/formats.md) explain application-defined framing.
The playground exposes only the choices documented by its interface.

For module builds, integration and technical limitations, follow the
[Core WebAssembly guide](../../development/webassembly.md). Portal contributors
can use the [portal operations guide](https://github.com/OpenTLV/opentlv-docs#readme)
for playground maintenance.

[All tools](../index.md)
