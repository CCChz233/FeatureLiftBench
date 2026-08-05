# pyotp__totp_hotp_core__001

- release: `external50`
- lift: `Direct`
- coupling: `data_model_coupling`
- strict validation: `PASS`
- tests/assertions: `8/12`

## Required API

- `featurelifted.TOTP` (class)
- `featurelifted.TOTP.at` (method)
- `featurelifted.TOTP.verify` (method)
- `featurelifted.HOTP` (class)
- `featurelifted.HOTP.at` (method)
- `featurelifted.HOTP.verify` (method)
- `featurelifted.random_base32` (function) `(length=32)`

## Public Behaviors

- **B001**: The extracted feature must support this observable behavior: TOTP.at/verify for fixed timestamps. Required observable cases include totp at verify; totp verify rejects wrong.
- **B002**: The extracted feature must support this observable behavior: HOTP.at/verify for counters. Required observable cases include hotp at verify; hotp counter increments.
- **B003**: The extracted feature must support this observable behavior: random_base32 generates base32 secrets with minimum length guard. Required observable cases include random base32; random base32 length guard.
- **B004**: Tests use at(timestamp) rather than now() to avoid time dependence.
- **B005**: The package exposes TOTP/HOTP/random_base32 with the kinds listed in this contract.
- **B006**: the submitted package does not import forbidden upstream packages: pyotp.

## Tests

### `public_tests/test_public_api.py::test_totp_at_verify`

- mapping: `B001`
- API: `featurelifted.TOTP`
- risk: `time_or_randomness`
- A001 `assert` L15: `code == '742275'`
- A002 `assert` L16: `totp.verify(code, when) is True`

### `public_tests/test_public_api.py::test_hotp_at_verify`

- mapping: `B002`
- API: `featurelifted.HOTP`
- risk: `none`
- A001 `assert` L22: `code == '282760'`
- A002 `assert` L23: `hotp.verify(code, 0) is True`

### `public_tests/test_public_api.py::test_random_base32`

- mapping: `B003`
- API: `featurelifted.random_base32`
- risk: `none`
- A001 `assert` L28: `len(secret) == 32`
- A002 `assert` L29: `set(secret) <= set('ABCDEFGHIJKLMNOPQRSTUVWXYZ234567')`

### `hidden_tests/test_hidden_behavior.py::test_totp_verify_rejects_wrong`

- mapping: `B001, B004`
- API: `featurelifted.TOTP`
- risk: `time_or_randomness`
- A001 `assert` L16: `totp.verify('000000', when) is False`

### `hidden_tests/test_hidden_behavior.py::test_hotp_counter_increments`

- mapping: `B002`
- API: `featurelifted.HOTP`
- risk: `none`
- A001 `assert` L21: `hotp.at(0) != hotp.at(1)`

### `hidden_tests/test_hidden_behavior.py::test_random_base32_length_guard`

- mapping: `B003`
- API: `featurelifted.random_base32`
- risk: `none`
- A001 `assert` L27: `False`

### `hidden_tests/test_hidden_behavior.py::test_no_upstream_import_surface`

- mapping: `B006`
- API: `featurelifted.__file__`
- risk: `filesystem_resource`
- A001 `assert` L38: `not pattern.search(path.read_text(encoding='utf-8'))`

### `hidden_tests/test_required_api_surface.py::test_required_api_surface`

- mapping: `B005`
- API: `featurelifted.HOTP, featurelifted.TOTP, featurelifted.random_base32`
- risk: `none`
- A001 `assert` L5: `TOTP is not None and HOTP is not None`
- A002 `assert` L6: `callable(random_base32)`

## Dependency / Oracle Evidence

- allowed dependencies: `none`
- forbidden imports: `pyotp`
- source entrypoints: `none`
- oracle source files: `pyotp/totp.py, pyotp/hotp.py, pyotp/__init__.py`
- runtime dependencies: `none`
- oracle notes: Direct TOTP/HOTP at/verify + random_base32.
- behavior contract lacks a completed review_status
- behavior contract schema_version missing or unsupported
