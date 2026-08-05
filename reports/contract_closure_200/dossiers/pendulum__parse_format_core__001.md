# pendulum__parse_format_core__001

- release: `frozen_python150`
- lift: `Adapted`
- coupling: `unknown`
- strict validation: `PASS`
- tests/assertions: `16/73`

## Required API

- `featurelifted.UTC` (constant)
- `featurelifted.Date` (class) `(*args, **kwargs)`
- `featurelifted.Date.day` (attribute)
- `featurelifted.Date.hour` (attribute)
- `featurelifted.Date.minute` (attribute)
- `featurelifted.Date.month` (attribute)
- `featurelifted.Date.year` (attribute)
- `featurelifted.DateTime` (class) `(*args, **kwargs)`
- `featurelifted.DateTime.hour` (attribute)
- `featurelifted.DateTime.microsecond` (attribute)
- `featurelifted.DateTime.minute` (attribute)
- `featurelifted.DateTime.offset` (attribute)
- `featurelifted.Duration` (class) `(days: 'float' = 0, seconds: 'float' = 0, microseconds: 'float' = 0, milliseconds: 'float' = 0, minutes: 'float' = 0, hours: 'float' = 0, weeks: 'float' = 0, years: 'float' = 0, months: 'float' = 0) -> 'Self'`
- `featurelifted.Duration.hours` (attribute)
- `featurelifted.Duration.in_days` (method) `(self) -> 'int'`
- `featurelifted.Duration.minutes` (attribute)
- `featurelifted.Duration.months` (attribute)
- `featurelifted.Duration.remaining_days` (attribute)
- `featurelifted.Duration.remaining_seconds` (attribute)
- `featurelifted.Duration.weeks` (attribute)
- `featurelifted.Duration.years` (attribute)
- `featurelifted.ParserError` (exception)
- `featurelifted.Time` (class) `(*args, **kwargs)`
- `featurelifted.datetime` (module)
- `featurelifted.duration` (module)
- `featurelifted.fixed_timezone` (function) `(offset: 'int') -> 'FixedTimezone'`
- `featurelifted.parse` (function) `(text: 'str', **options: 't.Any') -> 'Date | Time | DateTime | Duration'`

## Public Behaviors

- **B001**: The extracted feature must support this observable behavior: parse ISO8601 dates, datetimes with Z or numeric offsets, and durations. Required observable cases include parse iso date; parse iso datetime zulu; parse iso duration; parse iso week calendar date; parse duration weeks component; parse duration full components; parse fixed offset without colon; parse subsecond truncation; parse invalid iso raises.
- **B002**: The extracted feature must support this observable behavior: parse common YYYY-MM-DD and HH:mm:ss combinations. Required observable cases include parse common day first; parse subsecond truncation; parse invalid iso raises.
- **B003**: The extracted feature must support this observable behavior: construct DateTime and Duration instances. Required observable cases include parse subsecond truncation.
- **B004**: The extracted feature must support this observable behavior: format datetimes with Pendulum tokens (YYYY, MM, DD, HH, mm, ss, Z). Required observable cases include datetime format tokens; format literal brackets.
- **B005**: The extracted feature must support this observable behavior: duration component properties (years, months, weeks, days, hours, minutes, seconds). Required observable cases include duration constructor and total seconds; parse duration weeks component; parse duration full components; duration years months not float.
- **B006**: The package exposes the required task API paths `featurelifted.UTC`, `featurelifted.Date`, `featurelifted.Date.day`, `featurelifted.Date.hour`, `featurelifted.Date.minute`, `featurelifted.Date.month`, `featurelifted.Date.year`, `featurelifted.DateTime`, `featurelifted.DateTime.hour`, `featurelifted.DateTime.microsecond`, `featurelifted.DateTime.minute`, `featurelifted.DateTime.offset`, and 15 listed members with the kinds and callable signatures listed in this contract.

## Tests

### `public_tests/test_public_api.py::test_parse_iso_date`

- mapping: `B001`
- API: `featurelifted.parse`
- risk: `none`
- A001 `assert` L8: `result.year == 2024`
- A002 `assert` L9: `result.month == 6`
- A003 `assert` L10: `result.day == 15`

### `public_tests/test_public_api.py::test_parse_iso_datetime_zulu`

