# pyee__event_workflow_core__001

- release: `external50`
- lift: `Composite`
- coupling: `third_party_dependency_coupling`
- strict validation: `PASS`
- tests/assertions: `6/10`

## Required API

- `featurelifted.EventEmitter` (class)
- `featurelifted.EventEmitter.on` (method) `(event: str, f=None)`
- `featurelifted.EventEmitter.once` (method) `(event: str, f=None)`
- `featurelifted.EventEmitter.emit` (method) `(event: str, *args, **kwargs) -> bool`
- `featurelifted.EventEmitter.remove_listener` (method) `(event: str, f) -> None`
- `featurelifted.EventEmitter.remove_all_listeners` (method) `(event=None) -> None`
- `featurelifted.EventEmitter.listeners` (method) `(event: str) -> list`
- `featurelifted.PyeeError` (exception)

## Public Behaviors

- **B001**: EventEmitter dispatches listeners synchronously in registration order and forwards arguments.
- **B002**: once listeners remove themselves before invocation and listener removal updates subsequent dispatch.
- **B003**: An unhandled error event raises its Exception or PyeeError for a non-exception payload.
- **B004**: The submitted package uses only typing-extensions and does not import pyee.

## Tests

### `public_tests/test_public_api.py::test_emit_preserves_registration_order`

- mapping: `B001`
- API: `featurelifted.EventEmitter`
- risk: `ordering_semantics`
- A001 `assert` L8: `emitter.emit('data', 3) is True`
- A002 `assert` L9: `seen == [('a', 3), ('b', 3)]`

### `public_tests/test_public_api.py::test_once_listener_runs_once`

- mapping: `B002`
- API: `featurelifted.EventEmitter`
- risk: `none`
- A001 `assert` L16: `seen == [1]`

### `hidden_tests/test_hidden_behavior.py::test_remove_listener_changes_dispatch`

- mapping: `B001, B002`
- API: `featurelifted.EventEmitter`
- risk: `none`
- A001 `assert` L9: `emitter.emit('x') is False and seen == []`

### `hidden_tests/test_hidden_behavior.py::test_unhandled_error_semantics`

- mapping: `B003`
- API: `featurelifted.EventEmitter, featurelifted.PyeeError`
- risk: `exception_semantics`
- A001 `raises` L14: `pytest.raises(ValueError)`
- A002 `raises` L15: `pytest.raises(PyeeError)`

### `hidden_tests/test_hidden_behavior.py::test_required_api_surface`

- mapping: `B003`
- API: `featurelifted.EventEmitter, featurelifted.PyeeError`
- risk: `none`
- A001 `assert` L20: `isinstance(EventEmitter, type)`
- A002 `assert` L21: `issubclass(PyeeError, Exception)`
- A003 `assert` L22: `all((callable(getattr(EventEmitter, n)) for n in ('on', 'once', 'emit', 'remove_listener', 'remove_all_listeners', 'listeners')))`

### `hidden_tests/test_hidden_behavior.py::test_no_upstream_import_surface`

- mapping: `B004`
- API: `featurelifted.__file__`
- risk: `filesystem_resource`
- A001 `assert` L31: `not pattern.search(path.read_text(encoding='utf-8'))`

## Dependency / Oracle Evidence

- allowed dependencies: `typing-extensions`
- forbidden imports: `pyee`
- source entrypoints: `none`
- oracle source files: `pyee/base.py, pyee/__init__.py`
- runtime dependencies: `typing-extensions`
- oracle notes: Balanced Python-200 replacement slot workflow-composite-third-party-03; offline reference only.
- behavior contract lacks a completed review_status
- behavior contract schema_version missing or unsupported
