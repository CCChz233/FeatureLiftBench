# python_dateutil__rrule_core__001

- release: `frozen_python150`
- lift: `Direct`
- coupling: `unknown`
- strict validation: `PASS`
- tests/assertions: `11/29`

## Required API

- `featurelifted.rrule` (module)
- `featurelifted.rruleset` (function) `(cache=False)`
- `featurelifted.rrulestr` (function) `(s, **kwargs)`
- `featurelifted.YEARLY` (constant)
- `featurelifted.MONTHLY` (constant)
- `featurelifted.WEEKLY` (constant)
- `featurelifted.DAILY` (constant)
- `featurelifted.MO` (constant)
- `featurelifted.TU` (constant)
- `featurelifted.WE` (constant)
- `featurelifted.TH` (constant)
- `featurelifted.FR` (constant)
- `featurelifted.SA` (constant)
- `featurelifted.SU` (constant)

## Public Behaviors

- **B001**: The extracted feature must support this observable behavior: rrule iteration with freq, interval, count, until, and BY* filters. Required observable cases include weekly byweekday filter; count stops iteration; bysetpos last friday; invalid rrulestr freq raises.
- **B002**: The extracted feature must support this observable behavior: rruleset include rules with EXDATE/RDATE (naive). Required observable cases include rrulestr parses monthly rule; rruleset exdate skips.
- **B003**: The extracted feature must support this observable behavior: rrulestr for RRULE lines with naive iCalendar date values. Required observable cases include monthly rrule yields dates; rrulestr parses monthly rule; invalid rrulestr freq raises; rrulestr byday token.
- **B004**: The extracted feature must support this observable behavior: BYEASTER offsets via easter helper. Required observable cases include byeaster occurrence.
- **B005**: The extracted feature must support this observable behavior: weekday constants MO..SU and freq constants. Required observable cases include bysetpos last friday.
- **B006**: The package exposes the required task API paths `featurelifted.rrule`, `featurelifted.rruleset`, `featurelifted.rrulestr`, `featurelifted.YEARLY`, `featurelifted.MONTHLY`, `featurelifted.WEEKLY`, `featurelifted.DAILY`, `featurelifted.MO`, `featurelifted.TU`, `featurelifted.WE`, `featurelifted.TH`, `featurelifted.FR`, and 2 listed members with the kinds and callable signatures listed in this contract.

## Tests

### `public_tests/test_public_api.py::test_monthly_rrule_yields_dates`

- mapping: `B003`
- API: `featurelifted.MONTHLY, featurelifted.rrule`
- risk: `time_or_randomness`
- A001 `assert` L11: `list(rule) == [datetime.datetime(2020, 1, 15), datetime.datetime(2020, 2, 15), datetime.datetime(2020, 3, 15)]`

### `public_tests/test_public_api.py::test_weekly_byweekday_filter`

- mapping: `B001`
- API: `featurelifted.MO, featurelifted.WEEKLY, featurelifted.rrule`
- risk: `time_or_randomness`
- A001 `assert` L21: `list(rule) == [datetime.datetime(2020, 1, 6), datetime.datetime(2020, 1, 13)]`

### `public_tests/test_public_api.py::test_count_stops_iteration`

- mapping: `B001`
- API: `featurelifted.DAILY, featurelifted.rrule`
- risk: `time_or_randomness`
- A001 `assert` L30: `len(list(rule)) == 2`

### `public_tests/test_public_api.py::test_rrulestr_parses_monthly_rule`

- mapping: `B002, B003`
- API: `featurelifted.rrulestr`
- risk: `time_or_randomness`
- A001 `assert` L36: `list(rule) == [datetime.datetime(2020, 1, 15), datetime.datetime(2020, 2, 15)]`

### `hidden_tests/test_hidden_behavior.py::test_bysetpos_last_friday`

- mapping: `B001, B005`
- API: `featurelifted.FR, featurelifted.MONTHLY, featurelifted.rrule`
- risk: `time_or_randomness`
- A001 `assert` L16: `all((d.weekday() == 4 for d in got))`
- A002 `assert` L17: `got[0] == datetime.datetime(2020, 1, 31)`
- A003 `assert` L18: `got[1] == datetime.datetime(2020, 2, 28)`

### `hidden_tests/test_hidden_behavior.py::test_byeaster_occurrence`

- mapping: `B004`
- API: `featurelifted.YEARLY, featurelifted.rrule`
- risk: `time_or_randomness`
- A001 `assert` L25: `len(got) == 2`
- A002 `assert` L26: `got[0].month == 4 and got[0].day == 13`

### `hidden_tests/test_hidden_behavior.py::test_rruleset_exdate_skips`

- mapping: `B002`
- API: `featurelifted.DAILY, featurelifted.rrule, featurelifted.rruleset`
- risk: `time_or_randomness`
- A001 `assert` L34: `list(rs) == [datetime.datetime(2020, 1, 1), datetime.datetime(2020, 1, 3)]`

### `hidden_tests/test_hidden_behavior.py::test_invalid_rrulestr_freq_raises`

- mapping: `B001, B003`
- API: `featurelifted.rrulestr`
- risk: `exception_semantics, time_or_randomness`
- A001 `raises` L42: `pytest.raises(ValueError)`

### `hidden_tests/test_hidden_behavior.py::test_rrulestr_byday_token`

- mapping: `B003`
- API: `featurelifted.rrulestr`
- risk: `time_or_randomness`
- A001 `assert` L50: `len(got) == 2`
- A002 `assert` L51: `got[0].weekday() == 0`

### `hidden_tests/test_hidden_behavior.py::test_no_dateutil_import_surface`

- mapping: `B007`
- API: `featurelifted.__file__`
- risk: `filesystem_resource`
- A001 `assert` L60: `name not in exports`
- A002 `assert` L65: `not import_pattern.search(path.read_text(encoding='utf-8'))`

### `hidden_tests/test_required_api_surface.py::test_required_api_surface`

- mapping: `B006`
- API: `featurelifted.DAILY, featurelifted.FR, featurelifted.MO, featurelifted.MONTHLY, featurelifted.SA, featurelifted.SU, featurelifted.TH, featurelifted.TU, featurelifted.WE, featurelifted.WEEKLY, featurelifted.YEARLY, featurelifted.rrule, featurelifted.rruleset, featurelifted.rrulestr`
- risk: `none`
- A001 `assert` L22: `rrule is not None`
- A002 `assert` L23: `callable(rruleset)`
- A003 `assert` L24: `callable(rrulestr)`
- A004 `assert` L25: `YEARLY is not None`
- A005 `assert` L26: `MONTHLY is not None`
- A006 `assert` L27: `WEEKLY is not None`
- A007 `assert` L28: `DAILY is not None`
- A008 `assert` L29: `MO is not None`
- A009 `assert` L30: `TU is not None`
- A010 `assert` L31: `WE is not None`
- A011 `assert` L32: `TH is not None`
- A012 `assert` L33: `FR is not None`
- A013 `assert` L34: `SA is not None`
- A014 `assert` L35: `SU is not None`

## Dependency / Oracle Evidence

- allowed dependencies: `none`
- forbidden imports: `dateutil`
- source entrypoints: `dateutil.rrule.rrule, dateutil.rrule.rruleset, dateutil.rrule.rrulestr, dateutil.rrule.weekday, dateutil.easter.easter`
- oracle source files: `dateutil/_common.py, dateutil/easter.py, dateutil/rrule.py`
- runtime dependencies: `none`
- oracle notes: Oracle closure is rrule stack only; repo snapshot includes full dateutil package for extraction denominator.
