# FeatureLift Task: Bundled file-signature metadata detection

Extract pure-Python file signature detection from strings, streams, and extensions using bundled metadata.

The submitted implementation must not import the upstream package or read from `repo/` at runtime, must not use the network, and must not depend on external services. Use only the standard library unless the task lockfile allows otherwise.

## Target API

```python
from featurelifted import (
    from_extension,
    from_stream,
    from_string,
    magic_string,
    PureError,
)
```

## Required API Details

- `from_string(string: str | bytes, mime: bool = False, filename=None) -> str`
- `from_stream(stream, mime: bool = False, filename=None) -> str`
- `magic_string(string, filename=None) -> list`
- `from_extension(extension: str, mime: bool = True) -> str`
- `PureError` must be importable and raisable

## Required Behavior

- from_string and from_stream identify known byte signatures using bundled magic metadata.
- MIME mode and from_extension return metadata associated with the selected signature or extension.
- magic_string returns ranked match records and unknown or empty inputs raise documented errors.
- The submitted package does not import puremagic or access external signature services.

## Constraints

- Forbidden imports: `puremagic`.
- Do not implement CLI.
- Do not implement deep archive scanners.
- Do not implement large fixture corpus.
- Do not implement network lookups.
- Do not implement original puremagic import at runtime.

## Public vs Hidden Tests

Public tests cover common use. Hidden tests cover documented edge, configuration, state, API-surface, and isolation behavior only.

<!-- featureliftbench:behavior-clauses:start -->
## Public Behavior Contract

The stable clause IDs below define the public behavior contract. Hidden tests may exercise these clauses but do not introduce additional requirements.

- **B001** — from_string and from_stream identify known byte signatures using bundled magic metadata.
- **B002** — MIME mode and from_extension return metadata associated with the selected signature or extension.
- **B003** — magic_string returns ranked match records and unknown or empty inputs raise documented errors.
- **B004** — The submitted package does not import puremagic or access external signature services.
<!-- featureliftbench:behavior-clauses:end -->
