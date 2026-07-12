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
