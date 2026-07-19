# FeatureLift Task: normalize_project_metadata select_environment

Extract hatchling metadata normalization into `featurelifted`.

## Target API

```python
from featurelifted import normalize_project_metadata, select_environment, MetadataValidationError
```

## Required Behavior

- `normalize_project_metadata` lowercases names, sorts dependencies, and validates classifiers.
- `select_environment` resolves environment inheritance and include chains.
- Circular inheritance raises `ValueError`; invalid classifiers raise `MetadataValidationError`.

## Constraints

- Forbidden imports: `hatch`, `hatchling`.
- No build or environment execution.

<!-- featureliftbench:behavior-clauses:start -->
## Public Behavior Contract

The stable clause IDs below define the public behavior contract. Hidden tests may exercise
these clauses but do not introduce additional requirements.

- **B001** — project metadata normalization
- **B002** — environment inheritance
- **B003** — classifier validation
- **B004** — the declared target API remains importable and preserves upstream-observable semantics within the included and excluded feature scope
- **B005** — the submitted package does not import forbidden upstream packages: hatch, hatchling
<!-- featureliftbench:behavior-clauses:end -->
