# urllib3__retry_backoff_core__001

- release: `frozen_python150`
- lift: `Direct`
- coupling: `unknown`
- strict validation: `FAIL`
- tests/assertions: `14/37`

## Required API

- `featurelifted.Retry` (class) `(total: 'bool | int | None' = 10, connect: 'int | None' = None, read: 'int | None' = None, redirect: 'bool | int | None' = None, status: 'int | None' = None, other: 'int | None' = None, allowed_methods: 'typing.Collection[str] | None' = frozenset({'GET', 'DELETE', 'PUT', 'HEAD', 'TRACE', 'OPTIONS'}), status_forcelist: 'typing.Collection[int] | None' = None, backoff_factor: 'float' = 0, backoff_max: 'float' = 120, raise_on_redirect: 'bool' = True, raise_on_status: 'bool' = True, history: 'tuple[RequestHistory, ...] | None' = None, respect_retry_after_header: 'bool' = True, remove_headers_on_redirect: 'typing.Collection[str]' = frozenset({'Proxy-Authorization', 'Authorization', 'Cookie'}), backoff_jitter: 'float' = 0.0) -> 'None'`
- `featurelifted.Retry.get_backoff_time` (method) `(self) -> 'float'`
- `featurelifted.Retry.history` (attribute)
- `featurelifted.Retry.increment` (method) `(self, method: 'str | None' = None, url: 'str | None' = None, response: 'BaseHTTPResponse | None' = None, error: 'Exception | None' = None, _pool: 'ConnectionPool | None' = None, _stacktrace: 'TracebackType | None' = None) -> 'Self'`
- `featurelifted.Retry.is_retry` (method) `(self, method: 'str', status_code: 'int', has_retry_after: 'bool' = False) -> 'bool'`
- `featurelifted.Retry.parse_retry_after` (method) `(self, retry_after: 'str') -> 'float'`
- `featurelifted.Retry.remove_headers_on_redirect` (attribute)
- `featurelifted.RequestHistory` (class) `(method: ForwardRef('str | None'), url: ForwardRef('str | None'), error: ForwardRef('Exception | None'), status: ForwardRef('int | None'), redirect_location: ForwardRef('str | None'))`
- `featurelifted.ConnectTimeoutError` (exception)
- `featurelifted.ReadTimeoutError` (exception)
- `featurelifted.MaxRetryError` (exception)
- `featurelifted.ResponseError` (exception)
- `featurelifted.InvalidHeader` (exception)

## Public Behaviors

- **B001**: The extracted feature must support this observable behavior: Retry defaults and from_int coercion. Required observable cases include retry defaults and from int; total wins over connect.
- **B002**: The extracted feature must support this observable behavior: connect/read/status/redirect/other counter decrement and exhaustion. Required observable cases include connect timeout increment; total wins over connect.
- **B003**: The extracted feature must support this observable behavior: status_forcelist and allowed_methods conjunction. Required observable cases include is retry status forcelist; allowed methods and status forcelist and; read timeout requires allowed method; status increment raises specific error.
- **B004**: The extracted feature must support this observable behavior: exponential backoff with max cap and redirect reset. Required observable cases include backoff progression; backoff resets after redirect.
- **B005**: The extracted feature must support this observable behavior: Retry-After header parsing with numeric and HTTP-date forms. Required observable cases include parse retry after numeric and invalid.
- **B006**: The extracted feature must support this observable behavior: RequestHistory accumulation on increment. Required observable cases include connect timeout increment; history accumulates; status increment raises specific error.
- **B007**: The extracted feature must support this observable behavior: remove_headers_on_redirect lowercasing. Required observable cases include remove headers on redirect lowercased.
- **B008**: The package exposes the required task API paths `featurelifted.Retry`, `featurelifted.Retry.get_backoff_time`, `featurelifted.Retry.history`, `featurelifted.Retry.increment`, `featurelifted.Retry.is_retry`, `featurelifted.Retry.parse_retry_after`, `featurelifted.Retry.remove_headers_on_redirect`, `featurelifted.RequestHistory`, `featurelifted.ConnectTimeoutError`, `featurelifted.ReadTimeoutError`, `featurelifted.MaxRetryError`, `featurelifted.ResponseError`, and 1 listed members with the kinds and callable signatures listed in this contract.

## Tests

### `public_tests/test_retry_public.py::test_retry_defaults_and_from_int`

- mapping: `B001`
- API: `featurelifted.Retry, featurelifted.Retry.from_int, featurelifted.Retry.total`
- risk: `none`
- A001 `assert` L10: `retry.total == 10`
- A002 `assert` L11: `Retry.from_int(3).total == 3`
- A003 `assert` L12: `Retry.from_int(False).total is False`

### `public_tests/test_retry_public.py::test_is_retry_status_forcelist`

- mapping: `B003`
- API: `featurelifted.Retry`
- risk: `none`
- A001 `assert` L17: `not retry.is_retry('GET', status_code=200)`
- A002 `assert` L18: `retry.is_retry('GET', status_code=503)`

### `public_tests/test_retry_public.py::test_backoff_progression`

- mapping: `B004`
- API: `featurelifted.Retry`
- risk: `none`
- A001 `assert` L23: `retry.get_backoff_time() == 0`
- A002 `assert` L26: `retry.get_backoff_time() == 0.4`

### `public_tests/test_retry_public.py::test_connect_timeout_increment`

- mapping: `B002, B006`
- API: `featurelifted.ConnectTimeoutError, featurelifted.MaxRetryError, featurelifted.Retry`
- risk: `exception_semantics`
- A001 `raises` L33: `pytest.raises(MaxRetryError)`

### `hidden_tests/test_required_api_surface.py::test_required_api_surface`

