# marshmallow__schema_core__001

- release: `frozen_python150`
- lift: `Direct`
- coupling: `unknown`
- strict validation: `FAIL`
- tests/assertions: `4/18`

## Required API

- `featurelifted.Schema` (class) `(*, only: 'types.StrSequenceOrSet | None' = None, exclude: 'types.StrSequenceOrSet' = (), many: 'bool | None' = None, load_only: 'types.StrSequenceOrSet' = (), dump_only: 'types.StrSequenceOrSet' = (), partial: 'bool | types.StrSequenceOrSet | None' = None, unknown: 'types.UnknownOption | None' = None)`
- `featurelifted.Schema.load` (method) `(self, data: 'Mapping[str, typing.Any] | Sequence[Mapping[str, typing.Any]]', *, many: 'bool | None' = None, partial: 'bool | types.StrSequenceOrSet | None' = None, unknown: 'types.UnknownOption | None' = None)`
- `featurelifted.fields` (module)
- `featurelifted.ValidationError` (exception)
- `featurelifted.EXCLUDE` (constant)
- `featurelifted.RAISE` (constant)
- `featurelifted.decorators` (module)
- `featurelifted.decorators.post_load` (function) `(fn: 'typing.Callable[..., typing.Any] | None' = None, *, pass_collection: 'bool' = False, pass_original: 'bool' = False) -> 'typing.Callable[..., typing.Any]'`
- `featurelifted.decorators.validates_schema` (function) `(fn: 'typing.Callable[..., typing.Any] | None' = None, *, pass_collection: 'bool' = False, pass_original: 'bool' = False, skip_on_field_errors: 'bool' = True) -> 'typing.Callable[..., typing.Any]'`

## Public Behaviors

- **B001**: The extracted feature must support this observable behavior: declare Schema subclasses with typed fields. Required observable cases include unknown exclude post load and nested errors.
- **B002**: The extracted feature must support this observable behavior: load dict payloads with validation and nested schemas. Required observable cases include load dump nested schema; unknown exclude post load and nested errors.
- **B003**: The extracted feature must support this observable behavior: dump objects to dicts with field selection. Required observable cases include unknown exclude post load and nested errors.
- **B004**: The extracted feature must support this observable behavior: handle unknown=EXCLUDE and partial load validation errors. Required observable cases include unknown exclude post load and nested errors; many dump partial and raise unknown.
- **B005**: The package exposes the required task API paths `featurelifted.Schema`, `featurelifted.Schema.load`, `featurelifted.fields`, `featurelifted.ValidationError`, `featurelifted.EXCLUDE`, `featurelifted.RAISE`, `featurelifted.decorators`, `featurelifted.decorators.post_load`, `featurelifted.decorators.validates_schema` with the kinds and callable signatures listed in this contract.

## Tests

### `public_tests/test_public_api.py::test_load_dump_nested_schema`

- mapping: `B002`
- API: `featurelifted.ValidationError`
- risk: `exception_semantics`
- A001 `assert` L21: `loaded['profile']['city'] == 'Paris'`
- A002 `assert` L23: `dumped['name'] == 'Ada'`
- A003 `raises` L25: `pytest.raises(ValidationError)`

### `hidden_tests/test_hidden_behavior.py::test_unknown_exclude_post_load_and_nested_errors`

- mapping: `B001, B002, B003, B004`
- API: `featurelifted.ValidationError, featurelifted.decorators`
- risk: `exact_error_text, exception_semantics`
- A001 `assert` L40: `loaded['total_qty'] == 3`
- A002 `assert` L41: `'extra' not in loaded`
- A003 `raises` L43: `pytest.raises(ValidationError)`
- A004 `assert` L45: `'qty' in str(excinfo.value.messages)`

### `hidden_tests/test_hidden_behavior.py::test_many_dump_partial_and_raise_unknown`

- mapping: `B004`
- API: `featurelifted.RAISE, featurelifted.Schema, featurelifted.ValidationError, featurelifted.decorators, featurelifted.fields, featurelifted.fields.Str`
- risk: `exception_semantics`
- A001 `raises` L56: `pytest.raises(ValidationError)`
- A002 `assert` L61: `dumped == [{'name': 'a'}, {'name': 'b'}]`

### `hidden_tests/test_required_api_surface.py::test_required_api_surface`

- mapping: `B005`
- API: `featurelifted.EXCLUDE, featurelifted.RAISE, featurelifted.Schema, featurelifted.ValidationError, featurelifted.decorators, featurelifted.fields`
- risk: `none`
- A001 `assert` L14: `isinstance(Schema, type)`
- A002 `assert` L15: `hasattr(Schema, 'load')`
- A003 `assert` L16: `fields is not None`
- A004 `assert` L17: `issubclass(ValidationError, BaseException)`
- A005 `assert` L18: `EXCLUDE is not None`
- A006 `assert` L19: `RAISE is not None`
- A007 `assert` L20: `decorators is not None`
- A008 `assert` L21: `callable(getattr(decorators, 'post_load'))`
- A009 `assert` L22: `callable(getattr(decorators, 'validates_schema'))`

## Dependency / Oracle Evidence

- allowed dependencies: `none`
- forbidden imports: `marshmallow`
- source entrypoints: `marshmallow.Schema, marshmallow.fields, marshmallow.ValidationError, marshmallow.schema.Schema.load, marshmallow.schema.Schema.dump`
- oracle source files: `marshmallow/__init__.py, marshmallow/class_registry.py, marshmallow/constants.py, marshmallow/decorators.py, marshmallow/error_store.py, marshmallow/exceptions.py, marshmallow/experimental/__init__.py, marshmallow/experimental/context.py, marshmallow/fields.py, marshmallow/orderedset.py, marshmallow/py.typed, marshmallow/schema.py, marshmallow/types.py, marshmallow/utils.py, marshmallow/validate.py`
- runtime dependencies: `none`
- oracle notes: Full marshmallow runtime package (pure Python).

## Machine Issues

- public_tests/test_public_api.py uses undeclared API reference featurelifted.fields.Int
- public_tests/test_public_api.py uses undeclared API reference featurelifted.fields.Nested
- public_tests/test_public_api.py uses undeclared API reference featurelifted.fields.Str
- hidden_tests/test_hidden_behavior.py uses undeclared API reference featurelifted.fields.Int
- hidden_tests/test_hidden_behavior.py uses undeclared API reference featurelifted.fields.List
- hidden_tests/test_hidden_behavior.py uses undeclared API reference featurelifted.fields.Nested
- hidden_tests/test_hidden_behavior.py uses undeclared API reference featurelifted.fields.Str
