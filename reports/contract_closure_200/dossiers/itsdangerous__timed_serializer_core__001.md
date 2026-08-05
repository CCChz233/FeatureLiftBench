# itsdangerous__timed_serializer_core__001

- release: `frozen_python150`
- lift: `Adapted`
- coupling: `unknown`
- strict validation: `PASS`
- tests/assertions: `5/12`

## Required API

- `featurelifted.URLSafeTimedSerializer` (class) `(secret_key, salt='featurelift', *, now=None)`
- `featurelifted.URLSafeTimedSerializer.dumps` (method) `(self, obj)`
- `featurelifted.URLSafeTimedSerializer.loads` (method) `(self, token, max_age=None, now=None)`
- `featurelifted.BadSignature` (exception)
- `featurelifted.SignatureExpired` (exception)

## Public Behaviors

- **B001**: The extracted feature must support this observable behavior: deterministic URL-safe dumps and loads for JSON-compatible values. Required observable cases include roundtrip and salt separation; tampering raises bad signature; expiry boundary and error type; wrong key and malformed token.
- **B002**: The extracted feature must support this observable behavior: salt-separated HMAC-SHA256 signatures. Required observable cases include roundtrip and salt separation; tampering raises bad signature; expiry boundary and error type; wrong key and malformed token.
- **B003**: The extracted feature must support this observable behavior: timestamp max_age validation with injectable current time. Required observable cases include roundtrip and salt separation; tampering raises bad signature; expiry boundary and error type; wrong key and malformed token.
- **B004**: The extracted feature must support this observable behavior: BadSignature and SignatureExpired error distinctions. Required observable cases include roundtrip and salt separation; tampering raises bad signature; expiry boundary and error type; wrong key and malformed token.
- **B005**: The package exposes the required task API paths `featurelifted.URLSafeTimedSerializer`, `featurelifted.URLSafeTimedSerializer.dumps`, `featurelifted.URLSafeTimedSerializer.loads`, `featurelifted.BadSignature`, `featurelifted.SignatureExpired` with the kinds and callable signatures listed in this contract.

## Tests

### `public_tests/test_public_contract.py::test_roundtrip_and_salt_separation`

- mapping: `B001, B002, B003, B004`
- API: `featurelifted.BadSignature, featurelifted.URLSafeTimedSerializer, featurelifted.URLSafeTimedSerializer.loads`
- risk: `exception_semantics`
- A001 `assert` L7: `one.loads(token, now=100) == {'name': 'Ada', 'roles': ['admin']}`
- A002 `raises` L8: `pytest.raises(BadSignature)`

### `public_tests/test_public_contract.py::test_tampering_raises_bad_signature`

- mapping: `B001, B002, B003, B004`
- API: `featurelifted.BadSignature, featurelifted.URLSafeTimedSerializer`
- risk: `exception_semantics`
- A001 `raises` L14: `pytest.raises(BadSignature)`

### `hidden_tests/test_hidden_contract.py::test_expiry_boundary_and_error_type`

- mapping: `B001, B002, B003, B004`
- API: `featurelifted.SignatureExpired, featurelifted.URLSafeTimedSerializer`
- risk: `exception_semantics`
- A001 `assert` L7: `serializer.loads(token, max_age=5, now=105) == {'ok': True}`
- A002 `raises` L8: `pytest.raises(SignatureExpired)`

### `hidden_tests/test_hidden_contract.py::test_wrong_key_and_malformed_token`

- mapping: `B001, B002, B003, B004`
- API: `featurelifted.BadSignature, featurelifted.URLSafeTimedSerializer, featurelifted.URLSafeTimedSerializer.dumps, featurelifted.URLSafeTimedSerializer.loads`
- risk: `exception_semantics`
- A001 `raises` L13: `pytest.raises(BadSignature)`
- A002 `raises` L15: `pytest.raises(BadSignature)`

### `hidden_tests/test_required_api_surface.py::test_required_api_surface`

- mapping: `B005`
- API: `featurelifted.BadSignature, featurelifted.SignatureExpired, featurelifted.URLSafeTimedSerializer`
- risk: `none`
- A001 `assert` L11: `isinstance(URLSafeTimedSerializer, type)`
- A002 `assert` L12: `hasattr(URLSafeTimedSerializer, 'dumps')`
- A003 `assert` L13: `hasattr(URLSafeTimedSerializer, 'loads')`
- A004 `assert` L14: `issubclass(BadSignature, BaseException)`
- A005 `assert` L15: `issubclass(SignatureExpired, BaseException)`

## Dependency / Oracle Evidence

- allowed dependencies: `none`
- forbidden imports: `itsdangerous`
- source entrypoints: `itsdangerous.url_safe.URLSafeTimedSerializer, itsdangerous.exc.BadSignature, itsdangerous.exc.SignatureExpired`
- oracle source files: `itsdangerous.url_safe.URLSafeTimedSerializer, itsdangerous.exc.BadSignature, itsdangerous.exc.SignatureExpired`
- runtime dependencies: `none`
- oracle notes: Entrypoints are maintainer-private provenance and are never Agent-visible in Main.
- behavior contract lacks a completed review_status