- mapping: `B001`
- API: `featurelifted.DateTime, featurelifted.parse`
- risk: `none`
- A001 `assert` L15: `isinstance(result, DateTime)`
- A002 `assert` L16: `result.year == 2024`
- A003 `assert` L17: `result.month == 6`
- A004 `assert` L18: `result.day == 15`
- A005 `assert` L19: `result.hour == 10`
- A006 `assert` L20: `result.minute == 30`
- A007 `assert` L21: `result.second == 45`
- A008 `assert` L22: `result.timezone_name == 'UTC'`

### `public_tests/test_public_api.py::test_datetime_format_tokens`

- mapping: `B004`
- API: `featurelifted.UTC, featurelifted.datetime`
- risk: `none`
- A001 `assert` L27: `dt.format('YYYY-MM-DD HH:mm:ss') == '2024-06-15 10:30:05'`

### `public_tests/test_public_api.py::test_duration_constructor_and_total_seconds`

- mapping: `B005`
- API: `featurelifted.Duration, featurelifted.duration`
- risk: `none`
- A001 `assert` L32: `isinstance(d, Duration)`
- A002 `assert` L33: `d.total_seconds() == 95400.0`

### `public_tests/test_public_api.py::test_parse_iso_duration`

- mapping: `B001`
- API: `featurelifted.Duration, featurelifted.parse`
- risk: `none`
- A001 `assert` L38: `isinstance(result, Duration)`
- A002 `assert` L39: `result.days == 1`
- A003 `assert` L40: `result.hours == 12`

### `hidden_tests/test_hidden_behavior.py::test_parse_iso_week_calendar_date`

- mapping: `B001`
- API: `featurelifted.parse`
- risk: `none`
- A001 `assert` L13: `result.year == 2016`
- A002 `assert` L14: `result.month == 2`
- A003 `assert` L15: `result.day == 5`

### `hidden_tests/test_hidden_behavior.py::test_parse_duration_weeks_component`

- mapping: `B001, B005`
- API: `featurelifted.Duration, featurelifted.parse`
- risk: `none`
- A001 `assert` L20: `isinstance(result, Duration)`
- A002 `assert` L21: `result.weeks == 2`
- A003 `assert` L22: `result.remaining_days == 0`
- A004 `assert` L23: `result.in_days() == 14`

### `hidden_tests/test_hidden_behavior.py::test_parse_duration_full_components`

- mapping: `B001, B005`
- API: `featurelifted.Duration, featurelifted.parse`
- risk: `none`
- A001 `assert` L28: `isinstance(result, Duration)`
- A002 `assert` L29: `result.years == 1`
- A003 `assert` L30: `result.months == 2`
- A004 `assert` L31: `result.remaining_days == 3`
- A005 `assert` L32: `result.hours == 4`
- A006 `assert` L33: `result.minutes == 5`
- A007 `assert` L34: `result.remaining_seconds == 6`

### `hidden_tests/test_hidden_behavior.py::test_format_literal_brackets`

- mapping: `B004`
- API: `featurelifted.UTC, featurelifted.datetime`
- risk: `none`
- A001 `assert` L39: `dt.format('YYYY [MM] DD') == '2024 MM 07'`

### `hidden_tests/test_hidden_behavior.py::test_parse_fixed_offset_without_colon`

- mapping: `B001`
- API: `featurelifted.DateTime, featurelifted.parse`
- risk: `none`
- A001 `assert` L44: `isinstance(result, DateTime)`
- A002 `assert` L45: `result.hour == 10`
- A003 `assert` L46: `result.minute == 30`
- A004 `assert` L47: `result.offset == 5 * 3600 + 30 * 60`

### `hidden_tests/test_hidden_behavior.py::test_parse_common_day_first`

- mapping: `B002`
- API: `featurelifted.parse`
- risk: `none`
- A001 `assert` L52: `result.year == 2024`
- A002 `assert` L53: `result.month == 6`
- A003 `assert` L54: `result.day == 15`
- A004 `assert` L55: `result.hour == 8`
- A005 `assert` L56: `result.minute == 15`

### `hidden_tests/test_hidden_behavior.py::test_parse_subsecond_truncation`

- mapping: `B001, B002, B003`
- API: `featurelifted.DateTime, featurelifted.parse`
- risk: `none`
- A001 `assert` L61: `isinstance(result, DateTime)`
- A002 `assert` L62: `result.microsecond == 123456`

