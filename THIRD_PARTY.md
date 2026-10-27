# Third-party notices

This repository's own files are MIT licensed by Marek Cingel; see
[LICENSE](LICENSE). It contains no vendored third-party code, fonts or images.
The OpenTLV logo and favicon in `docs/assets/` are original project assets
under the same license. The wordmark names Arial, Helvetica and sans-serif as
fonts but embeds no font data.

## Published site

A built site and its versioned snapshots contain more than this repository's
files. Each part keeps the license of its owner:

| Part of the site | Origin | License and notice |
| --- | --- | --- |
| Assembled manuals, examples and API reference text | The Core, CLI, Lua, Python, Rust, Go and JS repositories at the revisions recorded in `source-revision.json` | Each repository's `LICENSE`, currently MIT by Marek Cingel; contributors retain copyright in their contributions. Page source links point to the owning repository. |
| `playground/wasm/` | `opentlv-js` and Core, compiled with Emscripten | MIT by Marek Cingel. Emscripten runtime and system library code linked into `opentlv-core.js` and `opentlv-core.wasm` is covered by the [Emscripten licenses](https://github.com/emscripten-core/emscripten/blob/main/LICENSE). |
| Page templates, `assets/javascripts/` and `assets/stylesheets/` | [Material for MkDocs](https://github.com/squidfunk/mkdocs-material), selected by `requirements-docs.txt` | MIT by Martin Donath; see its [LICENSE](https://github.com/squidfunk/mkdocs-material/blob/master/LICENSE). The minified bundles do not repeat the notice, so this file records it. The footer keeps the theme's "Made with Material for MkDocs" credit. |
| Interface icons inlined into pages | Material Design Icons by Pictogrammers, shipped with the theme | Apache License 2.0; see the [Pictogrammers license](https://github.com/Templarian/MaterialDesign/blob/master/LICENSE). |
| GitHub icon in the header and footer | Font Awesome Free, shipped with the theme | Icons under CC BY 4.0; each inlined SVG keeps the Font Awesome attribution comment. |
| `api/` generated reference pages | Doxygen, run on Core's sources | Doxygen's scripts keep their MIT notices and jQuery keeps its OpenJS Foundation notice in the generated files. |

The Roboto and Roboto Mono fonts are loaded by the visitor's browser from Google
Fonts; they are not part of the published files. MkDocs, mike, PyMdown
Extensions, Playwright and the other build and check tools are not distributed
with the site.

Update this file when a theme, generator, icon set or bundled dependency is
added or replaced. Keep notices that third-party files carry.
