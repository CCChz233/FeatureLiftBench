# FeatureLift Task: field_validator before/after

Extract pydantic-style field validator collection into `featurelifted`.

## Target API

```python
from featurelifted import field_validator, BaseModel, ValidationError
```

## Required Behavior

- `@field_validator` registers before/after validators on model classes.
- Before validators transform incoming values; after validators run on initialized attributes.
- `ValidationError` carries structured field errors.

## Constraints

- Forbidden imports: `pydantic`.
- No full type coercion or JSON schema export.
