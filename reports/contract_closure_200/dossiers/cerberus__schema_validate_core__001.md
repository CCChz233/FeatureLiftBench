# cerberus__schema_validate_core__001

- release: `frozen_python150`
- lift: `Direct`
- coupling: `unknown`
- strict validation: `PASS`
- tests/assertions: `9/26`

## Required API

- `featurelifted.Validator` (class) `(*args, **kwargs)`
- `featurelifted.Validator.document` (attribute)
- `featurelifted.Validator.errors` (attribute)
- `featurelifted.Validator.validate` (method) `(self, document, schema=None, update=False, normalize=True)`
- `featurelifted.DocumentError` (exception)
- `featurelifted.SchemaError` (exception)

## Public Behaviors

- **B001**: The extracted feature must support this observable behavior: validate dict documents against nested schema definitions. Required observable cases include validate returns bool; nested schema validation; coerce updates document; deep nested schema and coerce combo.
- **B002**: The extracted feature must support this observable behavior: enforce required fields and type rules on nested mappings and lists. Required observable cases include required field rejects missing; type rule rejects wrong type; nested list error paths.
- **B003**: The extracted feature must support this observable behavior: coerce field values during validation and reflect coerced document. Required observable cases include coerce updates document.
- **B004**: The extracted feature must support this observable behavior: aggregate nested validation failures into structured error trees. Required observable cases include nested schema validation; nested list error paths.
- **B005**: The package exposes the required task API paths `featurelifted.Validator`, `featurelifted.Validator.document`, `featurelifted.Validator.errors`, `featurelifted.Validator.validate`, `featurelifted.DocumentError`, `featurelifted.SchemaError` with the kinds and callable signatures listed in this contract.

## Tests

### `public_tests/test_public_api.py::test_required_field_rejects_missing`

- mapping: `B002`
- API: `featurelifted.Validator`
- risk: `none`
- A001 `assert` L8: `validator.validate({'name': 'ada'})`
- A002 `assert` L9: `not validator.validate({})`
- A003 `assert` L10: `'name' in validator.errors`

### `public_tests/test_public_api.py::test_type_rule_rejects_wrong_type`

- mapping: `B002`
- API: `featurelifted.Validator`
- risk: `none`
- A001 `assert` L15: `validator.validate({'age': 3})`
- A002 `assert` L16: `not validator.validate({'age': 'three'})`

### `public_tests/test_public_api.py::test_validate_returns_bool`

- mapping: `B001`
- API: `featurelifted.Validator`
- risk: `none`
- A001 `assert` L21: `validator.validate({'active': True}) is True`
- A002 `assert` L22: `validator.validate({'active': 'yes'}) is False`

### `hidden_tests/test_hidden_behavior.py::test_nested_schema_validation`

- mapping: `B001, B004`
- API: `featurelifted.Validator`
- risk: `none`
- A001 `assert` L28: `validator.validate({'name': 'Ada', 'profile': {'city': 'Paris'}})`
- A002 `assert` L29: `not validator.validate({'name': 'Ada', 'profile': {}})`
- A003 `assert` L30: `validator.errors['profile'][0]['city'] == ['required field']`

### `hidden_tests/test_hidden_behavior.py::test_coerce_updates_document`

- mapping: `B001, B003`
- API: `featurelifted.Validator`
- risk: `state_mutation`
- A001 `assert` L40: `validator.validate({'count': '12', 'ratio': '0.5'})`
- A002 `assert` L41: `validator.document == {'count': 12, 'ratio': 0.5}`
- A003 `assert` L42: `not validator.validate({'count': 'nope', 'ratio': '0.5'})`
- A004 `assert` L43: `'count' in validator.errors`

### `hidden_tests/test_hidden_behavior.py::test_nested_list_error_paths`

- mapping: `B002, B004`
- API: `featurelifted.Validator`
- risk: `none`
- A001 `assert` L58: `not validator.validate({'items': [{'id': 'nope'}]})`
- A002 `assert` L60: `nested == ['must be of integer type']`

### `hidden_tests/test_hidden_behavior.py::test_deep_nested_schema_and_coerce_combo`

- mapping: `B001`
- API: `featurelifted.Validator`
- risk: `none`
- A001 `assert` L83: `not validator.validate(payload)`
- A002 `assert` L84: `validator.document['batch']['entries'][0]['qty'] == 2`
- A003 `assert` L86: `entry_errors == ['min value is 1']`

### `hidden_tests/test_hidden_behavior.py::test_no_cerberus_import_surface`

- mapping: `B006`
- API: `featurelifted.__file__`
- risk: `filesystem_resource`
- A001 `assert` L96: `not import_pattern.search(text)`

### `hidden_tests/test_required_api_surface.py::test_required_api_surface`

- mapping: `B005`
- API: `featurelifted.DocumentError, featurelifted.SchemaError, featurelifted.Validator`
- risk: `none`
- A001 `assert` L11: `isinstance(Validator, type)`
- A002 `assert` L12: `Validator is not None`
- A003 `assert` L13: `Validator is not None`
- A004 `assert` L14: `hasattr(Validator, 'validate')`
- A005 `assert` L15: `issubclass(DocumentError, BaseException)`
- A006 `assert` L16: `issubclass(SchemaError, BaseException)`

## Dependency / Oracle Evidence

- allowed dependencies: `none`
- forbidden imports: `cerberus`
- source entrypoints: `cerberus.Validator, cerberus.Validator.validate, cerberus.Validator.normalized, cerberus.Validator.document, cerberus.Validator.errors, cerberus.schema.DefinitionSchema, cerberus.errors.ValidationError, cerberus.errors.BasicErrorHandler`
- oracle source files: `cerberus/__init__.py, cerberus/platform.py, cerberus/utils.py, cerberus/errors.py, cerberus/schema.py, cerberus/validator.py`
- runtime dependencies: `none`
- oracle notes: Oracle copies the six-module validation core; excludes benchmarks and upstream tests. Copy-all baseline may include benchmark modules for extraction calibration.
