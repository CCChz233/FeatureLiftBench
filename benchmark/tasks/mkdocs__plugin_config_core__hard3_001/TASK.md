# FeatureLift Task: Plugin config loading and event dispatch plan

Extract an offline MkDocs plugin planning subset into `featurelifted`.

## Target API

```python
from featurelifted import PluginConfig, PluginCollection, validate_plugin_config
```

## Required Behavior

- `validate_plugin_config` reports missing, mistyped, and unexpected options.
- `PluginCollection.load` skips disabled plugins and registers hooks.
- `run_event` invokes hooks in ascending priority order.

## Constraints

- Forbidden imports: `mkdocs`.
- Offline config-only slice.

<!-- featureliftbench:behavior-clauses:start -->
## Public Behavior Contract

The stable clause IDs below define the public behavior contract. Hidden tests may exercise
these clauses but do not introduce additional requirements.

- **B001** — plugin config validation
- **B002** — event dispatch ordering
- **B003** — disabled plugin handling
- **B004** — the declared target API remains importable and preserves upstream-observable semantics within the included and excluded feature scope
- **B005** — the submitted package does not import forbidden upstream packages: mkdocs
<!-- featureliftbench:behavior-clauses:end -->
