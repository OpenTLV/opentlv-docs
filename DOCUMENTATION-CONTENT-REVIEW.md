# Documentation content disposition review

Review for [#61](https://github.com/OpenTLV/opentlv-docs/issues/61), prepared
2026-10-21 against Docs `4bce915106be894f0c1a45ae024ed17d7313e7bb` after the
completed #62 ownership corrections. This dated review supplements the
[migration inventory](DOCUMENTATION-MIGRATION.md); it is not a second component
version or capability registry.

## Scope and disposition rules

All 129 navigable pages in the selected assembly are accounted for below:
108 Keep, 10 Relocate and 11 Archive. Two new portal entry pages provide
[component contributor guidance](docs/development/components.md) and
[historical records](docs/development/history.md), resulting in 131 pages.
There are no whole-source Remove decisions: every historical record still has
traceability, reproduction or technical value.

- **Keep:** retain the audience, technical owner and current destination.
- **Relocate:** change portal placement for eight component contributor guides
  and two active planning documents. Preserve their complete source content.
- **Archive:** retain the full body, anchors, ownership and supporting files in
  Development history, with a visible historical note and current-guide link.
  Remove these records from public product menus and ordinary search results.
- **Remove:** would require a named replacement and section-level preservation
  evidence. No reviewed whole source meets that condition.

Source paths below are immutable review inputs for components. Destinations are
relative to a portal version root. A presentation move never transfers ownership.
Previously published immutable snapshots and independent product publications
keep their existing layouts. New moved portal URLs have no compatibility aliases,
consistent with the migration policy.

## Selected source baseline

| Owner | Selected revision |
| --- | --- |
| core | `48e415d944c7e4ae6a30cff8566f0936bda7390d` |
| cli | `abd2bce09a9f25071a41d7c1f3249fd48e8a0b20` |
| lua | `ea6c937c8c7f094dae7386740e3a20574b43d703` |
| python | `d846b4ff7f2c74fbf0571a065da1d83698b6f40c` |

## Duplicate and mixed-content review

The retained Core Python guide duplicates the standalone guide from Reading
through Next step: 345 lines, 11 sections and seven fenced examples match after
normalizing only Markdown link destinations. Standalone setup already covers
the installation and version details. Archive the original Core copy intact;
the Python-owned manual remains the single active API entry point.

Shared terminology does not make the Lua, Python or CLI manuals redundant.
They document distinct conversions, buffers/userdata, exceptions, callbacks,
commands and JSON behavior. Their canonical Core-contract links remain intact.
Native C/C++ guides and language facades retain their distinct public boundaries.

Portal introductions and tutorials provide routing and short worked context,
not independent technical manuals. The #62 Escaped catalog uses Core-owned
rules. The existing DER/CER assembly retains both framing and validation source
parts with their source links; neither part is discarded as a duplicate.

Keep mixed current/historical pages intact when splitting would obscure an
active contract: Core Python coordination, layout/ownership, Query adversarial
verification/release checklists and Lua testing. Their historical sections keep
their original evidence limits. LLDP conformance limitations remain in Standards;
planned runtime work and boundary reuse remain proposals in Development.

## Page inventory

| Reviewed source | Owner | Decision | Portal destination | Justification |
| --- | --- | --- | --- | --- |
| [api/formats.md](docs/api/formats.md) | Portal | Keep | `api/formats/` | Shared public contracts, configurations or native reference; retain the canonical technical details and examples. |
| [api/index.md](docs/api/index.md) | Portal | Keep | `api/` | Shared public contracts, configurations or native reference; retain the canonical technical details and examples. |
| [assets/README.md](docs/assets/README.md) | Portal | Keep | `development/documentation/assets/` | Active contributor guidance, architecture or current portal routing; retain owner-maintained procedures. |
| [bindings/c/index.md](docs/bindings/c/index.md) | Portal | Keep | `languages/c/` | Language-specific API, setup, conversions, lifetime or versioning; shared Core semantics remain linked. |
| [bindings/cpp/index.md](docs/bindings/cpp/index.md) | Portal | Keep | `languages/cpp/` | Language-specific API, setup, conversions, lifetime or versioning; shared Core semantics remain linked. |
| [bindings/go/index.md](docs/bindings/go/index.md) | Portal | Keep | `languages/go/` | Language-specific API, setup, conversions, lifetime or versioning; shared Core semantics remain linked. |
| [bindings/index.md](docs/bindings/index.md) | Portal | Keep | `languages/` | Language-specific API, setup, conversions, lifetime or versioning; shared Core semantics remain linked. |
| [bindings/lua/index.md](docs/bindings/lua/index.md) | Portal | Keep | `languages/lua/` | Language-specific API, setup, conversions, lifetime or versioning; shared Core semantics remain linked. |
| [bindings/python/index.md](docs/bindings/python/index.md) | Portal | Keep | `languages/python/` | Language-specific API, setup, conversions, lifetime or versioning; shared Core semantics remain linked. |
| [bindings/rust/index.md](docs/bindings/rust/index.md) | Portal | Keep | `languages/rust/` | Language-specific API, setup, conversions, lifetime or versioning; shared Core semantics remain linked. |
| [bindings/wasm/index.md](docs/bindings/wasm/index.md) | Portal | Keep | `languages/wasm/` | Language-specific API, setup, conversions, lifetime or versioning; shared Core semantics remain linked. |
| [cli/README.md](https://github.com/OpenTLV/opentlv-cli/blob/abd2bce09a9f25071a41d7c1f3249fd48e8a0b20/docs/README.md) | cli | Keep | `tools/otlv/manual/` | Tool-specific commands, JSON/UI behavior or discovery; preserve the tool owner and examples. |
| [cli/development.md](https://github.com/OpenTLV/opentlv-cli/blob/abd2bce09a9f25071a41d7c1f3249fd48e8a0b20/docs/development.md) | cli | Relocate | `development/components/cli/development/` | Current component contributor testing, implementation or release procedure; move portal placement to Development while retaining public-manual links. |
| [cli/json-schema.md](https://github.com/OpenTLV/opentlv-cli/blob/abd2bce09a9f25071a41d7c1f3249fd48e8a0b20/docs/json-schema.md) | cli | Keep | `tools/otlv/manual/json-schema/` | Tool-specific commands, JSON/UI behavior or discovery; preserve the tool owner and examples. |
| [cli/releases.md](https://github.com/OpenTLV/opentlv-cli/blob/abd2bce09a9f25071a41d7c1f3249fd48e8a0b20/docs/releases.md) | cli | Relocate | `development/components/cli/releases/` | Current component contributor testing, implementation or release procedure; move portal placement to Development while retaining public-manual links. |
| [concepts/architectural-rules.md](https://github.com/OpenTLV/opentlv/blob/48e415d944c7e4ae6a30cff8566f0936bda7390d/docs/concepts/architectural-rules.md) | core | Keep | `development/architecture/architectural-rules/` | Active contributor guidance, architecture or current portal routing; retain owner-maintained procedures. |
| [concepts/architecture.md](https://github.com/OpenTLV/opentlv/blob/48e415d944c7e4ae6a30cff8566f0936bda7390d/docs/concepts/architecture.md) | core | Keep | `development/architecture/architecture/` | Active contributor guidance, architecture or current portal routing; retain owner-maintained procedures. |
| [concepts/bindings.md](https://github.com/OpenTLV/opentlv/blob/48e415d944c7e4ae6a30cff8566f0936bda7390d/docs/concepts/bindings.md) | core | Keep | `languages/contracts/` | Language-specific API, setup, conversions, lifetime or versioning; shared Core semantics remain linked. |
| [concepts/core-types.md](https://github.com/OpenTLV/opentlv/blob/48e415d944c7e4ae6a30cff8566f0936bda7390d/docs/concepts/core-types.md) | core | Keep | `api/concepts/core-types/` | Shared public contracts, configurations or native reference; retain the canonical technical details and examples. |
| [concepts/cxx-builtins.md](https://github.com/OpenTLV/opentlv/blob/48e415d944c7e4ae6a30cff8566f0936bda7390d/docs/concepts/cxx-builtins.md) | core | Keep | `languages/cpp/concepts/cxx-builtins/` | Language-specific API, setup, conversions, lifetime or versioning; shared Core semantics remain linked. |
| [concepts/cxx-formats.md](https://github.com/OpenTLV/opentlv/blob/48e415d944c7e4ae6a30cff8566f0936bda7390d/docs/concepts/cxx-formats.md) | core | Keep | `languages/cpp/concepts/cxx-formats/` | Language-specific API, setup, conversions, lifetime or versioning; shared Core semantics remain linked. |
| [concepts/cxx-native-boundary.md](https://github.com/OpenTLV/opentlv/blob/48e415d944c7e4ae6a30cff8566f0936bda7390d/docs/concepts/cxx-native-boundary.md) | core | Keep | `languages/cpp/concepts/cxx-native-boundary/` | Language-specific API, setup, conversions, lifetime or versioning; shared Core semantics remain linked. |
| [concepts/definition-boundaries.md](https://github.com/OpenTLV/opentlv/blob/48e415d944c7e4ae6a30cff8566f0936bda7390d/docs/concepts/definition-boundaries.md) | core | Keep | `development/architecture/definition-boundaries/` | Current dependency and identifier-meaning constraints remain architectural contracts despite the audit title. |
| [concepts/endian.md](https://github.com/OpenTLV/opentlv/blob/48e415d944c7e4ae6a30cff8566f0936bda7390d/docs/concepts/endian.md) | core | Keep | `api/concepts/endian/` | Shared public contracts, configurations or native reference; retain the canonical technical details and examples. |
| [concepts/error-model.md](https://github.com/OpenTLV/opentlv/blob/48e415d944c7e4ae6a30cff8566f0936bda7390d/docs/concepts/error-model.md) | core | Keep | `development/architecture/error-model/` | Implemented failure/propagation contract; correct the misleading design navigation label. |
| [concepts/field-policies.md](https://github.com/OpenTLV/opentlv/blob/48e415d944c7e4ae6a30cff8566f0936bda7390d/docs/concepts/field-policies.md) | core | Keep | `development/architecture/field-policies/` | Current field-policy ownership and reuse constraints; preserve implementation boundaries. |
| [concepts/format-capabilities.md](https://github.com/OpenTLV/opentlv/blob/48e415d944c7e4ae6a30cff8566f0936bda7390d/docs/concepts/format-capabilities.md) | core | Keep | `api/concepts/format-capabilities/` | Shared public contracts, configurations or native reference; retain the canonical technical details and examples. |
| [concepts/format-contract.md](https://github.com/OpenTLV/opentlv/blob/48e415d944c7e4ae6a30cff8566f0936bda7390d/docs/concepts/format-contract.md) | core | Keep | `api/concepts/format-contract/` | Shared public contracts, configurations or native reference; retain the canonical technical details and examples. |
| [concepts/learning-model.md](https://github.com/OpenTLV/opentlv/blob/48e415d944c7e4ae6a30cff8566f0936bda7390d/docs/concepts/learning-model.md) | core | Keep | `tutorials/concepts/learning-model/` | Task-oriented learning, workflows and owner examples remain available without copying their implementations. |
| [concepts/length.md](https://github.com/OpenTLV/opentlv/blob/48e415d944c7e4ae6a30cff8566f0936bda7390d/docs/concepts/length.md) | core | Keep | `api/concepts/length/` | Shared public contracts, configurations or native reference; retain the canonical technical details and examples. |
| [concepts/processing-pipeline.md](https://github.com/OpenTLV/opentlv/blob/48e415d944c7e4ae6a30cff8566f0936bda7390d/docs/concepts/processing-pipeline.md) | core | Keep | `development/architecture/processing-pipeline/` | Active contributor guidance, architecture or current portal routing; retain owner-maintained procedures. |
| [concepts/query-language.md](https://github.com/OpenTLV/opentlv/blob/48e415d944c7e4ae6a30cff8566f0936bda7390d/docs/concepts/query-language.md) | core | Keep | `api/query-language/` | Shared public contracts, configurations or native reference; retain the canonical technical details and examples. |
| [concepts/runtime-model.md](https://github.com/OpenTLV/opentlv/blob/48e415d944c7e4ae6a30cff8566f0936bda7390d/docs/concepts/runtime-model.md) | core | Relocate | `development/planning/runtime-model/` | Active runtime/IR proposal, not an implemented public API; keep design and diagrams under planning. |
| [concepts/value.md](https://github.com/OpenTLV/opentlv/blob/48e415d944c7e4ae6a30cff8566f0936bda7390d/docs/concepts/value.md) | core | Keep | `api/concepts/value/` | Shared public contracts, configurations or native reference; retain the canonical technical details and examples. |
| [development/abi-compatibility.md](https://github.com/OpenTLV/opentlv/blob/48e415d944c7e4ae6a30cff8566f0936bda7390d/docs/development/abi-compatibility.md) | core | Keep | `development/abi-compatibility/` | Active contributor guidance, architecture or current portal routing; retain owner-maintained procedures. |
| [development/architecture/index.md](docs/development/architecture/index.md) | Portal | Keep | `development/architecture/` | Active contributor guidance, architecture or current portal routing; retain owner-maintained procedures. |
| [development/building/index.md](docs/development/building/index.md) | Portal | Keep | `development/building/` | Active contributor guidance, architecture or current portal routing; retain owner-maintained procedures. |
| [development/contributing.md](docs/development/contributing.md) | Portal | Keep | `development/contributing/` | Active contributor guidance, architecture or current portal routing; retain owner-maintained procedures. |
| [development/cxx-facade-performance.md](https://github.com/OpenTLV/opentlv/blob/48e415d944c7e4ae6a30cff8566f0936bda7390d/docs/development/cxx-facade-performance.md) | core | Archive | `development/history/core/cxx-facade-performance/` | Recorded facade benchmark results; preserve reproduction details and current C++ contracts separately. |
| [development/documentation-audit.md](https://github.com/OpenTLV/opentlv/blob/48e415d944c7e4ae6a30cff8566f0936bda7390d/docs/development/documentation-audit.md) | core | Archive | `development/history/core/documentation-audit/` | Completed #513 audit; paths and findings describe the recorded baseline, not current portal operations. |
| [development/documentation-layout.md](https://github.com/OpenTLV/opentlv/blob/48e415d944c7e4ae6a30cff8566f0936bda7390d/docs/development/documentation-layout.md) | core | Keep | `development/documentation/layout/` | Current Core writing policy with labeled extraction context; portal conventions own current navigation. |
| [development/documentation-ownership.md](https://github.com/OpenTLV/opentlv/blob/48e415d944c7e4ae6a30cff8566f0936bda7390d/docs/development/documentation-ownership.md) | core | Keep | `development/documentation/ownership/` | Current technical ownership rules with labeled cutover evidence; preserve both scopes. |
| [development/documentation.md](docs/development/documentation.md) | Portal | Keep | `development/documentation/` | Active contributor guidance, architecture or current portal routing; retain owner-maintained procedures. |
| [development/fuzzing.md](https://github.com/OpenTLV/opentlv/blob/48e415d944c7e4ae6a30cff8566f0936bda7390d/docs/development/fuzzing.md) | core | Keep | `development/fuzzing/` | Active contributor guidance, architecture or current portal routing; retain owner-maintained procedures. |
| [development/go.md](https://github.com/OpenTLV/opentlv/blob/48e415d944c7e4ae6a30cff8566f0936bda7390d/docs/development/go.md) | core | Keep | `languages/go/manual/development/` | Language-specific API, setup, conversions, lifetime or versioning; shared Core semantics remain linked. |
| [development/indefinite-boundary-reuse.md](https://github.com/OpenTLV/opentlv/blob/48e415d944c7e4ae6a30cff8566f0936bda7390d/docs/development/indefinite-boundary-reuse.md) | core | Relocate | `development/planning/indefinite-boundary-reuse/` | Open optimization follow-up, not completed verification; retain analysis and proposed work under planning. |
| [development/index.md](docs/development/index.md) | Portal | Keep | `development/` | Active contributor guidance, architecture or current portal routing; retain owner-maintained procedures. |
| [development/product-catalogs.md](docs/development/product-catalogs.md) | Portal | Keep | `development/product-catalogs/` | Active contributor guidance, architecture or current portal routing; retain owner-maintained procedures. |
| [development/python.md](https://github.com/OpenTLV/opentlv/blob/48e415d944c7e4ae6a30cff8566f0936bda7390d/docs/development/python.md) | core | Keep | `development/bindings/python/` | Core still owns vocabulary generation, native fixtures and dependency coordination; standalone setup remains linked. |
| [development/quality-gates.md](https://github.com/OpenTLV/opentlv/blob/48e415d944c7e4ae6a30cff8566f0936bda7390d/docs/development/quality-gates.md) | core | Keep | `development/quality-gates/` | Active contributor guidance, architecture or current portal routing; retain owner-maintained procedures. |
| [development/query-adversarial.md](https://github.com/OpenTLV/opentlv/blob/48e415d944c7e4ae6a30cff8566f0936bda7390d/docs/development/query-adversarial.md) | core | Keep | `development/query-adversarial/` | Current reproduction and conformance procedures, including lifecycle/storage contracts; dated result blocks retain their stated scope. |
| [development/query-phase-audit.md](https://github.com/OpenTLV/opentlv/blob/48e415d944c7e4ae6a30cff8566f0936bda7390d/docs/development/query-phase-audit.md) | core | Archive | `development/history/core/query-phase-audit/` | Dated F1-F6 implementation evidence; keep current Query verification and release procedures active. |
| [development/query-release.md](https://github.com/OpenTLV/opentlv/blob/48e415d944c7e4ae6a30cff8566f0936bda7390d/docs/development/query-release.md) | core | Keep | `development/query-release/` | Current release checklist and evidence schema; this is an executable contributor procedure, not only history. |
| [development/reader-decode-performance.md](https://github.com/OpenTLV/opentlv/blob/48e415d944c7e4ae6a30cff8566f0936bda7390d/docs/development/reader-decode-performance.md) | core | Archive | `development/history/core/reader-decode-performance/` | Dated benchmark comparison; preserve setup, measurements and evidence without implying current performance. |
| [development/releases.md](docs/development/releases.md) | Portal | Keep | `development/releases/` | Active contributor guidance, architecture or current portal routing; retain owner-maintained procedures. |
| [development/rust.md](https://github.com/OpenTLV/opentlv/blob/48e415d944c7e4ae6a30cff8566f0936bda7390d/docs/development/rust.md) | core | Keep | `languages/rust/manual/development/` | Language-specific API, setup, conversions, lifetime or versioning; shared Core semantics remain linked. |
| [development/testing.md](docs/development/testing.md) | Portal | Keep | `development/testing/` | Active contributor guidance, architecture or current portal routing; retain owner-maintained procedures. |
| [development/valgrind.md](https://github.com/OpenTLV/opentlv/blob/48e415d944c7e4ae6a30cff8566f0936bda7390d/docs/development/valgrind.md) | core | Keep | `development/valgrind/` | Active contributor guidance, architecture or current portal routing; retain owner-maintained procedures. |
| [development/webassembly.md](https://github.com/OpenTLV/opentlv/blob/48e415d944c7e4ae6a30cff8566f0936bda7390d/docs/development/webassembly.md) | core | Keep | `languages/wasm/development/` | Language-specific API, setup, conversions, lifetime or versioning; shared Core semantics remain linked. |
| [development/workflow.md](https://github.com/OpenTLV/opentlv/blob/48e415d944c7e4ae6a30cff8566f0936bda7390d/docs/development/workflow.md) | core | Keep | `development/workflow/` | Active contributor guidance, architecture or current portal routing; retain owner-maintained procedures. |
| [formats/README.md](https://github.com/OpenTLV/opentlv/blob/48e415d944c7e4ae6a30cff8566f0936bda7390d/docs/formats/README.md) | core | Keep | `api/formats/guide/` | Shared public contracts, configurations or native reference; retain the canonical technical details and examples. |
| [formats/asn1/ber.md](https://github.com/OpenTLV/opentlv/blob/48e415d944c7e4ae6a30cff8566f0936bda7390d/docs/formats/asn1/ber.md) | core | Keep | `standards/asn1/ber/` | Protocol-specific behavior, wire examples and support limitations belong beside the standard. |
| [formats/asn1/cer.md](https://github.com/OpenTLV/opentlv/blob/48e415d944c7e4ae6a30cff8566f0936bda7390d/docs/formats/asn1/cer.md) | core | Keep | `standards/asn1/cer/` | Protocol-specific behavior, wire examples and support limitations belong beside the standard. |
| [formats/asn1/der.md](https://github.com/OpenTLV/opentlv/blob/48e415d944c7e4ae6a30cff8566f0936bda7390d/docs/formats/asn1/der.md) | core | Keep | `standards/asn1/der/` | Protocol-specific behavior, wire examples and support limitations belong beside the standard. |
| [formats/bluetooth/README.md](https://github.com/OpenTLV/opentlv/blob/48e415d944c7e4ae6a30cff8566f0936bda7390d/docs/formats/bluetooth/README.md) | core | Keep | `standards/bluetooth/` | Protocol-specific behavior, wire examples and support limitations belong beside the standard. |
| [formats/custom/README.md](https://github.com/OpenTLV/opentlv/blob/48e415d944c7e4ae6a30cff8566f0936bda7390d/docs/formats/custom/README.md) | core | Keep | `api/formats/custom/` | Shared public contracts, configurations or native reference; retain the canonical technical details and examples. |
| [formats/dhcp/README.md](https://github.com/OpenTLV/opentlv/blob/48e415d944c7e4ae6a30cff8566f0936bda7390d/docs/formats/dhcp/README.md) | core | Keep | `standards/dhcp/` | Protocol-specific behavior, wire examples and support limitations belong beside the standard. |
| [formats/escaped.md](docs/formats/escaped.md) | Portal | Keep | `api/formats/escaped/` | Shared public contracts, configurations or native reference; retain the canonical technical details and examples. |
| [formats/fixed/configurable.md](https://github.com/OpenTLV/opentlv/blob/48e415d944c7e4ae6a30cff8566f0936bda7390d/docs/formats/fixed/configurable.md) | core | Keep | `api/formats/fixed/configurable/` | Shared public contracts, configurations or native reference; retain the canonical technical details and examples. |
| [formats/format-catalogue.md](https://github.com/OpenTLV/opentlv/blob/48e415d944c7e4ae6a30cff8566f0936bda7390d/docs/formats/format-catalogue.md) | core | Keep | `development/planning/format-catalogue/` | Keep candidate research and wire diagrams; stale writer-trailer claims are corrected in Core without claiming a Diameter implementation. |
| [formats/format-examples.md](https://github.com/OpenTLV/opentlv/blob/48e415d944c7e4ae6a30cff8566f0936bda7390d/docs/formats/format-examples.md) | core | Keep | `tutorials/formats/` | Task-oriented learning, workflows and owner examples remain available without copying their implementations. |
| [formats/format-roadmap.md](https://github.com/OpenTLV/opentlv/blob/48e415d944c7e4ae6a30cff8566f0936bda7390d/docs/formats/format-roadmap.md) | core | Keep | `development/planning/format-roadmap/` | Keep planned expansion separate from implemented capabilities; the stale Variable status is corrected in Core. |
| [formats/lldp-review.md](https://github.com/OpenTLV/opentlv/blob/48e415d944c7e4ae6a30cff8566f0936bda7390d/docs/formats/lldp-review.md) | core | Keep | `development/planning/lldp-review/` | Planning and requirements review retains unresolved normative checks; it does not claim full standard conformance. |
| [formats/lldp/README.md](https://github.com/OpenTLV/opentlv/blob/48e415d944c7e4ae6a30cff8566f0936bda7390d/docs/formats/lldp/README.md) | core | Keep | `standards/lldp/` | Protocol-specific behavior, wire examples and support limitations belong beside the standard. |
| [formats/lldp/conformance.md](https://github.com/OpenTLV/opentlv/blob/48e415d944c7e4ae6a30cff8566f0936bda7390d/docs/formats/lldp/conformance.md) | core | Keep | `standards/lldp/conformance/` | Users need the supported subset and unresolved normative-audit boundary beside the LLDP standard guide. |
| [formats/nfc/README.md](https://github.com/OpenTLV/opentlv/blob/48e415d944c7e4ae6a30cff8566f0936bda7390d/docs/formats/nfc/README.md) | core | Keep | `standards/nfc/` | Protocol-specific behavior, wire examples and support limitations belong beside the standard. |
| [formats/overview.md](docs/formats/overview.md) | Portal | Keep | `standards/` | Protocol-specific behavior, wire examples and support limitations belong beside the standard. |
| [formats/packed.md](https://github.com/OpenTLV/opentlv/blob/48e415d944c7e4ae6a30cff8566f0936bda7390d/docs/formats/packed.md) | core | Keep | `api/formats/packed/` | Shared public contracts, configurations or native reference; retain the canonical technical details and examples. |
| [formats/support.md](https://github.com/OpenTLV/opentlv/blob/48e415d944c7e4ae6a30cff8566f0936bda7390d/docs/formats/support.md) | core | Keep | `api/capabilities/` | Shared public contracts, configurations or native reference; retain the canonical technical details and examples. |
| [formats/variable.md](https://github.com/OpenTLV/opentlv/blob/48e415d944c7e4ae6a30cff8566f0936bda7390d/docs/formats/variable.md) | core | Keep | `api/formats/variable/` | Shared public contracts, configurations or native reference; retain the canonical technical details and examples. |
| [getting-started/README.md](https://github.com/OpenTLV/opentlv/blob/48e415d944c7e4ae6a30cff8566f0936bda7390d/docs/getting-started/README.md) | core | Keep | `tutorials/first-program/` | Task-oriented learning, workflows and owner examples remain available without copying their implementations. |
| [getting-started/core-build.md](https://github.com/OpenTLV/opentlv/blob/48e415d944c7e4ae6a30cff8566f0936bda7390d/docs/getting-started/README.md) | core | Keep | `development/building/core/` | Active contributor guidance, architecture or current portal routing; retain owner-maintained procedures. |
| [getting-started/overview.md](docs/getting-started/overview.md) | Portal | Keep | `tutorials/` | Task-oriented learning, workflows and owner examples remain available without copying their implementations. |
| [guides/codecs.md](https://github.com/OpenTLV/opentlv/blob/48e415d944c7e4ae6a30cff8566f0936bda7390d/docs/guides/codecs.md) | core | Keep | `api/guides/codecs/` | Shared public contracts, configurations or native reference; retain the canonical technical details and examples. |
| [guides/copy.md](https://github.com/OpenTLV/opentlv/blob/48e415d944c7e4ae6a30cff8566f0936bda7390d/docs/guides/copy.md) | core | Keep | `api/guides/copy/` | Shared public contracts, configurations or native reference; retain the canonical technical details and examples. |
| [guides/cxx-examples.md](https://github.com/OpenTLV/opentlv/blob/48e415d944c7e4ae6a30cff8566f0936bda7390d/docs/guides/cxx-examples.md) | core | Keep | `tutorials/cpp-examples/` | Task-oriented learning, workflows and owner examples remain available without copying their implementations. |
| [guides/diagnostics.md](https://github.com/OpenTLV/opentlv/blob/48e415d944c7e4ae6a30cff8566f0936bda7390d/docs/guides/diagnostics.md) | core | Keep | `api/guides/diagnostics/` | Shared public contracts, configurations or native reference; retain the canonical technical details and examples. |
| [guides/document.md](https://github.com/OpenTLV/opentlv/blob/48e415d944c7e4ae6a30cff8566f0936bda7390d/docs/guides/document.md) | core | Keep | `api/guides/document/` | Shared public contracts, configurations or native reference; retain the canonical technical details and examples. |
| [guides/examples.md](https://github.com/OpenTLV/opentlv/blob/48e415d944c7e4ae6a30cff8566f0936bda7390d/docs/guides/examples.md) | core | Keep | `tutorials/examples/` | Task-oriented learning, workflows and owner examples remain available without copying their implementations. |
| [guides/go.md](https://github.com/OpenTLV/opentlv/blob/48e415d944c7e4ae6a30cff8566f0936bda7390d/docs/guides/go.md) | core | Keep | `languages/go/manual/` | Language-specific API, setup, conversions, lifetime or versioning; shared Core semantics remain linked. |
| [guides/memory.md](https://github.com/OpenTLV/opentlv/blob/48e415d944c7e4ae6a30cff8566f0936bda7390d/docs/guides/memory.md) | core | Keep | `api/guides/memory/` | Shared public contracts, configurations or native reference; retain the canonical technical details and examples. |
| [guides/processing.md](https://github.com/OpenTLV/opentlv/blob/48e415d944c7e4ae6a30cff8566f0936bda7390d/docs/guides/processing.md) | core | Keep | `tutorials/processing/` | Task-oriented learning, workflows and owner examples remain available without copying their implementations. |
| [guides/python.md](https://github.com/OpenTLV/opentlv/blob/48e415d944c7e4ae6a30cff8566f0936bda7390d/docs/guides/python.md) | core | Archive | `development/history/core/guides/python/` | Superseded Core copy; standalone Python owns the same API sections and examples. Preserve the old body as extraction evidence. |
| [guides/queries.md](https://github.com/OpenTLV/opentlv/blob/48e415d944c7e4ae6a30cff8566f0936bda7390d/docs/guides/queries.md) | core | Keep | `api/guides/queries/` | Shared public contracts, configurations or native reference; retain the canonical technical details and examples. |
| [guides/reader.md](https://github.com/OpenTLV/opentlv/blob/48e415d944c7e4ae6a30cff8566f0936bda7390d/docs/guides/reader.md) | core | Keep | `api/guides/reader/` | Shared public contracts, configurations or native reference; retain the canonical technical details and examples. |
| [guides/rust.md](https://github.com/OpenTLV/opentlv/blob/48e415d944c7e4ae6a30cff8566f0936bda7390d/docs/guides/rust.md) | core | Keep | `languages/rust/manual/` | Language-specific API, setup, conversions, lifetime or versioning; shared Core semantics remain linked. |
| [guides/schemas.md](https://github.com/OpenTLV/opentlv/blob/48e415d944c7e4ae6a30cff8566f0936bda7390d/docs/guides/schemas.md) | core | Keep | `api/guides/schemas/` | Shared public contracts, configurations or native reference; retain the canonical technical details and examples. |
| [guides/select-components.md](https://github.com/OpenTLV/opentlv/blob/48e415d944c7e4ae6a30cff8566f0936bda7390d/docs/guides/select-components.md) | core | Keep | `api/configuration/` | Shared public contracts, configurations or native reference; retain the canonical technical details and examples. |
| [guides/writer.md](https://github.com/OpenTLV/opentlv/blob/48e415d944c7e4ae6a30cff8566f0936bda7390d/docs/guides/writer.md) | core | Keep | `api/guides/writer/` | Shared public contracts, configurations or native reference; retain the canonical technical details and examples. |
| [index.md](docs/index.md) | Portal | Keep | `./` | Portal Home remains the ecosystem introduction and navigation entry point. |
| [lua/api.md](https://github.com/OpenTLV/opentlv-lua/blob/ea6c937c8c7f094dae7386740e3a20574b43d703/docs/api.md) | lua | Keep | `languages/lua/manual/api/` | Language-specific API, setup, conversions, lifetime or versioning; shared Core semantics remain linked. |
| [lua/development.md](https://github.com/OpenTLV/opentlv-lua/blob/ea6c937c8c7f094dae7386740e3a20574b43d703/docs/development.md) | lua | Keep | `languages/lua/manual/development/` | Mixed installation and contributor setup is required by users; keep linked from the language manual. |
| [lua/implementation.md](https://github.com/OpenTLV/opentlv-lua/blob/ea6c937c8c7f094dae7386740e3a20574b43d703/docs/implementation.md) | lua | Relocate | `development/components/lua/implementation/` | Current component contributor testing, implementation or release procedure; move portal placement to Development while retaining public-manual links. |
| [lua/migration.md](https://github.com/OpenTLV/opentlv-lua/blob/ea6c937c8c7f094dae7386740e3a20574b43d703/docs/migration.md) | lua | Archive | `development/history/lua/migration/` | Frozen source-import inventory and staged migration results; current setup and independent versioning have owner guides. |
| [lua/quality-gates.md](https://github.com/OpenTLV/opentlv-lua/blob/ea6c937c8c7f094dae7386740e3a20574b43d703/docs/quality-gates.md) | lua | Relocate | `development/components/lua/quality-gates/` | Current component contributor testing, implementation or release procedure; move portal placement to Development while retaining public-manual links. |
| [lua/releases.md](https://github.com/OpenTLV/opentlv-lua/blob/ea6c937c8c7f094dae7386740e3a20574b43d703/docs/releases.md) | lua | Relocate | `development/components/lua/releases/` | Current component contributor testing, implementation or release procedure; move portal placement to Development while retaining public-manual links. |
| [lua/testing.md](https://github.com/OpenTLV/opentlv-lua/blob/ea6c937c8c7f094dae7386740e3a20574b43d703/docs/testing.md) | lua | Relocate | `development/components/lua/testing/` | Current component contributor testing, implementation or release procedure; move portal placement to Development while retaining public-manual links. Keep its current test contract and clearly labeled historical validation section together. |
| [lua/versioning.md](https://github.com/OpenTLV/opentlv-lua/blob/ea6c937c8c7f094dae7386740e3a20574b43d703/docs/versioning.md) | lua | Keep | `languages/lua/manual/versioning/` | Language-specific API, setup, conversions, lifetime or versioning; shared Core semantics remain linked. |
| [playground/index.md](docs/playground/index.md) | Portal | Keep | `tools/playground/` | Tool-specific commands, JSON/UI behavior or discovery; preserve the tool owner and examples. |
| [python/development/python.md](https://github.com/OpenTLV/opentlv-python/blob/d846b4ff7f2c74fbf0571a065da1d83698b6f40c/docs/development/python.md) | python | Keep | `languages/python/manual/development/python/` | Mixed build, install and workspace instructions remain the canonical user setup entry point. |
| [python/guides/python.md](https://github.com/OpenTLV/opentlv-python/blob/d846b4ff7f2c74fbf0571a065da1d83698b6f40c/docs/guides/python.md) | python | Keep | `languages/python/manual/guides/python/` | Language-specific API, setup, conversions, lifetime or versioning; shared Core semantics remain linked. |
| [python/migration.md](https://github.com/OpenTLV/opentlv-python/blob/d846b4ff7f2c74fbf0571a065da1d83698b6f40c/docs/migration.md) | python | Archive | `development/history/python/migration/` | Frozen import provenance and Core-context comparison; current Python setup is maintained independently. |
| [python/quality-gates.md](https://github.com/OpenTLV/opentlv-python/blob/d846b4ff7f2c74fbf0571a065da1d83698b6f40c/docs/quality-gates.md) | python | Relocate | `development/components/python/quality-gates/` | Current component contributor testing, implementation or release procedure; move portal placement to Development while retaining public-manual links. |
| [python/releases.md](https://github.com/OpenTLV/opentlv-python/blob/d846b4ff7f2c74fbf0571a065da1d83698b6f40c/docs/releases.md) | python | Relocate | `development/components/python/releases/` | Current component contributor testing, implementation or release procedure; move portal placement to Development while retaining public-manual links. |
| [python/validation/ci.md](https://github.com/OpenTLV/opentlv-python/blob/d846b4ff7f2c74fbf0571a065da1d83698b6f40c/docs/validation/ci.md) | python | Archive | `development/history/python/validation/ci/` | Historical CI validation and repair record; preserve run links and pending-at-that-time statements. |
| [python/validation/layout.md](https://github.com/OpenTLV/opentlv-python/blob/d846b4ff7f2c74fbf0571a065da1d83698b6f40c/docs/validation/layout.md) | python | Archive | `development/history/python/validation/layout/` | Source-layout migration validation; preserve byte-fidelity evidence and historical scope. |
| [python/validation/packaging.md](https://github.com/OpenTLV/opentlv-python/blob/d846b4ff7f2c74fbf0571a065da1d83698b6f40c/docs/validation/packaging.md) | python | Archive | `development/history/python/validation/packaging/` | Dated packaging evidence and checksums; current release procedure has its own owner guide. |
| [python/validation/standalone-build.md](https://github.com/OpenTLV/opentlv-python/blob/d846b4ff7f2c74fbf0571a065da1d83698b6f40c/docs/validation/standalone-build.md) | python | Archive | `development/history/python/validation/standalone-build/` | Dated standalone-build validation with exact dependency/toolchain inputs and explicit evidence limits. |
| [python/versioning.md](https://github.com/OpenTLV/opentlv-python/blob/d846b4ff7f2c74fbf0571a065da1d83698b6f40c/docs/versioning.md) | python | Keep | `languages/python/manual/versioning/` | Language-specific API, setup, conversions, lifetime or versioning; shared Core semantics remain linked. |
| [reference/README.md](https://github.com/OpenTLV/opentlv/blob/48e415d944c7e4ae6a30cff8566f0936bda7390d/docs/reference/README.md) | core | Keep | `api/reference/` | Shared public contracts, configurations or native reference; retain the canonical technical details and examples. |
| [reference/c-api.md](https://github.com/OpenTLV/opentlv/blob/48e415d944c7e4ae6a30cff8566f0936bda7390d/docs/reference/c-api.md) | core | Keep | `api/reference/c/` | Shared public contracts, configurations or native reference; retain the canonical technical details and examples. |
| [reference/compilers.md](https://github.com/OpenTLV/opentlv/blob/48e415d944c7e4ae6a30cff8566f0936bda7390d/docs/reference/compilers.md) | core | Keep | `development/building/compilers/` | Active contributor guidance, architecture or current portal routing; retain owner-maintained procedures. |
| [reference/cxx-api.md](https://github.com/OpenTLV/opentlv/blob/48e415d944c7e4ae6a30cff8566f0936bda7390d/docs/reference/cxx-api.md) | core | Keep | `api/reference/cpp/` | Shared public contracts, configurations or native reference; retain the canonical technical details and examples. |
| [reference/errors.md](https://github.com/OpenTLV/opentlv/blob/48e415d944c7e4ae6a30cff8566f0936bda7390d/docs/reference/errors.md) | core | Keep | `api/reference/errors/` | Shared public contracts, configurations or native reference; retain the canonical technical details and examples. |
| [standards/emv/README.md](https://github.com/OpenTLV/opentlv/blob/48e415d944c7e4ae6a30cff8566f0936bda7390d/docs/standards/emv/README.md) | core | Keep | `standards/emv/` | Protocol-specific behavior, wire examples and support limitations belong beside the standard. |
| [tools/imtlv/index.md](docs/tools/imtlv/index.md) | Portal | Keep | `tools/imtlv/` | Tool-specific commands, JSON/UI behavior or discovery; preserve the tool owner and examples. |
| [tools/index.md](docs/tools/index.md) | Portal | Keep | `tools/` | Tool-specific commands, JSON/UI behavior or discovery; preserve the tool owner and examples. |
| [tools/otlv/index.md](docs/tools/otlv/index.md) | Portal | Keep | `tools/otlv/` | Tool-specific commands, JSON/UI behavior or discovery; preserve the tool owner and examples. |
| [tools/playground/overview.md](docs/tools/playground/overview.md) | Portal | Keep | `tools/playground/overview/` | Tool-specific commands, JSON/UI behavior or discovery; preserve the tool owner and examples. |

## Supporting evidence and source preservation

The non-navigation Core `docs/README.md` remains its repository index; its existing
site exclusion is unchanged. All imported Markdown owners and original paths are
preserved, including combined DER/CER parts. No owner source is silently omitted.
Archive notes and links are presentation additions, not edits to technical bodies.

Retain these ten component evidence files byte-for-byte: Lua `ci-baseline.json`
and `migration/source-inventory.json`; Python `migration/original-python.yml`,
`migration/source-inventory.json`, `migration/validation.json`,
`migration/windows-baseline.log`, `migration/windows-imported.log`, and
`validation/standalone-build.json`, `validation/ci.json`, `validation/packaging.json`.
Other Core/portal assets and machine-readable evidence remain in the original
assembled locations. Historical source-import READMEs and linked raw benchmark
evidence remain available in their owner repositories.

Generated C/C++ references, symbol anchors and example sources remain available.
The portal still validates source-relative links against original source identities
before resolving the moved outputs. Current contributor pages stay searchable;
the searchable history index links all included archived records.

## Owner corrections and completion

Full review identified two stale active planning claims in Core: Variable format
was still marked planned, and Diameter candidate notes said the writer lacked a
trailer hook. Corrections are prepared in Core's
`feature/61_documentation_content_review`: mark Variable implemented and describe
the existing complete Format measure/encode contract, while keeping Diameter
explicitly unimplemented. These are owner edits, not portal-authored technical
replacements. The selected Core revision in this review is unchanged until merge.

Merge the owner correction, adopt its exact commit through a reviewed Docs source
update, and validate the resulting combined set before closing #61. Portal
validation covers the current pins and a separately identified corrected-owner
preview; neither local results nor a new source pin claim hosted publication.

The obsolete Portal-injected pending-Python-cutover wording is corrected here.
The [ownership review](DOCUMENTATION-OWNERSHIP.md) records the completed #62 chain.
Final published-site, version-selector and WASM acceptance remains in #50.
