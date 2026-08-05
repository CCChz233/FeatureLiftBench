# Contract V2 P0: pyjwt__encode_decode_core__001

- release: `external50`
- lift: `Adapted`
- coupling: `data_model_coupling`
- strict validation: `PASS`
- tests/assertions: `8/13`

## Required API

- `featurelifted.encode` (function) `(payload: 'dict[str, Any]', key: 'AllowedPrivateKeyTypes', algorithm: 'str | None' = <object object>, headers: 'dict[str, Any] | None' = None, json_encoder: 'type[json.JSONEncoder] | None' = None, sort_headers: 'bool' = True) -> 'str'`
- `featurelifted.decode` (function) `(jwt: 'str | bytes', key: 'AllowedPublicKeys | PyJWK | str | bytes' = '', algorithms: 'Sequence[str] | None' = None, options: 'Options | None' = None, verify: 'bool | None' = None, detached_payload: 'bytes | None' = None, audience: 'str | Iterable[str] | None' = None, subject: 'str | None' = None, issuer: 'str | Container[str] | None' = None, leeway: 'float | timedelta' = 0, **kwargs: 'Any') -> 'dict[str, Any]'`
- `featurelifted.exceptions.InvalidTokenError` (exception)
- `featurelifted.exceptions.InvalidSignatureError` (exception)
- `featurelifted.exceptions.ExpiredSignatureError` (exception)
- `featurelifted.exceptions` (module)

## Public Behaviors

- **B001**: The extracted feature must support this observable behavior: encode/decode HS256 roundtrip. Required observable cases include encode decode hs256.
- **B002**: The extracted feature must support this observable behavior: wrong secret and expired tokens raise signature/expiry errors. Required observable cases include wrong secret; expired token.
- **B003**: The extracted feature must support this observable behavior: optional headers and InvalidTokenError hierarchy. Required observable cases include custom header; invalid token error base.
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

- mapping: `B002`
- API: `featurelifted.decode, featurelifted.encode, featurelifted.exceptions`
- risk: `time_or_randomness`
- A001 `assert` L28: `False`

### `hidden_tests/test_hidden_behavior.py::test_no_upstream_import_surface`

- mapping: `B006`
- API: `featurelifted.__file__, featurelifted.exceptions`
- risk: `filesystem_resource`
- A001 `assert` L18: `not pattern.search(path.read_text(encoding='utf-8'))`

### `hidden_tests/test_hidden_behavior.py::test_custom_header`

- mapping: `B001, B003`
- API: `featurelifted.decode, featurelifted.encode, featurelifted.exceptions`
- risk: `none`
- A001 `assert` L24: `payload['x'] == 1`

### `hidden_tests/test_hidden_behavior.py::test_invalid_token_error_base`

- mapping: `B003`
- API: `featurelifted.exceptions`
- risk: `none`
- A001 `assert` L28: `issubclass(InvalidTokenError, Exception)`

### `hidden_tests/test_hidden_behavior.py::test_wrong_secret_hidden`

- mapping: `B002`
- API: `featurelifted.decode, featurelifted.encode, featurelifted.exceptions`
- risk: `exception_semantics`
- A001 `raises` L33: `pytest.raises(InvalidSignatureError)`

### `hidden_tests/test_required_api_surface.py::test_required_api_surface`

- mapping: `B005`
- API: `featurelifted.decode, featurelifted.encode, featurelifted.exceptions`
- risk: `none`
- A001 `assert` L11: `callable(encode)`
- A002 `assert` L12: `callable(decode)`
- A003 `assert` L13: `issubclass(getattr(exceptions, 'InvalidTokenError'), BaseException)`
- A004 `assert` L14: `issubclass(getattr(exceptions, 'InvalidSignatureError'), BaseException)`
- A005 `assert` L15: `issubclass(getattr(exceptions, 'ExpiredSignatureError'), BaseException)`
- A006 `assert` L16: `exceptions is not None`

## Dependency / Oracle Evidence

- allowed dependencies: `none`
- forbidden imports: `jwt`
- source entrypoints: `none`
- oracle source files: `jwt/api_jwt.py, jwt/exceptions.py`
- runtime dependencies: `none`
- oracle notes: Adapted, self-contained HS256 JWT encode/decode scope. It uses standard-library HMAC and installs neither PyJWT nor optional asymmetric-algorithm dependencies.
