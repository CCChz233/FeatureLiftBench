# tenacity__retry_state_core__hard3_001

- release: `frozen_python150`
- lift: `Adapted`
- coupling: `unknown`
- strict validation: `PASS`
- tests/assertions: `9/29`

## Required API

- `featurelifted.Retrying` (class) `(*, stop: 'StopBase | None' = None, wait: 'WaitBase | None' = None, retry: 'RetryBase | None' = None, sleep: 'Callable[[float], None] | None' = None, before_sleep: 'Callable[[RetryCallState], None] | None' = None, reraise: 'bool' = False, retry_error_cls: 'type[RetryError]' = <class 'RetryError'>, retry_error_callback: 'Callable[[RetryCallState], Any] | None' = None) -> 'None'`
- `featurelifted.RetryError` (exception)
- `featurelifted.retry_if_exception_type` (function) `(exception_types: 'type[BaseException] | tuple[type[BaseException], ...]' = <class 'Exception'>) -> 'None'`
- `featurelifted.retry_if_result` (function) `(predicate: 'Callable[[Any], bool]') -> 'None'`
- `featurelifted.stop_after_attempt` (function) `(max_attempt_number: 'int') -> 'None'`
- `featurelifted.wait_fixed` (function) `(wait: 'float') -> 'None'`
- `featurelifted.wait_chain` (function) `(*strategies: 'WaitBase') -> 'None'`
- `featurelifted.wait_exponential` (function) `(multiplier: 'float' = 1, max: 'float' = 3600.0, exp_base: 'float' = 2, min: 'float' = 0) -> 'None'`
- `featurelifted.RetryCallState` (class) `(retry_object: "'Retrying'", fn: 'Callable[..., Any]', args: 'tuple[Any, ...]', kwargs: 'dict[str, Any]')`
- `featurelifted.stop_after_delay` (function) `(max_delay: 'float') -> 'None'`
- `featurelifted.stop_before_delay` (function) `(max_delay: 'float') -> 'None'`
- `featurelifted.wait_combine` (function) `(*strategies: 'WaitBase') -> 'None'`
- `featurelifted.wait_none` (function) `() -> 'None'`

## Public Behaviors

- **B001**: Retrying repeatedly calls the function while the retry predicate requests another attempt and stops when the function succeeds or a stop policy triggers.
- **B002**: Track a `RetryCallState` with `attempt_number`, `outcome`, `idle_for`, `upcoming_sleep`, and `seconds_since_start`.
- **B003**: When retries are exhausted, Retrying calls retry_error_callback if configured, reraises the final exception when requested, or raises RetryError.
- **B004**: retry_if_exception_type retries matching exceptions and retry_if_result retries matching returned results.
- **B005**: Retry predicates composed with | or & apply retry-any or retry-all semantics in operand order.
- **B006**: stop_after_attempt, stop_after_delay, and stop_before_delay stop according to attempt count and elapsed or upcoming delay boundaries.
- **B007**: wait_fixed, wait_none, wait_chain, wait_combine, and wait_exponential compute deterministic upcoming sleep durations; an empty wait_chain raises ValueError.
- **B008**: before_sleep receives the updated retry state before idle_for is incremented, and retry_error_callback receives the exhausted state.
- **B009**: The package exposes the required task API paths `featurelifted.Retrying`, `featurelifted.RetryError`, `featurelifted.retry_if_exception_type`, `featurelifted.retry_if_result`, `featurelifted.stop_after_attempt`, `featurelifted.wait_fixed`, `featurelifted.wait_chain`, `featurelifted.wait_exponential`, `featurelifted.RetryCallState`, `featurelifted.stop_after_delay`, `featurelifted.stop_before_delay`, `featurelifted.wait_combine`, and 1 listed members with the kinds and callable signatures listed in this contract.

## Tests

### `public_tests/test_public_contract.py::test_retry_exception_until_success_without_real_sleep`

- mapping: `B004, B008`
- API: `featurelifted.Retrying, featurelifted.retry_if_exception_type, featurelifted.stop_after_attempt, featurelifted.wait_fixed`
- risk: `time_or_randomness`
- A001 `assert` L30: `retrying(flaky) == 'ok'`
- A002 `assert` L31: `len(calls) == 3`
- A003 `assert` L32: `sleeps == [0.25, 0.25]`

### `public_tests/test_public_contract.py::test_retry_result_predicate`

- mapping: `B004`
- API: `featurelifted.Retrying, featurelifted.retry_if_result, featurelifted.stop_after_attempt, featurelifted.wait_fixed`
- risk: `none`
- A001 `assert` L44: `retrying(lambda: next(values)) == 'done'`

### `public_tests/test_public_contract.py::test_retry_error_when_stop_is_reached`

