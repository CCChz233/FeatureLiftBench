# jsonschema__validator_core__001

- release: `frozen_python150`
- lift: `Direct`
- coupling: `unknown`
- strict validation: `PASS`
- tests/assertions: `6/27`

## Required API

- `featurelifted.Draft202012Validator` (class) `(schema: 'referencing.jsonschema.Schema', resolver=None, format_checker: '_format.FormatChecker | None' = None, *, registry: 'referencing.jsonschema.SchemaRegistry' = <Registry (20 resources)>, _resolver=None) -> None`
- `featurelifted.Draft202012Validator.check_schema` (method) `(schema, format_checker=<unset>)`
- `featurelifted.Draft202012Validator.is_valid` (method) `(self, instance, _schema=None)`
- `featurelifted.Draft202012Validator.iter_errors` (method) `(self, instance, _schema=None)`
- `featurelifted.validate` (function) `(instance, schema, cls=None, *args, **kwargs)`
- `featurelifted.ValidationError` (exception)
- `featurelifted.SchemaError` (exception)
- `featurelifted.FormatChecker` (class) `(formats: 'typing.Iterable[str] | None' = None)`

## Public Behaviors

- **B001**: The extracted feature must support this observable behavior: validate object, array, string, integer, number, boolean, and null types. Required observable cases include validate object required properties and minimum; oneof and const keyword.
- **B002**: The extracted feature must support this observable behavior: support required, properties, additionalProperties, minimum, minLength, pattern, enum, anyOf, oneOf, and allOf. Required observable cases include validate object required properties and minimum; oneof and const keyword.
- **B003**: The extracted feature must support this observable behavior: iterate ValidationError objects with path, schema_path, validator, validator_value, and message. Required observable cases include iter errors exposes paths and validity; nested errors paths combinators and messages.
- **B004**: The extracted feature must support this observable behavior: perform format validation when a FormatChecker is provided. Required observable cases include format checker schema errors and additional properties.
- **B005**: The extracted feature must support this observable behavior: validate schemas and raise SchemaError for invalid schemas. Required observable cases include format checker schema errors and additional properties.
- **B006**: The package exposes the required task API paths `featurelifted.Draft202012Validator`, `featurelifted.Draft202012Validator.check_schema`, `featurelifted.Draft202012Validator.is_valid`, `featurelifted.Draft202012Validator.iter_errors`, `featurelifted.validate`, `featurelifted.ValidationError`, `featurelifted.SchemaError`, `featurelifted.FormatChecker` with the kinds and callable signatures listed in this contract.

## Tests

### `public_tests/test_public_api.py::test_validate_object_required_properties_and_minimum`

- mapping: `B001, B002`
- API: `featurelifted.ValidationError, featurelifted.validate`
- risk: `exception_semantics`
- A001 `raises` L23: `pytest.raises(ValidationError)`
- A002 `assert` L26: `excinfo.value.validator in {'required', 'minimum', 'additionalProperties'}`

### `public_tests/test_public_api.py::test_iter_errors_exposes_paths_and_validity`

- mapping: `B003`
- API: `featurelifted.Draft202012Validator`
- risk: `none`
- A001 `assert` L40: `not validator.is_valid({'age': -1})`
- A002 `assert` L41: `validator.is_valid({'age': 1})`
- A003 `assert` L42: `len(errors) == 1`
- A004 `assert` L43: `list(errors[0].path) == ['age']`
- A005 `assert` L44: `errors[0].validator == 'minimum'`

### `hidden_tests/test_hidden_behavior.py::test_nested_errors_paths_combinators_and_messages`

- mapping: `B003`
- API: `featurelifted.Draft202012Validator`
- risk: `none`
- A001 `assert` L38: `[(list(error.path), error.validator) for error in errors] == [(['items', 0, 'kind'], 'enum'), (['items', 0, 'rating'], 'anyOf')]`
- A002 `assert` L42: `'album' in errors[0].message`

### `hidden_tests/test_hidden_behavior.py::test_format_checker_schema_errors_and_additional_properties`

- mapping: `B004, B005`
- API: `featurelifted.Draft202012Validator, featurelifted.Draft202012Validator.check_schema, featurelifted.FormatChecker, featurelifted.SchemaError, featurelifted.ValidationError, featurelifted.validate`
- risk: `exception_semantics`
- A001 `raises` L46: `pytest.raises(ValidationError)`
- A002 `assert` L56: `list(excinfo.value.path) == ['email']`
- A003 `assert` L57: `excinfo.value.validator == 'format'`
- A004 `assert` L67: `len(errors) == 1`
- A005 `assert` L68: `errors[0].validator == 'additionalProperties'`
- A006 `assert` L69: `'extra' in errors[0].message`
- A007 `raises` L71: `pytest.raises(SchemaError)`

### `hidden_tests/test_hidden_behavior.py::test_oneof_and_const_keyword`

- mapping: `B001, B002`
- API: `featurelifted.Draft202012Validator`
- risk: `none`
- A001 `assert` L83: `validator.is_valid('yes')`
- A002 `assert` L84: `not validator.is_valid('maybe')`
- A003 `assert` L86: `errors and errors[0].validator == 'oneOf'`

### `hidden_tests/test_required_api_surface.py::test_required_api_surface`

- mapping: `B006`
- API: `featurelifted.Draft202012Validator, featurelifted.FormatChecker, featurelifted.SchemaError, featurelifted.ValidationError, featurelifted.validate`
- risk: `none`
- A001 `assert` L13: `isinstance(Draft202012Validator, type)`
- A002 `assert` L14: `hasattr(Draft202012Validator, 'check_schema')`
- A003 `assert` L15: `hasattr(Draft202012Validator, 'is_valid')`
- A004 `assert` L16: `hasattr(Draft202012Validator, 'iter_errors')`
- A005 `assert` L17: `callable(validate)`
- A006 `assert` L18: `issubclass(ValidationError, BaseException)`
- A007 `assert` L19: `issubclass(SchemaError, BaseException)`
- A008 `assert` L20: `isinstance(FormatChecker, type)`

## Dependency / Oracle Evidence

- allowed dependencies: `attrs, jsonschema-specifications, referencing, rpds-py`
- forbidden imports: `jsonschema`
- source entrypoints: `jsonschema.Draft202012Validator, jsonschema.validate, jsonschema.ValidationError, jsonschema.SchemaError, jsonschema.FormatChecker`
- oracle source files: `none`
- runtime dependencies: `none`
