# apscheduler__cron_trigger_core__hard3_001

- release: `frozen_python150`
- lift: `Adapted`
- coupling: `unknown`
- strict validation: `PASS`
- tests/assertions: `4/5`

## Required API

- `featurelifted.CronTrigger` (class) `(*, minute: 'str | int' = '*', hour: 'str | int' = '*', day: 'str | int' = '*', month: 'str | int' = '*', day_of_week: 'str | int' = '*', start_time: 'datetime | None' = None, end_time: 'datetime | None' = None) -> 'None'`
- `featurelifted.CronTrigger.get_next_fire_time` (method) `(self, now: 'datetime | None' = None) -> 'datetime | None'`

## Public Behaviors

- **B001**: When CronTrigger receives supported cron expressions, it parses wildcard, range, list, and step field forms into matching constraints.
- **B002**: When get_next_fire_time is called, it returns the first matching datetime after now while advancing across cron fields deterministically.
- **B003**: When a computed fire time would exceed end_time, get_next_fire_time returns no result; start_time remains the lower boundary.
- **B004**: The package exposes the required task API paths `featurelifted.CronTrigger`, `featurelifted.CronTrigger.get_next_fire_time` with the kinds and callable signatures listed in this contract.

## Tests

### `public_tests/test_public_contract.py::test_specific_minute_and_hour`

- mapping: `B004`
- API: `featurelifted.CronTrigger`
- risk: `none`
- A001 `assert` L11: `nxt == datetime(2024, 1, 1, 9, 15)`

### `hidden_tests/test_hidden_contract.py::test_end_time_boundary`

- mapping: `B003`
- API: `featurelifted.CronTrigger`
- risk: `none`
- A001 `assert` L11: `trigger.get_next_fire_time(now) is None`

### `hidden_tests/test_hidden_contract.py::test_specific_day_and_hour`

- mapping: `B001, B002, B004`
- API: `featurelifted.CronTrigger`
- risk: `none`
- A001 `assert` L18: `nxt == datetime(2024, 1, 1, 12, 30)`

### `hidden_tests/test_required_api_surface.py::test_required_api_surface`

- mapping: `B004`
- API: `featurelifted.CronTrigger`
- risk: `none`
- A001 `assert` L9: `isinstance(CronTrigger, type)`
- A002 `assert` L10: `hasattr(CronTrigger, 'get_next_fire_time')`

## Dependency / Oracle Evidence

- allowed dependencies: `none`
- forbidden imports: `apscheduler`
- source entrypoints: `apscheduler.triggers.cron.CronTrigger`
- oracle source files: `repo/src/apscheduler/triggers/cron/__init__.py`
- runtime dependencies: `none`
- oracle notes: Cron trigger subset without scheduler runtime.
