# FeatureLift Task: Result Success Failure safe

Extract returns Result pipeline helpers into `featurelifted`.

## Target API

```python
from featurelifted import Result, Success, Failure, safe
```

## Required Behavior

- `Success.map`/`bind` transform values; `Failure` short-circuits further transforms.
- `@safe` wraps callables and maps exceptions to `Failure`.

## Constraints

- Forbidden imports: `returns`.
- Result/Maybe subset only.

<!-- featureliftbench:behavior-clauses:start -->
## Public Behavior Contract

The stable clause IDs below define the public behavior contract. Hidden tests may exercise
these clauses but do not introduce additional requirements.

- **B001** — Result map/bind
- **B002** — Success/Failure containers
- **B003** — safe decorator
- **B004** — the declared target API remains importable and preserves upstream-observable semantics within the included and excluded feature scope
- **B005** — the submitted package does not import forbidden upstream packages: returns
<!-- featureliftbench:behavior-clauses:end -->
