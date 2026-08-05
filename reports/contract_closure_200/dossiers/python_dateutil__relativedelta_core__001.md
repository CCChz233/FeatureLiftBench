# python_dateutil__relativedelta_core__001

- release: `frozen_python150`
- lift: `Direct`
- coupling: `unknown`
- strict validation: `FAIL`
- tests/assertions: `14/29`

## Required API

- `featurelifted.relativedelta` (module)
- `featurelifted.MO` (constant)
- `featurelifted.TU` (constant)
- `featurelifted.WE` (constant)
- `featurelifted.TH` (constant)
- `featurelifted.FR` (constant)
- `featurelifted.SA` (constant)
- `featurelifted.SU` (constant)

## Public Behaviors

- **B001**: The extracted feature must support this observable behavior: relativedelta construction with relative and absolute fields. Required observable cases include absolute day replacement; subtract relativedelta.
- **B002**: The extracted feature must support this observable behavior: datetime/date addition and subtraction with month/year rollover. Required observable cases include add months to datetime; relativedelta diff months; last friday of month; yearday sets month day; non integer years months rejected.
- **B003**: The extracted feature must support this observable behavior: weekday nth helpers MO..SU with setpos semantics. Required observable cases include weekday constant identity; weekday nth first monday.
- **B004**: The extracted feature must support this observable behavior: normalized() for fractional day/hour cascading. Required observable cases include add days and hours; absolute day replacement; normalized fractional days.
- **B005**: The extracted feature must support this observable behavior: relativedelta(dt1, dt2) difference mode. Required observable cases include relativedelta diff months; subtract relativedelta.
- **B006**: The extracted feature must support this observable behavior: yearday/nlyearday and leapdays adjustments. Required observable cases include yearday sets month day; leapdays post february.
- **B007**: The package exposes the required task API paths `featurelifted.relativedelta`, `featurelifted.MO`, `featurelifted.TU`, `featurelifted.WE`, `featurelifted.TH`, `featurelifted.FR`, `featurelifted.SA`, `featurelifted.SU` with the kinds and callable signatures listed in this contract.

## Tests

### `public_tests/test_public_api.py::test_add_months_to_datetime`

- mapping: `B002`
- API: `featurelifted.relativedelta`
- risk: `time_or_randomness`
- A001 `assert` L11: `result == datetime.datetime(2020, 2, 15, 12, 0)`

### `public_tests/test_public_api.py::test_add_days_and_hours`

- mapping: `B004`
- API: `featurelifted.relativedelta`
- risk: `time_or_randomness`
- A001 `assert` L17: `result == datetime.datetime(2020, 1, 3, 3, 0)`

### `public_tests/test_public_api.py::test_weekday_constant_identity`

- mapping: `B003`
- API: `featurelifted.MO, featurelifted.MO.weekday`
- risk: `none`
- A001 `assert` L21: `MO.weekday == 0`
- A002 `assert` L22: `repr(MO(+2)) == 'MO(+2)'`

### `public_tests/test_public_api.py::test_absolute_day_replacement`

- mapping: `B001, B004`
- API: `featurelifted.relativedelta`
- risk: `time_or_randomness`
- A001 `assert` L28: `result == datetime.datetime(2020, 3, 1)`

### `hidden_tests/test_hidden_behavior.py::test_normalized_fractional_days`

- mapping: `B004`
- API: `featurelifted.relativedelta`
- risk: `none`
- A001 `assert` L15: `normalized.days == 1`
- A002 `assert` L16: `normalized.hours == 14`
- A003 `assert` L17: `normalized.minutes == 0`

### `hidden_tests/test_hidden_behavior.py::test_weekday_nth_first_monday`

- mapping: `B003`
- API: `featurelifted.MO, featurelifted.relativedelta`
- risk: `time_or_randomness`
- A001 `assert` L23: `result == datetime.datetime(2020, 4, 6)`
- A002 `assert` L24: `result.weekday() == 0`

### `hidden_tests/test_hidden_behavior.py::test_relativedelta_diff_months`

- mapping: `B002, B005`
- API: `featurelifted.relativedelta`
- risk: `time_or_randomness`
- A001 `assert` L31: `delta.months == 2`
- A002 `assert` L32: `delta.days == 5`

### `hidden_tests/test_hidden_behavior.py::test_last_friday_of_month`

- mapping: `B002`
- API: `featurelifted.FR, featurelifted.relativedelta`
- risk: `time_or_randomness`
- A001 `assert` L38: `result == datetime.datetime(2020, 1, 31)`
- A002 `assert` L39: `result.weekday() == 4`

### `hidden_tests/test_hidden_behavior.py::test_yearday_sets_month_day`

- mapping: `B002, B006`
- API: `featurelifted.relativedelta`
- risk: `time_or_randomness`
- A001 `assert` L46: `result.month == 2`
- A002 `assert` L47: `result.day == 29`

### `hidden_tests/test_hidden_behavior.py::test_leapdays_post_february`

- mapping: `B006`
- API: `featurelifted.relativedelta`
- risk: `time_or_randomness`
- A001 `assert` L53: `result == datetime.datetime(2020, 3, 29)`

### `hidden_tests/test_hidden_behavior.py::test_subtract_relativedelta`

- mapping: `B001, B005`
- API: `featurelifted.relativedelta`
- risk: `time_or_randomness`
- A001 `assert` L59: `result == datetime.datetime(2020, 4, 10)`

### `hidden_tests/test_hidden_behavior.py::test_no_dateutil_import_surface`

- mapping: `B008`
- API: `featurelifted.__file__`
- risk: `filesystem_resource`
- A001 `assert` L68: `name not in exports`
- A002 `assert` L73: `not import_pattern.search(path.read_text(encoding='utf-8'))`

### `hidden_tests/test_hidden_behavior.py::test_non_integer_years_months_rejected`

- mapping: `B002`
- API: `featurelifted.relativedelta`
- risk: `exception_semantics`
- A001 `raises` L77: `pytest.raises(ValueError)`

### `hidden_tests/test_required_api_surface.py::test_required_api_surface`

- mapping: `B007`
- API: `featurelifted.FR, featurelifted.MO, featurelifted.SA, featurelifted.SU, featurelifted.TH, featurelifted.TU, featurelifted.WE, featurelifted.relativedelta`
- risk: `none`
- A001 `assert` L16: `relativedelta is not None`
- A002 `assert` L17: `MO is not None`
- A003 `assert` L18: `TU is not None`
- A004 `assert` L19: `WE is not None`
- A005 `assert` L20: `TH is not None`
- A006 `assert` L21: `FR is not None`
- A007 `assert` L22: `SA is not None`
- A008 `assert` L23: `SU is not None`

## Dependency / Oracle Evidence

- allowed dependencies: `none`
- forbidden imports: `dateutil`
- source entrypoints: `dateutil.relativedelta.relativedelta, dateutil.relativedelta.weekday, dateutil._common.weekday`
- oracle source files: `dateutil/_common.py, dateutil/relativedelta.py`
- runtime dependencies: `none`
- oracle notes: Oracle closure is relativedelta stack only; repo snapshot includes full dateutil package for extraction denominator.

## Machine Issues

- public_tests/test_public_api.py uses undeclared API reference featurelifted.MO.weekday
