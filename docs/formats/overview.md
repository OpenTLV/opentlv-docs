# Formats

Choose the wire representation used by your input. OpenTLV supports the generic
configurations and protocol subsets below. A supported Format reads and writes
binary framing; it does not imply a complete protocol stack or automatic
validation of every Value.

## Choose a format

All entries below are implemented. **Partial** describes the supported subset
of a wider standard, not a future implementation. Generic configurations are
always built; protocol presets require their corresponding Core build option.
The [capability inventory](support.md) records native components and language
availability. Choose a language through [Bindings](../bindings/index.md).

### Generic configurations

These are application-defined wire representations with no external protocol
standard. Their rules are defined by the linked OpenTLV configuration contracts.

| Format and detailed guide | Description / specification | Supported capabilities | Limits |
| --- | --- | --- | --- |
| [Fixed-width TLV](fixed/configurable.md) | Fixed identifier and count widths; OpenTLV Fixed contract | TLV or LTV ordering, either byte order, Value or Tag-plus-Value length | Length field is 1–8 bytes; configuration lifetime and native buffer bounds apply |
| [Variable-width TLV](variable.md) | Inline/continuation identifiers and short/long counts; OpenTLV Variable contract | Configurable masks, byte order and declarative field policies | Definite generic lengths; concrete termination and protocol semantics are separate |
| [Packed Tag/Length](packed.md) | Bit fields sharing a header; OpenTLV Packed contract | 1–8-byte header, canonical Tags, explicit length scope | Immutable complete Tag table; large Tag spaces need impractical storage; no generic reserved-bit validation |
| [Escaped lengths](escaped.md) | Fixed identifiers and escape-prefixed counts; OpenTLV Escaped contract | Configurable marker, count width, byte order and tag-only identifiers | Caller applies protocol termination and padding; NFC's limits belong to its preset |

[Custom Format callbacks](custom/README.md) are the extension point for other
representations. They are not an additional supplied protocol implementation.
See the [generic capability space](../concepts/format-capabilities.md) before
designing application-specific framing.

### Protocols and standards

Each linked guide preserves the wire examples, diagrams, validation contracts
and detailed limitations maintained by Core.

| Format and detailed guide | Description / standard | Supported capabilities | Partial support and limitations |
| --- | --- | --- | --- |
| [BER-TLV](asn1/ber.md) | ASN.1 Basic Encoding Rules; ITU-T X.690 | Multi-byte identifiers, definite lengths, constructed indefinite lengths and EOC scanning; ASN.1 Value codecs | No ASN.1 notation compiler or complete protocol; framing does not interpret payloads |
| [DER-TLV](asn1/der.md) | ASN.1 Distinguished Encoding Rules; ITU-T X.690 | Minimal definite framing; recursive structural validation; strict universal Values; schema-aware supported type subset | Generic I/O checks current framing only; full type/time/schema conformance is limited to the documented subset |
| [CER-TLV](asn1/cer.md) | ASN.1 Canonical Encoding Rules; ITU-T X.690 | Constructed indefinite framing; recursive EOC and canonical string segmentation checks; strict universal Values | Generic I/O is not recursive canonical validation; schema constraints and SET/SET OF ordering are not implemented |
| [EMV](../standards/emv/README.md) | Contact Book 3 data objects; EMV Book 3 | Framing, contextual dictionaries, selected FCI/Application/GPO structural rules, codecs and Data Object Lists | Supported dictionary and validation subset; no payment kernel or transaction state machine |
| [Bluetooth LTV](bluetooth/README.md) | Advertising Data structures; Bluetooth Core GAP / Supplement | Length-before-Type framing, AD definitions, container/schema checks and selected Value codecs | At most 254 Value bytes; no radio stack or arbitrary GATT model |
| [LLDP](lldp/README.md) | Link Layer Discovery Protocol; IEEE 802.1AB-2016 | Packed 7-bit Type / 9-bit Length, base definitions, LLDPDU structure and Value codecs | At most 511 Value bytes; no Ethernet agent or MIB; [full-edition normative audit remains pending](lldp/conformance.md) |
| [DHCPv4 options](dhcp/README.md) | Option framing; RFC 2132 | One-byte codes/counts, tag-only Pad/End, selected definitions and generic Value codecs | At most 255 Value bytes; caller handles termination; no fragment joining, overload, nested suboptions or DHCPv6 |
| [NFC Type 2](nfc/README.md) | TLV data-area framing; NFC Forum Type 2 Tag Operation Specification 1.1 §2.3 | Short/escaped lengths, NULL/Terminator and opaque Values | At most 65534 Value bytes; contiguous stream only; no NDEF interpretation or physical memory mapping |

## Shared operations

The [Core format guide](README.md) preserves the detailed comparison tables,
read/write examples, traversal and generic interface contract. Those operations
are shared across formats; the format pages explain their particular wire rules.
Use [Reader](../guides/reader.md), [Writer](../guides/writer.md) or
[Document](../guides/document.md) according to your task, and follow the
[shared memory ownership rules](../guides/memory.md).

## Planned formats and extensions

The [candidate catalogue](format-catalogue.md) and
[format roadmap](format-roadmap.md) contain research, proposals and remaining
work. An entry there is not evidence of an available parser, encoder or
protocol validator. The implemented inventory above and each detailed guide's
supported scope define what is currently available.
