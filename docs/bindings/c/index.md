# C

The native C API is OpenTLV's canonical engine for reading, writing and
processing TLV data, including Query, Schema and owned Documents.

- **Language:** C99 or newer.
- **Status:** available as part of Core; enabled capabilities depend on the build.
- **Owner:** [OpenTLV Core](https://github.com/OpenTLV/opentlv), including all
  technical guides and generated C reference.

## Installation and first use

Follow [Core build and installation](../../getting-started/core-build.md) and
[application integration](../../getting-started/README.md). The
[C first program](../../getting-started/README.md#quick-start) writes and reads
one element and includes the complete runnable source and expected output.

## Detailed documentation

Shared operations and native references are organized under [API](../../api/index.md).

Start with [Reader](../../guides/reader.md), [Writer](../../guides/writer.md)
or [Document](../../guides/document.md), then use the
[C API reference](../../reference/c-api.md) for declarations. Check
[memory and lifetime contracts](../../guides/memory.md) and
[component selection](../../guides/select-components.md) for integration constraints.

[All languages](../index.md)
