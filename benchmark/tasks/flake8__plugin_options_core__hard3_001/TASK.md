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

<!-- featureliftbench:behavior-clauses:start -->
## Public Behavior Contract

The stable clause IDs below define the public behavior contract. Hidden tests may exercise
these clauses but do not introduce additional requirements.

- **B001** — plugin option registration
- **B002** — checker classification
- **B003** — select/ignore filtering
- **B004** — the declared target API remains importable and preserves upstream-observable semantics within the included and excluded feature scope
- **B005** — the submitted package does not import forbidden upstream packages: flake8
<!-- featureliftbench:behavior-clauses:end -->
