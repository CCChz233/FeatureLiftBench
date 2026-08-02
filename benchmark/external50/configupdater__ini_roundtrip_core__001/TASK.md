# FeatureLift Task: configupdater ini roundtrip

Extract a task-scoped subset of `ConfigUpdater` into a standalone `featurelifted` package.

The submitted implementation must not import the upstream package or read from `repo/` at runtime, must not use the network, and must not depend on external services. Use only the standard library unless the task lockfile allows otherwise.

## Target API

```python
from featurelifted import (
    ConfigUpdater,
)
```

## Required API Details

- `ConfigUpdater` class must be importable
- `ConfigUpdater.read_string` callable must exist
- `ConfigUpdater.write(fp: TextIO, validate: bool = True)`

## Required Behavior

- The extracted feature must support this observable behavior: read_string and section/option get/set. Required observable cases include read modify write stringio; section option access.
- The extracted feature must support this observable behavior: write to StringIO preserves comments and spacing. Required observable cases include add option; multiple sections roundtrip.
- Tests use ConfigUpdater.write(StringIO) rather than to_string().
- Mutable INI document supports multiple sections.
- The package exposes ConfigUpdater with read_string/write with the kinds listed in this contract.
- the submitted package does not import forbidden upstream packages: configupdater.

## Constraints

- Forbidden imports: `configupdater`.
- Do not implement interpolation beyond declared.
- Do not implement original configupdater import at runtime.

<!-- featureliftbench:behavior-clauses:start -->
## Public Behavior Contract

The stable clause IDs below define the public behavior contract. Hidden tests may exercise these clauses but do not introduce additional requirements.

- **B001** — The extracted feature must support this observable behavior: read_string and section/option get/set. Required observable cases include read modify write stringio; section option access.
- **B002** — The extracted feature must support this observable behavior: write to StringIO preserves comments and spacing. Required observable cases include add option; multiple sections roundtrip.
- **B003** — Tests use ConfigUpdater.write(StringIO) rather than to_string().
- **B004** — Mutable INI document supports multiple sections.
- **B005** — The package exposes ConfigUpdater with read_string/write with the kinds listed in this contract.
- **B006** — the submitted package does not import forbidden upstream packages: configupdater.
<!-- featureliftbench:behavior-clauses:end -->
