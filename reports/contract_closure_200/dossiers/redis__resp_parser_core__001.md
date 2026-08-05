# redis__resp_parser_core__001

- release: `frozen_python150`
- lift: `Adapted`
- coupling: `unknown`
- strict validation: `PASS`
- tests/assertions: `6/15`

## Required API

- `featurelifted._parsers` (module)
- `featurelifted._parsers.Encoder` (class) `(encoding, encoding_errors, decode_responses)`
- `featurelifted._parsers.Encoder.encode` (method) `(self, value)`
- `featurelifted._parsers._RESP2Parser` (function) `(socket_read_size)`
- `featurelifted._parsers._RESP3Parser` (function) `(socket_read_size)`
- `featurelifted.exceptions` (module)
- `featurelifted.exceptions.ResponseError` (exception)

## Public Behaviors

- **B001**: The extracted feature must support this observable behavior: parse RESP simple, bulk, and multi-bulk replies. Required observable cases include resp2 simple and bulk replies; resp2 array reply; resp2 error reply returns response error.
- **B002**: The extracted feature must support this observable behavior: decode bulk strings with optional byte preservation. Required observable cases include resp3 null and boolean.
- **B003**: The extracted feature must support this observable behavior: map Redis error prefixes to exception classes. Required observable cases include resp2 error reply returns response error.
- **B004**: The extracted feature must support this observable behavior: encode commands to RESP bulk arrays. Required observable cases include resp2 array reply; encoder rejects bool.
- **B005**: The extracted feature must support this observable behavior: buffer incremental socket reads via SocketBuffer. Required observable cases include resp3 null and boolean.
- **B006**: The package exposes the required task API paths `featurelifted._parsers`, `featurelifted._parsers.Encoder`, `featurelifted._parsers.Encoder.encode`, `featurelifted._parsers._RESP2Parser`, `featurelifted._parsers._RESP3Parser`, `featurelifted.exceptions`, `featurelifted.exceptions.ResponseError` with the kinds and callable signatures listed in this contract.

## Tests

### `public_tests/test_public_api.py::test_resp2_simple_and_bulk_replies`

- mapping: `B001`
- API: `featurelifted._parsers`
- risk: `none`
- A001 `assert` L30: `parser.read_response() == 42`
- A002 `assert` L33: `parser.read_response() == 'foo'`

### `public_tests/test_public_api.py::test_resp2_array_reply`

- mapping: `B001, B004`
- API: `featurelifted._parsers`
- risk: `none`
- A001 `assert` L39: `parser.read_response() == [1, 2]`

### `hidden_tests/test_hidden_behavior.py::test_resp2_error_reply_returns_response_error`

- mapping: `B001, B003`
- API: `featurelifted._parsers, featurelifted.exceptions`
- risk: `none`
- A001 `assert` L32: `isinstance(result, ResponseError)`
- A002 `assert` L33: `'unknown command' in str(result)`

### `hidden_tests/test_hidden_behavior.py::test_resp3_null_and_boolean`

- mapping: `B002, B005, B006`
- API: `featurelifted._parsers, featurelifted.exceptions`
- risk: `none`
- A001 `assert` L39: `parser.read_response() is None`
- A002 `assert` L42: `parser.read_response() is True`

### `hidden_tests/test_hidden_behavior.py::test_encoder_rejects_bool`

- mapping: `B004`
- API: `featurelifted._parsers, featurelifted.exceptions`
- risk: `none`
- A001 `assert` L52: `raised`

### `hidden_tests/test_required_api_surface.py::test_required_api_surface`

- mapping: `B006`
- API: `featurelifted._parsers, featurelifted.exceptions`
- risk: `none`
- A001 `assert` L10: `_parsers is not None`
- A002 `assert` L11: `isinstance(getattr(_parsers, 'Encoder'), type)`
- A003 `assert` L12: `hasattr(getattr(_parsers, 'Encoder'), 'encode')`
- A004 `assert` L13: `callable(getattr(_parsers, '_RESP2Parser'))`
- A005 `assert` L14: `callable(getattr(_parsers, '_RESP3Parser'))`
- A006 `assert` L15: `exceptions is not None`
- A007 `assert` L16: `issubclass(getattr(exceptions, 'ResponseError'), BaseException)`

## Dependency / Oracle Evidence

- allowed dependencies: `none`
- forbidden imports: `redis`
- source entrypoints: `redis._parsers._RESP2Parser, redis._parsers._RESP3Parser, redis._parsers.Encoder, redis._parsers.SocketBuffer`
- oracle source files: `none`
- runtime dependencies: `none`
