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
