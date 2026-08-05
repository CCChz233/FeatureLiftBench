# websockets__handshake_parse_core__001

- release: `frozen_python150`
- lift: `Adapted`
- coupling: `unknown`
- strict validation: `FAIL`
- tests/assertions: `23/59`

## Required API

- `featurelifted.Headers` (class) `(*args: 'HeadersLike', **kwargs: 'str') -> 'None'`
- `featurelifted.Headers.get_all` (method) `(self, key: 'str') -> 'list[str]'`
- `featurelifted.Request` (class) `(path: 'str', headers: 'Headers', _exception: 'Exception | None' = None) -> None`
- `featurelifted.Response` (class) `(status_code: 'int', reason_phrase: 'str', headers: 'Headers', body: 'bytes | bytearray' = b'', _exception: 'Exception | None' = None) -> None`
- `featurelifted.accept_key` (function) `(key: 'str') -> 'str'`
- `featurelifted.generate_key` (function) `() -> 'str'`
- `featurelifted.validate_handshake_request` (function) `(request: 'Request', *, origins: 'Sequence[Origin | re.Pattern[str] | None] | None' = None) -> 'str'`
- `featurelifted.exceptions` (module)
- `featurelifted.exceptions.InvalidHeader` (exception)
- `featurelifted.exceptions.InvalidHeaderFormat` (exception)
- `featurelifted.exceptions.InvalidHeaderValue` (exception)
- `featurelifted.exceptions.InvalidOrigin` (exception)
- `featurelifted.exceptions.InvalidUpgrade` (exception)
- `featurelifted.exceptions.SecurityError` (exception)
- `featurelifted.headers` (module)
- `featurelifted.headers.build_authorization_basic` (function) `(username: 'str', password: 'str') -> 'str'`
- `featurelifted.headers.build_subprotocol` (function) `(subprotocols: 'Sequence[Subprotocol]') -> 'str'`
- `featurelifted.headers.build_www_authenticate_basic` (function) `(realm: 'str') -> 'str'`
- `featurelifted.headers.parse_authorization_basic` (function) `(header: 'str') -> 'tuple[str, str]'`
- `featurelifted.headers.parse_connection` (function) `(header: 'str') -> 'list[ConnectionOption]'`
- `featurelifted.headers.parse_extension` (function) `(header: 'str') -> 'list[ExtensionHeader]'`
- `featurelifted.headers.parse_subprotocol` (function) `(header: 'str') -> 'list[Subprotocol]'`
- `featurelifted.headers.parse_upgrade` (function) `(header: 'str') -> 'list[UpgradeProtocol]'`
- `featurelifted.headers.validate_subprotocols` (function) `(subprotocols: 'Sequence[Subprotocol]') -> 'None'`
- `featurelifted.http11` (module)
- `featurelifted.http11.parse_headers` (function) `(read_line: 'Callable[[int], Generator[None, None, bytes | bytearray]]') -> 'Generator[None, None, Headers]'`
- `featurelifted.streams` (module)
- `featurelifted.streams.StreamReader` (class) `() -> 'None'`

## Public Behaviors

- **B001**: The extracted feature must support this observable behavior: parse Connection and Upgrade header lists with OWS and empty elements. Required observable cases include parse connection and upgrade; parse upgrade case insensitive list; headers multiple connection values.
- **B002**: The extracted feature must support this observable behavior: parse Sec-WebSocket-Extensions and Sec-WebSocket-Protocol grammars. Required observable cases include parse extension with quoted params; parse subprotocol skips empty elements; parse extension invalid quoted token; build subprotocol roundtrip; validate subprotocols rejects invalid token.
- **B003**: The extracted feature must support this observable behavior: parse WebSocket handshake HTTP requests from byte streams. Required observable cases include parse websocket request basic; parse request invalid method; parse headers security limit.
- **B004**: The extracted feature must support this observable behavior: case-insensitive Headers lookup with multiple values per name. Required observable cases include headers case insensitive lookup; headers multiple connection values.
- **B005**: The extracted feature must support this observable behavior: validate handshake request headers including Sec-WebSocket-Key and Version. Required observable cases include validate handshake rejects bad upgrade; validate handshake missing key; validate handshake invalid key length; validate handshake origin allowlist; validate handshake origin regex allowlist.
- **B006**: The extracted feature must support this observable behavior: compute Sec-WebSocket-Accept from Sec-WebSocket-Key. Required observable cases include accept key rfc6455 example; validate subprotocols rejects invalid token.
- **B007**: The extracted feature must support this observable behavior: raise typed errors for malformed headers and upgrade requests. Required observable cases include validate handshake rejects bad upgrade; parse request invalid method; parse headers security limit; parse extension invalid quoted token; validate subprotocols rejects invalid token.
- **B008**: The package exposes the required task API paths `featurelifted.Headers`, `featurelifted.Headers.get_all`, `featurelifted.Request`, `featurelifted.Response`, `featurelifted.accept_key`, `featurelifted.generate_key`, `featurelifted.validate_handshake_request`, `featurelifted.exceptions`, `featurelifted.exceptions.InvalidHeader`, `featurelifted.exceptions.InvalidHeaderFormat`, `featurelifted.exceptions.InvalidHeaderValue`, `featurelifted.exceptions.InvalidOrigin`, and 16 listed members with the kinds and callable signatures listed in this contract.

