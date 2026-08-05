# automat__methodical_workflow_core__001

- release: `external50`
- lift: `Composite`
- coupling: `framework_coupling`
- strict validation: `PASS`
- tests/assertions: `6/7`

## Required API

- `featurelifted.MethodicalMachine` (class)
- `featurelifted.NoTransition` (exception)

## Public Behaviors

- **B001**: MethodicalMachine composes declared states and inputs into deterministic transitions on host instances.
- **B002**: Transition outputs are collected and returned in declared order.
- **B003**: Serializer and unserializer decorators round-trip the active state for a new instance.
- **B004**: The submitted package does not import automat or use visualization dependencies.

## Tests

### `public_tests/test_public_api.py::test_transition_and_collected_output`

- mapping: `B001`
- API: `none detected`
- risk: `none`
- A001 `assert` L29: `switch.query() is False`
- A002 `assert` L31: `switch.query() is True`

### `public_tests/test_public_api.py::test_instances_keep_independent_state`

- mapping: `B001`
- API: `none detected`
- risk: `state_mutation`
- A001 `assert` L37: `left.query() is True and right.query() is False`

### `hidden_tests/test_hidden_behavior.py::test_serializer_roundtrip`

- mapping: `B001, B003`
- API: `featurelifted.MethodicalMachine`
- risk: `none`
- A001 `assert` L20: `second.save() == 'on'`

### `hidden_tests/test_hidden_behavior.py::test_undeclared_transition_raises`

- mapping: `B002`
- API: `featurelifted.MethodicalMachine, featurelifted.NoTransition`
- risk: `implicit_no_exception_assertion`
- assertion: implicit successful execution

### `hidden_tests/test_hidden_behavior.py::test_required_api_surface`

- mapping: `B003`
- API: `featurelifted.MethodicalMachine, featurelifted.NoTransition`
- risk: `none`
- A001 `assert` L41: `isinstance(MethodicalMachine, type)`
- A002 `assert` L42: `issubclass(NoTransition, Exception)`

### `hidden_tests/test_hidden_behavior.py::test_no_upstream_import_surface`

- mapping: `B004`
- API: `featurelifted.__file__`
- risk: `filesystem_resource`
- A001 `assert` L51: `not pattern.search(path.read_text(encoding='utf-8'))`

## Dependency / Oracle Evidence

- allowed dependencies: `none`
- forbidden imports: `automat`
- source entrypoints: `none`
- oracle source files: `src/automat/_methodical.py, src/automat/_core.py`
- runtime dependencies: `none`
- oracle notes: Balanced Python-200 replacement slot workflow-composite-framework-01; offline reference only.
- behavior contract lacks a completed review_status
- behavior contract schema_version missing or unsupported
