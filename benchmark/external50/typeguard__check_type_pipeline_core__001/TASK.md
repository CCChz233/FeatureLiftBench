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

- check_type returns the original value when lists and dictionaries satisfy their parameterized element, key, and value types, including dict[str, list[int]].
- check_type accepts None for Optional[int] and values matching any Union member, but raises TypeCheckError when a non-member value such as a string is checked against Optional[int].
- CollectionCheckStrategy.FIRST_ITEM may accept a heterogeneous collection after checking only its first item, whereas ALL_ITEMS checks every item and raises TypeCheckError on a later mismatch.
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

- **B001** — check_type returns the original value when lists and dictionaries satisfy their parameterized element, key, and value types, including dict[str, list[int]].
- **B002** — check_type accepts None for Optional[int] and values matching any Union member, but raises TypeCheckError when a non-member value such as a string is checked against Optional[int].
- **B003** — CollectionCheckStrategy.FIRST_ITEM may accept a heterogeneous collection after checking only its first item, whereas ALL_ITEMS checks every item and raises TypeCheckError on a later mismatch.
- **B004** — dict[str, list[int]] nesting is checked.
- **B005** — The package exposes check_type/TypeCheckError/CollectionCheckStrategy with the kinds listed in this contract.
- **B006** — the submitted package does not import forbidden upstream packages: typeguard.
<!-- featureliftbench:behavior-clauses:end -->
