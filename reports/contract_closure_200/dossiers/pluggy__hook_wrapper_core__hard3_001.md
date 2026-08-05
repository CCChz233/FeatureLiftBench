# pluggy__hook_wrapper_core__hard3_001

- release: `frozen_python150`
- lift: `Adapted`
- coupling: `unknown`
- strict validation: `PASS`
- tests/assertions: `6/10`

## Required API

- `featurelifted.HookCaller` (class) `(name: 'str', *, firstresult: 'bool' = False, historic: 'bool' = False) -> 'None'`
- `featurelifted.HookCaller.add_hookimpl` (method) `(self, function: 'Callable[..., Any]', *, tryfirst: 'bool' = False, trylast: 'bool' = False, optionalhook: 'bool' = False) -> 'None'`
- `featurelifted.HookCaller.call_extra` (method) `(self, methods: 'list[Callable[..., Any]]', kwargs: 'dict[str, Any]') -> 'Any'`
- `featurelifted.HookCaller.get_hookimpls` (method) `(self) -> 'list[HookImpl]'`

## Public Behaviors

- **B001**: `call_extra()` temporarily adds hook implementations without mutating permanent state.
- **B002**: `tryfirst`/`trylast` options control hookimpl ordering.
- **B003**: When HookCaller invokes multiple implementations, it aggregates results in hook order, honors firstresult, and lets wrappers observe or modify the outcome.
- **B004**: The package exposes the required task API paths `featurelifted.HookCaller`, `featurelifted.HookCaller.add_hookimpl`, `featurelifted.HookCaller.call_extra`, `featurelifted.HookCaller.get_hookimpls` with the kinds and callable signatures listed in this contract.

## Tests

### `public_tests/test_public_contract.py::test_historic_replays_for_late_registration`

- mapping: `B001`
- API: `featurelifted.HookCaller`
- risk: `none`
- A001 `assert` L10: `seen == [2]`

### `public_tests/test_public_contract.py::test_hookwrapper_runs_teardown`

- mapping: `B002`
- API: `featurelifted.HookCaller`
- risk: `none`
- A001 `assert` L25: `order == ['enter', 'inner', 'exit']`

### `hidden_tests/test_hidden_contract.py::test_tryfirst_trylast_ordering`

- mapping: `B002, B003`
- API: `featurelifted.HookCaller`
- risk: `ordering_semantics`
- A001 `assert` L12: `order == ['first', 'normal', 'last']`

### `hidden_tests/test_hidden_contract.py::test_call_extra_restores_state`

- mapping: `B004`
- API: `featurelifted.HookCaller`
- risk: `state_mutation`
- A001 `assert` L19: `result == [2, 1]`
- A002 `assert` L20: `len(hook.get_hookimpls()) == 1`

### `hidden_tests/test_hidden_contract.py::test_direct_call_on_historic_raises`

- mapping: `B001`
- API: `featurelifted.HookCaller`
- risk: `none`
- A001 `assert` L30: `raised`

### `hidden_tests/test_required_api_surface.py::test_required_api_surface`

- mapping: `B004`
- API: `featurelifted.HookCaller`
- risk: `none`
- A001 `assert` L9: `isinstance(HookCaller, type)`
- A002 `assert` L10: `hasattr(HookCaller, 'add_hookimpl')`
- A003 `assert` L11: `hasattr(HookCaller, 'call_extra')`
- A004 `assert` L12: `hasattr(HookCaller, 'get_hookimpls')`

## Dependency / Oracle Evidence

- allowed dependencies: `none`
- forbidden imports: `pluggy`
- source entrypoints: `pluggy._hooks.HookCaller`
- oracle source files: `repo/src/pluggy/_hooks.py, repo/src/pluggy/_callers.py`
- runtime dependencies: `none`
- oracle notes: Historic wrapper ordering subset without plugin manager.
