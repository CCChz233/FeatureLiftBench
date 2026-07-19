# FeatureLift Task: PEP 517 build-system table validation

Extract build-system table parsing into `featurelifted`.

## Target API

```python
from featurelifted import validate_source_directory, parse_build_system_table, BuildException, BuildSystemTableValidationError
```

## Constraints

- Forbidden imports: `build`.
- No isolated environment or wheel build execution.

<!-- featureliftbench:behavior-clauses:start -->
## Public Behavior Contract

The stable clause IDs below define the public behavior contract. Hidden tests may exercise
these clauses but do not introduce additional requirements.

- **B001** — pyproject build-system parsing
- **B002** — source directory validation
- **B003** — the declared target API remains importable and preserves upstream-observable semantics within the included and excluded feature scope
- **B004** — the submitted package does not import forbidden upstream packages: build
<!-- featureliftbench:behavior-clauses:end -->
