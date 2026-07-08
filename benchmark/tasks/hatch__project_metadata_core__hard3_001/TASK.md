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
