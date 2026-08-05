# Contract V2 P0: email_validator__validate_core__001

- release: `frozen_python150`
- lift: `Direct`
- coupling: `unknown`
- strict validation: `PASS`
- tests/assertions: `15/45`

## Required API

- `featurelifted.validate_email` (function) `(email: str | bytes, /, *, allow_smtputf8: Optional[bool] = None, allow_empty_local: Optional[bool] = None, allow_quoted_local: Optional[bool] = None, allow_domain_literal: Optional[bool] = None, allow_display_name: Optional[bool] = None, strict: Optional[bool] = None, check_deliverability: Optional[bool] = None, test_environment: Optional[bool] = None, globally_deliverable: Optional[bool] = None, timeout: Optional[int] = None, dns_resolver: Optional[Any] = None) -> ValidatedEmail`
- `featurelifted.ValidatedEmail` (class) `()`
- `featurelifted.ValidatedEmail.ascii_email` (attribute)
- `featurelifted.ValidatedEmail.domain` (attribute)
- `featurelifted.ValidatedEmail.local_part` (attribute)
- `featurelifted.ValidatedEmail.normalized` (attribute)
- `featurelifted.ValidatedEmail.ascii_domain` (attribute)
- `featurelifted.ValidatedEmail.display_name` (attribute)
- `featurelifted.ValidatedEmail.original` (attribute)
- `featurelifted.ValidatedEmail.smtputf8` (attribute)
- `featurelifted.ValidatedEmail.domain_address` (attribute)
- `featurelifted.EmailNotValidError` (exception)
- `featurelifted.EmailSyntaxError` (exception)

## Public Behaviors

- **B001**: The extracted feature must support this observable behavior: validate_email returns ValidatedEmail with normalized/local_part/domain fields. Required observable cases include validate basic ascii email; validate plus addressing; invalid empty local part; quoted local part dequoted; smtputf8 local part; domain literal ipv4.
- **B002**: The extracted feature must support this observable behavior: EmailSyntaxError and EmailNotValidError for invalid addresses. Required observable cases include invalid missing at sign; unicode nfc local part.
- **B003**: The extracted feature must support this observable behavior: IDNA domain encoding and internationalized local parts (SMTPUTF8). Required observable cases include idna domain normalization; smtputf8 local part.
- **B004**: The extracted feature must support this observable behavior: quoted local part parsing and de-quoting when allowed. Required observable cases include quoted local part dequoted.
- **B005**: The extracted feature must support this observable behavior: display name angle-bracket parsing when allowed. Required observable cases include display name parsing; test environment allows dot test.
- **B006**: The extracted feature must support this observable behavior: reserved/special-use domain rejection and test_environment bypass. Required observable cases include reserved domain rejected; test environment allows dot test; domain literal ipv4.
- **B007**: The extracted feature must support this observable behavior: case-insensitive mailbox names (e.g. POSTMASTER). Required observable cases include postmaster case insensitive.
- **B008**: Unicode local parts are normalized to NFC before ValidatedEmail.local_part and normalized are returned.
- **B009**: The package exposes the required task API paths `featurelifted.validate_email`, `featurelifted.ValidatedEmail`, `featurelifted.ValidatedEmail.ascii_email`, `featurelifted.ValidatedEmail.domain`, `featurelifted.ValidatedEmail.local_part`, `featurelifted.ValidatedEmail.normalized`, `featurelifted.ValidatedEmail.ascii_domain`, `featurelifted.ValidatedEmail.display_name`, `featurelifted.ValidatedEmail.original`, `featurelifted.ValidatedEmail.smtputf8`, `featurelifted.ValidatedEmail.domain_address`, `featurelifted.EmailNotValidError`, and 1 listed members with the kinds and callable signatures listed in this contract.

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

- mapping: `B002`
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

- mapping: `B002, B006`
- API: `featurelifted.EmailSyntaxError, featurelifted.validate_email`
- risk: `exception_semantics`
- A001 `raises` L46: `pytest.raises(EmailSyntaxError)`
- A002 `assert` L48: `'special-use or reserved name' in str(exc_info.value)`

### `hidden_tests/test_hidden_behavior.py::test_test_environment_allows_dot_test`

- mapping: `B006`
- API: `featurelifted.validate_email`
- risk: `none`
- A001 `assert` L53: `result.domain == 'mycompany.test'`

### `hidden_tests/test_hidden_behavior.py::test_unicode_nfc_local_part`

- mapping: `B008`
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
- API: `featurelifted.EmailNotValidError, featurelifted.EmailSyntaxError, featurelifted.ValidatedEmail, featurelifted.validate_email`
- risk: `none`
- A001 `assert` L12: `callable(validate_email)`
- A002 `assert` L13: `isinstance(ValidatedEmail, type)`
- A003 `assert` L14: `ValidatedEmail is not None`
- A004 `assert` L15: `ValidatedEmail is not None`
- A005 `assert` L16: `ValidatedEmail is not None`
- A006 `assert` L17: `ValidatedEmail is not None`
- A007 `assert` L18: `ValidatedEmail is not None`
- A008 `assert` L19: `ValidatedEmail is not None`
- A009 `assert` L20: `ValidatedEmail is not None`
- A010 `assert` L21: `ValidatedEmail is not None`
- A011 `assert` L22: `ValidatedEmail is not None`
- A012 `assert` L23: `issubclass(EmailNotValidError, BaseException)`
- A013 `assert` L24: `issubclass(EmailSyntaxError, BaseException)`

## Dependency / Oracle Evidence

- allowed dependencies: `idna`
- forbidden imports: `email_validator, emailvalidator, dns`
- source entrypoints: `email_validator.validate_email, email_validator.ValidatedEmail, email_validator.EmailNotValidError, email_validator.EmailSyntaxError, email_validator.syntax, email_validator.rfc_constants`
- oracle source files: `email_validator/exceptions.py, email_validator/rfc_constants.py, email_validator/syntax.py, email_validator/types.py, email_validator/validate_email.py`
- runtime dependencies: `idna`
- oracle notes: Oracle copies offline syntax-validation closure only; excludes deliverability.py, CLI, and upstream tests.
