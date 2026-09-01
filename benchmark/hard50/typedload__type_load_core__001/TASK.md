# FeatureLift Task: Typed JSON-like loader

Build a standalone `featurelifted` package that loads JSON-like data into typing-annotated dataclasses, unions, and TypedDicts.

The submitted implementation must not import the upstream package or read from `repo/` at runtime, must not use the network, and must not depend on external services. Use only the standard library unless the task lockfile allows otherwise.

## Target API

```python
from featurelifted import (
    dump,
    exceptions,
    load,
    typechecks,
)
```

## Required API Details

- `load(value, type_, **kwargs)`
- `dump(value, **kwargs)`
- `typechecks` module must be importable
- `typechecks.is_dataclass(type_) -> bool`
- `exceptions.TypedloadException` must be importable and raisable

## Required Behavior

- `load` constructs a dataclass, including nested dataclass fields, from a JSON-like mapping, and `dump` returns a JSON-like mapping of that instance.
- `load` selects a matching `Union` alternative for integers and strings.
- `load` into a TypedDict accepts the declared keys.
- When `failonextra=True`, extra mapping keys raise `TypedloadException`.
- The package exposes `load`, `dump`, `typechecks.is_dataclass`, and `exceptions.TypedloadException` with the callable paths listed in this contract.
- The submitted package source does not import the forbidden upstream package `typedload`.

## Constraints

- Forbidden imports: `typedload`.
- Do not implement attr plugin extras beyond declared.
- Do not implement runtime import of typedload.

<!-- featureliftbench:behavior-clauses:start -->
## Public Behavior Contract

The stable clause IDs below define the public behavior contract. Hidden tests may exercise these clauses but do not introduce additional requirements.

- **B001** — `load` constructs a dataclass, including nested dataclass fields, from a JSON-like mapping, and `dump` returns a JSON-like mapping of that instance.
- **B002** — `load` selects a matching `Union` alternative for integers and strings.
- **B003** — `load` into a TypedDict accepts the declared keys.
- **B004** — When `failonextra=True`, extra mapping keys raise `TypedloadException`.
- **B005** — The package exposes `load`, `dump`, `typechecks.is_dataclass`, and `exceptions.TypedloadException` with the callable paths listed in this contract.
- **B006** — The submitted package source does not import the forbidden upstream package `typedload`.
<!-- featureliftbench:behavior-clauses:end -->
