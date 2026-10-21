# Cross-repository documentation ownership review

Review for [Docs #62](https://github.com/OpenTLV/opentlv-docs/issues/62), prepared
2026-10-21 after the seven-section portal implementation. The
[contributor contract](docs/development/documentation.md) defines current ownership;
this file records the reviewed inputs, findings and correction dependencies.
It is not a registry of current component versions, capabilities or release status.

## Reviewed inputs

The portal baseline is `c415c0ed4070f1a254bfb3873fd1392fd65e1de4`.
Review covered active README/contribution guides, mounted documentation,
source/example manifests, ownership attribution and generated-reference links.
Historical audit and migration records were checked for misleading current
instructions; their original results and provenance remain evidence.

| Repository | Reviewed source commit | Selected by the portal baseline |
| --- | --- | --- |
| Core | `a5e2453c8cc156122cda01b02d3f91c33580b4f3` | Same commit |
| CLI | `4ed2fd0597402d383ae1c47bf2bf331aa997b675` | `abd2bce09a9f25071a41d7c1f3249fd48e8a0b20` |
| Lua | `09cc237ea481ee6e7f291ab2034a4cf9a38fb36c` | `6f610f5552a64efa21aeeb863ad161c91154dbc8` |
| Python | `d846b4ff7f2c74fbf0571a065da1d83698b6f40c` | Same commit |
| Workspace | `cff8655e35f54bdcb58e2139335a2534ea1610a7` | Not a mounted documentation source |

The review includes local corrections after these commits. Published builds
continue to use the reviewed pins in `docs-sources.json`; local corrected
checkouts are separately identified preview inputs. A newer component checkout
does not silently advance a portal source or prove a compatible release.

## Findings and dispositions

| Area | Finding | Correction and technical owner |
| --- | --- | --- |
| Core contribution and indexes | Current text describes completed CLI/Python/portal extraction as pending and treats Core's index as the website index. | Core corrects current ownership and links to standalone manuals and portal operations. |
| Core layout and Python handoff | Current guidance repeats old portal sections and pending Python selection; shared capability evidence can be mistaken for independently maintained binding policy. | Core distinguishes shared contracts and retained comparison evidence from current owner-specific setup, versions and functionality. Historical cutover records remain explicitly historical. |
| Generated C/C++ reference | Core Doxygen guide URLs still use removed portal paths. | Core updates guide destinations; Docs resolves both legacy source-relative paths and actual routed page destinations, including flat HTML and anchors. |
| Workspace setup and integration | README calls Python a scaffold/current Core binding; copied Lua build instructions and a fixed repository count can drift. | Workspace links component setup to owners and describes its actual integration pins and checkout-only coverage separately from current component status. Integration pins and smoke behavior remain unchanged. |
| Lua migration guide | The original selected-manual migration statement appears to govern current independent Lua publication. | Lua labels the migration-era scope and links its current versioning/release contract; original hashes, archived sources and validation results remain intact. |
| CLI and Python current manuals | Active setup, versioning, ownership and release guides already route to their implementation owners. | Keep. No source correction was identified in the reviewed active guides. Dated historical Python validation remains evidence, not current setup. |
| Portal language introductions | Runtime minimums and version-inspection snippets repeat independently changing owner documentation. | Keep product introductions and link the selected owner's setup and versioning guide instead of maintaining duplicate requirements or executable snippets. |
| Portal Escaped entry | Detailed encoding, lifetime and tag-only rules duplicate Core declarations and NFC generic composition. | Retain the entry and its section anchors as routing to those Core contracts. No unique rule or example is removed from its canonical owner. |
| Portal operations README | Completed Lua/Core handoffs are still phrased as pending operations. | State current assembly/publication ownership and label the original cutover sequence historical. Preserve the original procedure as evidence. |
| Source registration validation | Unknown or duplicate JSON keys, duplicate repository/document roots and overlapping mounts can silently alter or confuse ownership. | Reject malformed registrations before replacing assembled output; reuse existing source, example and compatibility schemas. |

The Escaped rule mapping was checked against Core's
`tlv/include/tlv/formats/escaped.h` (configuration, lifetime, ordering, tag-only
constraints), `tlv/include/tlv/field/escaped.h` (marker/count/byte-order rules)
and `docs/formats/nfc/README.md` (generic composition, build options, examples
and protocol boundaries). The portal keeps links to all three canonical inputs.

## Repository dependencies and completion

The following issues are registered as blocking dependencies of Docs #62:

| Owner issue | Prepared local correction | Completion needed for #62 |
| --- | --- | --- |
| [Core #667](https://github.com/OpenTLV/opentlv/issues/667) | Current ownership/handoff guidance and Doxygen URLs | Merge owner correction, then select its exact commit in Docs and validate generated references. |
| [Workspace #35](https://github.com/OpenTLV/opentlv-workspace/issues/35) | Current component routing and accurate pinned integration scope | Merge owner correction; no portal source pin exists for Workspace. |
| [Lua #21](https://github.com/OpenTLV/opentlv-lua/issues/21) | Historical migration versus independent manual versioning | Merge owner correction, then select its exact commit in Docs. |

The corrections are prepared locally; this review does not claim those issues
are merged or complete. Do not close #62 merely because dependencies exist.
After the owner merges, update only the affected source pins, rebuild the exact
selected source set, and verify source/edit links, examples and reference links.
Existing immutable release snapshots must remain unchanged.

## Validation boundary

The source manifest remains the single registration authority. Assembly derives
each imported page's owner from the selected source and tracked original path;
combined pages retain all technical source parts. No second ownership or
component-version registry is introduced.

Existing checks cover required sources, revisions, source locks, collisions,
cross-repository links and anchors, declared example files, ambiguous language
providers and compatibility evidence. The added checks reject duplicate JSON
keys, unknown metadata, non-integer schema versions, duplicate canonical
repository/document-root identities and overlapping non-Core mounts, including
absent optional components. PR validation runs the new registration and API
route regressions; Full retains the complete integration suite.

Local evidence is recorded in `build/issue62-validation.json`, associated logs
and each owner's `build/docs62-pr.md` or `build/issue667-pr.md`. Pinned-source
builds and previews using uncommitted owner corrections must be reported
separately. No component behavioral suite is duplicated. Hosted CI, release
publication and final published-site acceptance belong to their own runs and
to [#50](https://github.com/OpenTLV/opentlv-docs/issues/50).
