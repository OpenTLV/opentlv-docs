# Historical records

These records preserve migration provenance, dated validation and performance
results. Use them to investigate the recorded revision or reproduce that work;
they do not establish the behavior or release readiness of a new source selection.

The original technical content, source ownership, anchors and supporting evidence
remain available. Historical pages are grouped here and omitted from normal
search results so that current manuals lead users to current instructions.
Their source repositories and previously published release snapshots are unchanged.

<!-- opentlv-content: history -->

Each record keeps its original logs, inventories and provenance links. A successful
historical check is evidence for its recorded inputs, not for a current release.

The [Go migration baseline](https://github.com/OpenTLV/opentlv/tree/ec077a7eee7f59110c7b768acbb50015d86ab9df/docs/development/go-migration)
freezes the pre-extraction implementation and native linking configurations.
Core #686 removes those records and the old Go manuals from the current tree;
the immutable Git revision retains their inventory, results and source history.
Older selected Core revisions still expose their original archive pages here.
Historical evidence does not establish current standalone build or release readiness.

The [WASM migration baseline](https://github.com/OpenTLV/opentlv/tree/5002c686efc49574c33de3ce3b714162f02e4632/docs/development/wasm-migration) records the original Core implementation, toolchain,
exports and local reproducibility evidence for the JavaScript extraction. Its
inventory and validation results describe that immutable baseline; follow the
[WebAssembly guide](../bindings/wasm/index.md) for the selected source's build instructions.
Core #698 removes the old manual and baseline from the current tree; this
immutable Git revision and previously published snapshots retain the evidence.

## Review decisions

The [content disposition review](https://github.com/OpenTLV/opentlv-docs/blob/main/DOCUMENTATION-CONTENT-REVIEW.md)
accounts for every page in the reviewed assembly and explains each relocation
and archival decision. Planned work remains in Development planning; current
test and release procedures remain in [component guides](components.md) and
[Testing and Quality Gates](testing.md).
