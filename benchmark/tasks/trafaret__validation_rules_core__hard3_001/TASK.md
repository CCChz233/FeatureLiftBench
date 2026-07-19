# FeatureLift Task: Composable trafaret validation rules

Extract composable trafaret validation into `featurelifted`.

## Target API

```python
from featurelifted import Int, String, Dict, Key, Or, And, Forward, DataError
```

## Required Behavior

- `Dict`, `Key`, `Or`, `And`, and `Forward` compose validation rules.
- `DataError` carries a path tuple for nested validation failures.
- `Forward.set_type` enables recursive schemas.

## Constraints

- Forbidden imports: `trafaret`.
- No async or internet validators.

<!-- featureliftbench:behavior-clauses:start -->
## Public Behavior Contract

The stable clause IDs below define the public behavior contract. Hidden tests may exercise
these clauses but do not introduce additional requirements.

- **B001** — composable validators
- **B002** — DataError paths
- **B003** — Forward references
- **B004** — the declared target API remains importable and preserves upstream-observable semantics within the included and excluded feature scope
- **B005** — the submitted package does not import forbidden upstream packages: trafaret
<!-- featureliftbench:behavior-clauses:end -->
