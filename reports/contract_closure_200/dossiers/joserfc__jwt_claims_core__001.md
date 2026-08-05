# joserfc__jwt_claims_core__001

- release: `external50`
- lift: `Composite`
- coupling: `data_model_coupling`
- strict validation: `PASS`
- tests/assertions: `5/8`

## Required API

- `featurelifted.jwt` (module)
- `featurelifted.jwt.encode` (function)
- `featurelifted.jwt.decode` (function)
- `featurelifted.jwt.Token` (class)
- `featurelifted.jwk.OctKey` (class)
- `featurelifted.errors.ExpiredTokenError` (class)

## Public Behaviors

- **B001**: The extracted feature must support this observable behavior: HS256 encode/decode roundtrip. Required observable cases include encode decode hs256.
- **B002**: The extracted feature must support this observable behavior: OctKey import/generate. Required observable cases include generate key.
- **B003**: The extracted feature must support this observable behavior: exp claim validation raises ExpiredTokenError. Required observable cases include exp claim.
- **B004**: Decoded tokens expose .claims mapping.
- **B005**: The package exposes jwt/OctKey/ExpiredTokenError with the kinds listed in this contract.
- **B006**: the submitted package does not import forbidden upstream packages: joserfc.

## Tests

### `public_tests/test_public_api.py::test_encode_decode_hs256`

- mapping: `B001`
- API: `featurelifted.jwk, featurelifted.jwt, featurelifted.jwt.decode, featurelifted.jwt.encode`
- risk: `none`
- A001 `assert` L11: `decoded.claims['sub'] == 'user-1'`

### `public_tests/test_public_api.py::test_generate_key`

- mapping: `B002`
- API: `featurelifted.jwk, featurelifted.jwt, featurelifted.jwt.decode, featurelifted.jwt.encode`
- risk: `none`
- A001 `assert` L18: `decoded.claims['iss'] == 'test'`

### `hidden_tests/test_hidden_behavior.py::test_exp_claim`

- mapping: `B001, B002, B003, B004`
- API: `featurelifted.errors, featurelifted.jwk, featurelifted.jwt, featurelifted.jwt.decode, featurelifted.jwt.encode`
- risk: `time_or_randomness`
- A001 `assert` L17: `decoded.claims['sub'] == 'u'`
- A002 `assert` L22: `False`

### `hidden_tests/test_hidden_behavior.py::test_no_upstream_import_surface`

- mapping: `B006`
- API: `featurelifted.__file__, featurelifted.errors, featurelifted.jwk`
- risk: `filesystem_resource`
- A001 `assert` L38: `not pattern.search(path.read_text(encoding='utf-8'))`

### `hidden_tests/test_required_api_surface.py::test_required_api_surface`

- mapping: `B005`
- API: `featurelifted.errors, featurelifted.jwk, featurelifted.jwt`
- risk: `none`
- A001 `assert` L7: `jwt is not None`
- A002 `assert` L8: `OctKey is not None`
- A003 `assert` L9: `ExpiredTokenError is not None`

## Dependency / Oracle Evidence

- allowed dependencies: `cffi, cryptography, pycparser`
- forbidden imports: `joserfc`
- source entrypoints: `none`
- oracle source files: `src/joserfc/jwt.py, src/joserfc/jwk.py`
- runtime dependencies: `cffi, cryptography, pycparser`
- oracle notes: Composite jwt.encode/decode with OctKey HS256 offline.
- behavior contract lacks a completed review_status
- behavior contract schema_version missing or unsupported
