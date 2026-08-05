# isodate__duration_parse_core__001

- release: `frozen_python150`
- lift: `Adapted`
- coupling: `unknown`
- strict validation: `PASS`
- tests/assertions: `10/24`

## Required API

- `featurelifted.Duration` (class) `(days=0, seconds=0, microseconds=0, milliseconds=0, minutes=0, hours=0, weeks=0, months=0, years=0)`
- `featurelifted.Duration.months` (attribute)
- `featurelifted.Duration.tdelta` (attribute)
- `featurelifted.Duration.totimedelta` (method) `(self, start=None, end=None)`
- `featurelifted.Duration.years` (attribute)
- `featurelifted.ISO8601Error` (exception)
- `featurelifted.duration_isoformat` (function) `(tduration, format='P%P')`
- `featurelifted.parse_duration` (function) `(datestring, as_timedelta_if_possible=True)`
- `featurelifted.isodates` (module)
- `featurelifted.isodates.parse_date` (function) `(datestring, yeardigits=4, expanded=False, defaultmonth=1, defaultday=1)`

## Public Behaviors

- **B001**: The extracted feature must support this observable behavior: parse P-period durations to timedelta or Duration. Required observable cases include parse duration days hours; parse duration weeks; parse duration full components; parse duration comma decimal hours; duration totimedelta with start; duration isoformat timedelta; parse invalid raises.
- **B002**: The extracted feature must support this observable behavior: duration_isoformat for Duration and timedelta. Required observable cases include duration isoformat; duration totimedelta with start; duration isoformat timedelta.
- **B003**: The extracted feature must support this observable behavior: decimal comma fractions in components. Required observable cases include parse duration comma decimal hours.
- **B004**: The extracted feature must support this observable behavior: ISO8601Error on invalid input. Required observable cases include parse invalid raises.
- **B005**: The package exposes the required task API paths `featurelifted.Duration`, `featurelifted.Duration.months`, `featurelifted.Duration.tdelta`, `featurelifted.Duration.totimedelta`, `featurelifted.Duration.years`, `featurelifted.ISO8601Error`, `featurelifted.duration_isoformat`, `featurelifted.parse_duration`, `featurelifted.isodates`, `featurelifted.isodates.parse_date` with the kinds and callable signatures listed in this contract.

## Tests

### `public_tests/test_public_api.py::test_parse_duration_days_hours`

- mapping: `B001`
- API: `featurelifted.parse_duration`
- risk: `none`
- A001 `assert` L10: `isinstance(result, timedelta)`
- A002 `assert` L11: `result == timedelta(days=1, hours=12)`

### `public_tests/test_public_api.py::test_parse_duration_weeks`

- mapping: `B001`
- API: `featurelifted.parse_duration`
- risk: `none`
- A001 `assert` L16: `result == timedelta(weeks=2)`

### `public_tests/test_public_api.py::test_duration_isoformat`

- mapping: `B002`
- API: `featurelifted.Duration, featurelifted.duration_isoformat`
- risk: `none`
- A001 `assert` L20: `duration_isoformat(Duration(years=1, months=2, days=3)) == 'P1Y2M3D'`

### `hidden_tests/test_hidden_behavior.py::test_parse_duration_full_components`

- mapping: `B001`
- API: `featurelifted.Duration, featurelifted.parse_duration`
- risk: `none`
- A001 `assert` L14: `isinstance(result, Duration)`
- A002 `assert` L15: `result.years == 1`
- A003 `assert` L16: `result.months == 2`
- A004 `assert` L17: `result.tdelta.days == 3`
- A005 `assert` L18: `result.tdelta.seconds == 4 * 3600 + 5 * 60 + 6`

### `hidden_tests/test_hidden_behavior.py::test_parse_duration_comma_decimal_hours`

- mapping: `B001, B003`
- API: `featurelifted.parse_duration`
- risk: `none`
- A001 `assert` L23: `result == timedelta(hours=1, minutes=30)`

### `hidden_tests/test_hidden_behavior.py::test_duration_totimedelta_with_start`

- mapping: `B001, B002`
- API: `featurelifted.Duration, featurelifted.isodates`
- risk: `none`
- A001 `assert` L31: `td == timedelta(days=396)`

### `hidden_tests/test_hidden_behavior.py::test_duration_isoformat_timedelta`

- mapping: `B001, B002`
- API: `featurelifted.duration_isoformat`
- risk: `none`
- A001 `assert` L35: `duration_isoformat(timedelta(hours=2, minutes=30)) == 'PT2H30M'`

### `hidden_tests/test_hidden_behavior.py::test_parse_invalid_raises`

- mapping: `B001, B004`
- API: `featurelifted.ISO8601Error, featurelifted.parse_duration`
- risk: `exception_semantics`
- A001 `raises` L39: `pytest.raises(ISO8601Error)`

### `hidden_tests/test_hidden_behavior.py::test_no_isodate_import_surface`

- mapping: `B006`
- API: `featurelifted.__file__`
- risk: `filesystem_resource`
- A001 `assert` L49: `not import_pattern.search(path.read_text(encoding='utf-8'))`

### `hidden_tests/test_required_api_surface.py::test_required_api_surface`

- mapping: `B005`
- API: `featurelifted.Duration, featurelifted.ISO8601Error, featurelifted.duration_isoformat, featurelifted.isodates, featurelifted.parse_duration`
- risk: `none`
- A001 `assert` L13: `isinstance(Duration, type)`
- A002 `assert` L14: `Duration is not None`
- A003 `assert` L15: `Duration is not None`
- A004 `assert` L16: `hasattr(Duration, 'totimedelta')`
- A005 `assert` L17: `Duration is not None`
- A006 `assert` L18: `issubclass(ISO8601Error, BaseException)`
- A007 `assert` L19: `callable(duration_isoformat)`
- A008 `assert` L20: `callable(parse_duration)`
- A009 `assert` L21: `isodates is not None`
- A010 `assert` L22: `callable(getattr(isodates, 'parse_date'))`

## Dependency / Oracle Evidence

- allowed dependencies: `none`
- forbidden imports: `isodate`
- source entrypoints: `isodate.parse_duration, isodate.duration_isoformat, isodate.duration.Duration`
- oracle source files: `isodate/duration.py, isodate/isoduration.py, isodate/isoerror.py, isodate/isodatetime.py, isodate/isodates.py, isodate/isotime.py, isodate/isostrf.py, isodate/isotzinfo.py, isodate/tzinfo.py`
- runtime dependencies: `none`
- oracle notes: Oracle is duration parse/format chain; repo includes tz/time helpers for copy-all penalty.