- mapping: `B004, B008`
- API: `featurelifted.RetryError, featurelifted.Retrying, featurelifted.retry_if_exception_type, featurelifted.stop_after_attempt, featurelifted.wait_fixed`
- risk: `exception_semantics`
- A001 `raises` L55: `pytest.raises(RetryError)`
- A002 `assert` L58: `err.value.last_attempt.attempt_number == 2`
- A003 `assert` L59: `isinstance(err.value.last_attempt.exception(), RuntimeError)`

### `hidden_tests/test_hidden_contract.py::test_wait_chain_requires_at_least_one_strategy`

- mapping: `B007`
- API: `featurelifted.wait_chain`
- risk: `exact_error_text, exception_semantics`
- A001 `raises` L15: `pytest.raises(ValueError, match='at least one')`

### `hidden_tests/test_hidden_contract.py::test_wait_chain_uses_last_strategy_after_exhaustion`

- mapping: `B001, B002, B003, B006, B007`
- API: `featurelifted.Retrying, featurelifted.retry_if_exception_type, featurelifted.stop_after_attempt, featurelifted.wait_chain, featurelifted.wait_fixed`
- risk: `none`
- A001 `assert` L35: `retrying(always_bad) == 4`
- A002 `assert` L36: `sleeps == [1.0, 2.0, 2.0]`
- A003 `assert` L37: `len(calls) == 4`

### `hidden_tests/test_hidden_contract.py::test_before_sleep_observes_retry_state`

- mapping: `B008`
- API: `featurelifted.Retrying, featurelifted.retry_if_result, featurelifted.stop_after_attempt, featurelifted.wait_fixed`
- risk: `state_mutation`
- A001 `assert` L62: `retrying(lambda: next(values)) == 'ok'`
- A002 `assert` L63: `snapshots == [{'attempt': 1, 'sleep': 0.5, 'failed': False, 'idle': 0.0}, {'attempt': 2, 'sleep': 0.5, 'failed': False, 'idle': 0.5}]`

### `hidden_tests/test_hidden_contract.py::test_reraise_surfaces_last_exception`

- mapping: `B004`
- API: `featurelifted.Retrying, featurelifted.retry_if_exception_type, featurelifted.stop_after_attempt, featurelifted.wait_fixed`
- risk: `exact_error_text, exception_semantics`
- A001 `raises` L78: `pytest.raises(KeyError, match='missing')`

### `hidden_tests/test_hidden_contract.py::test_strategy_composition_and_exponential_wait`

- mapping: `B005, B007`
- API: `featurelifted.Retrying, featurelifted.retry_if_exception_type, featurelifted.retry_if_result, featurelifted.stop_after_attempt, featurelifted.wait_exponential`
- risk: `none`
- A001 `assert` L99: `retrying(action) == 'ok'`
- A002 `assert` L100: `sleeps == [0.5, 1.0]`

### `hidden_tests/test_required_api_surface.py::test_required_api_surface`

- mapping: `B009`
- API: `featurelifted.RetryCallState, featurelifted.RetryError, featurelifted.Retrying, featurelifted.retry_if_exception_type, featurelifted.retry_if_result, featurelifted.stop_after_attempt, featurelifted.stop_after_delay, featurelifted.stop_before_delay, featurelifted.wait_chain, featurelifted.wait_combine, featurelifted.wait_exponential, featurelifted.wait_fixed, featurelifted.wait_none`
- risk: `none`
- A001 `assert` L21: `isinstance(Retrying, type)`
- A002 `assert` L22: `issubclass(RetryError, BaseException)`
- A003 `assert` L23: `callable(retry_if_exception_type)`
- A004 `assert` L24: `callable(retry_if_result)`
- A005 `assert` L25: `callable(stop_after_attempt)`
- A006 `assert` L26: `callable(wait_fixed)`
- A007 `assert` L27: `callable(wait_chain)`
- A008 `assert` L28: `callable(wait_exponential)`
- A009 `assert` L29: `isinstance(RetryCallState, type)`
- A010 `assert` L30: `callable(stop_after_delay)`
- A011 `assert` L31: `callable(stop_before_delay)`
- A012 `assert` L32: `callable(wait_combine)`
- A013 `assert` L33: `callable(wait_none)`

## Dependency / Oracle Evidence

- allowed dependencies: `none`
- forbidden imports: `tenacity`
- source entrypoints: `tenacity.Retrying, tenacity.RetryCallState, tenacity.retry.retry_if_exception_type, tenacity.retry.retry_if_result, tenacity.stop.stop_after_attempt, tenacity.wait.wait_fixed, tenacity.wait.wait_chain`
- oracle source files: `repo/tenacity/__init__.py, repo/tenacity/retry.py, repo/tenacity/stop.py, repo/tenacity/wait.py, repo/tenacity/_utils.py`
- runtime dependencies: `none`
- oracle notes: Task-scoped synchronous retry state machine. Async, Tornado, decorator overloads, and logging helpers are intentionally excluded.
