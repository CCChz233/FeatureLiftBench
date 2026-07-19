# FeatureLift Task: Event registry dispatch core

Extract a SQLAlchemy-style event dispatch subset into `featurelifted`.

## Target API

```python
from featurelifted import listen, remove, dispatch, EventTarget
```

## Required Behavior

- `listen` registers listeners for `(target, identifier)` pairs.
- `dispatch` invokes active listeners; `once=True` listeners run at most once.
- `remove` during dispatch must not break in-flight dispatch.
- `propagate=True` also registers on subclasses.
- `named=True` invokes listeners with keyword arguments.

## Constraints

- Forbidden imports: `sqlalchemy`.
- No database or ORM runtime required.

<!-- featureliftbench:behavior-clauses:start -->
## Public Behavior Contract

The stable clause IDs below define the public behavior contract. Hidden tests may exercise
these clauses but do not introduce additional requirements.

- **B001** — listener registration/removal
- **B002** — dispatch ordering
- **B003** — once semantics
- **B004** — subclass propagation
- **B005** — named kwargs
- **B006** — the declared target API remains importable and preserves upstream-observable semantics within the included and excluded feature scope
- **B007** — the submitted package does not import forbidden upstream packages: sqlalchemy
<!-- featureliftbench:behavior-clauses:end -->
