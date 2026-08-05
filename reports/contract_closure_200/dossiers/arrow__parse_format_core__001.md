# arrow__parse_format_core__001

- release: `frozen_python150`
- lift: `Adapted`
- coupling: `unknown`
- strict validation: `PASS`
- tests/assertions: `10/23`

## Required API

- `featurelifted.Arrow` (class) `(year: int, month: int, day: int, hour: int = 0, minute: int = 0, second: int = 0, microsecond: int = 0, tzinfo: Union[datetime.tzinfo, str, NoneType] = None, **kwargs: Any) -> None`
- `featurelifted.Arrow.day` (attribute)
- `featurelifted.Arrow.format` (method) `(self, fmt: str = 'YYYY-MM-DD HH:mm:ssZZ', locale: str = 'en-us') -> str`
- `featurelifted.Arrow.humanize` (method) `(self, other: Union[ForwardRef('Arrow'), datetime.datetime, NoneType] = None, locale: str = 'en-us', only_distance: bool = False, granularity: Union[Literal['auto', 'second', 'minute', 'hour', 'day', 'week', 'month', 'quarter', 'year'], List[Literal['auto', 'second', 'minute', 'hour', 'day', 'week', 'month', 'quarter', 'year']]] = 'auto') -> str`
- `featurelifted.Arrow.month` (attribute)
- `featurelifted.Arrow.year` (attribute)
- `featurelifted.get` (function) `(*args: Any, **kwargs: Any) -> Arrow`

## Public Behaviors

- **B001**: The extracted feature must support this observable behavior: parse ISO and format-string datetimes. Required observable cases include get iso datetime; get with format string; parse lowercase month.
- **B002**: The extracted feature must support this observable behavior: format with token literals in brackets. Required observable cases include format basic tokens; format literal brackets.
- **B003**: The extracted feature must support this observable behavior: humanize relative deltas in English. Required observable cases include humanize relative hours; humanize past tense.
- **B004**: The extracted feature must support this observable behavior: ordinal Do token parsing. Required observable cases include parse ordinal day token.
- **B005**: The package exposes the required task API paths `featurelifted.Arrow`, `featurelifted.Arrow.day`, `featurelifted.Arrow.format`, `featurelifted.Arrow.humanize`, `featurelifted.Arrow.month`, `featurelifted.Arrow.year`, `featurelifted.get` with the kinds and callable signatures listed in this contract.

## Tests

### `public_tests/test_public_api.py::test_get_iso_datetime`

- mapping: `B001`
- API: `featurelifted.get`
- risk: `none`
- A001 `assert` L8: `a.year == 2020`
- A002 `assert` L9: `a.month == 1`
- A003 `assert` L10: `a.day == 15`
- A004 `assert` L11: `a.hour == 12`
- A005 `assert` L12: `a.minute == 30`

### `public_tests/test_public_api.py::test_format_basic_tokens`

- mapping: `B002`
- API: `featurelifted.get`
- risk: `none`
- A001 `assert` L17: `a.format('YYYY-MM-DD HH:mm:ss ZZ') == '2020-01-15 12:30:00 +00:00'`

### `public_tests/test_public_api.py::test_get_with_format_string`

- mapping: `B001`
- API: `featurelifted.get`
- risk: `none`
- A001 `assert` L22: `a.format('YYYY-MM-DD') == '2020-01-15'`

### `hidden_tests/test_hidden_behavior.py::test_format_literal_brackets`

- mapping: `B002`
- API: `featurelifted.get`
- risk: `none`
- A001 `assert` L11: `a.format('YYYY [MM] DD') == '2020 MM 15'`

### `hidden_tests/test_hidden_behavior.py::test_humanize_relative_hours`

- mapping: `B003`
- API: `featurelifted.get`
- risk: `none`
- A001 `assert` L17: `a.humanize(other) == 'in 2 hours'`

### `hidden_tests/test_hidden_behavior.py::test_parse_ordinal_day_token`

- mapping: `B004`
- API: `featurelifted.get`
- risk: `none`
- A001 `assert` L22: `a.year == 2020`
- A002 `assert` L23: `a.month == 1`
- A003 `assert` L24: `a.day == 5`

### `hidden_tests/test_hidden_behavior.py::test_parse_lowercase_month`

- mapping: `B001`
- API: `featurelifted.get`
- risk: `none`
- A001 `assert` L29: `a.month == 1`
- A002 `assert` L30: `a.day == 15`

### `hidden_tests/test_hidden_behavior.py::test_humanize_past_tense`

- mapping: `B003`
- API: `featurelifted.get`
- risk: `none`
- A001 `assert` L36: `a.humanize(other) == '2 hours ago'`

### `hidden_tests/test_hidden_behavior.py::test_no_arrow_import_surface`

- mapping: `B006`
- API: `featurelifted.__file__`
- risk: `filesystem_resource`
- A001 `assert` L45: `not import_pattern.search(path.read_text(encoding='utf-8'))`

### `hidden_tests/test_required_api_surface.py::test_required_api_surface`

- mapping: `B005`
- API: `featurelifted.Arrow, featurelifted.get`
- risk: `none`
- A001 `assert` L10: `isinstance(Arrow, type)`
- A002 `assert` L11: `Arrow is not None`
- A003 `assert` L12: `hasattr(Arrow, 'format')`
- A004 `assert` L13: `hasattr(Arrow, 'humanize')`
- A005 `assert` L14: `Arrow is not None`
- A006 `assert` L15: `Arrow is not None`
- A007 `assert` L16: `callable(get)`

## Dependency / Oracle Evidence

- allowed dependencies: `python-dateutil, six`
- forbidden imports: `arrow`
- source entrypoints: `arrow.get, arrow.Arrow.format, arrow.Arrow.humanize, arrow.parser.DateTimeParser`
- oracle source files: `arrow/parser.py, arrow/formatter.py, arrow/arrow.py, arrow/factory.py, arrow/api.py, arrow/constants.py, arrow/util.py, arrow/locales.py`
- runtime dependencies: `python-dateutil`
- oracle notes: Oracle uses English-only trimmed locales; repo ships full locales.py for copy-all penalty.
