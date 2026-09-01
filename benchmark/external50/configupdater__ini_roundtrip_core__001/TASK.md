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
- `ConfigUpdater.read_string(string: str, source: str = '<string>') -> None`
- `ConfigUpdater.write(fp: TextIO, validate: bool = True)`

## Required Behavior

- After read_string parses INI text, sections and options are accessible by mapping lookup, option values are mutable, and write serializes the updated document while retaining comments.
- Assigning an option value, including a previously absent option, produces a normalized `key = value` line when the document is written.
- ConfigUpdater.write accepts a text stream such as StringIO and writes the complete serialized INI document to it.
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

- **B001** — After read_string parses INI text, sections and options are accessible by mapping lookup, option values are mutable, and write serializes the updated document while retaining comments.
- **B002** — Assigning an option value, including a previously absent option, produces a normalized `key = value` line when the document is written.
- **B003** — ConfigUpdater.write accepts a text stream such as StringIO and writes the complete serialized INI document to it.
- **B004** — Mutable INI document supports multiple sections.
- **B005** — The package exposes ConfigUpdater with read_string/write with the kinds listed in this contract.
- **B006** — the submitted package does not import forbidden upstream packages: configupdater.
<!-- featureliftbench:behavior-clauses:end -->
