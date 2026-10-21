# OpenTLV

OpenTLV reads, writes and inspects binary data organized into tagged values.
Use it to traverse protocol records, build messages, or parse data into an
editable document. A shared C engine supplies the processing contracts;
language APIs and tools provide different ways to use them.

**New to OpenTLV? [Start with a small input](getting-started/overview.md).**
The learning path explains TLV, walks through a first element and document,
and helps you choose a format, language or command-line workflow.

## Formats and capabilities

OpenTLV provides configurable fixed-width and variable-width formats, packed
Tag/Length headers, and support for BER, DER, CER, EMV, LLDP, NFC Type 2,
DHCPv4 options and Bluetooth advertising data. These cover TLV and related
layouts such as length-before-type records.

Start with [Formats](formats/overview.md) to choose the wire layout. Consult
[implemented capabilities](formats/support.md) for the scope of framing,
validation, definitions and value codecs. A format's presence does not imply
complete protocol semantics or the same feature coverage in every binding.

## Choose your entry point

| What you want to do | Start here |
| --- | --- |
| Understand TLV and complete a first task | [Getting Started](getting-started/overview.md) |
| Choose a wire representation or protocol | [Formats](formats/overview.md) |
| Use C, C++, Python, Lua, Rust, Go or WebAssembly | [Bindings](bindings/index.md), including capability and experimental-status guidance |
| Inspect data in a terminal or explore it in a browser | [Tools](tools/index.md): the `otlv` CLI and TLV playground |
| Build, test or contribute to a component | [Development](development/index.md) |

For runnable programs, use the [executable examples](guides/examples.md).
For exact declarations, use the [C and C++ reference](reference/README.md);
each product manual owns its language or command-line API.

## Project information

Check [language coverage](concepts/bindings.md), [compiler requirements](reference/compilers.md)
and [component selection](guides/select-components.md) before integrating.
The [runtime model](concepts/runtime-model.md) and
[Core roadmap](https://github.com/OpenTLV/opentlv/blob/main/ROADMAP.md)
distinguish future plans from implemented behavior.

See the Core [changelog](https://github.com/OpenTLV/opentlv/blob/main/CHANGELOG.md),
[security policy](https://github.com/OpenTLV/opentlv/blob/main/SECURITY.md)
and [license](https://github.com/OpenTLV/opentlv/blob/main/LICENSE)
for project policies and release history.
