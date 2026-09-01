# FeatureLift Task: Typed serialize/deserialize

Build a standalone `featurelifted` package providing apischema-style dataclass (de)serialization, validators, and conversions.

The submitted implementation must not import the upstream package or read from `repo/` at runtime, must not use the network, and must not depend on external services. Use only the standard library unless the task lockfile allows otherwise.

## Target API

```python
from featurelifted import (
    deserialize,
    deserializer,
    serialize,
    ValidationError,
    validator,
)
```

## Required API Details

- `deserialize(type, data, *, additional_properties=None, aliaser=None, coerce=None, conversion=None, default_conversion=None, fall_back_on_default=None, no_copy=None, pass_through=None, schema=None, validators=())`
- `serialize(type=..., obj=..., *, additional_properties=None, aliaser=None, check_type=None, conversion=None, default_conversion=None, exclude_defaults=None, exclude_none=None, exclude_unset=None, fall_back_on_any=None, no_copy=None, pass_through=None)`
- `validator` callable must exist
- `deserializer` callable must exist
- `ValidationError` must be importable and raisable

## Required Behavior

- `deserialize` constructs a dataclass from a mapping, filling declared defaults for omitted optional fields, and `serialize` returns a mapping of the dataclass fields.
- A method decorated with `validator` that yields an error message causes `deserialize` to raise `ValidationError` for invalid instances.
- A class registered with `deserializer` is constructed from matching input; values rejected by that constructor raise an error.
- `deserialize` of a dataclass raises `ValidationError` when a required field is missing from the input mapping.
- The package exposes `deserialize`, `serialize`, `validator`, `deserializer`, and `ValidationError` with the callable paths listed in this contract.
- The submitted package source does not import the forbidden upstream package `apischema`.

## Constraints

- Forbidden imports: `apischema`.
- Do not implement GraphQL extra.
- Do not implement runtime import of apischema.

<!-- featureliftbench:behavior-clauses:start -->
## Public Behavior Contract

The stable clause IDs below define the public behavior contract. Hidden tests may exercise these clauses but do not introduce additional requirements.

- **B001** — `deserialize` constructs a dataclass from a mapping, filling declared defaults for omitted optional fields, and `serialize` returns a mapping of the dataclass fields.
- **B002** — A method decorated with `validator` that yields an error message causes `deserialize` to raise `ValidationError` for invalid instances.
- **B003** — A class registered with `deserializer` is constructed from matching input; values rejected by that constructor raise an error.
- **B004** — `deserialize` of a dataclass raises `ValidationError` when a required field is missing from the input mapping.
- **B005** — The package exposes `deserialize`, `serialize`, `validator`, `deserializer`, and `ValidationError` with the callable paths listed in this contract.
- **B006** — The submitted package source does not import the forbidden upstream package `apischema`.
<!-- featureliftbench:behavior-clauses:end -->
