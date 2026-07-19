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

<!-- featureliftbench:behavior-clauses:start -->
## Public Behavior Contract

The stable clause IDs below define the public behavior contract. Hidden tests may exercise
these clauses but do not introduce additional requirements.

- **B001** — nested dict validation
- **B002** — Optional defaults
- **B003** — Or/And composition
- **B004** — the declared target API remains importable and preserves upstream-observable semantics within the included and excluded feature scope
- **B005** — the submitted package does not import forbidden upstream packages: schema
<!-- featureliftbench:behavior-clauses:end -->
