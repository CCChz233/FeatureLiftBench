# stamina__retry_context_core__001

- release: `external50`
- lift: `Direct`
- coupling: `third_party_dependency_coupling`
- strict validation: `PASS`
- tests/assertions: `7/10`

## Required API

- `featurelifted.retry` (function) `(*, on, attempts=10, timeout=45.0, wait_initial=0.1, wait_max=5.0, wait_jitter=1.0, wait_exp_base=2)`
- `featurelifted.retry_context` (function) `(on, attempts=10, timeout=45.0, wait_initial=0.1, wait_max=5.0, wait_jitter=1.0, wait_exp_base=2)`
- `featurelifted.Attempt` (class)
- `featurelifted.Attempt.num` (attribute)
- `featurelifted.Attempt.next_wait` (attribute)
- `featurelifted.set_active` (function) `(active: bool) -> None`
- `featurelifted.set_testing` (function) `(testing: bool) -> None`

## Public Behaviors

- **B001**: retry retries only configured exceptions and returns the first successful result.
- **B002**: retry_context exposes one-based Attempt.num values and stops at the configured attempt limit.
- **B003**: set_active and set_testing change retry execution policy without changing the wrapped callable API.
- **B004**: The submitted package uses only the locked tenacity dependency and does not import stamina.

## Tests

### `public_tests/test_public_api.py::test_retry_decorator_succeeds_after_failures`

- mapping: `B001`
- API: `featurelifted.retry`
- risk: `none`
- A001 `assert` L11: `work() == 'ok' and len(calls) == 3`

### `public_tests/test_public_api.py::test_retry_context_attempt_numbers`

- mapping: `B002`
- API: `featurelifted.retry_context`
- risk: `none`
- A001 `assert` L20: `seen == [1, 2, 3]`

### `hidden_tests/test_hidden_behavior.py::test_unconfigured_exception_is_not_retried`

- mapping: `B001`
- API: `featurelifted.retry`
- risk: `exception_semantics`
- A001 `raises` L9: `pytest.raises(TypeError)`
- A002 `assert` L10: `len(calls) == 1`

### `hidden_tests/test_hidden_behavior.py::test_retry_context_stops_after_success`

- mapping: `B002`
- API: `featurelifted.retry_context`
- risk: `none`
- A001 `assert` L20: `seen == [1, 2]`

### `hidden_tests/test_hidden_behavior.py::test_inactive_policy_calls_once`

- mapping: `B003`
- API: `featurelifted.retry, featurelifted.set_active, featurelifted.set_testing`
- risk: `exception_semantics`
- A001 `raises` L29: `pytest.raises(ValueError)`
- A002 `assert` L30: `len(calls) == 1`

### `hidden_tests/test_hidden_behavior.py::test_required_api_surface`

- mapping: `B003`
- API: `featurelifted.Attempt, featurelifted.retry, featurelifted.retry_context, featurelifted.set_active, featurelifted.set_testing`
- risk: `none`
- A001 `assert` L37: `all((callable(x) for x in (retry, retry_context, set_active, set_testing)))`
- A002 `assert` L38: `isinstance(Attempt, type)`

### `hidden_tests/test_hidden_behavior.py::test_no_upstream_import_surface`

- mapping: `B004`
- API: `featurelifted.__file__`
- risk: `filesystem_resource`
- A001 `assert` L47: `not pattern.search(path.read_text(encoding='utf-8'))`

## Dependency / Oracle Evidence

- allowed dependencies: `tenacity`
- forbidden imports: `stamina`
- source entrypoints: `none`
- oracle source files: `src/stamina/_core.py, src/stamina/_config.py`
- runtime dependencies: `tenacity`
- oracle notes: Balanced Python-200 replacement slot cache-direct-third-party-02; offline reference only.
- behavior contract lacks a completed review_status
- behavior contract schema_version missing or unsupported
