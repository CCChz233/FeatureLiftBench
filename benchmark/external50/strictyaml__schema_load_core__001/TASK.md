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

- load parses YAML through Map, Seq, Str, Int, and Bool validators and exposes converted Python primitives through document.data, including absent Optional keys without inserting a value.
- Nested Seq(Map(...)) schemas convert every nested item, while a scalar that does not satisfy its validator, such as `x` for Int(), raises YAMLValidationError.
- Optional keys may be omitted from Map schemas, and MapPattern(Str(), Int()) converts arbitrary string keys with integer values into a Python dictionary.
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

- **B001** — load parses YAML through Map, Seq, Str, Int, and Bool validators and exposes converted Python primitives through document.data, including absent Optional keys without inserting a value.
- **B002** — Nested Seq(Map(...)) schemas convert every nested item, while a scalar that does not satisfy its validator, such as `x` for Int(), raises YAMLValidationError.
- **B003** — Optional keys may be omitted from Map schemas, and MapPattern(Str(), Int()) converts arbitrary string keys with integer values into a Python dictionary.
- **B004** — YAMLValidationError is a StrictYAMLError subclass.
- **B005** — The package exposes load and declared validators/errors with the kinds listed in this contract.
- **B006** — the submitted package does not import forbidden upstream packages: strictyaml.
<!-- featureliftbench:behavior-clauses:end -->
