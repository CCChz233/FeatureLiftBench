# FeatureLift Task: Spec evaluation with Coalesce, T, and error paths

Extract a bounded glom interpreter subset into `featurelifted`.

## Target API

```python
from featurelifted import glom, T, Coalesce, PathAccessError
```

## Required Behavior

- `glom` evaluates dict/list/tuple specs, dotted path strings, callables, `T`, and `Coalesce`.
- `Coalesce` returns the first successful child spec or a configured default.
- Missing nested paths raise `PathAccessError`; `default=` on `glom` catches that error.

## Constraints

- Forbidden imports: `glom`.
- No CLI or streaming/grouping operators beyond this subset.

<!-- featureliftbench:behavior-clauses:start -->
## Public Behavior Contract

The stable clause IDs below define the public behavior contract. Hidden tests may exercise
these clauses but do not introduce additional requirements.

- **B001** — glom path evaluation
- **B002** — Coalesce
- **B003** — T target reference
- **B004** — path access errors
- **B005** — the declared target API remains importable and preserves upstream-observable semantics within the included and excluded feature scope
- **B006** — the submitted package does not import forbidden upstream packages: glom
<!-- featureliftbench:behavior-clauses:end -->
