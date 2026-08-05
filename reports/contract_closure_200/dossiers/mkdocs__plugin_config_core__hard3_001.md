# mkdocs__plugin_config_core__hard3_001

- release: `frozen_python150`
- lift: `Composite`
- coupling: `unknown`
- strict validation: `PASS`
- tests/assertions: `5/12`

## Required API

- `featurelifted.PluginConfig` (class) `(name: 'str', enabled: 'bool' = True, options: 'dict[str, Any]' = <factory>, priority: 'int' = 0) -> None`
- `featurelifted.PluginCollection` (class) `() -> 'None'`
- `featurelifted.PluginCollection.load` (method) `(self, specs: 'list[PluginConfig]', hook_registry: 'dict[str, Callable[..., Any]] | None' = None) -> 'None'`
- `featurelifted.PluginCollection.names` (attribute)
- `featurelifted.PluginCollection.run_event` (method) `(self, event_name: 'str', **kwargs) -> 'list[Any]'`
- `featurelifted.validate_plugin_config` (function) `(name: 'str', options: 'dict[str, Any]', schema: 'dict[str, type]') -> 'list[str]'`

## Public Behaviors

- **B001**: `validate_plugin_config` reports missing, mistyped, and unexpected options.
- **B002**: `PluginCollection.load` skips disabled plugins and registers hooks.
- **B003**: `run_event` invokes hooks in ascending priority order.
- **B004**: The package exposes the required task API paths `featurelifted.PluginConfig`, `featurelifted.PluginCollection`, `featurelifted.PluginCollection.load`, `featurelifted.PluginCollection.names`, `featurelifted.PluginCollection.run_event`, `featurelifted.validate_plugin_config` with the kinds and callable signatures listed in this contract.

## Tests

### `public_tests/test_public_contract.py::test_plugin_collection_runs_event_by_priority`

- mapping: `B002`
- API: `featurelifted.PluginCollection, featurelifted.PluginConfig`
- risk: `ordering_semantics`
- A001 `assert` L15: `collection.run_event('on_config') == ['b', 'a']`

### `hidden_tests/test_hidden_contract.py::test_disabled_plugins_are_excluded`

- mapping: `B003`
- API: `featurelifted.PluginCollection, featurelifted.PluginConfig`
- risk: `none`
- A001 `assert` L12: `collection.names == ['enabled']`
- A002 `assert` L13: `collection.run_event('on_config') == [1]`

### `hidden_tests/test_hidden_contract.py::test_validate_plugin_config_reports_schema_errors`

- mapping: `B001, B002`
- API: `featurelifted.validate_plugin_config`
- risk: `none`
- A001 `assert` L18: `any(('missing required option enabled' in e for e in errors))`
- A002 `assert` L19: `any(('lang must be str' in e for e in errors))`

### `hidden_tests/test_hidden_contract.py::test_unexpected_option_reported`

- mapping: `B001`
- API: `featurelifted.validate_plugin_config`
- risk: `none`
- A001 `assert` L24: `any(('unexpected option extra' in e for e in errors))`

### `hidden_tests/test_required_api_surface.py::test_required_api_surface`

- mapping: `B004`
- API: `featurelifted.PluginCollection, featurelifted.PluginConfig, featurelifted.validate_plugin_config`
- risk: `none`
- A001 `assert` L11: `isinstance(PluginConfig, type)`
- A002 `assert` L12: `isinstance(PluginCollection, type)`
- A003 `assert` L13: `hasattr(PluginCollection, 'load')`
- A004 `assert` L14: `PluginCollection is not None`
- A005 `assert` L15: `hasattr(PluginCollection, 'run_event')`
- A006 `assert` L16: `callable(validate_plugin_config)`

## Dependency / Oracle Evidence

- allowed dependencies: `none`
- forbidden imports: `mkdocs`
- source entrypoints: `mkdocs.plugins.BasePlugin, mkdocs.plugins.PluginCollection`
- oracle source files: `repo/mkdocs/plugins.py, repo/mkdocs/config/base.py`
- runtime dependencies: `none`
- oracle notes: Plugin planning subset without build/render pipeline.
