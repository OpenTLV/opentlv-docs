# Rust

The `opentlv` crate offers a safe Rust API over the OpenTLV C library, with
Readers, Writers, owned Documents, Query, Schema and codec support. The
`opentlv-sys` crate declares the raw C API it uses.

- **Language:** Rust; the supported toolchain and build requirements belong to
  the [selected setup guide](../../rust/guides/rust.md#cargo-setup).
- **Status:** available as an experimental standalone binding. The selected
  manual documents a path dependency on a repository checkout, not a crates.io
  release.
- **Owner:** [opentlv-rust](https://github.com/OpenTLV/opentlv-rust).

## Installation and first use

Follow [Cargo setup](../../rust/guides/rust.md#cargo-setup) for the native
toolchain, the pinned Core dependency and library selection. The guide links
its runnable quick start.

The [Rust development guide](../../rust/development/rust.md#versioning) owns
Cargo features, crate versions and Core selection;
[packaging and versioning](../../rust/packaging.md) records the package
identities and their compatible Core dependency.

## Detailed documentation

Open the [Rust manual](../../rust/guides/rust.md) for API usage, examples and
local Rustdoc generation, or the
[build, features and contribution guide](../../rust/development/rust.md).
Check the [capability matrix](../../concepts/bindings.md) for API coverage.
These pages are selected from the binding repository and use a separate
product menu.

Rust does not publish independent documentation releases yet. The selected
manual identifies its source revision independently of the portal version
number; a portal version is not a Rust crate version.

[All languages](../index.md)
