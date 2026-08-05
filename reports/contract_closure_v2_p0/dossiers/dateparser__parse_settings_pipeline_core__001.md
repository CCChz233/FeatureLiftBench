# Contract V2 P0: dateparser__parse_settings_pipeline_core__001

- release: `external50`
- lift: `Composite`
- coupling: `parser_state_coupling`
- strict validation: `PASS`
- tests/assertions: `9/16`

## Required API

- `featurelifted.parse` (function) `(date_string, date_formats=None, languages=None, locales=None, region=None, settings=None, detect_languages_function=None)`
- `featurelifted.Settings` (class) `(settings=None, **options)`
- `featurelifted.detect_languages` (function) `(text: str, languages: list[str] | None = None) -> list[str]`

## Public Behaviors

- **B001**: The extracted feature must support this observable behavior: parse ISO/English/Spanish/French dates. Required observable cases include parse iso and english; parse with languages.
- **B002**: Settings accepts one optional mapping plus keyword options from the documented allowlist, controls timezone awareness and DATE_ORDER, and raises TypeError when a recognized option receives an invalid None value.
- **B003**: The extracted feature must support this observable behavior: detect_languages returns list[str] shortcodes for the en/es/fr subset. Required observable cases include detect languages es fr.
- **B004**: Parsing remains offline using bundled locale/date data without network access.
- **B005**: The package exposes the required task API paths `featurelifted.parse`, `featurelifted.Settings`, `featurelifted.detect_languages` with the kinds and callable signatures listed in this contract.
- **B006**: the submitted package does not import forbidden upstream packages: dateparser.

## Tests

### `public_tests/test_public_api.py::test_parse_iso_and_english`

- mapping: `B001`
- API: `featurelifted.parse`
- risk: `none`
- A001 `assert` L9: `parse('2020-01-15') == datetime(2020, 1, 15, 0, 0)`
- A002 `assert` L10: `parse('January 15, 2020') == datetime(2020, 1, 15, 0, 0)`

### `public_tests/test_public_api.py::test_parse_with_languages`

- mapping: `B001`
- API: `featurelifted.parse`
- risk: `none`
- A001 `assert` L16: `es is not None and es.year == 2020 and (es.month == 1) and (es.day == 15)`
- A002 `assert` L17: `fr is not None and fr.year == 2020 and (fr.month == 1) and (fr.day == 15)`

### `public_tests/test_public_api.py::test_settings_timezone_aware`

- mapping: `B002`
- API: `featurelifted.Settings, featurelifted.parse`
- risk: `none`
- A001 `assert` L29: `dt is not None`
- A002 `assert` L30: `dt.tzinfo is not None`

### `hidden_tests/test_hidden_behavior.py::test_detect_languages_es_fr`

- mapping: `B003`
- API: `featurelifted.detect_languages`
- risk: `none`
- A001 `assert` L13: `'es' in es`
- A002 `assert` L14: `'fr' in fr`

### `hidden_tests/test_hidden_behavior.py::test_prefer_dates_from_past`

- mapping: `B001, B002`
- API: `featurelifted.Settings, featurelifted.parse`
- risk: `none`
- A001 `assert` L19: `parse('2020-01-15', settings=settings) is not None`

### `hidden_tests/test_hidden_behavior.py::test_date_order_dmy`

- mapping: `B002`
- API: `featurelifted.Settings, featurelifted.parse`
- risk: `ordering_semantics`
- A001 `assert` L25: `dt is not None`
- A002 `assert` L26: `dt.day == 15 and dt.month == 1 and (dt.year == 2020)`

### `hidden_tests/test_hidden_behavior.py::test_invalid_settings_key`

- mapping: `B002`
- API: `featurelifted.Settings`
- risk: `exception_semantics`
- A001 `raises` L30: `pytest.raises(TypeError)`

### `hidden_tests/test_hidden_behavior.py::test_no_upstream_import_surface`

- mapping: `B004, B006`
- API: `featurelifted.__file__`
- risk: `filesystem_resource`
- A001 `assert` L40: `not pattern.search(path.read_text(encoding='utf-8'))`

### `hidden_tests/test_required_api_surface.py::test_required_api_surface`

- mapping: `B005`
- API: `featurelifted.Settings, featurelifted.detect_languages, featurelifted.parse`
- risk: `none`
- A001 `assert` L11: `callable(parse)`
- A002 `assert` L12: `isinstance(Settings, type)`
- A003 `assert` L13: `callable(detect_languages)`

## Dependency / Oracle Evidence

- allowed dependencies: `python-dateutil, pytz, regex, six, tzlocal`
- forbidden imports: `dateparser`
- source entrypoints: `none`
- oracle source files: `dateparser/__init__.py, dateparser/conf.py, dateparser/search/search.py, dateparser/data/`
- runtime dependencies: `python-dateutil, pytz, regex, six, tzlocal`
- oracle notes: Composite Settings + parse + detect_languages; offline data bundled in repo/reference.
