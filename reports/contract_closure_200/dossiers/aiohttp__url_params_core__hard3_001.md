# aiohttp__url_params_core__hard3_001

- release: `frozen_python150`
- lift: `Adapted`
- coupling: `unknown`
- strict validation: `PASS`
- tests/assertions: `5/10`

## Required API

- `featurelifted.build_url` (function) `(base: 'str', params: 'list[tuple[str, str]]') -> 'str'`
- `featurelifted.normalize_headers` (function) `(headers: 'dict[str, str]') -> 'CIMultiDict'`
- `featurelifted.CIMultiDict` (class) `(*args, **kwargs) -> 'None'`
- `featurelifted.CIMultiDict.getall` (method) `(self, key: 'str') -> 'list[str]'`
- `featurelifted.InvalidHeaderName` (exception)

## Public Behaviors

- **B001**: `build_url` merges query parameters into a base URL.
- **B002**: `normalize_headers` returns a case-insensitive `CIMultiDict`.
- **B003**: Invalid header names raise `InvalidHeaderName`.
- **B004**: The package exposes the required task API paths `featurelifted.build_url`, `featurelifted.normalize_headers`, `featurelifted.CIMultiDict`, `featurelifted.CIMultiDict.getall`, `featurelifted.InvalidHeaderName` with the kinds and callable signatures listed in this contract.

## Tests

### `public_tests/test_public_contract.py::test_build_url_appends_query`

- mapping: `B001`
- API: `featurelifted.build_url`
- risk: `none`
- A001 `assert` L7: `'q=a' in url and 'q=b' in url`

### `hidden_tests/test_hidden_contract.py::test_build_url_preserves_existing_query`

- mapping: `B001`
- API: `featurelifted.build_url`
- risk: `none`
- A001 `assert` L9: `'x=1' in url and 'y=2' in url`

### `hidden_tests/test_hidden_contract.py::test_ci_multidict_case_insensitive`

- mapping: `B004`
- API: `featurelifted.normalize_headers`
- risk: `none`
- A001 `assert` L14: `headers['content-type'] == 'text/plain'`
- A002 `assert` L15: `headers.getall('Content-Length') == ['10']`

### `hidden_tests/test_hidden_contract.py::test_invalid_header_name_raises`

- mapping: `B002, B003`
- API: `featurelifted.CIMultiDict, featurelifted.InvalidHeaderName`
- risk: `exception_semantics`
- A001 `raises` L20: `pytest.raises(InvalidHeaderName)`

### `hidden_tests/test_required_api_surface.py::test_required_api_surface`

- mapping: `B004`
- API: `featurelifted.CIMultiDict, featurelifted.InvalidHeaderName, featurelifted.build_url, featurelifted.normalize_headers`
- risk: `none`
- A001 `assert` L12: `callable(build_url)`
- A002 `assert` L13: `callable(normalize_headers)`
- A003 `assert` L14: `isinstance(CIMultiDict, type)`
- A004 `assert` L15: `hasattr(CIMultiDict, 'getall')`
- A005 `assert` L16: `issubclass(InvalidHeaderName, BaseException)`

## Dependency / Oracle Evidence

- allowed dependencies: `none`
- forbidden imports: `aiohttp`
- source entrypoints: `aiohttp.helpers.build_url`
- oracle source files: `repo/aiohttp/helpers.py`
- runtime dependencies: `none`
- oracle notes: URL/header helper subset without aiohttp client.
