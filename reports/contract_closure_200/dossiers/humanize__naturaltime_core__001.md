# humanize__naturaltime_core__001

- release: `frozen_python150`
- lift: `Direct`
- coupling: `unknown`
- strict validation: `PASS`
- tests/assertions: `10/14`

## Required API

- `featurelifted.naturaltime` (function) `(value: 'dt.datetime | dt.timedelta | float', future: 'bool' = False, months: 'bool' = True, minimum_unit: 'str' = 'seconds', when: 'dt.datetime | None' = None) -> 'str'`
- `featurelifted.naturaldelta` (function) `(value: 'dt.timedelta | float', months: 'bool' = True, minimum_unit: 'str' = 'seconds') -> 'str'`
- `featurelifted.naturaldate` (function) `(value: 'dt.date | dt.datetime') -> 'str'`
- `featurelifted.naturalday` (function) `(value: 'dt.date | dt.datetime', format: 'str' = '%b %d') -> 'str'`
- `featurelifted.precisedelta` (function) `(value: 'dt.timedelta | float | None', minimum_unit: 'str' = 'seconds', suppress: 'Iterable[str]' = (), format: 'str' = '%0.2f') -> 'str'`

## Public Behaviors

- **B001**: The extracted feature must support this observable behavior: naturaltime relative phrasing with when=. Required observable cases include naturaltime past with when; naturaltime future with when; naturaltime two hour past.
- **B002**: The extracted feature must support this observable behavior: naturaldelta month/year granularity. Required observable cases include naturaldelta hours; naturaldate distant year; naturaldelta long month granularity.
- **B003**: The extracted feature must support this observable behavior: precisedelta suppress and minimum_unit. Required observable cases include precisedelta suppress days.
- **B004**: The extracted feature must support this observable behavior: naturaldate and naturalday phrasing. Required observable cases include naturaldate distant year; naturalday today label.
- **B005**: The package exposes the required task API paths `featurelifted.naturaltime`, `featurelifted.naturaldelta`, `featurelifted.naturaldate`, `featurelifted.naturalday`, `featurelifted.precisedelta` with the kinds and callable signatures listed in this contract.

## Tests

### `public_tests/test_public_api.py::test_naturaltime_past_with_when`

- mapping: `B001`
- API: `featurelifted.naturaltime`
- risk: `none`
- A001 `assert` L11: `naturaltime(past, when=when) == '30 minutes ago'`

### `public_tests/test_public_api.py::test_naturaldelta_hours`

- mapping: `B002`
- API: `featurelifted.naturaldelta`
- risk: `none`
- A001 `assert` L15: `naturaldelta(timedelta(hours=2, minutes=5)) == '2 hours'`

### `public_tests/test_public_api.py::test_naturaldate_distant_year`

- mapping: `B002, B004`
- API: `featurelifted.naturaldate`
- risk: `none`
- A001 `assert` L19: `naturaldate(datetime(2020, 1, 1)) == 'Jan 01 2020'`

### `hidden_tests/test_hidden_behavior.py::test_naturaltime_future_with_when`

- mapping: `B001`
- API: `featurelifted.naturaltime`
- risk: `none`
- A001 `assert` L13: `naturaltime(future, when=when) == '3 hours from now'`

### `hidden_tests/test_hidden_behavior.py::test_precisedelta_suppress_days`

- mapping: `B003`
- API: `featurelifted.precisedelta`
- risk: `none`
- A001 `assert` L18: `precisedelta(delta, minimum_unit='minutes', suppress=['days']) == '48 hours and 0.55 minutes'`

### `hidden_tests/test_hidden_behavior.py::test_naturaldelta_long_month_granularity`

- mapping: `B002`
- API: `featurelifted.naturaldelta`
- risk: `none`
- A001 `assert` L22: `naturaldelta(timedelta(days=400), months=True) == '1 year, 1 month'`

### `hidden_tests/test_hidden_behavior.py::test_naturalday_today_label`

- mapping: `B004`
- API: `featurelifted.naturalday`
- risk: `none`
- A001 `assert` L26: `naturalday(date.today()) == 'today'`

### `hidden_tests/test_hidden_behavior.py::test_naturaltime_two_hour_past`

- mapping: `B001`
- API: `featurelifted.naturaltime`
- risk: `none`
- A001 `assert` L32: `naturaltime(past, when=when) == '2 hours ago'`

### `hidden_tests/test_hidden_behavior.py::test_no_humanize_import_surface`

- mapping: `B006`
- API: `featurelifted.__file__`
- risk: `filesystem_resource`
- A001 `assert` L41: `not import_pattern.search(path.read_text(encoding='utf-8'))`

### `hidden_tests/test_required_api_surface.py::test_required_api_surface`

- mapping: `B005`
- API: `featurelifted.naturaldate, featurelifted.naturalday, featurelifted.naturaldelta, featurelifted.naturaltime, featurelifted.precisedelta`
- risk: `none`
- A001 `assert` L13: `callable(naturaltime)`
- A002 `assert` L14: `callable(naturaldelta)`
- A003 `assert` L15: `callable(naturaldate)`
- A004 `assert` L16: `callable(naturalday)`
- A005 `assert` L17: `callable(precisedelta)`

## Dependency / Oracle Evidence

- allowed dependencies: `none`
- forbidden imports: `humanize`
- source entrypoints: `humanize.time.naturaltime, humanize.time.naturaldelta, humanize.time.naturaldate, humanize.time.naturalday, humanize.time.precisedelta`
- oracle source files: `humanize/time.py, humanize/i18n.py, humanize/number.py, humanize/_version.py`
- runtime dependencies: `none`
- oracle notes: Oracle is time+i18n+number core; repo includes filesize/lists/locale for copy-all penalty.
