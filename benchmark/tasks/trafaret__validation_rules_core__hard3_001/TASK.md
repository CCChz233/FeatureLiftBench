# FeatureLift Task: Composable trafaret validation rules

Extract composable trafaret validation into `featurelifted`.

## Target API

```python
from featurelifted import Int, String, Dict, Key, Or, And, Forward, DataError
```

## Required Behavior

- `Dict`, `Key`, `Or`, `And`, and `Forward` compose validation rules.
- `DataError` carries a path tuple for nested validation failures.
- `Forward.set_type` enables recursive schemas.

## Constraints

- Forbidden imports: `trafaret`.
- No async or internet validators.
