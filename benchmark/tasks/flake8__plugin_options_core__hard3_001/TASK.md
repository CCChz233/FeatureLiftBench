# FeatureLift Task: Plugin option registration and checker selection

Extract a flake8 plugin planning subset into `featurelifted`.

## Target API

```python
from featurelifted import OptionManager, PluginSpec, OptionSpec, classify_plugins, apply_select_ignore
```

## Required Behavior

- Register per-plugin options in `OptionManager`.
- Classify plugins into tree, logical_line, and physical_line checker groups.
- `apply_select_ignore` enables plugins whose codes intersect `select` and not `ignore`; when `select` is empty, ignore disables matching plugins.

## Constraints

- Forbidden imports: `flake8`.
- No file linting or CLI required.