## Tests

### `public_tests/test_public_api.py::test_parse_connection_and_upgrade`

- mapping: `B001`
- API: `featurelifted.headers, featurelifted.streams`
- risk: `none`
- A001 `assert` L20: `parse_connection('keep-alive, Upgrade') == ['keep-alive', 'Upgrade']`
- A002 `assert` L21: `parse_upgrade('websocket') == ['websocket']`

### `public_tests/test_public_api.py::test_headers_case_insensitive_lookup`

- mapping: `B004`
- API: `featurelifted.Headers, featurelifted.headers, featurelifted.streams`
- risk: `none`
- A001 `assert` L26: `headers['upgrade'] == 'websocket'`
- A002 `assert` L27: `headers['CONNECTION'] == 'Upgrade'`

### `public_tests/test_public_api.py::test_parse_websocket_request_basic`

- mapping: `B003`
- API: `featurelifted.headers, featurelifted.streams`
- risk: `none`
- A001 `assert` L41: `request.path == '/chat'`
- A002 `assert` L42: `request.headers['Host'] == 'server.example.com'`
- A003 `assert` L43: `request.headers['Upgrade'] == 'websocket'`

### `public_tests/test_public_api.py::test_accept_key_rfc6455_example`

- mapping: `B006`
- API: `featurelifted.accept_key, featurelifted.generate_key, featurelifted.headers, featurelifted.streams`
- risk: `none`
- A001 `assert` L47: `accept_key('dGhlIHNhbXBsZSBub25jZQ==') == 's3pPLMBiTxaQ9kYGzzhZRbK+xOo='`
- A002 `assert` L49: `isinstance(key, str)`
- A003 `assert` L50: `len(key) > 0`

### `hidden_tests/test_hidden_behavior.py::test_parse_extension_with_quoted_params`

- mapping: `B002`
- API: `featurelifted.exceptions, featurelifted.headers, featurelifted.http11, featurelifted.streams`
- risk: `none`
- A001 `assert` L73: `parsed == [('foo', [('name', None), ('token', 'token'), ('quoted-string', 'quoted-string')]), ('bar', [('quux', None), ('quuux', None)])]`

### `hidden_tests/test_hidden_behavior.py::test_parse_upgrade_case_insensitive_list`

- mapping: `B001`
- API: `featurelifted.exceptions, featurelifted.headers, featurelifted.http11, featurelifted.streams`
- risk: `none`
- A001 `assert` L87: `parse_upgrade(',,  WebSocket,  \t,,') == ['WebSocket']`

### `hidden_tests/test_hidden_behavior.py::test_parse_subprotocol_skips_empty_elements`

- mapping: `B002`
- API: `featurelifted.exceptions, featurelifted.headers, featurelifted.http11, featurelifted.streams`
- risk: `none`
- A001 `assert` L91: `parse_subprotocol(',\t, ,  ,foo  ,,   bar,baz,,') == ['foo', 'bar', 'baz']`

### `hidden_tests/test_hidden_behavior.py::test_headers_multiple_connection_values`

- mapping: `B001, B004`
- API: `featurelifted.Headers, featurelifted.exceptions, featurelifted.headers, featurelifted.http11, featurelifted.streams`
- risk: `exception_semantics`
- A001 `assert` L102: `headers.get_all('connection') == ['keep-alive', 'Upgrade']`
- A002 `raises` L103: `pytest.raises(Exception)`

### `hidden_tests/test_hidden_behavior.py::test_validate_handshake_rejects_bad_upgrade`

