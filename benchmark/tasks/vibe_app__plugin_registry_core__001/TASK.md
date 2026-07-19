# FeatureLift Task: Plugin registry and metaclass discovery

Extract VibeShop plugin registration, metaclass discovery, and dispatch as a standalone package.

## Target API

- Import: `from featurelifted import BasePlugin, PluginMeta, PluginRegistry; from featurelifted.state import GLOBAL_STATE, reset_state`
- Callable: `featurelifted.PluginRegistry.register`
- Signature: `PluginRegistry.register(plugin: BasePlugin) -> str`

## Excluded Behavior

- Flask-ish routes and HTTP handlers
- YAML bootstrap, pricing, CSV, and ORM modules
- get_plugin_v1 and register_plugin_legacy wrong helpers
- setuptools entry point loading
- original project tests and CLI entrypoints

## Constraints

- Output package: `featurelifted`
- Network access: `false`
- Forbidden upstream imports: `vibe_app`

<!-- featureliftbench:behavior-clauses:start -->
## Public Behavior Contract

The stable clause IDs below define the public behavior contract. Hidden tests may exercise
these clauses but do not introduce additional requirements.

- **B001** — register plugin instances and resolve them by name
- **B002** — dispatch run(payload) on registered plugins
- **B003** — auto-register plugin subclasses via PluginMeta into GLOBAL_STATE
- **B004** — discover plugin classes registered by metaclass
- **B005** — track plugin names in GLOBAL_STATE plugin_names list
- **B006** — the declared target API remains importable and preserves upstream-observable semantics within the included and excluded feature scope
- **B007** — the submitted package does not import forbidden upstream packages: vibe_app
<!-- featureliftbench:behavior-clauses:end -->
