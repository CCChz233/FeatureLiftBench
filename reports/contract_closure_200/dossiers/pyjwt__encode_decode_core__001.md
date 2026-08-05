# pyjwt__encode_decode_core__001

- release: `external50`
- lift: `Adapted`
- coupling: `data_model_coupling`
- strict validation: `PASS`
- tests/assertions: `7/9`

## Required API

- `featurelifted.encode` (function)
- `featurelifted.decode` (function)
- `featurelifted.exceptions.InvalidTokenError` (exception)
- `featurelifted.exceptions.InvalidSignatureError` (exception)
- `featurelifted.exceptions.ExpiredSignatureError` (exception)

## Public Behaviors

- **B001**: The extracted feature must support this observable behavior: encode/decode HS256 roundtrip. Required observable cases include encode decode hs256.
- **B002**: The extracted feature must support this observable behavior: wrong secret and expired tokens raise signature/expiry errors. Required observable cases include wrong secret; expired token.
- **B003**: The extracted feature must support this observable behavior: optional headers and InvalidTokenError hierarchy. Required observable cases include custom header; invalid token error base.
- **B004**: cryptography is required for HS256 via PyJWT[crypto].
- **B005**: The package exposes encode/decode and JWT exceptions with the kinds listed in this contract.
- **B006**: the submitted package does not import forbidden upstream packages: jwt.

## Tests

### `public_tests/test_public_api.py::test_encode_decode_hs256`

- mapping: `B001`
- API: `featurelifted.decode, featurelifted.encode, featurelifted.exceptions`
- risk: `none`
- A001 `assert` L12: `payload['sub'] == 'user1'`

### `public_tests/test_public_api.py::test_wrong_secret`

- mapping: `B002`
- API: `featurelifted.decode, featurelifted.encode, featurelifted.exceptions`
- risk: `none`
- A001 `assert` L19: `False`

### `public_tests/test_public_api.py::test_expired_token`

- mapping: `B003`
- API: `featurelifted.decode, featurelifted.encode, featurelifted.exceptions`
- risk: `time_or_randomness`
- A001 `assert` L28: `False`

### `hidden_tests/test_hidden_behavior.py::test_no_upstream_import_surface`

- mapping: `B006`
- API: `featurelifted.__file__, featurelifted.exceptions`
- risk: `filesystem_resource`
- A001 `assert` L13: `not pattern.search(path.read_text(encoding='utf-8'))`

### `hidden_tests/test_hidden_behavior.py::test_custom_header`

- mapping: `B001, B002, B004`
- API: `featurelifted.decode, featurelifted.encode, featurelifted.exceptions`
- risk: `none`
- A001 `assert` L23: `payload['x'] == 1`

### `hidden_tests/test_hidden_behavior.py::test_invalid_token_error_base`

- mapping: `B003`
- API: `featurelifted.exceptions`
- risk: `none`
- A001 `assert` L27: `issubclass(InvalidTokenError, Exception)`

### `hidden_tests/test_required_api_surface.py::test_required_api_surface`

- mapping: `B005`
- API: `featurelifted.decode, featurelifted.encode, featurelifted.exceptions`
- risk: `none`
- A001 `assert` L6: `callable(encode) and callable(decode)`
- A002 `assert` L7: `InvalidTokenError is not None`
- A003 `assert` L8: `ExpiredSignatureError is not None and InvalidSignatureError is not None`

## Dependency / Oracle Evidence

- allowed dependencies: `cffi, cryptography, pycparser, pyjwt`
- forbidden imports: `jwt`
- source entrypoints: `none`
- oracle source files: `jwt/api_jwt.py, jwt/exceptions.py`
- runtime dependencies: `cffi, cryptography, pycparser, pyjwt`
- oracle notes: Adapted jwt encode/decode HS256 with crypto extra.
- behavior contract lacks a completed review_status
- behavior contract schema_version missing or unsupported
