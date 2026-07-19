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

<!-- featureliftbench:behavior-clauses:start -->
## Public Behavior Contract

The stable clause IDs below define the public behavior contract. Hidden tests may exercise
these clauses but do not introduce additional requirements.

- **B001** — field_validator decorator
- **B002** — before/after modes
- **B003** — ValidationError aggregation
- **B004** — the declared target API remains importable and preserves upstream-observable semantics within the included and excluded feature scope
- **B005** — the submitted package does not import forbidden upstream packages: pydantic
<!-- featureliftbench:behavior-clauses:end -->
