# FeatureLift Task: strictyaml schema load

Extract a task-scoped subset of `strictyaml` into a standalone `featurelifted` package.

The submitted implementation must not import the upstream package or read from `repo/` at runtime, must not use the network, and must not depend on external services. Use only the standard library unless the task lockfile allows otherwise.

## Target API

```python
from featurelifted import (
    Bool,
    Int,
    load,
    Map,
    MapPattern,
    Optional,
    Seq,
    Str,
    StrictYAMLError,
    YAMLValidationError,
)
```

## Required API Details

- `load(yaml_string, schema, label='string')`
- `Map` class must be importable
- `Seq` class must be importable
- `Str` class must be importable
- `Int` class must be importable
- `Bool` class must be importable
- `Optional` class must be importable
- `MapPattern` class must be importable
- `YAMLValidationError` class must be importable
- `StrictYAMLError` class must be importable

## Required Behavior

- The extracted feature must support this observable behavior: load Map/Seq/Bool schemas to .data primitives. Required observable cases include load map seq.
- The extracted feature must support this observable behavior: YAMLValidationError on type mismatch. Required observable cases include validation error.
- The extracted feature must support this observable behavior: Optional keys and MapPattern. Required observable cases include optional key absent; map pattern.
- YAMLValidationError is a StrictYAMLError subclass.
- The package exposes load and declared validators/errors with the kinds listed in this contract.
- the submitted package does not import forbidden upstream packages: strictyaml.

## Constraints

- Forbidden imports: `strictyaml`.
- Do not implement external ruamel beyond vendored.
- Do not implement original strictyaml import at runtime.

<!-- featureliftbench:behavior-clauses:start -->
## Public Behavior Contract

The stable clause IDs below define the public behavior contract. Hidden tests may exercise these clauses but do not introduce additional requirements.

- **B001** — The extracted feature must support this observable behavior: load Map/Seq/Bool schemas to .data primitives. Required observable cases include load map seq.
- **B002** — The extracted feature must support this observable behavior: YAMLValidationError on type mismatch. Required observable cases include validation error.
- **B003** — The extracted feature must support this observable behavior: Optional keys and MapPattern. Required observable cases include optional key absent; map pattern.
- **B004** — YAMLValidationError is a StrictYAMLError subclass.
- **B005** — The package exposes load and declared validators/errors with the kinds listed in this contract.
- **B006** — the submitted package does not import forbidden upstream packages: strictyaml.
<!-- featureliftbench:behavior-clauses:end -->
