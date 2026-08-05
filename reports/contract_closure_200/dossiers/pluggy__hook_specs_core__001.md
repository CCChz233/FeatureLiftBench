# pluggy__hook_specs_core__001

- release: `frozen_python150`
- lift: `Direct`
- coupling: `unknown`
- strict validation: `PASS`
- tests/assertions: `6/13`

## Required API

- `featurelifted.PluginManager` (class) `(project_name)`
- `featurelifted.PluginManager.check_pending` (method) `(self)`
- `featurelifted.PluginManager.add_hookspecs` (method) `(self, module_or_class)`
- `featurelifted.PluginManager.hook` (attribute)
- `featurelifted.PluginManager.register` (method) `(self, plugin, name=None)`
- `featurelifted.HookspecMarker` (class) `(project_name)`
- `featurelifted.HookimplMarker` (class) `(project_name)`
- `featurelifted.PluginValidationError` (exception)

## Public Behaviors

- **B001**: The extracted feature must support this observable behavior: declare hook specifications with HookspecMarker including firstresult and historic flags. Required observable cases include hookwrapper must be generator.
- **B002**: The extracted feature must support this observable behavior: reject hook implementations with unknown arguments during registration. Required observable cases include unknown hook argument rejected; hookwrapper must be generator.
- **B003**: The extracted feature must support this observable behavior: reject hookwrapper implementations that are not generator functions. Required observable cases include hookwrapper must be generator.
- **B004**: The extracted feature must support this observable behavior: reject historic hookwrapper combinations via PluginValidationError. Required observable cases include historic hookwrapper combination rejected.
- **B005**: The extracted feature must support this observable behavior: check_pending raises for unknown non-optional hook implementations. Required observable cases include check pending requires optional for unknown hooks; hookwrapper must be generator.
- **B006**: The extracted feature must support this observable behavior: support optionalhook implementations for undeclared hooks. Required observable cases include hookwrapper must be generator.
- **B007**: The extracted feature must support this observable behavior: replay historic hook calls for plugins registered after the first dispatch. Required observable cases include historic hook replays for late registration.
- **B008**: The package exposes the required task API paths `featurelifted.PluginManager`, `featurelifted.PluginManager.check_pending`, `featurelifted.PluginManager.add_hookspecs`, `featurelifted.PluginManager.hook`, `featurelifted.PluginManager.register`, `featurelifted.HookspecMarker`, `featurelifted.HookimplMarker`, `featurelifted.PluginValidationError` with the kinds and callable signatures listed in this contract.

## Tests

### `public_tests/test_public_api.py::test_unknown_hook_argument_rejected`

- mapping: `B002`
- API: `featurelifted.HookimplMarker, featurelifted.HookspecMarker, featurelifted.PluginManager, featurelifted.PluginValidationError`
- risk: `exception_semantics`
- A001 `raises` L28: `pytest.raises(PluginValidationError)`

### `public_tests/test_public_api.py::test_check_pending_requires_optional_for_unknown_hooks`

- mapping: `B005`
- API: `featurelifted.HookimplMarker, featurelifted.HookspecMarker, featurelifted.PluginManager`
- risk: `implicit_no_exception_assertion`
- assertion: implicit successful execution

### `hidden_tests/test_hidden_behavior.py::test_historic_hook_replays_for_late_registration`

- mapping: `B007`
- API: `featurelifted.HookimplMarker, featurelifted.HookspecMarker, featurelifted.PluginManager`
- risk: `none`
- A001 `assert` L32: `results == []`
- A002 `assert` L34: `results == ['seed-configured']`

### `hidden_tests/test_hidden_behavior.py::test_hookwrapper_must_be_generator`

- mapping: `B001, B002, B003, B005, B006`
- API: `featurelifted.HookimplMarker, featurelifted.HookspecMarker, featurelifted.PluginManager, featurelifted.PluginValidationError`
- risk: `exact_error_text, exception_semantics`
- A001 `raises` L54: `pytest.raises(PluginValidationError, match='generator function')`

### `hidden_tests/test_hidden_behavior.py::test_historic_hookwrapper_combination_rejected`

- mapping: `B004`
- API: `featurelifted.HookimplMarker, featurelifted.HookspecMarker, featurelifted.PluginManager, featurelifted.PluginValidationError`
- risk: `exact_error_text, exception_semantics`
- A001 `raises` L76: `pytest.raises(PluginValidationError, match='historic incompatible')`

### `hidden_tests/test_required_api_surface.py::test_required_api_surface`

- mapping: `B008`
- API: `featurelifted.HookimplMarker, featurelifted.HookspecMarker, featurelifted.PluginManager, featurelifted.PluginValidationError`
- risk: `none`
- A001 `assert` L12: `isinstance(PluginManager, type)`
- A002 `assert` L13: `hasattr(PluginManager, 'check_pending')`
- A003 `assert` L14: `hasattr(PluginManager, 'add_hookspecs')`
- A004 `assert` L15: `PluginManager is not None`
- A005 `assert` L16: `hasattr(PluginManager, 'register')`
- A006 `assert` L17: `isinstance(HookspecMarker, type)`
- A007 `assert` L18: `isinstance(HookimplMarker, type)`
- A008 `assert` L19: `issubclass(PluginValidationError, BaseException)`

## Dependency / Oracle Evidence

- allowed dependencies: `none`
- forbidden imports: `pluggy`
- source entrypoints: `pluggy.PluginManager, pluggy.HookspecMarker, pluggy.HookimplMarker, pluggy.PluginValidationError, pluggy.PluginManager.check_pending, pluggy.PluginManager.add_hookspecs`
- oracle source files: `pluggy/__init__.py, pluggy/_version.py, pluggy/_tracing.py, pluggy/_result.py, pluggy/_callers.py, pluggy/_hooks.py, pluggy/_manager.py`
- runtime dependencies: `none`
- oracle notes: Full pluggy core package for hookspec validation task.
