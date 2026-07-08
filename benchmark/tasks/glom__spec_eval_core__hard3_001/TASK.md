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
