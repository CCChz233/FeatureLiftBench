# jupyter_server__extension_config_core__hard3_001

- release: `frozen_python150`
- lift: `Composite`
- coupling: `unknown`
- strict validation: `PASS`
- tests/assertions: `5/14`

## Required API

- `featurelifted.ExtensionConfigStore` (class) `(config_dir: 'str | Path') -> 'None'`
- `featurelifted.ExtensionConfigStore.disable` (method) `(self, name: 'str') -> 'None'`
- `featurelifted.ExtensionConfigStore.enabled` (method) `(self, name: 'str') -> 'bool'`
- `featurelifted.ExtensionConfigStore.get_extensions` (method) `(self) -> 'dict[str, bool]'`
- `featurelifted.merge_extension_configs` (function) `(config_paths: 'list[str | Path]') -> 'dict[str, bool]'`
- `featurelifted.filter_enabled_extensions` (function) `(entry_points: 'list[str]', extensions: 'dict[str, bool]') -> 'list[str]'`
- `featurelifted.recursive_update` (function) `(target: 'dict[str, Any]', new: 'dict[str, Any]') -> 'None'`

## Public Behaviors

- **B001**: When extension config fragments are merged, recursive_update combines nested mappings while later fragments override earlier scalar values.
- **B002**: When ExtensionConfigStore enables or disables an extension, it writes and reloads the corresponding per-extension JSON state.
- **B003**: When entry-point extensions are filtered, explicitly disabled names are omitted and enabled or unspecified names remain discoverable.
- **B004**: The package exposes the required task API paths `featurelifted.ExtensionConfigStore`, `featurelifted.ExtensionConfigStore.disable`, `featurelifted.ExtensionConfigStore.enabled`, `featurelifted.ExtensionConfigStore.get_extensions`, `featurelifted.merge_extension_configs`, `featurelifted.filter_enabled_extensions`, `featurelifted.recursive_update` with the kinds and callable signatures listed in this contract.

## Tests

### `public_tests/test_public_contract.py::test_recursive_update_and_enable`

- mapping: `B001, B002`
- API: `featurelifted.ExtensionConfigStore, featurelifted.recursive_update`
- risk: `filesystem_resource, state_mutation`
- A001 `assert` L11: `target['ServerApp']['jpserver_extensions'] == {'a': True, 'b': True}`
- A002 `assert` L15: `store.enabled('demo')`

### `hidden_tests/test_hidden_contract.py::test_config_precedence_and_disable`

- mapping: `B001, B002`
- API: `featurelifted.ExtensionConfigStore, featurelifted.merge_extension_configs`
- risk: `filesystem_resource`
- A001 `assert` L16: `store.get_extensions() == {'a': True, 'b': False}`
- A002 `assert` L18: `store.enabled('a') is False`
- A003 `assert` L21: `merged['b'] is False`

### `hidden_tests/test_hidden_contract.py::test_filter_enabled_extensions_masks_disabled`

- mapping: `B002, B003`
- API: `featurelifted.filter_enabled_extensions`
- risk: `none`
- A001 `assert` L27: `filter_enabled_extensions(eps, cfg) == ['a', 'c']`

### `hidden_tests/test_hidden_contract.py::test_recursive_update_prunes_empty_nested_dicts`

- mapping: `B001`
- API: `featurelifted.recursive_update`
- risk: `state_mutation`
- A001 `assert` L33: `'ServerApp' not in target or 'jpserver_extensions' not in target.get('ServerApp', {})`

### `hidden_tests/test_required_api_surface.py::test_required_api_surface`

- mapping: `B004`
- API: `featurelifted.ExtensionConfigStore, featurelifted.filter_enabled_extensions, featurelifted.merge_extension_configs, featurelifted.recursive_update`
- risk: `none`
- A001 `assert` L12: `isinstance(ExtensionConfigStore, type)`
- A002 `assert` L13: `hasattr(ExtensionConfigStore, 'disable')`
- A003 `assert` L14: `hasattr(ExtensionConfigStore, 'enabled')`
- A004 `assert` L15: `hasattr(ExtensionConfigStore, 'get_extensions')`
- A005 `assert` L16: `callable(merge_extension_configs)`
- A006 `assert` L17: `callable(filter_enabled_extensions)`
- A007 `assert` L18: `callable(recursive_update)`

## Dependency / Oracle Evidence

- allowed dependencies: `none`
- forbidden imports: `jupyter_server`
- source entrypoints: `jupyter_server.extension.config.ExtensionConfigManager`
- oracle source files: `repo/jupyter_server/extension/config.py, repo/jupyter_server/config_manager.py`
- runtime dependencies: `none`
- oracle notes: Extension config merge subset without server runtime.
