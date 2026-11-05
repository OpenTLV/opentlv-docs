# Third-party notices

This repository's own files are MIT licensed by Marek Cingel; see
[LICENSE](LICENSE). It contains no vendored third-party code, fonts or images. The `notices/`
directory preserves upstream runtime license and copyright texts.
The OpenTLV logo and favicon in `docs/assets/` are original project assets
under the same license. The wordmark names Arial, Helvetica and sans-serif as
fonts but embeds no font data.

## Published site

Every new portal and component snapshot contains `licenses/index.html` and the
complete notice files linked there. The footer uses a relative link into that
snapshot, so copies, nested pages, release versions and aliases retain their
notices without requiring GitHub access. Previously published immutable snapshots
are not rewritten.

| Distributed content | Included notice |
| --- | --- |
| Portal pages, tools and original logo | `portal-LICENSE.txt`, copied from this repository |
| Component manuals and API reference text | `<component>-LICENSE.txt`, copied from each selected checkout |
| Material for MkDocs templates, JavaScript and CSS | `material-LICENSE.txt`, from the installed distribution's license metadata |
| Theme icon collections | Original Material, Font Awesome, Octicons and Simple Icons notices from that same installed distribution; full Apache 2.0 text is also included |
| Playground JS/WASM | Notices shipped by the pinned `@opentlv/opentlv` npm package: `npm-opentlv-LICENSE.txt`, `npm-opentlv-MIT.txt`, `npm-opentlv-THIRD_PARTY.txt`, `npm-opentlv-core-LICENSE.txt` and the Emscripten, musl and compiler-rt notices below |
| Doxygen-generated reference assets | Original notices remain in generated scripts and jQuery files |

`licenses/manifest.json` records the installed theme version, selected component
commits, the playground package version and integrity when present, and SHA-256 hashes of the bundled
notice bytes. The build rejects missing, empty, symlinked, shadowed or modified
notices. New `source-revision.json` records bind that manifest by SHA-256; publication
verification checks it again. Component snapshots also hash every distributed file.

## Playground runtime notices

The following files are copied byte-for-byte from Emscripten **4.0.10**, commit
`b7dc6e5747465580df5984e723b9d1f10d8e804b`. The playground package ships its own
copies; the license hook distributes them only when they equal these reviewed
bytes and hashes. Historical snapshots built from Core/JS sources used the same notices.

| Local file | Upstream path | Upstream terms |
| --- | --- | --- |
| `notices/emscripten-LICENSE.txt` | `LICENSE` | MIT or NCSA, plus retained Node contributor notices |
| `notices/musl-COPYRIGHT.txt` | `system/lib/libc/musl/COPYRIGHT` | musl MIT notice and file-specific origins |
| `notices/compiler-rt-LICENSE.txt` | `system/lib/compiler-rt/LICENSE.TXT` | Apache 2.0 with LLVM exception and legacy MIT/NCSA terms |

[Exact upstream tree](https://github.com/emscripten-core/emscripten/tree/b7dc6e5747465580df5984e723b9d1f10d8e804b).
These notices describe upstream inputs, not a claim that every upstream file is
linked. Keep their original bytes and terms; the portal's MIT license does not
relicense the runtime. A toolchain, allocator or optional runtime-library change,
or a package version with changed or additional notices, requires reviewing the
linked inputs and updating the notice set and hashes.

The Roboto and Roboto Mono fonts are loaded by browsers from Google Fonts, not
bundled in the site. Build tools such as MkDocs, mike and Playwright are not
redistributed as runtime programs. Update this document and the distribution
checks when adding a bundled dependency or changing the theme's icon collections.
