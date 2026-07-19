# FeatureLift Task: Signal registry and receiver dispatch

Extract Celery-style signal dispatch into `featurelifted`.

## Target API

```python
from featurelifted import Signal
```

## Required Behavior

- `connect` registers receivers with optional sender filtering, `dispatch_uid`, and weak references.
- `send` invokes matching receivers and captures exceptions in response tuples.
- Weak receivers are removed after their bound object is collected.

## Constraints

- Forbidden imports: `celery`.
- No broker or task execution.

<!-- featureliftbench:behavior-clauses:start -->
## Public Behavior Contract

The stable clause IDs below define the public behavior contract. Hidden tests may exercise
these clauses but do not introduce additional requirements.

- **B001** — receiver registration
- **B002** — sender filtering
- **B003** — dispatch responses
- **B004** — weak receiver cleanup
- **B005** — the declared target API remains importable and preserves upstream-observable semantics within the included and excluded feature scope
- **B006** — the submitted package does not import forbidden upstream packages: celery
<!-- featureliftbench:behavior-clauses:end -->
