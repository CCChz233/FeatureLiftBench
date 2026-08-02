# FeatureLift Task: typeguard check_type pipeline

Extract a task-scoped subset of `typeguard` into a standalone `featurelifted` package.

The submitted implementation must not import the upstream package or read from `repo/` at runtime, must not use the network, and must not depend on external services. Use only the standard library unless the task lockfile allows otherwise.

## Target API

```python
from featurelifted import (
    check_type,
    CollectionCheckStrategy,
    TypeCheckError,
)
```

## Required API Details

- `check_type(value, expected_type, *, collection_check_strategy=...)`
- `TypeCheckError` class must be importable
- `CollectionCheckStrategy` class must be importable

## Required Behavior

- The extracted feature must support this observable behavior: check_type for nested list/dict. Required observable cases include nested collections.
- The extracted feature must support this observable behavior: Optional/Union handling. Required observable cases include optional union.
- The extracted feature must support this observable behavior: TypeCheckError on mismatch and CollectionCheckStrategy differences. Required observable cases include type check error; first item strategy can miss.
- dict[str, list[int]] nesting is checked.
- The package exposes check_type/TypeCheckError/CollectionCheckStrategy with the kinds listed in this contract.
- the submitted package does not import forbidden upstream packages: typeguard.

## Constraints

- Forbidden imports: `typeguard`.
- Do not implement pytest plugin.
- Do not implement import hook.
- Do not implement original typeguard import at runtime.

<!-- featureliftbench:behavior-clauses:start -->
## Public Behavior Contract

The stable clause IDs below define the public behavior contract. Hidden tests may exercise these clauses but do not introduce additional requirements.

- **B001** — The extracted feature must support this observable behavior: check_type for nested list/dict. Required observable cases include nested collections.
- **B002** — The extracted feature must support this observable behavior: Optional/Union handling. Required observable cases include optional union.
- **B003** — The extracted feature must support this observable behavior: TypeCheckError on mismatch and CollectionCheckStrategy differences. Required observable cases include type check error; first item strategy can miss.
- **B004** — dict[str, list[int]] nesting is checked.
- **B005** — The package exposes check_type/TypeCheckError/CollectionCheckStrategy with the kinds listed in this contract.
- **B006** — the submitted package does not import forbidden upstream packages: typeguard.
<!-- featureliftbench:behavior-clauses:end -->
