# TLV playground

The playground is an interactive browser interface for exploring TLV bytes.

- **Capabilities:** parse and inspect input through the JavaScript binding to Core;
  the interface exposes the operations available in its matching binding build.
- **Status:** the interface is available in the portal. Parsing requires the
  matching JavaScript binding assets; the application reports when they are unavailable.
- **Owner:** the portal maintains the interface, `opentlv-js` maintains the JavaScript
  API and bridge, and Core maintains native parsing and processing.

## Access and documentation

[Open the TLV playground](../../playground/index.md). No native installation is
needed to use a deployed build. The JavaScript binding loads Core as a WebAssembly
module; local documentation previews may lack those generated assets.

The [Standards catalog](../../formats/overview.md) describes protocol scope;
[generic configurations](../../api/formats.md) explain application-defined framing.
The playground exposes only the choices documented by its interface.

For module builds, integration and technical limitations, follow the
[selected JavaScript guide](../../bindings/javascript/index.md). Portal contributors
can use the [portal operations guide](https://github.com/OpenTLV/opentlv-docs#readme)
for playground maintenance.

[All tools](../index.md)
