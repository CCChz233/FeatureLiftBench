# python_statemachine__json_workflow_core__001

- release: `external50`
- lift: `Composite`
- coupling: `config_environment_coupling`
- strict validation: `PASS`
- tests/assertions: `6/10`

## Required API

- `featurelifted.load` (function) `(source: str | Path, *, format=None, trusted=False, validate=False, name=None) -> type[StateChart]`
- `featurelifted.StateChart` (class)
- `featurelifted.StateChart.send` (method) `(event, *args, **kwargs)`
- `featurelifted.StateChart.configuration` (attribute)
- `featurelifted.InvalidDefinition` (exception)

## Public Behaviors

- **B001**: load parses an inline JSON statechart definition and returns an instantiable StateChart subclass.
- **B002**: The instantiated chart starts in the configured initial state and routes declared events to target states.
- **B003**: The default trusted=False mode rejects unsupported executable expressions at load time.
- **B004**: The submitted package does not import statemachine and performs no file or network lookup for inline JSON.

## Tests

### `public_tests/test_public_api.py::test_load_inline_json_returns_machine_class`

- mapping: `B001`
- API: `featurelifted.load`
- risk: `none`
- A001 `assert` L12: `[state.id for state in machine.configuration] == ['draft']`

### `public_tests/test_public_api.py::test_declared_event_moves_to_target`

- mapping: `B002`
- API: `featurelifted.load`
- risk: `none`
- A001 `assert` L18: `[state.id for state in machine.configuration] == ['sent']`

### `hidden_tests/test_hidden_behavior.py::test_instances_have_independent_configuration`

- mapping: `B001, B002`
- API: `featurelifted.load`
- risk: `none`
- A001 `assert` L10: `[state.id for state in first.configuration] == ['done']`
- A002 `assert` L11: `[state.id for state in second.configuration] == ['idle']`

### `hidden_tests/test_hidden_behavior.py::test_invalid_definition_is_rejected`

- mapping: `B003`
- API: `featurelifted.InvalidDefinition, featurelifted.load`
- risk: `exception_semantics`
- A001 `raises` L15: `pytest.raises(InvalidDefinition)`

### `hidden_tests/test_hidden_behavior.py::test_required_api_surface`

- mapping: `B003`
- API: `featurelifted.InvalidDefinition, featurelifted.StateChart, featurelifted.StateChart.send, featurelifted.load`
- risk: `none`
- A001 `assert` L21: `callable(load)`
- A002 `assert` L22: `isinstance(StateChart, type)`
- A003 `assert` L23: `callable(StateChart.send)`
- A004 `assert` L24: `issubclass(InvalidDefinition, Exception)`

### `hidden_tests/test_hidden_behavior.py::test_no_upstream_import_surface`

- mapping: `B004`
- API: `featurelifted.__file__`
- risk: `filesystem_resource`
- A001 `assert` L33: `not pattern.search(path.read_text(encoding='utf-8'))`

## Dependency / Oracle Evidence

- allowed dependencies: `none`
- forbidden imports: `statemachine`
- source entrypoints: `none`
- oracle source files: `statemachine/io/loader.py, statemachine/io/json/reader.py, statemachine/statemachine.py`
- runtime dependencies: `none`
- oracle notes: Balanced Python-200 replacement slot workflow-composite-config-02; offline reference only.
- behavior contract lacks a completed review_status
- behavior contract schema_version missing or unsupported
