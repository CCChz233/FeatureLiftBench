# yamale__schema_validate_core__hard3_001

- release: `frozen_python150`
- lift: `Adapted`
- coupling: `unknown`
- strict validation: `PASS`
- tests/assertions: `5/8`

## Required API

- `featurelifted.make_schema` (function) `(content: 'str', name: 'str' = 'schema') -> 'Schema'`
- `featurelifted.validate` (function) `(schema: 'Schema', data: 'list[tuple[dict, str]]', strict: 'bool' = True, _raise_error: 'bool' = True)`
- `featurelifted.ValidationResult` (class) `(data_name: 'str', schema_name: 'str', errors: 'list[str]' = <factory>) -> None`
- `featurelifted.YamaleError` (exception)

## Public Behaviors

- **B001**: `make_schema` parses one or more YAML documents; later documents provide `include` targets.
- **B002**: Validate maps, lists, primitive types, optional fields, and included schemas.
- **B003**: `strict=True` rejects unexpected keys; non-strict bool validation may accept common string/int aliases.
- **B004**: `validate` returns `ValidationResult` objects and raises `YamaleError` when invalid and `_raise_error=True`.
- **B005**: The package exposes the required task API paths `featurelifted.make_schema`, `featurelifted.validate`, `featurelifted.ValidationResult`, `featurelifted.YamaleError` with the kinds and callable signatures listed in this contract.

## Tests

### `public_tests/test_public_contract.py::test_basic_schema_validation`

- mapping: `B001, B004`
- API: `featurelifted.make_schema, featurelifted.validate`
- risk: `none`
- A001 `assert` L8: `results[0].isValid()`

### `hidden_tests/test_hidden_contract.py::test_strict_mode_rejects_extra_keys`

- mapping: `B001, B003, B004`
- API: `featurelifted.YamaleError, featurelifted.make_schema, featurelifted.validate`
- risk: `exception_semantics`
- A001 `raises` L9: `pytest.raises(YamaleError)`

### `hidden_tests/test_hidden_contract.py::test_include_and_list_validator`

- mapping: `B002`
- API: `featurelifted.make_schema, featurelifted.validate`
- risk: `none`
- A001 `assert` L17: `results[0].isValid()`

### `hidden_tests/test_hidden_contract.py::test_bool_non_strict_coercion`

- mapping: `B004`
- API: `featurelifted.make_schema, featurelifted.validate`
- risk: `none`
- A001 `assert` L23: `results[0].isValid()`

### `hidden_tests/test_required_api_surface.py::test_required_api_surface`

- mapping: `B005`
- API: `featurelifted.ValidationResult, featurelifted.YamaleError, featurelifted.make_schema, featurelifted.validate`
- risk: `none`
- A001 `assert` L12: `callable(make_schema)`
- A002 `assert` L13: `callable(validate)`
- A003 `assert` L14: `isinstance(ValidationResult, type)`
- A004 `assert` L15: `issubclass(YamaleError, BaseException)`

## Dependency / Oracle Evidence

- allowed dependencies: `PyYAML`
- forbidden imports: `yamale`
- source entrypoints: `yamale.make_schema, yamale.validate`
- oracle source files: `repo/yamale/yamale.py, repo/yamale/schema/schema.py, repo/yamale/validators/validators.py, repo/yamale/syntax/parser.py`
- runtime dependencies: `PyYAML`
- oracle notes: In-memory Yamale subset with PyYAML dependency.
