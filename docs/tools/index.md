# Tools

Use the command-line interface for files and automation, or the browser
playground to inspect a small byte sequence interactively.

## otlv command-line interface

The [otlv manual](../cli/README.md) covers commands and examples. Use the
[TLV JSON document reference](../cli/json-schema.md) when exchanging decoded
documents, and the [CLI development guide](../cli/development.md) to build or
contribute to the tool.

The CLI manual has its own navigation and a return link to the portal. These
pages use the CLI source selected for this portal version. The
[CLI documentation entry](https://opentlv.github.io/opentlv-docs/cli/) provides
independently published versions when available; the selected manual remains
accessible here without requiring a matching CLI release.

## TLV playground

Open the [TLV playground](../playground/index.md) to parse bytes in your
browser. Its interface is maintained by the portal and uses Core's
[WebAssembly tooling](../development/webassembly.md). The playground reports
whether the required WebAssembly module is available in this build.
