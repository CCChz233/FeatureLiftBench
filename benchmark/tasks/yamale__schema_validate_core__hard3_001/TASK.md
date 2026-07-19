# FeatureLift Task: YAML schema rule validation core

Extract an in-memory Yamale validation subset into `featurelifted`.

## Target API

```python
from featurelifted import make_schema, validate, ValidationResult, YamaleError
```

## Required Behavior

- `make_schema` parses one or more YAML documents; later documents provide `include` targets.
- Validate maps, lists, primitive types, optional fields, and included schemas.
- `strict=True` rejects unexpected keys; non-strict bool validation may accept common string/int aliases.
- `validate` returns `ValidationResult` objects and raises `YamaleError` when invalid and `_raise_error=True`.

## Constraints

- Forbidden imports: `yamale`.
- Allowed dependency: `PyYAML` from `requirements.lock`.
- Use in-memory YAML strings only.

<!-- featureliftbench:behavior-clauses:start -->
## Public Behavior Contract

The stable clause IDs below define the public behavior contract. Hidden tests may exercise
these clauses but do not introduce additional requirements.

- **B001** — in-memory YAML schema parsing
- **B002** — map/list validators
- **B003** — include documents
- **B004** — strict validation
- **B005** — the declared target API remains importable and preserves upstream-observable semantics within the included and excluded feature scope
- **B006** — the submitted package does not import forbidden upstream packages: yamale
<!-- featureliftbench:behavior-clauses:end -->
