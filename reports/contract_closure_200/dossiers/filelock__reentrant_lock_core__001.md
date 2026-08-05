# filelock__reentrant_lock_core__001

- release: `frozen_python150`
- lift: `Adapted`
- coupling: `unknown`
- strict validation: `PASS`
- tests/assertions: `5/11`

## Required API

- `featurelifted.FileLock` (class) `(lock_file, timeout=-1, poll_interval=0.05)`
- `featurelifted.FileLock.acquire` (method) `(self, timeout=None, poll_interval=None, blocking=True)`
- `featurelifted.FileLock.is_locked` (attribute)
- `featurelifted.FileLock.release` (method) `(self, force=False)`
- `featurelifted.Timeout` (exception)

## Public Behaviors

- **B001**: The extracted feature must support this observable behavior: exclusive lock-file acquisition across instances. Required observable cases include context and reentrant release; nonblocking contention; force release and idempotence; two instances can acquire sequentially.
- **B002**: The extracted feature must support this observable behavior: reentrant acquire and balanced release on one instance. Required observable cases include context and reentrant release; nonblocking contention; force release and idempotence; two instances can acquire sequentially.
- **B003**: The extracted feature must support this observable behavior: timeout and non-blocking acquisition. Required observable cases include context and reentrant release; nonblocking contention; force release and idempotence; two instances can acquire sequentially.
- **B004**: The extracted feature must support this observable behavior: context-manager release and lock-file cleanup. Required observable cases include context and reentrant release; nonblocking contention; force release and idempotence; two instances can acquire sequentially.
- **B005**: The package exposes the required task API paths `featurelifted.FileLock`, `featurelifted.FileLock.acquire`, `featurelifted.FileLock.is_locked`, `featurelifted.FileLock.release`, `featurelifted.Timeout` with the kinds and callable signatures listed in this contract.

## Tests

### `public_tests/test_public_contract.py::test_context_and_reentrant_release`

- mapping: `B001, B002, B003, B004`
- API: `featurelifted.FileLock`
- risk: `filesystem_resource`
- A001 `assert` L12: `not lock.is_locked and (not path.exists())`
- A002 `assert` L8: `lock.is_locked and path.exists()`
- A003 `assert` L11: `lock.is_locked`

### `public_tests/test_public_contract.py::test_nonblocking_contention`

- mapping: `B001, B002, B003, B004`
- API: `featurelifted.FileLock, featurelifted.Timeout`
- risk: `exception_semantics, filesystem_resource`
- A001 `raises` L18: `pytest.raises(Timeout)`

### `hidden_tests/test_hidden_contract.py::test_force_release_and_idempotence`

- mapping: `B001, B002, B003, B004`
- API: `featurelifted.FileLock`
- risk: `filesystem_resource`
- A001 `assert` L7: `not lock.is_locked`

### `hidden_tests/test_hidden_contract.py::test_two_instances_can_acquire_sequentially`

- mapping: `B001, B002, B003, B004`
- API: `featurelifted.FileLock`
- risk: `filesystem_resource`
- A001 `assert` L15: `b.lock_counter == 1`

### `hidden_tests/test_required_api_surface.py::test_required_api_surface`

- mapping: `B005`
- API: `featurelifted.FileLock, featurelifted.Timeout`
- risk: `none`
- A001 `assert` L10: `isinstance(FileLock, type)`
- A002 `assert` L11: `hasattr(FileLock, 'acquire')`
- A003 `assert` L12: `FileLock is not None`
- A004 `assert` L13: `hasattr(FileLock, 'release')`
- A005 `assert` L14: `issubclass(Timeout, BaseException)`

## Dependency / Oracle Evidence

- allowed dependencies: `none`
- forbidden imports: `filelock`
- source entrypoints: `filelock._api.BaseFileLock, filelock._unix.UnixFileLock, filelock._error.Timeout`
- oracle source files: `filelock._api.BaseFileLock, filelock._unix.UnixFileLock, filelock._error.Timeout`
- runtime dependencies: `none`
- oracle notes: Entrypoints are maintainer-private provenance and are never Agent-visible in Main.
- behavior contract lacks a completed review_status
