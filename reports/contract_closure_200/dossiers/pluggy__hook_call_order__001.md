# pluggy__hook_call_order__001

- release: `frozen_python150`
- lift: `Direct`
- coupling: `unknown`
- strict validation: `PASS`
- tests/assertions: `5/22`

## Required API

- `featurelifted.PluginManager` (class) `(project_name)`
- `featurelifted.PluginManager.add_hookspecs` (method) `(self, module_or_class)`
- `featurelifted.PluginManager.get_name` (method) `(self, plugin)`
- `featurelifted.PluginManager.has_plugin` (method) `(self, name)`
- `featurelifted.PluginManager.hook` (attribute)
- `featurelifted.PluginManager.register` (method) `(self, plugin, name=None)`
- `featurelifted.PluginManager.unregister` (method) `(self, plugin=None, name=None)`
- `featurelifted.HookspecMarker` (class) `(project_name)`
- `featurelifted.HookimplMarker` (class) `(project_name)`
- `featurelifted.PluginValidationError` (exception)

## Public Behaviors

- **B001**: The extracted feature must support this observable behavior: declare hook specifications with HookspecMarker. Required observable cases include basic hook registration and ordering; validation unregister and plugin names.
- **B002**: The extracted feature must support this observable behavior: register plugins and call hook implementations through PluginManager. Required observable cases include basic hook registration and ordering; hook historic and subset hooknames.
- **B003**: The extracted feature must support this observable behavior: respect tryfirst and trylast ordering. Required observable cases include basic hook registration and ordering; validation unregister and plugin names.
- **B004**: The extracted feature must support this observable behavior: support firstresult hooks. Required observable cases include validation unregister and plugin names.
- **B005**: The extracted feature must support this observable behavior: support hookwrapper implementations that inspect or modify results. Required observable cases include firstresult and hookwrapper result mutation.
- **B006**: The extracted feature must support this observable behavior: reject unknown hook implementation arguments during validation. Required observable cases include validation unregister and plugin names.
- **B007**: The extracted feature must support this observable behavior: support unregistering plugins and querying registered plugin names. Required observable cases include validation unregister and plugin names.
- **B008**: The package exposes the required task API paths `featurelifted.PluginManager`, `featurelifted.PluginManager.add_hookspecs`, `featurelifted.PluginManager.get_name`, `featurelifted.PluginManager.has_plugin`, `featurelifted.PluginManager.hook`, `featurelifted.PluginManager.register`, `featurelifted.PluginManager.unregister`, `featurelifted.HookspecMarker`, `featurelifted.HookimplMarker`, `featurelifted.PluginValidationError` with the kinds and callable signatures listed in this contract.

## Tests

### `public_tests/test_public_api.py::test_basic_hook_registration_and_ordering`

- mapping: `B001, B002, B003`
- API: `featurelifted.HookimplMarker, featurelifted.HookspecMarker, featurelifted.PluginManager`
- risk: `ordering_semantics`
- A001 `assert` L32: `manager.hook.step(value='x') == ['first:x', 'last:x']`
- A002 `assert` L33: `manager.get_plugin('first') is not None`
- A003 `assert` L34: `manager.has_plugin('last')`

### `hidden_tests/test_hidden_behavior.py::test_firstresult_and_hookwrapper_result_mutation`

- mapping: `B005`
- API: `featurelifted.HookimplMarker, featurelifted.HookspecMarker, featurelifted.PluginManager`
- risk: `state_mutation`
- A001 `assert` L51: `manager.hook.choose(value='x') == 'x-last'`
- A002 `assert` L52: `manager.hook.wrapped(value='x') == ['x-base', 'wrapper']`

### `hidden_tests/test_hidden_behavior.py::test_validation_unregister_and_plugin_names`

- mapping: `B001, B003, B004, B006, B007`
- API: `featurelifted.HookimplMarker, featurelifted.HookspecMarker, featurelifted.PluginManager, featurelifted.PluginValidationError`
- risk: `exception_semantics`
- A001 `raises` L77: `pytest.raises(PluginValidationError)`
- A002 `assert` L82: `manager.get_name(plugin) == 'good'`
- A003 `assert` L83: `manager.hook.step(value='ok') == ['OK']`
- A004 `assert` L84: `manager.unregister(name='good') is plugin`
- A005 `assert` L85: `not manager.has_plugin('good')`

### `hidden_tests/test_hidden_behavior.py::test_hook_historic_and_subset_hooknames`

- mapping: `B002, B008`
- API: `featurelifted.HookimplMarker, featurelifted.HookspecMarker, featurelifted.PluginManager`
- risk: `none`
- A001 `assert` L109: `manager.hook.alpha(value='x') == ['x-a']`
- A002 `assert` L110: `set(manager.hook.__dict__.keys()) >= {'alpha', 'beta'}`

### `hidden_tests/test_required_api_surface.py::test_required_api_surface`

- mapping: `B008`
- API: `featurelifted.HookimplMarker, featurelifted.HookspecMarker, featurelifted.PluginManager, featurelifted.PluginValidationError`
- risk: `none`
- A001 `assert` L12: `isinstance(PluginManager, type)`
- A002 `assert` L13: `hasattr(PluginManager, 'add_hookspecs')`
- A003 `assert` L14: `hasattr(PluginManager, 'get_name')`
- A004 `assert` L15: `hasattr(PluginManager, 'has_plugin')`
- A005 `assert` L16: `PluginManager is not None`
- A006 `assert` L17: `hasattr(PluginManager, 'register')`
- A007 `assert` L18: `hasattr(PluginManager, 'unregister')`
- A008 `assert` L19: `isinstance(HookspecMarker, type)`
- A009 `assert` L20: `isinstance(HookimplMarker, type)`
- A010 `assert` L21: `issubclass(PluginValidationError, BaseException)`

## Dependency / Oracle Evidence

- allowed dependencies: `none`
- forbidden imports: `pluggy`
- source entrypoints: `pluggy.PluginManager, pluggy.HookspecMarker, pluggy.HookimplMarker, pluggy.PluginValidationError, pluggy.HookCallError`
- oracle source files: `none`
- runtime dependencies: `none`
