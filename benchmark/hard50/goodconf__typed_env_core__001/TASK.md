# FeatureLift Task: Typed env and file settings

Build a standalone `featurelifted` package providing a typed settings model loaded from environment variables and JSON files.

The submitted implementation must not import the upstream package or read from `repo/` at runtime, must not use the network, and must not depend on external services. Use only the standard library unless the task lockfile allows otherwise.

## Target API

```python
from featurelifted import (
    Field,
    GoodConf,
)
```

## Required API Details

- `GoodConf(load: bool = False, config_file: str | None = None, **kwargs)` class constructor
  - `GoodConf.load(self, filename: str | None = None) -> None`
  - `GoodConf.generate_json(cls, **override) -> str`
- `Field(default=..., *, initial=None, **kwargs)`

## Required Behavior

- A `GoodConf` subclass with typed `Field`s loads values from environment variables whose names match the field names in uppercase, for example `HOST` for a `host` field.
- `load(path)` overlays values from a JSON object file onto the settings model so file keys populate the matching fields when those names are not already set by the environment.
- When both a JSON file and an environment variable define the same field, the environment value is used after `load`.
- Loading a value that cannot be coerced to the annotated field type raises an exception. `generate_json` returns a JSON object string containing the model's initial field values.
- The package exposes `GoodConf` and `Field` with `load` and `generate_json` as listed in this contract.
- The submitted package source does not import the forbidden upstream package `goodconf`.

## Constraints

- Forbidden imports: `goodconf`.
- Do not implement Django integration extras.
- Do not implement YAML dump helpers that need extra YAML libraries.
- Do not implement runtime import of goodconf.

<!-- featureliftbench:behavior-clauses:start -->
## Public Behavior Contract

The stable clause IDs below define the public behavior contract. Hidden tests may exercise these clauses but do not introduce additional requirements.

- **B001** — A `GoodConf` subclass with typed `Field`s loads values from environment variables whose names match the field names in uppercase, for example `HOST` for a `host` field.
- **B002** — `load(path)` overlays values from a JSON object file onto the settings model so file keys populate the matching fields when those names are not already set by the environment.
- **B003** — When both a JSON file and an environment variable define the same field, the environment value is used after `load`.
- **B004** — Loading a value that cannot be coerced to the annotated field type raises an exception. `generate_json` returns a JSON object string containing the model's initial field values.
- **B005** — The package exposes `GoodConf` and `Field` with `load` and `generate_json` as listed in this contract.
- **B006** — The submitted package source does not import the forbidden upstream package `goodconf`.
<!-- featureliftbench:behavior-clauses:end -->
