# pydantic__field_validator_core__hard3_001

- release: `frozen_python150`
- lift: `Adapted`
- coupling: `unknown`
- strict validation: `PASS`
- tests/assertions: `4/7`

## Required API

- `featurelifted.field_validator` (function) `(*fields: 'str', mode: 'str' = 'after')`
- `featurelifted.BaseModel` (class) `(**data: 'Any') -> 'None'`
- `featurelifted.ValidationError` (exception)

## Public Behaviors

- **B001**: `@field_validator` registers before/after validators on model classes.
- **B002**: Before validators transform incoming values; after validators run on initialized attributes.
- **B003**: `ValidationError` carries structured field errors.
- **B004**: The package exposes the required task API paths `featurelifted.field_validator`, `featurelifted.BaseModel`, `featurelifted.ValidationError` with the kinds and callable signatures listed in this contract.

## Tests

### `public_tests/test_public_contract.py::test_after_validator_strips`

- mapping: `B001, B002`
- API: `none detected`
- risk: `none`
- A001 `assert` L15: `user.name == 'ada'`

### `hidden_tests/test_hidden_contract.py::test_before_validator_normalizes`

- mapping: `B001, B002`
- API: `none detected`
- risk: `none`
- A001 `assert` L17: `obj.version == '1.2'`

### `hidden_tests/test_hidden_contract.py::test_validation_error_on_after_failure`

- mapping: `B002, B003`
- API: `featurelifted.BaseModel, featurelifted.ValidationError, featurelifted.field_validator`
- risk: `exception_semantics`
- A001 `raises` L30: `pytest.raises(ValidationError)`
- A002 `assert` L32: `exc.value.errors[0]['field'] == 'age'`

### `hidden_tests/test_required_api_surface.py::test_required_api_surface`

- mapping: `B004`
- API: `featurelifted.BaseModel, featurelifted.ValidationError, featurelifted.field_validator`
- risk: `none`
- A001 `assert` L11: `callable(field_validator)`
- A002 `assert` L12: `isinstance(BaseModel, type)`
- A003 `assert` L13: `issubclass(ValidationError, BaseException)`

## Dependency / Oracle Evidence

- allowed dependencies: `none`
- forbidden imports: `pydantic`
- source entrypoints: `pydantic.functional_validators.field_validator`
- oracle source files: `repo/pydantic/functional_validators.py, repo/pydantic/main.py`
- runtime dependencies: `none`
- oracle notes: Field validator subset without full pydantic runtime.
