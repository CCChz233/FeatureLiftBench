# transitions__state_machine_core__hard3_001

- release: `frozen_python150`
- lift: `Adapted`
- coupling: `unknown`
- strict validation: `PASS`
- tests/assertions: `5/8`

## Required API

- `featurelifted.MachineError` (exception)
- `featurelifted.Machine` (class) `(model: 'Any', states: 'list[str] | None' = None, initial: 'str' = 'initial', transitions: 'list[dict] | None' = None, before_state_change: 'list[str] | None' = None, after_state_change: 'list[str] | None' = None, ignore_invalid_triggers: 'bool' = False, send_event: 'bool' = False, auto_transitions: 'bool' = False) -> 'None'`
- `featurelifted.Machine.__init__` (method) `(self, model: 'Any', states: 'list[str] | None' = None, initial: 'str' = 'initial', transitions: 'list[dict] | None' = None, before_state_change: 'list[str] | None' = None, after_state_change: 'list[str] | None' = None, ignore_invalid_triggers: 'bool' = False, send_event: 'bool' = False, auto_transitions: 'bool' = False) -> 'None'`

## Public Behaviors

- **B001**: When a registered trigger method is invoked on a model, the machine executes the matching transition and updates model.state.
- **B002**: When a transition declares conditions, the transition is skipped unless every condition callable returns a truthy value.
- **B003**: When transition before/after callbacks are configured, they run around the state change in upstream order.
- **B004**: When a machine is created with a dotted nested state name such as parent.child, the model exposes the nested hierarchy such that model.parent.state == "child".
- **B005**: The package exposes the required task API paths `featurelifted.MachineError`, `featurelifted.Machine`, `featurelifted.Machine.__init__` with the kinds and callable signatures listed in this contract.

## Tests

### `public_tests/test_public_contract.py::test_machine_runs_transition`

- mapping: `B001`
- API: `featurelifted.Machine`
- risk: `none`
- A001 `assert` L20: `model.state == 'b'`

### `hidden_tests/test_hidden_contract.py::test_conditional_transition_and_callbacks`

- mapping: `B002, B003`
- API: `featurelifted.Machine`
- risk: `none`
- A001 `assert` L31: `model.state == 'b'`
- A002 `assert` L32: `model.log == ['before', 'after']`

### `hidden_tests/test_hidden_contract.py::test_nested_state_name`

- mapping: `B004`
- API: `featurelifted.Machine`
- risk: `state_mutation`
- A001 `assert` L38: `model.parent.state == 'child'`

### `hidden_tests/test_hidden_contract.py::test_invalid_trigger_raises`

- mapping: `B001`
- API: `featurelifted.Machine, featurelifted.MachineError`
- risk: `exception_semantics`
- A001 `raises` L49: `pytest.raises(MachineError)`

### `hidden_tests/test_required_api_surface.py::test_required_api_surface`

- mapping: `B005`
- API: `featurelifted.Machine, featurelifted.MachineError`
- risk: `none`
- A001 `assert` L10: `issubclass(MachineError, BaseException)`
- A002 `assert` L11: `isinstance(Machine, type)`
- A003 `assert` L12: `hasattr(Machine, '__init__')`

## Dependency / Oracle Evidence

- allowed dependencies: `none`
- forbidden imports: `transitions`
- source entrypoints: `transitions.Machine, transitions.MachineError`
- oracle source files: `repo/transitions/__init__.py, repo/transitions/core.py`
- runtime dependencies: `none`
- oracle notes: Synchronous state machine core only.
