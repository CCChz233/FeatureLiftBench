# FeatureLift Task: Server extension discovery and enable/disable config merge

Extract a Jupyter Server extension config subset into `featurelifted`.

## Target API

```python
from featurelifted import ExtensionConfigStore, merge_extension_configs, filter_enabled_extensions, recursive_update
```

## Required Behavior

- `recursive_update` deep-merges dicts; `None` removes keys; empty nested dicts are pruned.
- `ExtensionConfigStore` reads merged `jpserver_extensions` from root config and `config.d` fragments.
- `enable`/`disable` write per-extension JSON fragments.
- `filter_enabled_extensions` drops entry points explicitly disabled in config.

## Constraints

- Forbidden imports: `jupyter_server`.
- No network or server process.
