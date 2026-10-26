# Architecture

The [Core architecture overview](../../concepts/architecture.md) is the
canonical source for OpenTLV's architecture. Start there for the dependency
direction and implemented contracts; this page routes contributors to their
owners rather than defining another architecture.

## Find the boundary you are changing

| Area | Responsibility and canonical explanation |
| --- | --- |
| Core execution | The [processing pipeline](../../concepts/processing-pipeline.md) explains Reader, Writer, structural events and traversal; the [architectural rules](../../concepts/architectural-rules.md) constrain changes. |
| Formats | The [Format and Element contract](../../concepts/format-contract.md) defines framing and preservation. [Definition boundaries](../../concepts/definition-boundaries.md) separate identifier meaning from format operations. Protocol policy stays with the relevant format or standard. |
| Document | The [Document guide](../../guides/document.md) owns the mutable, owned message representation and its storage/lifetime contract. Document is not a wire format or the planned runtime model. |
| Query | The [Query language contract](../../concepts/query-language.md) and [Query guide](../../guides/queries.md) describe selection and execution over the shared model. |
| Schema and Codec | [Schemas](../../guides/schemas.md) describe structural and value constraints; [codecs](../../guides/codecs.md) convert Value bytes and application representations. They are optional capabilities, not mandatory processing stages. |
| Language bindings | The [binding contracts](../../concepts/bindings.md) describe facades over the canonical C engine. C++ remains Core-owned; [language overviews](../../bindings/index.md) lead to each implementation and manual. |
| Tools | The [Tools catalog](../../tools/index.md) identifies the CLI, playground and planned imtlv. CLI behavior belongs to its repository; the portal owns the playground UI, `opentlv-js` owns its JavaScript binding, and Core owns native processing. |

## Current implementation and planned work

The architecture overview explicitly separates the existing execution foundation
from [planned runtime and compiled models](../../concepts/architecture.md#planned-runtime-and-compiled-models).
The [runtime model and canonical IR](../../concepts/runtime-model.md) is design
documentation for that planned work, not an available parsing mode. Check the
[implemented capabilities](../../formats/support.md) and the selected binding's
manual before assuming an API is exposed.

Preserve the [failure model](../../concepts/error-model.md), ownership and
continuation contracts when changing a component. Update the owning technical
source and its examples with the implementation; use the
[contribution entry points](../contributing.md) to find the repository.
