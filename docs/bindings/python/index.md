# Python

The `opentlv` package provides Python Readers, Writers, Elements and mutable
Documents over the native engine, with Query, Schema and codec support.

- **Language:** Python 3.11 or newer.
- **Status:** available as an experimental standalone binding. The selected
  manual documents installation from source; it does not advertise a PyPI release.
- **Owner:** [opentlv-python](https://github.com/OpenTLV/opentlv-python).

## Installation and first use

Follow [Python setup](../../python/guides/python.md#setup) to install the native
and Python packages together from a checkout. The guide links its runnable
quick start and lists the required build tools.

After installation, check the binding version:

```python
import opentlv

print(opentlv.__version__)
```

## Detailed documentation

Open the [Python manual](../../python/guides/python.md) for API usage and
examples, or [build and contribution instructions](../../python/development/python.md)
for workspace integration. These pages are selected from the binding repository
and use a separate product menu.

Independent Python documentation at `/python/`, relative to the documentation
site root, is not available yet. Use the selected manual above without requiring
a matching release. Its source revision, not the portal version number,
identifies the binding documentation.

[All bindings](../index.md)
