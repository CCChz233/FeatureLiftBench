# FeatureLift Task: Dataclass dict codec

Build a standalone `featurelifted` package providing mashumaro-style `DataClassDictMixin` dict codecs with aliases and omit_none.

The submitted implementation must not import the upstream package or read from `repo/` at runtime, must not use the network, and must not depend on external services. Use only the standard library unless the task lockfile allows otherwise.

## Target API

```python
from featurelifted import (
    config,
    DataClassDictMixin,
    field_options,
    MissingField,
)
```

## Required API Details

- `DataClassDictMixin` class must be importable
  - `DataClassDictMixin.to_dict(self, **kwargs) -> dict`
  - `DataClassDictMixin.from_dict(cls, d, **kwargs)`
- `field_options(serialize=None, deserialize=None, serialization_strategy=None, alias=None, **kwargs) -> dict`
- `MissingField` must be importable and raisable
- `config.BaseConfig` class must be importable

## Required Behavior

- A dataclass mixing in `DataClassDictMixin` round-trips nested mixin dataclasses through `from_dict` and `to_dict`.
- A field constructed with `field_options(alias=...)` is read from and, when `Config.serialize_by_alias` is true, written to that alias key rather than the Python field name.
- When `Config.omit_none` is true, `to_dict` omits fields whose value is `None`.
- `from_dict` raises `MissingField` when a required field is absent from the input mapping.
- The package exposes `DataClassDictMixin`, `field_options`, `MissingField`, and `config.BaseConfig` with the callable paths listed in this contract.
- The submitted package source does not import the forbidden upstream package `mashumaro`.

## Constraints

- Forbidden imports: `mashumaro`.
- Do not implement orjson/msgpack engines.
- Do not implement YAML/TOML codecs.
- Do not implement runtime import of mashumaro.

<!-- featureliftbench:behavior-clauses:start -->
## Public Behavior Contract

The stable clause IDs below define the public behavior contract. Hidden tests may exercise these clauses but do not introduce additional requirements.

- **B001** — A dataclass mixing in `DataClassDictMixin` round-trips nested mixin dataclasses through `from_dict` and `to_dict`.
- **B002** — A field constructed with `field_options(alias=...)` is read from and, when `Config.serialize_by_alias` is true, written to that alias key rather than the Python field name.
- **B003** — When `Config.omit_none` is true, `to_dict` omits fields whose value is `None`.
- **B004** — `from_dict` raises `MissingField` when a required field is absent from the input mapping.
- **B005** — The package exposes `DataClassDictMixin`, `field_options`, `MissingField`, and `config.BaseConfig` with the callable paths listed in this contract.
- **B006** — The submitted package source does not import the forbidden upstream package `mashumaro`.
<!-- featureliftbench:behavior-clauses:end -->
