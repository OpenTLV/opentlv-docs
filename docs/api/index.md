# API

Use the shared OpenTLV model, processing operations and native reference from
this section. Core maintains the technical contracts linked below; language
manuals document their own interfaces and coverage. For a first working program,
start with [Tutorials](../getting-started/overview.md). Choose an interface through
[Languages](../bindings/index.md) and a protocol through
[Standards](../formats/overview.md).

## Public model and contracts

The [canonical conceptual model](../concepts/architecture.md#conceptual-model)
defines the responsibilities of Definition, Format, Layout and Element. These
are conceptual boundaries, not a promise of one public API type for each name.

| Concept | Canonical contract |
| --- | --- |
| Definition | [Definition boundaries](../concepts/definition-boundaries.md) explain identifier/name registries and their separation from protocol dictionaries. |
| Format | The [Format and Element contract](../concepts/format-contract.md) owns wire decoding, encoding and preservation; [generic configurations](formats.md) introduce available framing mechanisms. |
| Layout | [Semantic content and source](../concepts/format-contract.md#semantic-content-and-source) describes source ranges and framing alongside the decoded Element. |
| Element | [Core types](../concepts/core-types.md) explain the semantic identifier and Value, with [borrowed values](../concepts/value.md), [logical lengths](../concepts/length.md) and [byte order](../concepts/endian.md). |

Use the [memory and lifetime contracts](../guides/memory.md) when retaining
borrowed data, copying it or moving between owned and borrowed representations.
The [copy helpers](../guides/copy.md) distinguish content copying from preserving
encoded source bytes.

## Processing operations

| Operation | Guide |
| --- | --- |
| Reader | [Read and traverse elements](../guides/reader.md). |
| Writer | [Write elements and construct nested values](../guides/writer.md). |
| Document | [Own, edit and encode a message tree](../guides/document.md). |
| Query | [Select elements](../guides/queries.md), with the [Query language contract](../concepts/query-language.md). |
| Schema | [Apply structural and value constraints](../guides/schemas.md). |
| Codec | [Convert Value bytes and application representations](../guides/codecs.md). |

[Choose a processing API](../guides/processing.md) compares these workflows.
Their availability in each language is recorded in the
[language contracts and capability matrix](../concepts/bindings.md).

## Diagnostics, configuration and reference

Use [diagnostics](../guides/diagnostics.md) and the
[error-code reference](../reference/errors.md) for failures. Choose reusable wire
mechanisms in [Generic formats](formats.md), then consult the
[shared format operations](../formats/README.md). The
[implemented capability inventory](../formats/support.md) and
[component selection guide](../guides/select-components.md) identify build options.

The [native reference overview](../reference/README.md) leads to the generated
[C API](../reference/c-api.md) and [C++ API](../reference/cxx-api.md), maintained
from Core's public declarations. Their location in API does not create an
independent reference owner or release.

For implementation architecture, planned runtime work and contributor guidance,
continue with [Development](../development/index.md).
