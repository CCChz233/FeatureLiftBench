# schema__nested_validate_core__hard3_001

- release: `frozen_python150`
- lift: `Adapted`
- coupling: `unknown`
- strict validation: `FAIL`
- tests/assertions: `5/12`

## Required API

- `featurelifted.Schema` (class) `(schema: 'Any') -> 'None'`
- `featurelifted.Schema.validate` (method) `(self, data: 'Any') -> 'Any'`
- `featurelifted.Optional` (class) `(key: 'str', default: 'Any' = Ellipsis) -> 'None'`
- `featurelifted.Or` (class) `(*validators: 'Any') -> 'None'`
- `featurelifted.Or.validate` (method) `(self, data: 'Any') -> 'Any'`
- `featurelifted.And` (class) `(*validators: 'Any') -> 'None'`
- `featurelifted.SchemaError` (exception)

## Public Behaviors

- **B001**: `Schema` validates nested dicts with type and literal rules.
- **B002**: `Optional` supplies defaults for missing keys.
- **B003**: Or accepts the first validating alternative, while And applies each validator in sequence and reports SchemaError when composition fails.
- **B004**: The package exposes the required task API paths `featurelifted.Schema`, `featurelifted.Schema.validate`, `featurelifted.Optional`, `featurelifted.Or`, `featurelifted.Or.validate`, `featurelifted.And`, `featurelifted.SchemaError` with the kinds and callable signatures listed in this contract.

## Tests

### `public_tests/test_public_contract.py::test_schema_validates_nested_dict`

- mapping: `B001`
- API: `featurelifted.Schema`
- risk: `none`
- A001 `assert` L7: `validator.validate({'name': 'Ada', 'age': 2}) == {'name': 'Ada', 'age': 2}`

### `hidden_tests/test_hidden_contract.py::test_optional_default`

- mapping: `B002`
- API: `featurelifted.Optional, featurelifted.Schema`
- risk: `none`
- A001 `assert` L9: `validator.validate({})['tag'] == 'latest'`

### `hidden_tests/test_hidden_contract.py::test_or_and_composition`

- mapping: `B003`
- API: `featurelifted.And, featurelifted.And.validate, featurelifted.Or`
- risk: `none`
- A001 `assert` L14: `validator.validate('x') == 'x'`
- A002 `assert` L15: `And(str, lambda s: s.upper()).validate('hi') == 'HI'`

### `hidden_tests/test_hidden_contract.py::test_extra_keys_rejected`

- mapping: `B001`
- API: `featurelifted.Schema, featurelifted.SchemaError`
- risk: `exception_semantics`
- A001 `raises` L20: `pytest.raises(SchemaError)`

### `hidden_tests/test_required_api_surface.py::test_required_api_surface`

- mapping: `B004`
- API: `featurelifted.And, featurelifted.Optional, featurelifted.Or, featurelifted.Schema, featurelifted.SchemaError`
- risk: `none`
- A001 `assert` L13: `isinstance(Schema, type)`
- A002 `assert` L14: `hasattr(Schema, 'validate')`
- A003 `assert` L15: `isinstance(Optional, type)`
- A004 `assert` L16: `isinstance(Or, type)`
- A005 `assert` L17: `hasattr(Or, 'validate')`
- A006 `assert` L18: `isinstance(And, type)`
- A007 `assert` L19: `issubclass(SchemaError, BaseException)`

## Dependency / Oracle Evidence

- allowed dependencies: `none`
- forbidden imports: `schema`
- source entrypoints: `schema.Schema`
- oracle source files: `repo/schema/__init__.py`
- runtime dependencies: `none`
- oracle notes: Nested schema validation subset.

## Machine Issues

- hidden_tests/test_hidden_contract.py uses undeclared API reference featurelifted.And.validate
