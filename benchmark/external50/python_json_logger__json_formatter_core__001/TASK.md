# FeatureLift Task: python json logger formatter

Extract a task-scoped subset of `python-json-logger` into a standalone `featurelifted` package.

The submitted implementation must not import the upstream package or read from `repo/` at runtime, must not use the network, and must not depend on external services. Use only the standard library unless the task lockfile allows otherwise.

## Target API

```python
from featurelifted import (
    JsonFormatter,
)
```

## Required API Details

- `JsonFormatter` class must be importable
- `JsonFormatter.format` callable must exist

## Required Behavior

- The extracted feature must support this observable behavior: format LogRecord to JSON. Required observable cases include basic json line.
- The extracted feature must support this observable behavior: rename_fields and static_fields. Required observable cases include rename and static fields.
- The extracted feature must support this observable behavior: custom fmt and json submodule import. Required observable cases include custom fmt fields; from json submodule.
- Output is a single JSON object line per record.
- The package exposes JsonFormatter with the kinds listed in this contract.
- the submitted package does not import forbidden upstream packages: pythonjsonlogger.

## Constraints

- Forbidden imports: `pythonjsonlogger`.
- Do not implement SocketHandler networking.
- Do not implement original pythonjsonlogger import at runtime.

<!-- featureliftbench:behavior-clauses:start -->
## Public Behavior Contract

The stable clause IDs below define the public behavior contract. Hidden tests may exercise these clauses but do not introduce additional requirements.

- **B001** — The extracted feature must support this observable behavior: format LogRecord to JSON. Required observable cases include basic json line.
- **B002** — The extracted feature must support this observable behavior: rename_fields and static_fields. Required observable cases include rename and static fields.
- **B003** — The extracted feature must support this observable behavior: custom fmt and json submodule import. Required observable cases include custom fmt fields; from json submodule.
- **B004** — Output is a single JSON object line per record.
- **B005** — The package exposes JsonFormatter with the kinds listed in this contract.
- **B006** — the submitted package does not import forbidden upstream packages: pythonjsonlogger.
<!-- featureliftbench:behavior-clauses:end -->
