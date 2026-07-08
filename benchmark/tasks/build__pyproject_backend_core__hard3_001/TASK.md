# FeatureLift Task: PEP 517 build-system table validation

Extract build-system table parsing into `featurelifted`.

## Target API

```python
from featurelifted import validate_source_directory, parse_build_system_table, BuildException, BuildSystemTableValidationError
```

## Constraints

- Forbidden imports: `build`.
- No isolated environment or wheel build execution.
