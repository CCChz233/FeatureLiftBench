# httpx__request_model_core__001

- release: `frozen_python150`
- lift: `Adapted`
- coupling: `unknown`
- strict validation: `FAIL`
- tests/assertions: `14/54`

## Required API

- `featurelifted.URL` (constant)
- `featurelifted.QueryParams` (class) `(*args: 'QueryParamTypes | None', **kwargs: 'typing.Any') -> 'None'`
- `featurelifted.QueryParams.multi_items` (method) `(self) -> 'list[tuple[str, str]]'`
- `featurelifted.Headers` (class) `(headers: 'HeaderTypes | None' = None, encoding: 'str | None' = None) -> 'None'`
- `featurelifted.Headers.raw` (attribute)
- `featurelifted.Cookies` (class) `(cookies: 'CookieTypes | None' = None) -> 'None'`
- `featurelifted.Request` (class) `(method: 'str | bytes', url: 'URL | str', *, params: 'QueryParamTypes | None' = None, headers: 'HeaderTypes | None' = None, cookies: 'CookieTypes | None' = None, content: 'RequestContent | None' = None, data: 'RequestData | None' = None, files: 'RequestFiles | None' = None, json: 'typing.Any | None' = None, stream: 'SyncByteStream | AsyncByteStream | None' = None, extensions: 'RequestExtensions | None' = None) -> 'None'`
- `featurelifted.Request.content` (attribute)
- `featurelifted.Request.headers` (attribute)
- `featurelifted.Request.url` (attribute)
- `featurelifted.build_request` (function) `(method: 'str', url: 'URLTypes', *, base_url: 'str | URL' = '', params: 'QueryParamTypes | None' = None, headers: 'HeaderTypes | None' = None, cookies: 'CookieTypes | None' = None, default_params: 'QueryParamTypes | None' = None, default_headers: 'HeaderTypes | None' = None, default_cookies: 'CookieTypes | None' = None, content: 'typing.Any' = None, data: 'typing.Any' = None, json: 'typing.Any' = None, files: 'typing.Any' = None) -> 'Request'`
- `featurelifted.InvalidURL` (exception)

## Public Behaviors

- **B001**: The extracted feature must support this observable behavior: construct and join URL objects with base URL and query parameters. Required observable cases include url path and query; base url join and duplicate query params; url idna and percent encoding.
- **B002**: The extracted feature must support this observable behavior: preserve query parameter ordering and duplicate keys in QueryParams. Required observable cases include query params from mapping; query params duplicate and empty value.
- **B003**: The extracted feature must support this observable behavior: case-insensitive header lookup with raw header preservation. Required observable cases include headers case insensitive lookup; url idna and percent encoding.
- **B004**: The extracted feature must support this observable behavior: merge default and per-request headers, query params, and cookies. Required observable cases include query params from mapping; cookies simple header; build request merges defaults; headers cookie merge and request object; build request merges client defaults; query params duplicate and empty value.
- **B005**: The extracted feature must support this observable behavior: build Request objects with content, data, and json body helpers. Required observable cases include build request merges defaults; request content data json headers.
- **B006**: The extracted feature must support this observable behavior: raise compatible errors for invalid URL and request input. Required observable cases include url idna and percent encoding; invalid url raises.
- **B007**: The package exposes the required task API paths `featurelifted.URL`, `featurelifted.QueryParams`, `featurelifted.QueryParams.multi_items`, `featurelifted.Headers`, `featurelifted.Headers.raw`, `featurelifted.Cookies`, `featurelifted.Request`, `featurelifted.Request.content`, `featurelifted.Request.headers`, `featurelifted.Request.url`, `featurelifted.build_request`, `featurelifted.InvalidURL` with the kinds and callable signatures listed in this contract.

## Tests

### `public_tests/test_public_api.py::test_url_path_and_query`

- mapping: `B001`
- API: `featurelifted.URL`
- risk: `none`
- A001 `assert` L8: `url.scheme == 'https'`
- A002 `assert` L9: `url.host == 'example.com'`
- A003 `assert` L10: `url.path == '/api/items'`
- A004 `assert` L11: `url.query == b'search=ab'`

### `public_tests/test_public_api.py::test_query_params_from_mapping`

- mapping: `B002, B004`
- API: `featurelifted.QueryParams`
- risk: `exact_error_text`
- A001 `assert` L16: `list(params.multi_items()) == [('a', '1'), ('b', '2')]`
- A002 `assert` L17: `str(params) == 'a=1&b=2'`

### `public_tests/test_public_api.py::test_headers_case_insensitive_lookup`

- mapping: `B003`
- API: `featurelifted.Headers`
- risk: `none`
- A001 `assert` L22: `headers['x-token'] == 'abc'`
- A002 `assert` L24: `headers['X-TOKEN'] == 'def'`

### `public_tests/test_public_api.py::test_cookies_simple_header`

- mapping: `B004`
- API: `featurelifted.Cookies, featurelifted.Request`
- risk: `none`
- A001 `assert` L30: `'session=abc123' in request.headers.get('cookie', '')`

### `public_tests/test_public_api.py::test_build_request_merges_defaults`

- mapping: `B004, B005`
- API: `featurelifted.build_request`
- risk: `exact_error_text`
- A001 `assert` L43: `str(request.url) == 'https://api.example.com/v1/items?limit=10&offset=0'`
- A002 `assert` L44: `request.headers['X-Api-Key'] == 'secret'`
- A003 `assert` L45: `request.headers['Accept'] == 'application/json'`

### `hidden_tests/test_hidden_behavior.py::test_base_url_join_and_duplicate_query_params`

