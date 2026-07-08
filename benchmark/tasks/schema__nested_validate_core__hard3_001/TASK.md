# FeatureLift Task: Schema Optional Or And

Extract keleshev/schema validation core into `featurelifted`.

## Target API

```python
from featurelifted import Schema, Optional, Or, And, SchemaError
```

## Required Behavior

- `Schema` validates nested dicts with type and literal rules.
- `Optional` supplies defaults for missing keys.
- `Or` and `And` compose validators.
- Extra keys raise `SchemaError`.

## Constraints

- Forbidden imports: `schema`.
- No network access.
