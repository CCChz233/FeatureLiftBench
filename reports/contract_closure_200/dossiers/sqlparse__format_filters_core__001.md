# sqlparse__format_filters_core__001

- release: `frozen_python150`
- lift: `Direct`
- coupling: `unknown`
- strict validation: `PASS`
- tests/assertions: `4/7`

## Required API

- `featurelifted.format` (function) `(sql: str, encoding: str | None = None, **options: Any) -> str`
- `featurelifted.exceptions` (module)
- `featurelifted.exceptions.SQLParseError` (exception)

## Public Behaviors

- **B001**: The extracted feature must support this observable behavior: format common SQL with keyword case, identifier case, comment stripping, reindentation, indentation width, and operator spacing. Required observable cases include format supports common options; formatter comment stripping and spacing.
- **B002**: The extracted feature must support this observable behavior: preserve original formatter behavior for comments, whitespace, string literals, aliases, and nested expressions. Required observable cases include formatter rejects invalid options.
- **B003**: The extracted feature must support this observable behavior: validate formatter options and reject invalid values. Required observable cases include formatter rejects invalid options.
- **B004**: The package exposes the required task API paths `featurelifted.format`, `featurelifted.exceptions`, `featurelifted.exceptions.SQLParseError` with the kinds and callable signatures listed in this contract.

## Tests

### `public_tests/test_public_api.py::test_format_supports_common_options`

- mapping: `B001`
- API: `featurelifted.format`
- risk: `none`
- A001 `assert` L14: `formatted == 'SELECT a,\n       b\nFROM t\nWHERE a = 1\n  AND b = 2'`

### `hidden_tests/test_hidden_behavior.py::test_formatter_comment_stripping_and_spacing`

- mapping: `B001`
- API: `featurelifted.exceptions, featurelifted.format`
- risk: `none`
- A001 `assert` L10: `format('select a, -- inline\n b from t', strip_comments=True, reindent=True, keyword_case='upper') == 'SELECT a, b\nFROM t'`
- A002 `assert` L20: `format('select a+b as total from t', use_space_around_operators=True) == 'select a + b as total from t'`

### `hidden_tests/test_hidden_behavior.py::test_formatter_rejects_invalid_options`

- mapping: `B002, B003`
- API: `featurelifted.exceptions, featurelifted.format`
- risk: `exact_error_text, exception_semantics`
- A001 `raises` L27: `pytest.raises(SQLParseError, match='Invalid value for keyword_case')`

### `hidden_tests/test_required_api_surface.py::test_required_api_surface`

- mapping: `B004`
- API: `featurelifted.exceptions, featurelifted.format`
- risk: `none`
- A001 `assert` L10: `callable(format)`
- A002 `assert` L11: `exceptions is not None`
- A003 `assert` L12: `issubclass(getattr(exceptions, 'SQLParseError'), BaseException)`

## Dependency / Oracle Evidence

- allowed dependencies: `none`
- forbidden imports: `sqlparse`
- source entrypoints: `sqlparse.format`
- oracle source files: `none`
- runtime dependencies: `none`
- oracle notes: Format and filter-stack closure. CLI, tests, docs, and packaging metadata are excluded.
