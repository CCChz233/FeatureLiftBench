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
