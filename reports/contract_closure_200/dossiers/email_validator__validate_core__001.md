# email_validator__validate_core__001

- release: `frozen_python150`
- lift: `Direct`
- coupling: `unknown`
- strict validation: `PASS`
- tests/assertions: `15/37`

## Required API

- `featurelifted.validate_email` (module)
- `featurelifted.ValidatedEmail` (class) `()`
- `featurelifted.EmailNotValidError` (exception)
- `featurelifted.EmailSyntaxError` (exception)
- `featurelifted.EmailUndeliverableError` (exception)

## Public Behaviors

- **B001**: The extracted feature must support this observable behavior: validate_email returns ValidatedEmail with normalized/local_part/domain fields. Required observable cases include validate basic ascii email; validate plus addressing; invalid empty local part; quoted local part dequoted; smtputf8 local part; domain literal ipv4.
- **B002**: The extracted feature must support this observable behavior: EmailSyntaxError and EmailNotValidError for invalid addresses. Required observable cases include invalid missing at sign; unicode nfc local part.
- **B003**: The extracted feature must support this observable behavior: IDNA domain encoding and internationalized local parts (SMTPUTF8). Required observable cases include idna domain normalization; smtputf8 local part.
- **B004**: The extracted feature must support this observable behavior: quoted local part parsing and de-quoting when allowed. Required observable cases include quoted local part dequoted.
- **B005**: The extracted feature must support this observable behavior: display name angle-bracket parsing when allowed. Required observable cases include display name parsing; test environment allows dot test.
- **B006**: The extracted feature must support this observable behavior: reserved/special-use domain rejection and test_environment bypass. Required observable cases include reserved domain rejected; test environment allows dot test; domain literal ipv4.
- **B007**: The extracted feature must support this observable behavior: case-insensitive mailbox names (e.g. POSTMASTER). Required observable cases include postmaster case insensitive.
- **B008**: The extracted feature must support this observable behavior: Unicode NFC normalization of local parts. Required observable cases include invalid empty local part; unicode nfc local part.
- **B009**: The package exposes the required task API paths `featurelifted.validate_email`, `featurelifted.ValidatedEmail`, `featurelifted.EmailNotValidError`, `featurelifted.EmailSyntaxError`, `featurelifted.EmailUndeliverableError` with the kinds and callable signatures listed in this contract.

## Tests

### `public_tests/test_public_api.py::test_validate_basic_ascii_email`

- mapping: `B001`
- API: `featurelifted.ValidatedEmail, featurelifted.validate_email`
- risk: `none`
- A001 `assert` L10: `isinstance(result, ValidatedEmail)`
- A002 `assert` L11: `result.normalized == 'user@example.com'`
- A003 `assert` L12: `result.local_part == 'user'`
- A004 `assert` L13: `result.domain == 'example.com'`
- A005 `assert` L14: `result.ascii_email == 'user@example.com'`

### `public_tests/test_public_api.py::test_validate_plus_addressing`

- mapping: `B001`
- API: `featurelifted.validate_email`
- risk: `none`
- A001 `assert` L19: `result.normalized == 'user+tag@example.org'`
- A002 `assert` L20: `result.local_part == 'user+tag'`

### `public_tests/test_public_api.py::test_invalid_missing_at_sign`

- mapping: `B002`
- API: `featurelifted.EmailNotValidError, featurelifted.EmailSyntaxError, featurelifted.validate_email`
- risk: `exception_semantics`
- A001 `raises` L24: `pytest.raises(EmailSyntaxError)`
- A002 `assert` L26: `'@' in str(exc_info.value)`
- A003 `assert` L27: `isinstance(exc_info.value, EmailNotValidError)`

### `public_tests/test_public_api.py::test_invalid_empty_local_part`

- mapping: `B001, B008`
- API: `featurelifted.EmailSyntaxError, featurelifted.validate_email`
- risk: `exception_semantics`
- A001 `raises` L31: `pytest.raises(EmailSyntaxError)`

### `hidden_tests/test_hidden_behavior.py::test_idna_domain_normalization`

- mapping: `B003`
- API: `featurelifted.validate_email`
- risk: `none`
- A001 `assert` L13: `result.domain == '臺網中心.tw'`
- A002 `assert` L14: `result.ascii_domain == 'xn--fiqq24b10vi0d.tw'`
- A003 `assert` L15: `result.normalized == 'jeff@臺網中心.tw'`
- A004 `assert` L16: `result.ascii_email == 'jeff@xn--fiqq24b10vi0d.tw'`

