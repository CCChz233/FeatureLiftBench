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
