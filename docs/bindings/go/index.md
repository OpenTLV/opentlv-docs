# Go

The `opentlv` package exposes the C engine through Go types, slices and errors,
keeping cgo and native handles inside the binding.

- **Language:** Go with cgo; supported versions belong to the [selected setup guide](../../go/guides/go.md#install-and-integrate).
- **Status:** available as an experimental standalone binding; requires matching
  native headers and a library from its selected Core source.
- **Owner:** [opentlv-go](https://github.com/OpenTLV/opentlv-go).

## Installation and first use

Follow [Go installation and integration](../../go/guides/go.md#install-and-integrate)
for the module path and native library setup, then run its linked quick start.

## Detailed documentation

Use the [Go manual](../../go/guides/go.md),
[development guide](../../go/development/go.md),
[packaging and versioning](../../go/packaging.md) and
[capability matrix](../../concepts/bindings.md). Go owns its API, examples and
manuals; Core owns native semantics. Contributor material is available through
[Go tests and CI](../../go/development/ci.md) and
[implementation and ownership](../../go/implementation.md).

Go has no independent documentation release yet. These pages follow the exact
Go revision selected for this portal snapshot. The portal version, Go binding
version and linked Core version are separate identities; the portal's selected
Core is not automatically the Go binding's tested native dependency.

[All languages](../index.md)
