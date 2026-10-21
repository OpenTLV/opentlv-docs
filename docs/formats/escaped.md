# Escaped lengths

## Overview

Escaped is an implemented generic configuration for fixed-width identifiers and
short or escape-prefixed lengths. It is available independently of the NFC
preset and does not select a protocol. The technical explanation remains in
Core's [generic composition guide](nfc/README.md#generic-composition).

## Format structure

The configuration combines a fixed identifier, an escaped Length and an opaque
Value. Field order, count scope and an optional table of tag-only identifiers
are explicit configuration. See the
[Core Format declaration](https://github.com/OpenTLV/opentlv/blob/main/tlv/include/tlv/formats/escaped.h)
for the complete contract.

## Encoding rules

The escape marker, extended count width, byte order and accepted count range
belong to the configuration. NFC's short/extended boundary is one preset,
described in [NFC length encoding](nfc/README.md#length-encoding).

## Supported capabilities

The descriptor uses the shared [Reader](../guides/reader.md) and
[Writer](../guides/writer.md) operations. The
[generic composition guide](nfc/README.md#generic-composition) also describes
the shared tag-only mechanism used by NFC and DHCP. These mechanisms remain
available when `OPENTLV_NFC=OFF`.

## Examples

The [NFC example and corpus](nfc/README.md#example) exercise the existing preset,
including short and extended lengths and tag-only controls. Its NDEF bytes are
opaque Values; the example does not validate NDEF.

## Limitations

Configuration, the tag-only table and its identifier bytes are borrowed and must
outlive the descriptor and its users. Tag-only identifiers require TLV ordering,
Value-only length scope and empty Values. They do not imply skipping padding or
stopping traversal. Callers supply those policies and protocol semantics.

## References

This is the OpenTLV Escaped contract, not a separate external standard:
[Format configuration](https://github.com/OpenTLV/opentlv/blob/main/tlv/include/tlv/formats/escaped.h),
[Length encoding](https://github.com/OpenTLV/opentlv/blob/main/tlv/include/tlv/field/escaped.h)
and [shared Format concepts](../concepts/format-capabilities.md).
