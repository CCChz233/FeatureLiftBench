# FeatureLift Task: Plugin registry and metaclass discovery

Extract a task-scoped subset of `vibe_app` into a standalone `featurelifted` package.

The submitted implementation must not import the upstream package or read from `repo/` at runtime, must not use the network, and must not depend on external services. Use only the standard library unless the task lockfile allows otherwise.

## Target API

```python
from featurelifted import (
    BasePlugin,
    PluginMeta,
    PluginRegistry,
    state,
)
```

## Required API Details

- `BasePlugin()` class constructor
- `PluginMeta(name: 'str', bases: 'tuple[type, ...]', namespace: 'dict[str, Any]') -> 'None'` class constructor
- `PluginRegistry() -> 'None'` class constructor
  - `PluginRegistry.register(self, plugin: 'BasePlugin') -> 'str'`
  - `PluginRegistry.discover_classes(self) -> 'dict[str, type[BasePlugin]]'`
  - `PluginRegistry.run(self, name: 'str', payload: 'dict[str, Any]') -> 'dict[str, Any]'`
- `state` module must be importable
  - `state.GLOBAL_STATE` constant must exist
  - `state.reset_state() -> 'None'`

## Required Behavior

- The extracted feature must support this observable behavior: register plugin instances and resolve them by name. Required observable cases include register and run plugin; list plugins returns registered names; run raises for disabled plugin.
- The extracted feature must support this observable behavior: dispatch run(payload) on registered plugins. Required observable cases include register and run plugin; run raises for disabled plugin.
- The extracted feature must support this observable behavior: auto-register plugin subclasses via PluginMeta into GLOBAL_STATE. Required observable cases include register tracks names in global state.
- The extracted feature must support this observable behavior: discover plugin classes registered by metaclass. Required observable cases include metaclass registers plugin classes.
- The extracted feature must support this observable behavior: track plugin names in GLOBAL_STATE plugin_names list. Required observable cases include register tracks names in global state.
- The package exposes the required task API paths `featurelifted.BasePlugin`, `featurelifted.PluginMeta`, `featurelifted.PluginRegistry`, `featurelifted.PluginRegistry.register`, `featurelifted.PluginRegistry.discover_classes`, `featurelifted.PluginRegistry.run`, `featurelifted.state`, `featurelifted.state.GLOBAL_STATE`, `featurelifted.state.reset_state` with the kinds and callable signatures listed in this contract.

## Constraints

- Forbidden imports: `vibe_app`.
- Do not implement Flask-ish routes and HTTP handlers.
- Do not implement YAML bootstrap, pricing, CSV, and ORM modules.
- Do not implement get_plugin_v1 and register_plugin_legacy wrong helpers.
- Do not implement setuptools entry point loading.
- Do not implement original project tests and CLI entrypoints.

## Public vs Hidden Tests

Benchmark evaluator tests remain private. Each evaluator test maps to the public behaviors above and only deepens examples, boundaries, or combinations within those declared behaviors.

<!-- featureliftbench:behavior-clauses:start -->
## Public Behavior Contract

The stable clause IDs below define the public behavior contract. Hidden tests may exercise these clauses but do not introduce additional requirements.

- **B001** — The extracted feature must support this observable behavior: register plugin instances and resolve them by name. Required observable cases include register and run plugin; list plugins returns registered names; run raises for disabled plugin.
- **B002** — The extracted feature must support this observable behavior: dispatch run(payload) on registered plugins. Required observable cases include register and run plugin; run raises for disabled plugin.
- **B003** — The extracted feature must support this observable behavior: auto-register plugin subclasses via PluginMeta into GLOBAL_STATE. Required observable cases include register tracks names in global state.
- **B004** — The extracted feature must support this observable behavior: discover plugin classes registered by metaclass. Required observable cases include metaclass registers plugin classes.
- **B005** — The extracted feature must support this observable behavior: track plugin names in GLOBAL_STATE plugin_names list. Required observable cases include register tracks names in global state.
- **B006** — The package exposes the required task API paths `featurelifted.BasePlugin`, `featurelifted.PluginMeta`, `featurelifted.PluginRegistry`, `featurelifted.PluginRegistry.register`, `featurelifted.PluginRegistry.discover_classes`, `featurelifted.PluginRegistry.run`, `featurelifted.state`, `featurelifted.state.GLOBAL_STATE`, `featurelifted.state.reset_state` with the kinds and callable signatures listed in this contract.
- **B007** — the submitted package does not import forbidden upstream packages: vibe_app.
<!-- featureliftbench:behavior-clauses:end -->
