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

<!-- featureliftbench:behavior-clauses:start -->
## Public Behavior Contract

The stable clause IDs below define the public behavior contract. Hidden tests may exercise
these clauses but do not introduce additional requirements.

- **B001** — extension config merge
- **B002** — enable/disable
- **B003** — entry point filtering
- **B004** — the declared target API remains importable and preserves upstream-observable semantics within the included and excluded feature scope
- **B005** — the submitted package does not import forbidden upstream packages: jupyter_server
<!-- featureliftbench:behavior-clauses:end -->
