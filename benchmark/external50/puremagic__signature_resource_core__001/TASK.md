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

- Given bytes or a binary stream whose leading bytes match bundled metadata, the detector recognizes the format: `from_string` and `from_stream` return its extension and `magic_string` returns matching records.
- For a recognized signature or extension, MIME mode and `from_extension` return the associated MIME type.
- `magic_string` returns a non-empty ranked list of match records for recognized bytes, with the best match first and its `extension` attribute identifying the format.
- Calling `magic_string` with empty input raises `PureError` or `ValueError`.
- The package exposes the required task API paths `featurelifted.from_string`, `featurelifted.from_stream`, `featurelifted.magic_string`, `featurelifted.from_extension`, and `featurelifted.PureError` with the kinds and callable signatures listed in this contract.
- the submitted package does not import forbidden upstream packages: puremagic.

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

- **B001** — Given bytes or a binary stream whose leading bytes match bundled metadata, the detector recognizes the format: `from_string` and `from_stream` return its extension and `magic_string` returns matching records.
- **B002** — For a recognized signature or extension, MIME mode and `from_extension` return the associated MIME type.
- **B003** — `magic_string` returns a non-empty ranked list of match records for recognized bytes, with the best match first and its `extension` attribute identifying the format.
- **B004** — Calling `magic_string` with empty input raises `PureError` or `ValueError`.
- **B005** — The package exposes the required task API paths `featurelifted.from_string`, `featurelifted.from_stream`, `featurelifted.magic_string`, `featurelifted.from_extension`, and `featurelifted.PureError` with the kinds and callable signatures listed in this contract.
- **B006** — the submitted package does not import forbidden upstream packages: puremagic.
<!-- featureliftbench:behavior-clauses:end -->
