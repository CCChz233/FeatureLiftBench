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
