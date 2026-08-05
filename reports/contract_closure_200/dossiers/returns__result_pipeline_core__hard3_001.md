# returns__result_pipeline_core__hard3_001

- release: `frozen_python150`
- lift: `Adapted`
- coupling: `unknown`
- strict validation: `FAIL`
- tests/assertions: `4/15`

## Required API

- `featurelifted.Result` (class) `()`
- `featurelifted.Success` (class) `(value: 'T') -> 'None'`
- `featurelifted.Success.map` (method) `(self, function: 'Callable[[T], U]') -> 'Result[U, E]'`
- `featurelifted.Success.value` (attribute)
- `featurelifted.Failure` (class) `(error: 'E') -> 'None'`
- `featurelifted.Failure.failure` (attribute)
- `featurelifted.safe` (function) `(function: 'Callable[..., T] | None' = None, *, exceptions: 'tuple[type[BaseException], ...]' = (<class 'Exception'>,))`

## Public Behaviors

- **B001**: When map or bind is called, Success transforms its value while Failure short-circuits and preserves its error.
- **B002**: Success and Failure expose their contained value or error through the declared Result container operations.
- **B003**: `@safe` wraps callables and maps exceptions to `Failure`.
- **B004**: The package exposes the required task API paths `featurelifted.Result`, `featurelifted.Success`, `featurelifted.Success.map`, `featurelifted.Success.value`, `featurelifted.Failure`, `featurelifted.Failure.failure`, `featurelifted.safe` with the kinds and callable signatures listed in this contract.

## Tests

### `public_tests/test_public_contract.py::test_success_map_and_bind`

- mapping: `B001`
- API: `featurelifted.Success, featurelifted.Success.bind, featurelifted.Success.map`
- risk: `none`
- A001 `assert` L7: `isinstance(value, Success)`
- A002 `assert` L8: `value.value == 9`

### `hidden_tests/test_hidden_contract.py::test_failure_short_circuits`

- mapping: `B002`
- API: `featurelifted.Failure, featurelifted.Failure.bind, featurelifted.Failure.map, featurelifted.Success`
- risk: `none`
- A001 `assert` L7: `isinstance(result, Failure)`
- A002 `assert` L8: `result.failure == 'boom'`

### `hidden_tests/test_hidden_contract.py::test_safe_decorator_maps_exceptions`

- mapping: `B001, B003`
- API: `featurelifted.Failure, featurelifted.Success`
- risk: `none`
- A001 `assert` L19: `isinstance(ok, Success)`
- A002 `assert` L20: `ok.value == 2`
- A003 `assert` L21: `isinstance(bad, Failure)`
- A004 `assert` L22: `isinstance(bad.failure, ZeroDivisionError)`

### `hidden_tests/test_required_api_surface.py::test_required_api_surface`

- mapping: `B004`
- API: `featurelifted.Failure, featurelifted.Result, featurelifted.Success, featurelifted.safe`
- risk: `none`
- A001 `assert` L12: `isinstance(Result, type)`
- A002 `assert` L13: `isinstance(Success, type)`
- A003 `assert` L14: `hasattr(Success, 'map')`
- A004 `assert` L15: `Success is not None`
- A005 `assert` L16: `isinstance(Failure, type)`
- A006 `assert` L17: `Failure is not None`
- A007 `assert` L18: `callable(safe)`

## Dependency / Oracle Evidence

- allowed dependencies: `none`
- forbidden imports: `returns`
- source entrypoints: `returns.result.Success, returns.pipeline.safe`
- oracle source files: `repo/returns/result.py`
- runtime dependencies: `none`
- oracle notes: Result pipeline subset without other containers.

## Machine Issues

- public_tests/test_public_contract.py uses undeclared API reference featurelifted.Success.bind
- hidden_tests/test_hidden_contract.py uses undeclared API reference featurelifted.Failure.bind
- hidden_tests/test_hidden_contract.py uses undeclared API reference featurelifted.Failure.map
