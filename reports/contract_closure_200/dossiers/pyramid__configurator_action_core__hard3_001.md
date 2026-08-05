# pyramid__configurator_action_core__hard3_001

- release: `frozen_python150`
- lift: `Composite`
- coupling: `unknown`
- strict validation: `PASS`
- tests/assertions: `5/9`

## Required API

- `featurelifted.ActionRegistry` (class) `() -> 'None'`
- `featurelifted.ActionRegistry.commit` (method) `(self) -> 'list[Any]'`
- `featurelifted.ActionRegistry.introspect` (method) `(self, category: 'str | None' = None) -> 'list[Action]'`
- `featurelifted.ActionRegistry.register` (method) `(self, discriminator: 'Any', callable: 'Callable[..., Any] | None' = None, order: 'int' = 0, args=(), kw=None, category: 'str | None' = None) -> 'None'`
- `featurelifted.ConfigurationConflictError` (exception)

## Public Behaviors

- **B001**: `register` queues actions with discriminators and order values.
- **B002**: `commit` executes actions in order; duplicate discriminators raise `ConfigurationConflictError`.
- **B003**: `None` discriminators never conflict.
- **B004**: `introspect(category=...)` filters committed actions.
- **B005**: The package exposes the required task API paths `featurelifted.ActionRegistry`, `featurelifted.ActionRegistry.commit`, `featurelifted.ActionRegistry.introspect`, `featurelifted.ActionRegistry.register`, `featurelifted.ConfigurationConflictError` with the kinds and callable signatures listed in this contract.

## Tests

### `public_tests/test_public_contract.py::test_action_registry_executes_in_order`

- mapping: `B001, B003`
- API: `featurelifted.ActionRegistry`
- risk: `ordering_semantics`
- A001 `assert` L11: `log == ['b', 'a']`

### `hidden_tests/test_hidden_contract.py::test_duplicate_discriminator_raises`

- mapping: `B003`
- API: `featurelifted.ActionRegistry, featurelifted.ConfigurationConflictError`
- risk: `exception_semantics`
- A001 `raises` L11: `pytest.raises(ConfigurationConflictError)`

### `hidden_tests/test_hidden_contract.py::test_none_discriminator_never_conflicts`

- mapping: `B001, B002, B004`
- API: `featurelifted.ActionRegistry`
- risk: `none`
- A001 `assert` L19: `registry.commit() == [1, 2]`

### `hidden_tests/test_hidden_contract.py::test_introspect_category_filter`

- mapping: `B003`
- API: `featurelifted.ActionRegistry`
- risk: `none`
- A001 `assert` L27: `len(registry.introspect(category='view')) == 1`

### `hidden_tests/test_required_api_surface.py::test_required_api_surface`

- mapping: `B005`
- API: `featurelifted.ActionRegistry, featurelifted.ConfigurationConflictError`
- risk: `none`
- A001 `assert` L10: `isinstance(ActionRegistry, type)`
- A002 `assert` L11: `hasattr(ActionRegistry, 'commit')`
- A003 `assert` L12: `hasattr(ActionRegistry, 'introspect')`
- A004 `assert` L13: `hasattr(ActionRegistry, 'register')`
- A005 `assert` L14: `issubclass(ConfigurationConflictError, BaseException)`

## Dependency / Oracle Evidence

- allowed dependencies: `none`
- forbidden imports: `pyramid`
- source entrypoints: `pyramid.config.actions.ActionConfiguratorMixin`
- oracle source files: `repo/src/pyramid/config/actions.py, repo/src/pyramid/exceptions.py`
- runtime dependencies: `none`
- oracle notes: Action registry subset without WSGI startup.
