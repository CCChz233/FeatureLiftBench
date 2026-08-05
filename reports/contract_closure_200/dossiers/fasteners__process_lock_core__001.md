# fasteners__process_lock_core__001

- release: `external50`
- lift: `Direct`
- coupling: `resource_coupling`
- strict validation: `PASS`
- tests/assertions: `6/6`

## Required API

- `featurelifted.InterProcessLock` (class)
- `featurelifted.InterProcessLock.acquire` (method) `(blocking: bool = True) -> bool`
- `featurelifted.InterProcessLock.release` (method)

## Public Behaviors

- **B001**: The extracted feature must support this observable behavior: InterProcessLock acquire/release. Required observable cases include acquire release; reacquire after release.
- **B002**: The extracted feature must support this observable behavior: context manager acquires and releases. Required observable cases include context manager.
- **B003**: The extracted feature must support this observable behavior: non-blocking acquire succeeds on a free lock. Required observable cases include nonblocking acquire free lock.
- **B004**: Lock files are created under the provided path in temp directories during tests.
- **B005**: The package exposes InterProcessLock with the kinds listed in this contract.
- **B006**: the submitted package does not import forbidden upstream packages: fasteners.

## Tests

### `public_tests/test_public_api.py::test_acquire_release`

- mapping: `B001`
- API: `featurelifted.InterProcessLock`
- risk: `filesystem_resource`
- A001 `assert` L9: `lock.acquire() is True`

### `public_tests/test_public_api.py::test_context_manager`

- mapping: `B002`
- API: `featurelifted.InterProcessLock`
- risk: `filesystem_resource, implicit_no_exception_assertion`
- assertion: implicit successful execution

### `hidden_tests/test_hidden_behavior.py::test_reacquire_after_release`

- mapping: `B001, B003, B004`
- API: `featurelifted.InterProcessLock`
- risk: `filesystem_resource`
- A001 `assert` L12: `lock.acquire() is True`
- A002 `assert` L14: `lock.acquire() is True`

### `hidden_tests/test_hidden_behavior.py::test_nonblocking_acquire_free_lock`

- mapping: `B002`
- API: `featurelifted.InterProcessLock`
- risk: `filesystem_resource`
- A001 `assert` L21: `lock.acquire(blocking=False) is True`

### `hidden_tests/test_hidden_behavior.py::test_no_upstream_import_surface`

- mapping: `B006`
- API: `featurelifted.__file__`
- risk: `filesystem_resource`
- A001 `assert` L31: `not pattern.search(path.read_text(encoding='utf-8'))`

### `hidden_tests/test_required_api_surface.py::test_required_api_surface`

- mapping: `B005`
- API: `featurelifted.InterProcessLock`
- risk: `none`
- A001 `assert` L5: `InterProcessLock is not None`

## Dependency / Oracle Evidence

- allowed dependencies: `none`
- forbidden imports: `fasteners`
- source entrypoints: `none`
- oracle source files: `fasteners/process_lock.py, fasteners/process_mechanism.py`
- runtime dependencies: `none`
- oracle notes: Direct InterProcessLock acquire/release/context manager.
- behavior contract lacks a completed review_status
- behavior contract schema_version missing or unsupported