### `hidden_tests/test_hidden_behavior.py::test_quoted_local_part_dequoted`

- mapping: `B001, B004`
- API: `featurelifted.validate_email`
- risk: `none`
- A001 `assert` L25: `result.local_part == 'de-quoted.local.part'`
- A002 `assert` L26: `result.normalized == 'de-quoted.local.part@example.org'`

### `hidden_tests/test_hidden_behavior.py::test_display_name_parsing`

- mapping: `B005`
- API: `featurelifted.validate_email`
- risk: `none`
- A001 `assert` L35: `result.display_name == 'My Name'`
- A002 `assert` L36: `result.normalized == 'me@example.org'`
- A003 `assert` L37: `result.original == 'me@example.org'`

### `hidden_tests/test_hidden_behavior.py::test_postmaster_case_insensitive`

- mapping: `B007`
- API: `featurelifted.validate_email`
- risk: `none`
- A001 `assert` L42: `result.normalized == 'postmaster@test'`

### `hidden_tests/test_hidden_behavior.py::test_reserved_domain_rejected`

- mapping: `B006`
- API: `featurelifted.EmailSyntaxError, featurelifted.validate_email`
- risk: `exception_semantics`
- A001 `raises` L46: `pytest.raises(EmailSyntaxError)`
- A002 `assert` L48: `'special-use or reserved name' in str(exc_info.value)`

### `hidden_tests/test_hidden_behavior.py::test_test_environment_allows_dot_test`

- mapping: `B005, B006`
- API: `featurelifted.validate_email`
- risk: `none`
- A001 `assert` L53: `result.domain == 'mycompany.test'`

### `hidden_tests/test_hidden_behavior.py::test_unicode_nfc_local_part`

- mapping: `B002, B008`
- API: `featurelifted.validate_email`
- risk: `none`
- A001 `assert` L63: `result.local_part == 'ṩ'`
- A002 `assert` L64: `result.normalized == 'ṩ@nfc.tld'`

### `hidden_tests/test_hidden_behavior.py::test_smtputf8_local_part`

- mapping: `B001, B003`
- API: `featurelifted.validate_email`
- risk: `none`
- A001 `assert` L69: `result.smtputf8 is True`
- A002 `assert` L70: `result.ascii_email is None`
- A003 `assert` L71: `result.normalized == 'ñoñó@example.tld'`

### `hidden_tests/test_hidden_behavior.py::test_domain_literal_ipv4`

- mapping: `B001, B006`
- API: `featurelifted.validate_email`
- risk: `none`
- A001 `assert` L76: `result.domain == '[127.0.0.1]'`
- A002 `assert` L77: `repr(result.domain_address) == "IPv4Address('127.0.0.1')"`

### `hidden_tests/test_hidden_behavior.py::test_no_email_validator_import_surface`

- mapping: `B010`
- API: `featurelifted.__file__`
- risk: `filesystem_resource`
- A001 `assert` L87: `not import_pattern.search(text)`

### `hidden_tests/test_required_api_surface.py::test_required_api_surface`

- mapping: `B009`
- API: `featurelifted.EmailNotValidError, featurelifted.EmailSyntaxError, featurelifted.EmailUndeliverableError, featurelifted.ValidatedEmail, featurelifted.validate_email`
- risk: `none`
- A001 `assert` L13: `validate_email is not None`
- A002 `assert` L14: `isinstance(ValidatedEmail, type)`
- A003 `assert` L15: `issubclass(EmailNotValidError, BaseException)`
- A004 `assert` L16: `issubclass(EmailSyntaxError, BaseException)`
- A005 `assert` L17: `issubclass(EmailUndeliverableError, BaseException)`

## Dependency / Oracle Evidence

- allowed dependencies: `idna`
- forbidden imports: `email_validator, emailvalidator, dns`
- source entrypoints: `email_validator.validate_email, email_validator.ValidatedEmail, email_validator.EmailNotValidError, email_validator.EmailSyntaxError, email_validator.syntax, email_validator.rfc_constants`
- oracle source files: `email_validator/exceptions.py, email_validator/rfc_constants.py, email_validator/syntax.py, email_validator/types.py, email_validator/validate_email.py`
- runtime dependencies: `idna`
- oracle notes: Oracle copies offline syntax-validation closure only; excludes deliverability.py, CLI, and upstream tests.
