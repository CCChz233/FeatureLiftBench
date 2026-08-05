# phonenumbers__parse_format_core__001

- release: `frozen_python150`
- lift: `Direct`
- coupling: `unknown`
- strict validation: `FAIL`
- tests/assertions: `6/16`

## Required API

- `featurelifted.PhoneNumberFormat` (class) `()`
- `featurelifted.PhoneNumberFormat.E164` (attribute)
- `featurelifted.NumberParseException` (exception)
- `featurelifted.format_number` (function) `(numobj, num_format)`
- `featurelifted.is_valid_number` (function) `(numobj)`
- `featurelifted.parse` (function) `(number, region=None, keep_raw_input=False, numobj=None, _check_region=True)`
- `featurelifted.phonenumberutil` (module)
- `featurelifted.phonenumberutil.NumberParseException` (exception)

## Public Behaviors

- **B001**: The extracted feature must support this observable behavior: parse E.164 and national numbers for US and GB. Required observable cases include parse e164 and format; parse national us; gb national equals e164 parse; is valid and e164 us.
- **B002**: The extracted feature must support this observable behavior: format NATIONAL, INTERNATIONAL, and E164. Required observable cases include parse e164 and format; is valid and e164 us.
- **B003**: The extracted feature must support this observable behavior: validate numbers against region metadata. Required observable cases include invalid region raises.
- **B004**: The package exposes the required task API paths `featurelifted.PhoneNumberFormat`, `featurelifted.PhoneNumberFormat.E164`, `featurelifted.NumberParseException`, `featurelifted.format_number`, `featurelifted.is_valid_number`, `featurelifted.parse`, `featurelifted.phonenumberutil`, `featurelifted.phonenumberutil.NumberParseException` with the kinds and callable signatures listed in this contract.

## Tests

### `public_tests/test_public_api.py::test_parse_e164_and_format`

- mapping: `B001, B002`
- API: `featurelifted.PhoneNumberFormat, featurelifted.PhoneNumberFormat.E164, featurelifted.PhoneNumberFormat.INTERNATIONAL, featurelifted.format_number, featurelifted.parse`
- risk: `none`
- A001 `assert` L8: `format_number(num, PhoneNumberFormat.E164) == '+442083661177'`
- A002 `assert` L9: `'+44' in format_number(num, PhoneNumberFormat.INTERNATIONAL)`

### `public_tests/test_public_api.py::test_parse_national_us`

- mapping: `B001`
- API: `featurelifted.PhoneNumberFormat, featurelifted.PhoneNumberFormat.NATIONAL, featurelifted.format_number, featurelifted.parse`
- risk: `none`
- A001 `assert` L14: `format_number(num, PhoneNumberFormat.NATIONAL).startswith('(202)')`

### `hidden_tests/test_hidden_behavior.py::test_gb_national_equals_e164_parse`

- mapping: `B001`
- API: `featurelifted.parse, featurelifted.phonenumberutil`
- risk: `none`
- A001 `assert` L12: `a.country_code == b.country_code == 44`
- A002 `assert` L13: `a.national_number == b.national_number`

### `hidden_tests/test_hidden_behavior.py::test_invalid_region_raises`

- mapping: `B003`
- API: `featurelifted.parse, featurelifted.phonenumberutil`
- risk: `exception_semantics`
- A001 `raises` L17: `pytest.raises(NumberParseException)`

### `hidden_tests/test_hidden_behavior.py::test_is_valid_and_e164_us`

- mapping: `B001, B002`
- API: `featurelifted.PhoneNumberFormat, featurelifted.PhoneNumberFormat.E164, featurelifted.format_number, featurelifted.is_valid_number, featurelifted.parse, featurelifted.phonenumberutil`
- risk: `none`
- A001 `assert` L23: `is_valid_number(num)`
- A002 `assert` L24: `format_number(num, PhoneNumberFormat.E164) == '+12025550123'`

### `hidden_tests/test_required_api_surface.py::test_required_api_surface`

- mapping: `B004`
- API: `featurelifted.NumberParseException, featurelifted.PhoneNumberFormat, featurelifted.format_number, featurelifted.is_valid_number, featurelifted.parse, featurelifted.phonenumberutil`
- risk: `none`
- A001 `assert` L14: `isinstance(PhoneNumberFormat, type)`
- A002 `assert` L15: `PhoneNumberFormat is not None`
- A003 `assert` L16: `issubclass(NumberParseException, BaseException)`
- A004 `assert` L17: `callable(format_number)`
- A005 `assert` L18: `callable(is_valid_number)`
- A006 `assert` L19: `callable(parse)`
- A007 `assert` L20: `phonenumberutil is not None`
- A008 `assert` L21: `issubclass(getattr(phonenumberutil, 'NumberParseException'), BaseException)`

## Dependency / Oracle Evidence

- allowed dependencies: `none`
- forbidden imports: `phonenumbers`
- source entrypoints: `phonenumbers.parse, phonenumbers.format_number, phonenumbers.PhoneNumberFormat, phonenumbers.is_valid_number, phonenumbers.phonenumberutil`
- oracle source files: `none`
- runtime dependencies: `none`
- oracle notes: Oracle uses core util modules plus trimmed US/GB metadata; repo keeps full geodata for copy-all.

## Machine Issues

- public_tests/test_public_api.py uses undeclared API reference featurelifted.PhoneNumberFormat.INTERNATIONAL
- public_tests/test_public_api.py uses undeclared API reference featurelifted.PhoneNumberFormat.NATIONAL