- mapping: `B005, B007`
- API: `featurelifted.exceptions, featurelifted.headers, featurelifted.http11, featurelifted.streams, featurelifted.validate_handshake_request`
- risk: `exception_semantics`
- A001 `raises` L109: `pytest.raises(InvalidUpgrade)`

### `hidden_tests/test_hidden_behavior.py::test_validate_handshake_missing_key`

- mapping: `B005`
- API: `featurelifted.exceptions, featurelifted.headers, featurelifted.http11, featurelifted.streams, featurelifted.validate_handshake_request`
- risk: `exception_semantics`
- A001 `raises` L123: `pytest.raises(InvalidHeader)`

### `hidden_tests/test_hidden_behavior.py::test_validate_handshake_invalid_key_length`

- mapping: `B005`
- API: `featurelifted.exceptions, featurelifted.headers, featurelifted.http11, featurelifted.streams, featurelifted.validate_handshake_request`
- risk: `exception_semantics`
- A001 `raises` L138: `pytest.raises(InvalidHeaderValue)`

### `hidden_tests/test_hidden_behavior.py::test_validate_handshake_origin_allowlist`

- mapping: `B005`
- API: `featurelifted.exceptions, featurelifted.headers, featurelifted.http11, featurelifted.streams, featurelifted.validate_handshake_request`
- risk: `exception_semantics`
- A001 `raises` L144: `pytest.raises(InvalidOrigin)`

### `hidden_tests/test_hidden_behavior.py::test_parse_request_invalid_method`

- mapping: `B003, B007`
- API: `featurelifted.exceptions, featurelifted.headers, featurelifted.http11, featurelifted.streams`
- risk: `exact_error_text, exception_semantics`
- A001 `raises` L153: `pytest.raises(ValueError, match='unsupported HTTP method')`

### `hidden_tests/test_hidden_behavior.py::test_parse_headers_security_limit`

- mapping: `B003, B007`
- API: `featurelifted.exceptions, featurelifted.headers, featurelifted.http11, featurelifted.streams`
- risk: `exception_semantics`
- A001 `raises` L159: `pytest.raises(SecurityError)`

### `hidden_tests/test_hidden_behavior.py::test_parse_extension_invalid_quoted_token`

- mapping: `B002, B007`
- API: `featurelifted.exceptions, featurelifted.headers, featurelifted.http11, featurelifted.streams`
- risk: `exception_semantics`
- A001 `raises` L164: `pytest.raises(InvalidHeaderFormat)`

### `hidden_tests/test_hidden_behavior.py::test_build_subprotocol_roundtrip`

- mapping: `B002, B008`
- API: `featurelifted.exceptions, featurelifted.headers, featurelifted.http11, featurelifted.streams`
- risk: `none`
- A001 `assert` L172: `parse_subprotocol(header) == subprotocols`

### `hidden_tests/test_hidden_behavior.py::test_validate_subprotocols_rejects_invalid_token`

- mapping: `B002, B006, B007`
- API: `featurelifted.exceptions, featurelifted.headers, featurelifted.http11, featurelifted.streams`
- risk: `exact_error_text, exception_semantics`
- A001 `raises` L176: `pytest.raises(ValueError, match='invalid subprotocol')`

### `hidden_tests/test_hidden_behavior.py::test_parse_authorization_basic_credentials`

- mapping: `B008`
- API: `featurelifted.exceptions, featurelifted.headers, featurelifted.http11, featurelifted.streams`
- risk: `none`
- A001 `assert` L182: `parse_authorization_basic(header) == ('alice', 's3cret!')`

### `hidden_tests/test_hidden_behavior.py::test_parse_authorization_basic_rejects_non_basic_scheme`

- mapping: `B008`
- API: `featurelifted.exceptions, featurelifted.headers, featurelifted.http11, featurelifted.streams`
- risk: `exact_error_text, exception_semantics`
- A001 `raises` L186: `pytest.raises(InvalidHeaderValue, match='unsupported scheme')`

### `hidden_tests/test_hidden_behavior.py::test_build_www_authenticate_basic_format`

- mapping: `B008`
- API: `featurelifted.exceptions, featurelifted.headers, featurelifted.http11, featurelifted.streams`
- risk: `none`
- A001 `assert` L192: `header.startswith('Basic realm=')`
- A002 `assert` L193: `'charset=' in header`

### `hidden_tests/test_hidden_behavior.py::test_validate_handshake_origin_regex_allowlist`

