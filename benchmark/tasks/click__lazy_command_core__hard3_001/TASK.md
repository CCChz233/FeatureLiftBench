# FeatureLift Task: LazyCommandCollection

Extract click lazy command collection into `featurelifted`.

## Target API

```python
from featurelifted import LazyCommandCollection, Command, UsageError
```

## Required Behavior

- `LazyCommandCollection` lazily loads commands from callables and caches them.
- `resolve()` returns `(Context, Command, args)` for an argv list.
- Optional `envvar` supplies JSON default maps for nested command contexts.
- Missing commands raise `UsageError`.

## Constraints

- Forbidden imports: `click`.
- No shell completion or full CLI runner.

<!-- featureliftbench:behavior-clauses:start -->
## Public Behavior Contract

The stable clause IDs below define the public behavior contract. Hidden tests may exercise
these clauses but do not introduce additional requirements.

- **B001** — lazy command loading
- **B002** — context defaults
- **B003** — command resolution
- **B004** — the declared target API remains importable and preserves upstream-observable semantics within the included and excluded feature scope
- **B005** — the submitted package does not import forbidden upstream packages: click
<!-- featureliftbench:behavior-clauses:end -->
