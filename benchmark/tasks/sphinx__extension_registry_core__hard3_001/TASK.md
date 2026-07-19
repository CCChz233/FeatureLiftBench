# FeatureLift Task: Directive/role registry and extension setup loader

Extract a bounded Sphinx registry subset into `featurelifted`.

## Target API

```python
from featurelifted import ComponentRegistry, ExtensionMetadata, ExtensionError
```

## Required Behavior

- `add_directive` and `add_role` register components; duplicates raise `ExtensionError` unless `override=True`.
- `load_extension` invokes a setup callable, records the extension, and returns `ExtensionMetadata`.
- Setup failures are wrapped in `ExtensionError`.

## Constraints

- Forbidden imports: `sphinx`.
- No builder or application startup required.

<!-- featureliftbench:behavior-clauses:start -->
## Public Behavior Contract

The stable clause IDs below define the public behavior contract. Hidden tests may exercise
these clauses but do not introduce additional requirements.

- **B001** — directive/role registry
- **B002** — extension setup loader
- **B003** — duplicate registration errors
- **B004** — the declared target API remains importable and preserves upstream-observable semantics within the included and excluded feature scope
- **B005** — the submitted package does not import forbidden upstream packages: sphinx
<!-- featureliftbench:behavior-clauses:end -->