- mapping: `B001`
- API: `featurelifted.QueryParams, featurelifted.build_request`
- risk: `exact_error_text`
- A001 `assert` L19: `str(request.url).startswith('https://example.com/api/path')`
- A002 `assert` L21: `('extra', '1') in pairs`
- A003 `assert` L22: `('limit', '10') in pairs`
- A004 `assert` L23: `('offset', '0') in pairs`
- A005 `assert` L26: `list(duplicate.multi_items()) == [('a', '1'), ('a', '2')]`

### `hidden_tests/test_hidden_behavior.py::test_headers_cookie_merge_and_request_object`

- mapping: `B004`
- API: `featurelifted.Headers, featurelifted.build_request`
- risk: `none`
- A001 `assert` L31: `len(repeated.raw) == 2`
- A002 `assert` L42: `request.headers['x-trace'] == '3'`
- A003 `assert` L43: `request.headers['content-type'] == 'text/plain'`
- A004 `assert` L45: `'a=1' in cookie_header`
- A005 `assert` L46: `'b=2' in cookie_header`
- A006 `assert` L47: `request.content == b'payload'`

### `hidden_tests/test_hidden_behavior.py::test_build_request_merges_client_defaults`

- mapping: `B004`
- API: `featurelifted.build_request`
- risk: `none`
- A001 `assert` L61: `request.headers['Authorization'] == 'Bearer override'`
- A002 `assert` L62: `list(request.url.params.multi_items()) == [('keep', 'yes'), ('q', 'new')]`
- A003 `assert` L64: `'sid=override' in cookie_header`
- A004 `assert` L65: `'pref=dark' in cookie_header`

### `hidden_tests/test_hidden_behavior.py::test_request_content_data_json_headers`

- mapping: `B005`
- API: `featurelifted.build_request`
- risk: `none`
- A001 `assert` L70: `json_request.headers['content-type'].startswith('application/json')`
- A002 `assert` L71: `b'"x": 1' in json_request.content`
- A003 `assert` L78: `'application/x-www-form-urlencoded' in data_request.headers['content-type']`
- A004 `assert` L79: `b'a=b' in data_request.content`
- A005 `assert` L87: `content_request.content == b'bytes'`
- A006 `assert` L88: `content_request.headers['content-type'] == 'application/octet-stream'`

### `hidden_tests/test_hidden_behavior.py::test_url_idna_and_percent_encoding`

- mapping: `B001, B003, B006`
- API: `featurelifted.URL, featurelifted.build_request`
- risk: `exact_error_text`
- A001 `assert` L93: `url.host == '中国.icom.museum'`
- A002 `assert` L94: `url.raw_host == b'xn--fiqs8s.icom.museum'`
- A003 `assert` L95: `url.path == '/pa th'`
- A004 `assert` L102: `str(joined.url) == 'https://example.com/api/v1/search'`

### `hidden_tests/test_hidden_behavior.py::test_query_params_duplicate_and_empty_value`

- mapping: `B002, B004`
- API: `featurelifted.QueryParams, featurelifted.QueryParams.merge`
- risk: `none`
- A001 `assert` L107: `list(params.multi_items()) == [('a', ''), ('a', '2'), ('b', '1')]`
- A002 `assert` L109: `list(merged.multi_items()) == [('a', '2'), ('c', '3')]`

### `hidden_tests/test_hidden_behavior.py::test_invalid_url_raises`

- mapping: `B006`
- API: `featurelifted.InvalidURL, featurelifted.URL`
- risk: `exception_semantics`
- A001 `raises` L113: `pytest.raises(InvalidURL)`

### `hidden_tests/test_hidden_behavior.py::test_no_network_api_surface`

- mapping: `B007`
- API: `featurelifted.__file__`
- risk: `filesystem_resource`
- A001 `assert` L131: `not hasattr(featurelifted, name)`
- A002 `assert` L137: `not import_pattern.search(text)`

### `hidden_tests/test_required_api_surface.py::test_required_api_surface`

- mapping: `B007`
- API: `featurelifted.Cookies, featurelifted.Headers, featurelifted.InvalidURL, featurelifted.QueryParams, featurelifted.Request, featurelifted.URL, featurelifted.build_request`
- risk: `none`
- A001 `assert` L15: `URL is not None`
- A002 `assert` L16: `isinstance(QueryParams, type)`
- A003 `assert` L17: `hasattr(QueryParams, 'multi_items')`
- A004 `assert` L18: `isinstance(Headers, type)`
- A005 `assert` L19: `Headers is not None`
- A006 `assert` L20: `isinstance(Cookies, type)`
- A007 `assert` L21: `isinstance(Request, type)`
- A008 `assert` L22: `Request is not None`
- A009 `assert` L23: `Request is not None`
- A010 `assert` L24: `Request is not None`
- A011 `assert` L25: `callable(build_request)`
- A012 `assert` L26: `issubclass(InvalidURL, BaseException)`

## Dependency / Oracle Evidence

- allowed dependencies: `idna`
- forbidden imports: `httpx`
- source entrypoints: `httpx.URL, httpx.QueryParams, httpx.Headers, httpx.Cookies, httpx.Request, httpx.Client.build_request, httpx._client.BaseClient._merge_url, httpx._client.BaseClient._merge_headers, httpx._client.BaseClient._merge_cookies, httpx._client.BaseClient._merge_queryparams`
- oracle source files: `httpx/_urlparse.py, httpx/_urls.py, httpx/_types.py, httpx/_utils.py, httpx/_exceptions.py, httpx/_content.py, httpx/_multipart.py, httpx/_models.py`
- runtime dependencies: `none`
- oracle notes: Request-model closure: URL/query/header/cookie containers, Request body helpers, and standalone build_request merge logic. Transports, clients, auth, decoders, and response machinery excluded.

## Machine Issues

- hidden_tests/test_hidden_behavior.py uses undeclared API reference featurelifted.QueryParams.merge
