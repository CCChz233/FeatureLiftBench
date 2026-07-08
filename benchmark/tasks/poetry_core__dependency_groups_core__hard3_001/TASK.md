# FeatureLift Task: PEP 621 metadata and dependency group resolver

Extract dependency group resolution into `featurelifted`.

## Target API

```python
from featurelifted import parse_project_dependencies, resolve_group, DependencyGroup, DependencySpec
```

## Required Behavior

- `parse_project_dependencies` builds `DependencyGroup` objects from PEP 621 project metadata.
- `resolve_group` resolves a group's dependencies including transitive `include-group` references.
- Circular includes raise `ValueError`.

## Constraints

- Forbidden imports: `poetry`, `poetry_core`.
- No package build backend.
