# Escaped lengths

## Overview

Escaped is an implemented generic configuration for fixed-width identifiers and
short or escape-prefixed lengths. It is available independently of the NFC
preset and does not select a protocol. The technical explanation remains in
Core's [generic composition guide](nfc/README.md#generic-composition).

## Format structure

For field composition, ordering, count scope and tag-only configuration, use the
[Core Format declaration](https://github.com/OpenTLV/opentlv/blob/main/tlv/include/tlv/formats/escaped.h)
and [generic composition guide](nfc/README.md#generic-composition).

## Encoding rules

The owner-maintained
[Length declaration](https://github.com/OpenTLV/opentlv/blob/main/tlv/include/tlv/field/escaped.h)
defines marker, count and byte-order rules. The separate
[NFC length encoding](nfc/README.md#length-encoding) describes the protocol preset.

## Supported capabilities

Consult [generic composition](nfc/README.md#generic-composition) for capability
and build-option details, then use the shared [Reader](../guides/reader.md) and
[Writer](../guides/writer.md) guides for processing operations.

## Examples

The Core-owned [NFC example and corpus](nfc/README.md#example) demonstrate the
preset and document the example's validation boundaries.

## Limitations

The [Format contract](https://github.com/OpenTLV/opentlv/blob/main/tlv/include/tlv/formats/escaped.h)
owns configuration lifetimes and tag-only restrictions. Read it together with
the [generic composition boundaries](nfc/README.md#generic-composition) before
applying protocol policy. This portal entry routes to those contracts rather
than maintaining another copy of their technical rules.

## References

This is the OpenTLV Escaped contract, not a separate external standard:
[Format configuration](https://github.com/OpenTLV/opentlv/blob/main/tlv/include/tlv/formats/escaped.h),
[Length encoding](https://github.com/OpenTLV/opentlv/blob/main/tlv/include/tlv/field/escaped.h)
and [shared Format concepts](../concepts/format-capabilities.md).