- mapping: `B008`
- API: `featurelifted.ConnectTimeoutError, featurelifted.InvalidHeader, featurelifted.MaxRetryError, featurelifted.ReadTimeoutError, featurelifted.RequestHistory, featurelifted.ResponseError, featurelifted.Retry`
- risk: `none`
- A001 `assert` L15: `isinstance(Retry, type)`
- A002 `assert` L16: `hasattr(Retry, 'get_backoff_time')`
- A003 `assert` L17: `Retry is not None`
- A004 `assert` L18: `hasattr(Retry, 'increment')`
- A005 `assert` L19: `hasattr(Retry, 'is_retry')`
- A006 `assert` L20: `hasattr(Retry, 'parse_retry_after')`
- A007 `assert` L21: `Retry is not None`
- A008 `assert` L22: `isinstance(RequestHistory, type)`
- A009 `assert` L23: `issubclass(ConnectTimeoutError, BaseException)`
- A010 `assert` L24: `issubclass(ReadTimeoutError, BaseException)`
- A011 `assert` L25: `issubclass(MaxRetryError, BaseException)`
- A012 `assert` L26: `issubclass(ResponseError, BaseException)`
- A013 `assert` L27: `issubclass(InvalidHeader, BaseException)`

### `hidden_tests/test_retry_hidden.py::test_total_wins_over_connect`

- mapping: `B001, B002`
- API: `featurelifted.ConnectTimeoutError, featurelifted.MaxRetryError, featurelifted.Retry`
- risk: `exception_semantics`
- A001 `raises` L25: `pytest.raises(MaxRetryError)`
- A002 `assert` L27: `exc.value.reason is error`

### `hidden_tests/test_retry_hidden.py::test_allowed_methods_and_status_forcelist_and`

- mapping: `B003`
- API: `featurelifted.Retry`
- risk: `none`
- A001 `assert` L32: `not retry.is_retry('GET', status_code=500)`
- A002 `assert` L33: `retry.is_retry('POST', status_code=500)`

### `hidden_tests/test_retry_hidden.py::test_backoff_resets_after_redirect`

- mapping: `B004`
- API: `featurelifted.Retry`
- risk: `state_mutation`
- A001 `assert` L40: `retry.get_backoff_time() == 0.4`
- A002 `assert` L43: `retry.get_backoff_time() == 0`
- A003 `assert` L46: `retry.get_backoff_time() == 0.4`

### `hidden_tests/test_retry_hidden.py::test_parse_retry_after_numeric_and_invalid`

- mapping: `B005`
- API: `featurelifted.InvalidHeader, featurelifted.Retry`
- risk: `exception_semantics`
- A001 `assert` L51: `retry.parse_retry_after('5') == 5.0`
- A002 `raises` L52: `pytest.raises(InvalidHeader)`

### `hidden_tests/test_retry_hidden.py::test_history_accumulates`

- mapping: `B006`
- API: `featurelifted.ConnectTimeoutError, featurelifted.RequestHistory, featurelifted.Retry`
- risk: `none`
- A001 `assert` L60: `retry.history == (RequestHistory('GET', '/a', error, None, None),)`
- A002 `assert` L63: `len(retry.history) == 2`
- A003 `assert` L64: `retry.history[-1].status == 500`

### `hidden_tests/test_retry_hidden.py::test_read_timeout_requires_allowed_method`

- mapping: `B003`
- API: `featurelifted.ReadTimeoutError, featurelifted.Retry`
- risk: `exception_semantics`
- A001 `raises` L70: `pytest.raises(ReadTimeoutError)`

### `hidden_tests/test_retry_hidden.py::test_remove_headers_on_redirect_lowercased`

- mapping: `B007`
- API: `featurelifted.Retry`
- risk: `none`
- A001 `assert` L76: `retry.remove_headers_on_redirect == {'cookie', 'authorization'}`

### `hidden_tests/test_retry_hidden.py::test_status_increment_raises_specific_error`

- mapping: `B003, B006`
- API: `featurelifted.MaxRetryError, featurelifted.ResponseError, featurelifted.ResponseError.SPECIFIC_ERROR, featurelifted.Retry`
- risk: `exact_error_text, exception_semantics`
- A001 `raises` L84: `pytest.raises(MaxRetryError, match=re.escape(msg))`

### `hidden_tests/test_retry_hidden.py::test_no_urllib3_import_surface`

- mapping: `B009`
- API: `featurelifted.__file__`
- risk: `filesystem_resource`
- A001 `assert` L94: `not import_pattern.search(path.read_text(encoding='utf-8'))`

## Dependency / Oracle Evidence

- allowed dependencies: `none`
- forbidden imports: `urllib3`
- source entrypoints: `urllib3.util.retry.Retry, urllib3.util.retry.RequestHistory, urllib3.util.retry.Retry.get_backoff_time, urllib3.util.retry.Retry.is_retry, urllib3.util.retry.Retry.increment, urllib3.util.retry.Retry.parse_retry_after, urllib3.exceptions.MaxRetryError`
- oracle source files: `src/urllib3/exceptions.py, src/urllib3/util/retry.py, src/urllib3/util/util.py`
- runtime dependencies: `none`
- oracle notes: Oracle copies Retry policy modules and required exception types; repo snapshot is trimmed to util/ + exceptions.py for extraction-ratio calibration.

## Machine Issues

- public_tests/test_retry_public.py uses undeclared API reference featurelifted.Retry.from_int
- public_tests/test_retry_public.py uses undeclared API reference featurelifted.Retry.total
- hidden_tests/test_retry_hidden.py uses undeclared API reference featurelifted.ResponseError.SPECIFIC_ERROR
