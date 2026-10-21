# Generic format configurations

Choose an application-defined wire representation from the generic Core
configurations below. For protocol-specific presets, validation and limitations,
use [Standards](../formats/overview.md). Generic configurations are always built;
protocol presets require their corresponding Core build option. The
[capability inventory](../formats/support.md) records native components and
language availability.

## Generic configurations

These are application-defined wire representations with no external protocol
standard. Their rules are defined by the linked OpenTLV configuration contracts.

| Format and detailed guide | Description / specification | Supported capabilities | Limits |
| --- | --- | --- | --- |
| [Fixed-width TLV](../formats/fixed/configurable.md) | Fixed identifier and count widths; OpenTLV Fixed contract | TLV or LTV ordering, either byte order, Value or Tag-plus-Value length | Length field is 1–8 bytes; configuration lifetime and native buffer bounds apply |
| [Variable-width TLV](../formats/variable.md) | Inline/continuation identifiers and short/long counts; OpenTLV Variable contract | Configurable masks, byte order and declarative field policies | Definite generic lengths; concrete termination and protocol semantics are separate |
| [Packed Tag/Length](../formats/packed.md) | Bit fields sharing a header; OpenTLV Packed contract | 1–8-byte header, canonical Tags, explicit length scope | Immutable complete Tag table; large Tag spaces need impractical storage; no generic reserved-bit validation |
| [Escaped lengths](../formats/escaped.md) | Fixed identifiers and escape-prefixed counts; OpenTLV Escaped contract | Configurable marker, count width, byte order and tag-only identifiers | Caller applies protocol termination and padding; NFC's limits belong to its preset |

[Custom Format callbacks](../formats/custom/README.md) are the extension point for other
representations. They are not an additional supplied protocol implementation.
See the [generic capability space](../concepts/format-capabilities.md) before
designing application-specific framing.

## Shared operations and configuration

The [Core format guide](../formats/README.md) preserves detailed comparison
tables, read/write examples, traversal and the generic interface contract.
Follow the [Format and Element contract](../concepts/format-contract.md) for
encoding and source preservation, and the [memory ownership rules](../guides/memory.md)
for storage lifetimes. The [format examples](../formats/format-examples.md)
exercise existing configurations and standards.

Use [Reader](../guides/reader.md), [Writer](../guides/writer.md) or
[Document](../guides/document.md) according to your task. Return to
[API](index.md) for shared operations, diagnostics and native references.
