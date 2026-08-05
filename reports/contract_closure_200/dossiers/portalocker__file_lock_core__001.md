# portalocker__file_lock_core__001

- release: `external50`
- lift: `Direct`
- coupling: `resource_coupling`
- strict validation: `PASS`
- tests/assertions: `7/8`

## Required API

- `featurelifted.lock` (function) `(file, flags=LOCK_EX)`
- `featurelifted.unlock` (function) `(file)`
- `featurelifted.Lock` (class)
- `featurelifted.LOCK_EX` (constant)
- `featurelifted.LOCK_SH` (constant)
- `featurelifted.LOCK_NB` (constant)
- `featurelifted.LockException` (class)

## Public Behaviors

- **B001**: The extracted feature must support this observable behavior: Lock context manager and lock/unlock on file handles. Required observable cases include lock context manager; lock unlock functions.
- **B002**: The extracted feature must support this observable behavior: LOCK_EX and related constants are exposed. Required observable cases include lock constants.
- **B003**: The extracted feature must support this observable behavior: Lock accepts timeout and LockException exists. Required observable cases include lock timeout; lock exception type.
- **B004**: Tests use local temp files only; no network resources.
- **B005**: The package exposes Lock/lock/unlock/LOCK_EX/LockException with the kinds listed in this contract.
- **B006**: the submitted package does not import forbidden upstream packages: portalocker.

## Tests

### `public_tests/test_public_api.py::test_lock_context_manager`

- mapping: `B001`
- API: `featurelifted.Lock`
- risk: `filesystem_resource`
- A001 `assert` L11: `'xy' in path.read_text(encoding='utf-8')`

### `public_tests/test_public_api.py::test_lock_unlock_functions`

- mapping: `B002`
- API: `featurelifted.LOCK_EX, featurelifted.lock, featurelifted.unlock`
- risk: `filesystem_resource`
- A001 `assert` L24: `path.read_text(encoding='utf-8') == 'ab'`

### `hidden_tests/test_hidden_behavior.py::test_lock_constants`

- mapping: `B001, B004`
- API: `featurelifted.LOCK_EX, featurelifted.LOCK_NB, featurelifted.LOCK_SH`
- risk: `none`
- A001 `assert` L10: `LOCK_EX is not None and LOCK_SH is not None and (LOCK_NB is not None)`

### `hidden_tests/test_hidden_behavior.py::test_lock_exception_type`

- mapping: `B002`
- API: `featurelifted.LockException`
- risk: `none`
- A001 `assert` L14: `issubclass(LockException, Exception)`

### `hidden_tests/test_hidden_behavior.py::test_lock_timeout`

- mapping: `B003`
- API: `featurelifted.Lock`
- risk: `filesystem_resource`
- A001 `assert` L21: `path.exists()`

### `hidden_tests/test_hidden_behavior.py::test_no_upstream_import_surface`

- mapping: `B006`
- API: `featurelifted.__file__`
- risk: `filesystem_resource`
- A001 `assert` L30: `not pattern.search(path.read_text(encoding='utf-8'))`

### `hidden_tests/test_required_api_surface.py::test_required_api_surface`

- mapping: `B005`
- API: `featurelifted.LOCK_EX, featurelifted.Lock, featurelifted.lock, featurelifted.unlock`
- risk: `none`
- A001 `assert` L5: `Lock is not None and callable(lock) and callable(unlock)`
- A002 `assert` L6: `LOCK_EX is not None`

## Dependency / Oracle Evidence

- allowed dependencies: `none`
- forbidden imports: `portalocker`
- source entrypoints: `none`
- oracle source files: `portalocker/portalocker.py, portalocker/utils.py, portalocker/constants.py`
- runtime dependencies: `none`
- oracle notes: Direct lock/unlock + Lock context manager + LOCK_EX.
- behavior contract lacks a completed review_status
- behavior contract schema_version missing or unsupported
