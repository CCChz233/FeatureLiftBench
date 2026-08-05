# huey__task_schedule_core__001

- release: `external50`
- lift: `Composite`
- coupling: `framework_coupling`
- strict validation: `PASS`
- tests/assertions: `6/14`

## Required API

- `featurelifted.MemoryHuey` (class)
- `featurelifted.MemoryHuey.task` (method)
- `featurelifted.MemoryHuey.pending_count` (method)
- `featurelifted.MemoryHuey.flush` (method)
- `featurelifted.crontab` (function)

## Public Behaviors

- **B001**: The extracted feature must support this observable behavior: enqueue tasks and read results via result.get after execute. Required observable cases include task enqueue and result.
- **B002**: The extracted feature must support this observable behavior: crontab schedule helper. Required observable cases include crontab helper.
- **B003**: The extracted feature must support this observable behavior: multiple tasks and flush clears queue. Required observable cases include multiple tasks; flush clears queue.
- **B004**: MemoryHuey is the only broker backend required.
- **B005**: The package exposes MemoryHuey and crontab with the kinds listed in this contract.
- **B006**: the submitted package does not import forbidden upstream packages: huey.

## Tests

### `public_tests/test_public_api.py::test_task_enqueue_and_result`

- mapping: `B001`
- API: `featurelifted.MemoryHuey`
- risk: `none`
- A001 `assert` L22: `result.get(blocking=False) == 3`

### `public_tests/test_public_api.py::test_crontab_helper`

- mapping: `B002`
- API: `featurelifted.crontab`
- risk: `none`
- A001 `assert` L27: `callable(schedule)`
- A002 `assert` L29: `schedule(when) is True`
- A003 `assert` L30: `schedule(datetime(2024, 1, 1, 10, 3, 0)) is False`

### `hidden_tests/test_hidden_behavior.py::test_multiple_tasks`

- mapping: `B001, B003, B004`
- API: `featurelifted.MemoryHuey`
- risk: `none`
- A001 `assert` L22: `r1.get(blocking=False) == 6`
- A002 `assert` L23: `r2.get(blocking=False) == 20`

### `hidden_tests/test_hidden_behavior.py::test_flush_clears_queue`

- mapping: `B002`
- API: `featurelifted.MemoryHuey`
- risk: `none`
- A001 `assert` L33: `huey.pending_count() >= 1`
- A002 `assert` L35: `huey.pending_count() == 0`

### `hidden_tests/test_hidden_behavior.py::test_no_upstream_import_surface`

- mapping: `B006`
- API: `featurelifted.__file__`
- risk: `filesystem_resource`
- A001 `assert` L49: `not pattern.search(path.read_text(encoding='utf-8'))`

### `hidden_tests/test_required_api_surface.py::test_required_api_surface`

- mapping: `B005`
- API: `featurelifted.MemoryHuey, featurelifted.MemoryHuey.flush, featurelifted.MemoryHuey.pending_count, featurelifted.MemoryHuey.task`
- risk: `none`
- A001 `assert` L5: `hasattr(featurelifted, 'MemoryHuey')`
- A002 `assert` L6: `hasattr(featurelifted, 'crontab')`
- A003 `assert` L7: `callable(featurelifted.MemoryHuey.task)`
- A004 `assert` L8: `callable(featurelifted.MemoryHuey.pending_count)`
- A005 `assert` L9: `callable(featurelifted.MemoryHuey.flush)`

## Dependency / Oracle Evidence

- allowed dependencies: `none`
- forbidden imports: `huey`
- source entrypoints: `none`
- oracle source files: `huey/api.py, huey/storage.py`
- runtime dependencies: `none`
- oracle notes: Composite MemoryHuey task decorator + crontab + dequeue/execute result.get.
- behavior contract lacks a completed review_status
- behavior contract schema_version missing or unsupported
