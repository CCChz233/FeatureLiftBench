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
