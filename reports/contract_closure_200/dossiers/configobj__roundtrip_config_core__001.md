# configobj__roundtrip_config_core__001

- release: `frozen_python150`
- lift: `Direct`
- coupling: `unknown`
- strict validation: `PASS`
- tests/assertions: `10/24`

## Required API

- `featurelifted.ConfigObj` (class) `(infile=None, options=None, configspec=None, encoding=None, interpolation=True, raise_errors=False, list_values=True, create_empty=False, file_error=False, stringify=True, indent_type=None, default_encoding=None, unrepr=False, write_empty_values=False, _inspec=False)`
- `featurelifted.ConfigObj.validate` (method) `(self, validator, preserve_errors=False, copy=False, section=None)`
- `featurelifted.ConfigObj.write` (method) `(self, outfile=None, section=None)`
- `featurelifted.DuplicateError` (exception)
- `featurelifted.flatten_errors` (function) `(cfg, res, levels=None, results=None)`
- `featurelifted.get_extra_values` (function) `(conf, _prepend=())`
- `featurelifted.validate` (module)
- `featurelifted.validate.Validator` (class) `(functions=None)`
- `featurelifted.validate.VdtValueTooSmallError` (exception)

## Public Behaviors

- **B001**: The extracted feature must support this observable behavior: parse INI-like config from strings with nested sections. Required observable cases include parse sections and values; no configobj import surface.
- **B002**: The extracted feature must support this observable behavior: write configs preserving comments and key order metadata. Required observable cases include write roundtrip keys; scalar order metadata; comment preserved on write.
- **B003**: The extracted feature must support this observable behavior: validate values against configspec via Validator. Required observable cases include configspec validation failure flattened; get extra values from configspec.
- **B004**: The extracted feature must support this observable behavior: report validation failures with flatten_errors. Required observable cases include configspec validation failure flattened.
- **B005**: The extracted feature must support this observable behavior: detect duplicate sections and parse errors. Required observable cases include parse sections and values; duplicate section raises.
- **B006**: The package exposes the required task API paths `featurelifted.ConfigObj`, `featurelifted.ConfigObj.validate`, `featurelifted.ConfigObj.write`, `featurelifted.DuplicateError`, `featurelifted.flatten_errors`, `featurelifted.get_extra_values`, `featurelifted.validate`, `featurelifted.validate.Validator`, `featurelifted.validate.VdtValueTooSmallError` with the kinds and callable signatures listed in this contract.

## Tests

### `public_tests/test_public_api.py::test_parse_sections_and_values`

- mapping: `B001, B005`
- API: `featurelifted.ConfigObj`
- risk: `none`
- A001 `assert` L17: `conf['title'] == 'FeatureLift'`
- A002 `assert` L18: `conf['owner']['name'] == 'Ada'`

### `public_tests/test_public_api.py::test_write_roundtrip_keys`

- mapping: `B002`
- API: `featurelifted.ConfigObj`
- risk: `none`
- A001 `assert` L29: `again['alpha'] == '1'`
- A002 `assert` L30: `again['beta'] == '2'`
- A003 `assert` L31: `again['group']['inner'] == 'x'`

### `public_tests/test_public_api.py::test_scalar_order_metadata`

- mapping: `B002`
- API: `featurelifted.ConfigObj`
- risk: `ordering_semantics`
- A001 `assert` L38: `conf.scalars == ['z', 'a']`

### `hidden_tests/test_hidden_behavior.py::test_comment_preserved_on_write`

- mapping: `B002`
- API: `featurelifted.ConfigObj, featurelifted.validate`
- risk: `none`
- A001 `assert` L22: `'# banner' in out`
- A002 `assert` L23: `'name = Ada' in out`

### `hidden_tests/test_hidden_behavior.py::test_configspec_validation_failure_flattened`

- mapping: `B003, B004`
- API: `featurelifted.ConfigObj, featurelifted.flatten_errors, featurelifted.validate`
- risk: `none`
- A001 `assert` L32: `result is False`
- A002 `assert` L34: `flat`
- A003 `assert` L35: `any((item[2] is False for item in flat))`

### `hidden_tests/test_hidden_behavior.py::test_duplicate_section_raises`

- mapping: `B005`
- API: `featurelifted.ConfigObj, featurelifted.DuplicateError, featurelifted.validate`
- risk: `exception_semantics`
- A001 `raises` L47: `pytest.raises(DuplicateError)`

### `hidden_tests/test_hidden_behavior.py::test_get_extra_values_from_configspec`

- mapping: `B003`
- API: `featurelifted.ConfigObj, featurelifted.get_extra_values, featurelifted.validate`
- risk: `none`
- A001 `assert` L64: `'extra' in names`

### `hidden_tests/test_hidden_behavior.py::test_configparser_interpolation_resolves`

- mapping: `B006`
- API: `featurelifted.ConfigObj, featurelifted.validate`
- risk: `none`
- A001 `assert` L75: `conf['greeting'] == 'Hello World'`

### `hidden_tests/test_hidden_behavior.py::test_no_configobj_import_surface`

- mapping: `B001, B007`
- API: `featurelifted.__file__, featurelifted.validate`
- risk: `filesystem_resource`
- A001 `assert` L85: `not import_pattern.search(text)`

### `hidden_tests/test_required_api_surface.py::test_required_api_surface`

- mapping: `B006`
- API: `featurelifted.ConfigObj, featurelifted.DuplicateError, featurelifted.flatten_errors, featurelifted.get_extra_values, featurelifted.validate`
- risk: `none`
- A001 `assert` L13: `isinstance(ConfigObj, type)`
- A002 `assert` L14: `hasattr(ConfigObj, 'validate')`
- A003 `assert` L15: `hasattr(ConfigObj, 'write')`
- A004 `assert` L16: `issubclass(DuplicateError, BaseException)`
- A005 `assert` L17: `callable(flatten_errors)`
- A006 `assert` L18: `callable(get_extra_values)`
- A007 `assert` L19: `validate is not None`
- A008 `assert` L20: `isinstance(getattr(validate, 'Validator'), type)`
- A009 `assert` L21: `issubclass(getattr(validate, 'VdtValueTooSmallError'), BaseException)`

## Dependency / Oracle Evidence

- allowed dependencies: `none`
- forbidden imports: `configobj`
- source entrypoints: `configobj.ConfigObj, configobj.validate.Validator, configobj.flatten_errors, configobj.get_extra_values`
- oracle source files: `configobj/__init__.py, configobj/validate.py, configobj/_version.py`
- runtime dependencies: `none`
- oracle notes: Oracle splits __init__.py into core/errors/interpolation modules plus validate.py.
