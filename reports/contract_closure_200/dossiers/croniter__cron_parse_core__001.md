# croniter__cron_parse_core__001

- release: `frozen_python150`
- lift: `Direct`
- coupling: `unknown`
- strict validation: `PASS`
- tests/assertions: `10/18`

## Required API

- `featurelifted.croniter` (function) `(expr_format, start_time=None, ret_type=<class 'float'>, day_or=True, max_years_between_matches=None, is_prev=False, hash_id=None, implement_cron_bug=False, second_at_beginning=None, expand_from_start_time=False)`
- `featurelifted.datetime_to_timestamp` (function) `(d)`
- `featurelifted.CroniterBadCronError` (exception)
- `featurelifted.CroniterBadDateError` (exception)
- `featurelifted.CroniterNotAlphaError` (exception)

## Public Behaviors

- **B001**: The extracted feature must support this observable behavior: parse standard 5-field cron expressions. Required observable cases include weekday field parses; step and range fields.
- **B002**: The extracted feature must support this observable behavior: compute next matching naive datetime from a base time. Required observable cases include daily noon next; daily noon prev; hourly on base minute; combined next prev walk; dom dow union next.
- **B003**: The extracted feature must support this observable behavior: compute previous matching naive datetime from a base time. Required observable cases include daily noon prev; hourly on base minute; step and range fields.
- **B004**: The extracted feature must support this observable behavior: step and range field expansion (e.g. */15, 9-17). Required observable cases include step and range fields.
- **B005**: The extracted feature must support this observable behavior: reject invalid field values with CroniterBadCronError. Required observable cases include invalid minute raises.
- **B006**: The package exposes the required task API paths `featurelifted.croniter`, `featurelifted.datetime_to_timestamp`, `featurelifted.CroniterBadCronError`, `featurelifted.CroniterBadDateError`, `featurelifted.CroniterNotAlphaError` with the kinds and callable signatures listed in this contract.

## Tests

### `public_tests/test_public_api.py::test_daily_noon_next`

- mapping: `B002`
- API: `featurelifted.croniter`
- risk: `none`
- A001 `assert` L13: `itr.get_next(datetime) == datetime(2024, 1, 16, 12, 0, 0)`

### `public_tests/test_public_api.py::test_daily_noon_prev`

- mapping: `B002, B003`
- API: `featurelifted.croniter`
- risk: `none`
- A001 `assert` L18: `itr.get_prev(datetime) == datetime(2024, 1, 14, 12, 0, 0)`

### `public_tests/test_public_api.py::test_hourly_on_base_minute`

- mapping: `B002, B003`
- API: `featurelifted.croniter`
- risk: `none`
- A001 `assert` L23: `itr.get_next(datetime) == datetime(2024, 1, 15, 12, 30, 0)`

### `public_tests/test_public_api.py::test_weekday_field_parses`

- mapping: `B001`
- API: `featurelifted.croniter`
- risk: `none`
- A001 `assert` L28: `itr.get_next(datetime) == datetime(2024, 1, 22, 9, 0, 0)`

### `hidden_tests/test_hidden_behavior.py::test_step_and_range_fields`

- mapping: `B001, B003, B004`
- API: `featurelifted.croniter`
- risk: `none`
- A001 `assert` L17: `itr.get_next(datetime) == datetime(2024, 1, 15, 12, 15, 0)`
- A002 `assert` L18: `itr.get_next(datetime) == datetime(2024, 1, 15, 12, 30, 0)`

### `hidden_tests/test_hidden_behavior.py::test_invalid_minute_raises`

- mapping: `B005`
- API: `featurelifted.CroniterBadCronError, featurelifted.croniter`
- risk: `exception_semantics`
- A001 `raises` L22: `pytest.raises(CroniterBadCronError)`

### `hidden_tests/test_hidden_behavior.py::test_combined_next_prev_walk`

- mapping: `B002`
- API: `featurelifted.croniter`
- risk: `none`
- A001 `assert` L29: `forward.get_next(datetime) == datetime(2024, 1, 15, 20, 0, 0)`
- A002 `assert` L30: `forward.get_next(datetime) == datetime(2024, 1, 16, 8, 0, 0)`
- A003 `assert` L33: `backward.get_prev(datetime) == datetime(2024, 1, 15, 8, 0, 0)`
- A004 `assert` L34: `backward.get_prev(datetime) == datetime(2024, 1, 14, 20, 0, 0)`

### `hidden_tests/test_hidden_behavior.py::test_dom_dow_union_next`

- mapping: `B002`
- API: `featurelifted.croniter`
- risk: `none`
- A001 `assert` L39: `itr.get_next(datetime) == datetime(2024, 1, 22, 12, 0, 0)`

### `hidden_tests/test_hidden_behavior.py::test_no_croniter_import_surface`

- mapping: `B007`
- API: `featurelifted.__file__`
- risk: `filesystem_resource`
- A001 `assert` L49: `not import_pattern.search(text)`

### `hidden_tests/test_required_api_surface.py::test_required_api_surface`

- mapping: `B006`
- API: `featurelifted.CroniterBadCronError, featurelifted.CroniterBadDateError, featurelifted.CroniterNotAlphaError, featurelifted.croniter, featurelifted.datetime_to_timestamp`
- risk: `none`
- A001 `assert` L13: `callable(croniter)`
- A002 `assert` L14: `callable(datetime_to_timestamp)`
- A003 `assert` L15: `issubclass(CroniterBadCronError, BaseException)`
- A004 `assert` L16: `issubclass(CroniterBadDateError, BaseException)`
- A005 `assert` L17: `issubclass(CroniterNotAlphaError, BaseException)`

## Dependency / Oracle Evidence

- allowed dependencies: `python-dateutil, six`
- forbidden imports: `croniter`
- source entrypoints: `croniter.croniter, croniter.croniter.croniter, croniter.croniter.croniter.get_next, croniter.croniter.croniter.get_prev, croniter.croniter.datetime_to_timestamp`
- oracle source files: `croniter/__init__.py, croniter/croniter.py`
- runtime dependencies: `python-dateutil`
- oracle notes: Oracle splits croniter.py into constants/errors/utils/iterator modules; omits croniter_range, HashExpander, and match_range.
