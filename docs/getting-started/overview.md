# Tutorials

Start with a few bytes, then choose the API or tool that fits your task.
You can follow the steps in order or go directly to
[language setup](#choose-a-language) or [terminal inspection](#use-the-cli).
Detailed examples and API contracts remain in the linked component manuals.

## Choose a task

| Task | Existing walkthrough or example |
| --- | --- |
| Parse TLV bytes | Start with [the first program](README.md#quick-start), then follow the [Reader examples](../guides/reader.md). |
| Write TLV data | Use the [Writer guide](../guides/writer.md) for individual elements and scoped construction. |
| Edit a message | Follow the [Document guide](../guides/document.md) and [C++ Document example](../guides/cxx-examples.md#owning-document-and-query). |
| Find matching elements | Use the [Query guide](../guides/queries.md) and its existing query examples. |
| Work with a particular wire format | Run the [format examples](../formats/format-examples.md); check the [Standards catalog](../formats/overview.md) or [generic configurations](../api/formats.md) for the supported scope. |

The [executable example index](../guides/examples.md) identifies runnable
programs. Use [API](../api/index.md) for shared contracts and reference material.

## Understand TLV

TLV usually means **Tag, Length, Value**: a tag identifies a field, a length
describes its size, and the value contains its bytes. The chosen **Format**
defines how those parts appear on the wire; their order, widths and nesting
rules vary. Value bytes acquire meaning from the application or protocol.

The [basic model](../concepts/learning-model.md) uses this Fixed-format record:

```text
01 02 48 69
|  |  +---- value: two bytes, "Hi" in ASCII
|  +------- length: 2
+---------- tag: 01
```

This interpretation assumes one tag byte and one length byte. It is not a
format detector. Continue with the model's Element, Reader/Writer and Document
diagrams when you need the shared concepts behind a particular API.

## Read your first element

Choose a language below and run the existing
[first program](README.md#quick-start). It writes `Hello, world!`, then reads
the element back and prints the same text. The guide includes the exact wire
bytes, expected output, error handling and language-specific storage rules.

Reading an **Element** exposes its tag and value according to the selected
Format. The C example reads from a caller-owned buffer; its value borrows that
buffer. Keep borrowed input alive and unchanged while using it. For repeated
elements, continue with [Reader](../guides/reader.md), or your language manual's
reading example. [Memory contracts](../guides/memory.md) explain lifetimes.

## Parse and edit a document

Use a Reader when you want to inspect elements without retaining an owned
tree. Use **Document** when you need to keep data independently of the input,
change values, insert or remove nodes, then encode the result.

Follow the existing [Document guide](../guides/document.md) or the
[C++ Document example](../guides/cxx-examples.md#owning-document-and-query). The workflow is:

```text
wire bytes -> parse into an owned tree -> inspect or edit nodes -> encode
```

Document copies tags and values and allocates storage. Nested parsing depends
on the Format's rules for constructed values. Parsing alone does not establish
all protocol or application semantics: add [Schema validation](../guides/schemas.md)
or [value codecs](../guides/codecs.md) when needed. Use
[Choose a processing API](../guides/processing.md) to compare borrowed traversal,
owned editing and writing; Document is optional, not a mandatory processing stage.

## Choose a format

Use [Standards](../formats/overview.md) for a protocol preset or
[generic configurations](../api/formats.md) for application-defined wire
layouts. Fixed is a small starting example; real protocol data needs its
corresponding configuration or built-in format. Check
[implemented capabilities](../formats/support.md) for each standard's supported
scope and [language coverage](../concepts/bindings.md) for access through your API.
Custom framing starts with the [Format extension guide](../formats/custom/README.md).

## Choose a language

| Language or environment | Setup and first task |
| --- | --- |
| C | [Build Core and run the first program](README.md), including CMake integration |
| C++ | [Shared first program](README.md#quick-start), then [C++ examples](../guides/cxx-examples.md) |
| Python | [Standalone Python setup and examples](../python/guides/python.md) |
| Lua | [Standalone Lua manual](../lua/api.md) and [installation](../lua/development.md) |
| Rust | [Standalone Rust setup and usage](../rust/guides/rust.md) |
| Go | [Go setup and usage](../go/guides/go.md) |
| WebAssembly | [WebAssembly integration](../development/webassembly.md); for browser exploration, use the [playground](../playground/index.md) |

The [Languages catalog](../bindings/index.md) explains the available manuals and
their versions. Check each guide's prerequisites, experimental status and
limitations; language coverage is not identical. The
[executable example index](../guides/examples.md) provides further tasks without
requiring you to learn the native C interface first.

For C/C++ integration, the first-program guide retains toolchain prerequisites,
static/shared linkage, runtime library discovery and source/installed CMake
consumption. Use [component selection](../guides/select-components.md) for a
smaller build. [Installation, archives and developer tests](core-build.md)
belong to Development.

## Use the CLI

For a first result without writing a program, follow
[the CLI's first inspection](../cli/README.md#first-inspection). It uses the
same `01 02 48 69` record above and shows the command and expected output.
Install `otlv` using the [standalone CLI build instructions](../cli/README.md#build-and-install).
The format must be supplied explicitly; the tool does not infer value semantics.

Continue with [CLI commands](../cli/README.md#commands) for files, nested data,
validation and JSON conversion, or return to [Tools](../tools/index.md).
