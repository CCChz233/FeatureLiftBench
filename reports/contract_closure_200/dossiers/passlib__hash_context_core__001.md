# passlib__hash_context_core__001

- release: `frozen_python150`
- lift: `Direct`
- coupling: `unknown`
- strict validation: `PASS`
- tests/assertions: `4/11`

## Required API

- `featurelifted.CryptContext` (class) `(schemes=None, policy=<object object>, _autoload=True, **kwds)`
- `featurelifted.CryptContext.hash` (method) `(self, secret, scheme=None, category=None, **kwds)`
- `featurelifted.CryptContext.identify` (method) `(self, hash, category=None, resolve=False, required=False, unconfigured=False)`
- `featurelifted.CryptContext.verify` (method) `(self, secret, hash, scheme=None, category=None, **kwds)`

## Public Behaviors

- **B001**: The extracted feature must support this observable behavior: CryptContext hash and verify for pbkdf2_sha256. Required observable cases include hash and verify pbkdf2; context hash includes rounds; context verify and update roundtrip.
- **B002**: The extracted feature must support this observable behavior: scheme options like default_rounds and deprecated schemes. Required observable cases include context verify and update roundtrip.
- **B003**: The extracted feature must support this observable behavior: needs_update and identify handlers. Required observable cases include context verify and update roundtrip.
- **B004**: The package exposes the required task API paths `featurelifted.CryptContext`, `featurelifted.CryptContext.hash`, `featurelifted.CryptContext.identify`, `featurelifted.CryptContext.verify` with the kinds and callable signatures listed in this contract.

## Tests

### `public_tests/test_public_api.py::test_hash_and_verify_pbkdf2`

- mapping: `B001`
- API: `featurelifted.CryptContext`
- risk: `none`
- A001 `assert` L9: `digest.startswith('$pbkdf2-sha256$')`
- A002 `assert` L10: `ctx.verify('hunter2', digest)`
- A003 `assert` L11: `not ctx.verify('wrong', digest)`

### `hidden_tests/test_hidden_behavior.py::test_context_hash_includes_rounds`

- mapping: `B001`
- API: `featurelifted.CryptContext`
- risk: `none`
- A001 `assert` L9: `ctx.identify(digest) == 'pbkdf2_sha256'`
- A002 `assert` L10: `'$pbkdf2-sha256$12$' in digest`

### `hidden_tests/test_hidden_behavior.py::test_context_verify_and_update_roundtrip`

- mapping: `B001, B002, B003`
- API: `featurelifted.CryptContext`
- risk: `state_mutation`
- A001 `assert` L16: `ctx.verify('pw', old)`
- A002 `assert` L18: `ctx.verify('pw', new)`

### `hidden_tests/test_required_api_surface.py::test_required_api_surface`

- mapping: `B004`
- API: `featurelifted.CryptContext`
- risk: `none`
- A001 `assert` L9: `isinstance(CryptContext, type)`
- A002 `assert` L10: `hasattr(CryptContext, 'hash')`
- A003 `assert` L11: `hasattr(CryptContext, 'identify')`
- A004 `assert` L12: `hasattr(CryptContext, 'verify')`

## Dependency / Oracle Evidence

- allowed dependencies: `none`
- forbidden imports: `passlib`
- source entrypoints: `passlib.context.CryptContext, passlib.context.LazyCryptContext, passlib.registry.get_crypt_handler, passlib.handlers.pbkdf2`
- oracle source files: `none`
- runtime dependencies: `none`
- oracle notes: Oracle copies context/registry/pbkdf2 handler closure; repo includes full passlib for copy-all.
