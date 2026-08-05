# voluptuous__schema_validate_core__001

- release: `frozen_python150`
- lift: `Direct`
- coupling: `unknown`
- strict validation: `PASS`
- tests/assertions: `8/23`

## Required API

- `featurelifted.Schema` (class) `(schema: 'Schemable', required: 'bool' = False, extra: 'int' = 0) -> 'None'`
- `featurelifted.Required` (class) `(schema: 'Schemable', msg: 'typing.Optional[str]' = None, default: 'typing.Any' = ..., description: 'typing.Any | None' = None) -> 'None'`
- `featurelifted.Optional` (class) `(schema: 'Schemable', msg: 'typing.Optional[str]' = None, default: 'typing.Any' = ..., description: 'typing.Any | None' = None) -> 'None'`
- `featurelifted.All` (class) `(*validators, msg=None, required=False, discriminant=None, **kwargs) -> 'None'`
- `featurelifted.Any` (class) `(*validators, msg=None, required=False, discriminant=None, **kwargs) -> 'None'`
- `featurelifted.In` (class) `(container: 'typing.Container | typing.Iterable', msg: 'typing.Optional[str]' = None) -> 'None'`
- `featurelifted.Coerce` (class) `(type: 'typing.Union[type, typing.Callable]', msg: 'typing.Optional[str]' = None) -> 'None'`
- `featurelifted.Invalid` (exception)
- `featurelifted.MultipleInvalid` (exception)
- `featurelifted.SchemaError` (exception)

## Public Behaviors

- **B001**: The extracted feature must support this observable behavior: declare Schema with Required and Optional markers. Required observable cases include schema required field; optional missing key; nested schema validation.
- **B002**: The extracted feature must support this observable behavior: validate dict payloads with type and nested schema matching. Required observable cases include basic type validation; nested schema validation.
- **B003**: The extracted feature must support this observable behavior: compose All, Any, and In validators with Coerce. Required observable cases include all any in and coerce.
- **B004**: The extracted feature must support this observable behavior: aggregate validation failures as MultipleInvalid with error paths. Required observable cases include basic type validation; multiple invalid error paths.
- **B005**: The package exposes the required task API paths `featurelifted.Schema`, `featurelifted.Required`, `featurelifted.Optional`, `featurelifted.All`, `featurelifted.Any`, `featurelifted.In`, `featurelifted.Coerce`, `featurelifted.Invalid`, `featurelifted.MultipleInvalid`, `featurelifted.SchemaError` with the kinds and callable signatures listed in this contract.

## Tests

### `public_tests/test_public_api.py::test_schema_required_field`

- mapping: `B001`
- API: `featurelifted.MultipleInvalid, featurelifted.Required, featurelifted.Schema`
- risk: `exception_semantics`
- A001 `assert` L10: `schema({'name': 'ada'}) == {'name': 'ada'}`
- A002 `raises` L11: `pytest.raises(MultipleInvalid)`

### `public_tests/test_public_api.py::test_optional_missing_key`

- mapping: `B001`
- API: `featurelifted.Optional, featurelifted.Schema`
- risk: `none`
- A001 `assert` L17: `schema({}) == {}`

### `public_tests/test_public_api.py::test_basic_type_validation`

- mapping: `B002, B004`
- API: `featurelifted.MultipleInvalid, featurelifted.Schema`
- risk: `exception_semantics`
- A001 `assert` L22: `schema({'name': 'ada', 'age': 3}) == {'name': 'ada', 'age': 3}`
- A002 `raises` L23: `pytest.raises(MultipleInvalid)`

### `hidden_tests/test_hidden_behavior.py::test_nested_schema_validation`

- mapping: `B001, B002`
- API: `featurelifted.MultipleInvalid, featurelifted.Required, featurelifted.Schema`
- risk: `exception_semantics`
- A001 `assert` L15: `result['profile']['city'] == 'Paris'`
- A002 `raises` L17: `pytest.raises(MultipleInvalid)`

### `hidden_tests/test_hidden_behavior.py::test_all_any_in_and_coerce`

- mapping: `B003`
- API: `featurelifted.All, featurelifted.Any, featurelifted.Coerce, featurelifted.In, featurelifted.MultipleInvalid, featurelifted.Required, featurelifted.Schema`
- risk: `exception_semantics`
- A001 `assert` L34: `schema({'mode': 'alpha', 'count': '3', 'color': 'red'}) == {'mode': 'alpha', 'count': 3, 'color': 'red'}`
- A002 `raises` L40: `pytest.raises(MultipleInvalid)`

### `hidden_tests/test_hidden_behavior.py::test_multiple_invalid_error_paths`

- mapping: `B004`
- API: `featurelifted.MultipleInvalid, featurelifted.Required, featurelifted.Schema`
- risk: `exception_semantics`
- A001 `raises` L47: `pytest.raises(MultipleInvalid)`
- A002 `assert` L50: `len(err.errors) >= 1`
- A003 `assert` L51: `err.errors[0].path == ['items', 0, 'id']`

### `hidden_tests/test_hidden_behavior.py::test_no_voluptuous_import_surface`

- mapping: `B006`
- API: `featurelifted.__file__`
- risk: `filesystem_resource`
- A001 `assert` L61: `not import_pattern.search(text)`

### `hidden_tests/test_required_api_surface.py::test_required_api_surface`

- mapping: `B005`
- API: `featurelifted.All, featurelifted.Any, featurelifted.Coerce, featurelifted.In, featurelifted.Invalid, featurelifted.MultipleInvalid, featurelifted.Optional, featurelifted.Required, featurelifted.Schema, featurelifted.SchemaError`
- risk: `none`
- A001 `assert` L18: `isinstance(Schema, type)`
- A002 `assert` L19: `isinstance(Required, type)`
- A003 `assert` L20: `isinstance(Optional, type)`
- A004 `assert` L21: `isinstance(All, type)`
- A005 `assert` L22: `isinstance(Any, type)`
- A006 `assert` L23: `isinstance(In, type)`
- A007 `assert` L24: `isinstance(Coerce, type)`
- A008 `assert` L25: `issubclass(Invalid, BaseException)`
- A009 `assert` L26: `issubclass(MultipleInvalid, BaseException)`
- A010 `assert` L27: `issubclass(SchemaError, BaseException)`

## Dependency / Oracle Evidence

- allowed dependencies: `none`
- forbidden imports: `voluptuous`
- source entrypoints: `voluptuous.Schema, voluptuous.Required, voluptuous.Optional, voluptuous.validators.All, voluptuous.validators.Any, voluptuous.validators.In, voluptuous.validators.Coerce, voluptuous.error.MultipleInvalid`
- oracle source files: `voluptuous/__init__.py, voluptuous/error.py, voluptuous/schema_builder.py, voluptuous/util.py, voluptuous/validators.py`
- runtime dependencies: `none`
- oracle notes: Oracle omits humanize.py and trims validators to Coerce/All/Any/In; excludes Email/Url/File validators.