### `hidden_tests/test_hidden_behavior.py::test_duration_years_months_not_float`

- mapping: `B005`
- API: `featurelifted.duration`
- risk: `exception_semantics`
- A001 `raises` L66: `pytest.raises(ValueError)`

### `hidden_tests/test_hidden_behavior.py::test_parse_invalid_iso_raises`

- mapping: `B001, B002`
- API: `featurelifted.ParserError, featurelifted.parse`
- risk: `exception_semantics`
- A001 `raises` L71: `pytest.raises(ParserError)`

### `hidden_tests/test_hidden_behavior.py::test_no_pendulum_import_surface`

- mapping: `B007`
- API: `featurelifted.__file__`
- risk: `filesystem_resource`
- A001 `assert` L82: `not import_pattern.search(text)`

### `hidden_tests/test_required_api_surface.py::test_required_api_surface`

- mapping: `B006`
- API: `featurelifted.Date, featurelifted.DateTime, featurelifted.Duration, featurelifted.ParserError, featurelifted.Time, featurelifted.UTC, featurelifted.datetime, featurelifted.duration, featurelifted.fixed_timezone, featurelifted.parse`
- risk: `none`
- A001 `assert` L18: `UTC is not None`
- A002 `assert` L19: `isinstance(Date, type)`
- A003 `assert` L20: `Date is not None`
- A004 `assert` L21: `Date is not None`
- A005 `assert` L22: `Date is not None`
- A006 `assert` L23: `Date is not None`
- A007 `assert` L24: `Date is not None`
- A008 `assert` L25: `isinstance(DateTime, type)`
- A009 `assert` L26: `DateTime is not None`
- A010 `assert` L27: `DateTime is not None`
- A011 `assert` L28: `DateTime is not None`
- A012 `assert` L29: `DateTime is not None`
- A013 `assert` L30: `isinstance(Duration, type)`
- A014 `assert` L31: `Duration is not None`
- A015 `assert` L32: `hasattr(Duration, 'in_days')`
- A016 `assert` L33: `Duration is not None`
- A017 `assert` L34: `Duration is not None`
- A018 `assert` L35: `Duration is not None`
- A019 `assert` L36: `Duration is not None`
- A020 `assert` L37: `Duration is not None`
- A021 `assert` L38: `Duration is not None`
- A022 `assert` L39: `issubclass(ParserError, BaseException)`
- A023 `assert` L40: `isinstance(Time, type)`
- A024 `assert` L41: `datetime is not None`
- A025 `assert` L42: `duration is not None`
- A026 `assert` L43: `callable(fixed_timezone)`
- A027 `assert` L44: `callable(parse)`

## Dependency / Oracle Evidence

- allowed dependencies: `python-dateutil, six`
- forbidden imports: `pendulum`
- source entrypoints: `pendulum.parse, pendulum.parser.parse, pendulum.parsing.parse, pendulum.parsing.iso8601.parse_iso8601, pendulum.formatting.Formatter, pendulum.duration.Duration, pendulum.datetime.DateTime.format`
- oracle source files: `pendulum/constants.py, pendulum/day.py, pendulum/exceptions.py, pendulum/utils/__init__.py, pendulum/utils/_compat.py, pendulum/_helpers.py, pendulum/helpers.py, pendulum/duration.py, pendulum/date.py, pendulum/time.py, pendulum/datetime.py, pendulum/interval.py, pendulum/mixins/__init__.py, pendulum/mixins/default.py, pendulum/formatting/__init__.py, pendulum/formatting/formatter.py, pendulum/parsing/__init__.py, pendulum/parsing/iso8601.py, pendulum/parsing/exceptions/__init__.py, pendulum/parser.py, pendulum/tz/__init__.py, pendulum/tz/exceptions.py, pendulum/tz/timezone.py, pendulum/locales/__init__.py, pendulum/locales/locale.py, pendulum/locales/en/__init__.py, pendulum/locales/en/custom.py, pendulum/locales/en/locale.py`
- runtime dependencies: `python-dateutil`
- oracle notes: Oracle closure is parse/format/duration core with UTC/fixed offsets and English locale only; excludes tzdata bundle, other locales, humanize, and runtime now/travel.
