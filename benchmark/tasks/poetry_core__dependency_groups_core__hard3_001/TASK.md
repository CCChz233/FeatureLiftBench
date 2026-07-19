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

<!-- featureliftbench:behavior-clauses:start -->
## Public Behavior Contract

The stable clause IDs below define the public behavior contract. Hidden tests may exercise
these clauses but do not introduce additional requirements.

- **B001** — PEP 621 dependency parsing
- **B002** — dependency groups
- **B003** — include-group resolution
- **B004** — the declared target API remains importable and preserves upstream-observable semantics within the included and excluded feature scope
- **B005** — the submitted package does not import forbidden upstream packages: poetry, poetry_core
<!-- featureliftbench:behavior-clauses:end -->
