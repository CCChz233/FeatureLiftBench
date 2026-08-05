# cachier__memoize_backend_core__001

- release: `external50`
- lift: `Composite`
- coupling: `third_party_dependency_coupling`
- strict validation: `PASS`
- tests/assertions: `7/15`

## Required API

- `featurelifted.cachier` (function) `(*, backend='pickle', stale_after=..., next_time=False, cache_dir=None, ...)`
- `featurelifted.set_default_params` (function) `(**params) -> None`
- `featurelifted.get_default_params` (function) `() -> dict`
- `featurelifted.enable_caching` (function) `() -> None`
- `featurelifted.disable_caching` (function) `() -> None`

## Public Behaviors

- **B001**: The memory backend memoizes by arguments and exposes clear_cache and precache_value on wrapped callables.
- **B002**: Per-call skip-cache and overwrite-cache controls bypass or replace an existing entry deterministically.
- **B003**: Global enable and disable controls affect decorated functions and can be restored between tests.
- **B004**: The submitted package uses only locked backend dependencies and does not import cachier.

## Tests

### `public_tests/test_public_api.py::test_memory_backend_memoizes_by_arguments`

- mapping: `B001`
- API: `featurelifted.cachier`
- risk: `none`
- A001 `assert` L8: `add(1, 2) == add(1, 2) == 3`
- A002 `assert` L9: `add(2, 3) == 5 and calls == [(1, 2), (2, 3)]`

### `public_tests/test_public_api.py::test_skip_and_overwrite_controls`

- mapping: `B002`
- API: `featurelifted.cachier`
- risk: `none`
- A001 `assert` L16: `value(1) == 1 and value(1) == 1`
- A002 `assert` L17: `value(1, cachier__skip_cache=True) == 2`
- A003 `assert` L18: `value(1) == 1`
- A004 `assert` L19: `value(1, cachier__overwrite_cache=True) == 3`
- A005 `assert` L20: `value(1) == 3`

### `hidden_tests/test_hidden_behavior.py::test_clear_and_precache_methods`

- mapping: `B001`
- API: `featurelifted.cachier`
- risk: `state_mutation`
- A001 `assert` L9: `value(3) == 7 and calls == []`
- A002 `assert` L11: `value(3) == 6 and calls == [3]`

### `hidden_tests/test_hidden_behavior.py::test_overwrite_replaces_existing_entry`

- mapping: `B002`
- API: `featurelifted.cachier`
- risk: `none`
- A001 `assert` L18: `value() == 1 and value() == 1`
- A002 `assert` L19: `value(cachier__overwrite_cache=True) == 2`
- A003 `assert` L20: `value() == 2`

### `hidden_tests/test_hidden_behavior.py::test_global_disable_bypasses_cache`

- mapping: `B003`
- API: `featurelifted.cachier, featurelifted.disable_caching, featurelifted.enable_caching`
- risk: `state_mutation`
- A001 `assert` L29: `(value(), value()) == (1, 2)`

### `hidden_tests/test_hidden_behavior.py::test_required_api_surface`

- mapping: `B003`
- API: `featurelifted.cachier, featurelifted.disable_caching, featurelifted.enable_caching, featurelifted.get_default_params, featurelifted.set_default_params`
- risk: `none`
- A001 `assert` L36: `all((callable(x) for x in (cachier, set_default_params, get_default_params, enable_caching, disable_caching)))`

### `hidden_tests/test_hidden_behavior.py::test_no_upstream_import_surface`

- mapping: `B004`
- API: `featurelifted.__file__`
- risk: `filesystem_resource`
- A001 `assert` L45: `not pattern.search(path.read_text(encoding='utf-8'))`

## Dependency / Oracle Evidence

- allowed dependencies: `portalocker, pympler, watchdog`
- forbidden imports: `cachier`
- source entrypoints: `none`
- oracle source files: `src/cachier/core.py, src/cachier/config.py, src/cachier/cores/memory.py`
- runtime dependencies: `portalocker, pympler, watchdog`
- oracle notes: Balanced Python-200 replacement slot cache-composite-third-party-03; offline reference only.
- behavior contract lacks a completed review_status
- behavior contract schema_version missing or unsupported
