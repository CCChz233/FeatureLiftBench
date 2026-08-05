# hyperlink__url_parse_core__001

- release: `external50`
- lift: `Adapted`
- coupling: `data_model_coupling`
- strict validation: `PASS`
- tests/assertions: `7/12`

## Required API

- `featurelifted.URL` (class)
- `featurelifted.URL.from_text` (method)
- `featurelifted.URL.replace` (method)
- `featurelifted.URL.click` (method)
- `featurelifted.URL.to_text` (method)
- `featurelifted.URLParseError` (exception)

## Public Behaviors

- **B001**: The extracted feature must support this observable behavior: URL.from_text and to_text roundtrip fields. Required observable cases include from text and to text; replace scheme host.
- **B002**: The extracted feature must support this observable behavior: click resolves relative refs. Required observable cases include click relative.
- **B003**: The extracted feature must support this observable behavior: replace returns new URL without mutating original. Required observable cases include immutable replace.
- **B004**: URLParseError is raised on malformed authority segments.
- **B005**: The package exposes URL/URLParseError with the kinds listed in this contract.
- **B006**: the submitted package does not import forbidden upstream packages: hyperlink.

## Tests

### `public_tests/test_public_api.py::test_from_text_and_to_text`

- mapping: `B001`
- API: `featurelifted.URL, featurelifted.URL.from_text`
- risk: `none`
- A001 `assert` L9: `text.startswith('https://example.com/')`
- A002 `assert` L10: `'x=1' in text`
- A003 `assert` L11: `'#frag' in text`

### `public_tests/test_public_api.py::test_replace_scheme_host`

- mapping: `B002`
- API: `featurelifted.URL, featurelifted.URL.from_text`
- risk: `none`
- A001 `assert` L17: `updated.to_text().startswith('https://new.test')`

### `public_tests/test_public_api.py::test_click_relative`

- mapping: `B003`
- API: `featurelifted.URL, featurelifted.URL.from_text`
- risk: `none`
- A001 `assert` L23: `'/a/c' in clicked.to_text() or clicked.to_text().endswith('/a/c')`

### `hidden_tests/test_hidden_behavior.py::test_no_upstream_import_surface`

- mapping: `B006`
- API: `featurelifted.__file__`
- risk: `filesystem_resource`
- A001 `assert` L13: `not pattern.search(path.read_text(encoding='utf-8'))`

### `hidden_tests/test_hidden_behavior.py::test_immutable_replace`

- mapping: `B001, B002, B004`
- API: `featurelifted.URL, featurelifted.URL.from_text`
- risk: `none`
- A001 `assert` L22: `original.to_text().endswith('/x')`
- A002 `assert` L23: `changed.to_text().endswith('/y')`

### `hidden_tests/test_hidden_behavior.py::test_parse_error`

- mapping: `B003`
- API: `featurelifted.URL, featurelifted.URL.from_text, featurelifted.URLParseError`
- risk: `none`
- A001 `assert` L29: `False`

### `hidden_tests/test_required_api_surface.py::test_required_api_surface`

- mapping: `B005`
- API: `featurelifted.URL, featurelifted.URL.from_text, featurelifted.URLParseError`
- risk: `none`
- A001 `assert` L5: `URL is not None and URLParseError is not None`
- A002 `assert` L6: `hasattr(URL, 'from_text')`
- A003 `assert` L8: `callable(url.to_text) and callable(url.replace) and callable(url.click)`

## Dependency / Oracle Evidence

- allowed dependencies: `none`
- forbidden imports: `hyperlink`
- source entrypoints: `none`
- oracle source files: `src/hyperlink/_url.py, src/hyperlink/__init__.py`
- runtime dependencies: `none`
- oracle notes: Adapted URL.from_text/replace/click/to_text immutable API.
- behavior contract lacks a completed review_status
- behavior contract schema_version missing or unsupported