- mapping: `B005`
- API: `featurelifted.exceptions, featurelifted.headers, featurelifted.http11, featurelifted.streams, featurelifted.validate_handshake_request`
- risk: `none`
- A001 `assert` L198: `validate_handshake_request(request, origins=[re.compile('https://.*\\.example\\.com')])`

### `hidden_tests/test_hidden_behavior.py::test_no_websockets_import_surface`

- mapping: `B009`
- API: `featurelifted.__file__, featurelifted.exceptions, featurelifted.headers, featurelifted.http11, featurelifted.streams`
- risk: `filesystem_resource`
- A001 `assert` L209: `not hasattr(featurelifted, name)`
- A002 `assert` L215: `not import_pattern.search(text)`

### `hidden_tests/test_required_api_surface.py::test_required_api_surface`

- mapping: `B008`
- API: `featurelifted.Headers, featurelifted.Request, featurelifted.Response, featurelifted.accept_key, featurelifted.exceptions, featurelifted.generate_key, featurelifted.headers, featurelifted.http11, featurelifted.streams, featurelifted.validate_handshake_request`
- risk: `none`
- A001 `assert` L18: `isinstance(Headers, type)`
- A002 `assert` L19: `hasattr(Headers, 'get_all')`
- A003 `assert` L20: `isinstance(Request, type)`
- A004 `assert` L21: `isinstance(Response, type)`
- A005 `assert` L22: `callable(accept_key)`
- A006 `assert` L23: `callable(generate_key)`
- A007 `assert` L24: `callable(validate_handshake_request)`
- A008 `assert` L25: `exceptions is not None`
- A009 `assert` L26: `issubclass(getattr(exceptions, 'InvalidHeader'), BaseException)`
- A010 `assert` L27: `issubclass(getattr(exceptions, 'InvalidHeaderFormat'), BaseException)`
- A011 `assert` L28: `issubclass(getattr(exceptions, 'InvalidHeaderValue'), BaseException)`
- A012 `assert` L29: `issubclass(getattr(exceptions, 'InvalidOrigin'), BaseException)`
- A013 `assert` L30: `issubclass(getattr(exceptions, 'InvalidUpgrade'), BaseException)`
- A014 `assert` L31: `issubclass(getattr(exceptions, 'SecurityError'), BaseException)`
- A015 `assert` L32: `headers is not None`
- A016 `assert` L33: `callable(getattr(headers, 'build_authorization_basic'))`
- A017 `assert` L34: `callable(getattr(headers, 'build_subprotocol'))`
- A018 `assert` L35: `callable(getattr(headers, 'build_www_authenticate_basic'))`
- A019 `assert` L36: `callable(getattr(headers, 'parse_authorization_basic'))`
- A020 `assert` L37: `callable(getattr(headers, 'parse_connection'))`
- A021 `assert` L38: `callable(getattr(headers, 'parse_extension'))`
- A022 `assert` L39: `callable(getattr(headers, 'parse_subprotocol'))`
- A023 `assert` L40: `callable(getattr(headers, 'parse_upgrade'))`
- A024 `assert` L41: `callable(getattr(headers, 'validate_subprotocols'))`
- A025 `assert` L42: `http11 is not None`
- A026 `assert` L43: `callable(getattr(http11, 'parse_headers'))`
- A027 `assert` L44: `streams is not None`
- A028 `assert` L45: `isinstance(getattr(streams, 'StreamReader'), type)`

## Dependency / Oracle Evidence

- allowed dependencies: `none`
- forbidden imports: `websockets`
- source entrypoints: `websockets.headers.parse_connection, websockets.headers.parse_upgrade, websockets.headers.parse_extension, websockets.headers.parse_subprotocol, websockets.http11.Request.parse, websockets.http11.Response.parse, websockets.datastructures.Headers, websockets.server.ServerProtocol.process_request, websockets.utils.accept_key`
- oracle source files: `websockets/datastructures.py, websockets/headers.py, websockets/http11.py, websockets/streams.py, websockets/typing.py, websockets/version.py, websockets/utils.py`
- runtime dependencies: `none`
- oracle notes: Handshake closure: header grammars, HTTP/1.1 Request/Response parsing, StreamReader buffer, and extracted validate_handshake_request. Trimmed exceptions module; frame/async/sync stacks excluded.

## Machine Issues

- public_tests/test_public_api.py uses undeclared API reference featurelifted.Request.parse
- hidden_tests/test_hidden_behavior.py uses undeclared API reference featurelifted.Request.parse
