# trafaret__validation_rules_core__hard3_001

- release: `frozen_python150`
- lift: `Adapted`
- coupling: `unknown`
- strict validation: `FAIL`
- tests/assertions: `5/19`

## Required API

- `featurelifted.Int` (class) `()`
- `featurelifted.String` (class) `()`
- `featurelifted.Dict` (class) `(schema: 'dict[str, Trafaret]', allow_extra: 'bool' = False)`
- `featurelifted.Dict.check` (method) `(self, value, path=())`
- `featurelifted.Key` (class) `(name: 'str', validator: 'Trafaret', optional: 'bool' = False)`
- `featurelifted.Or` (class) `(*options: 'Trafaret')`
- `featurelifted.Or.check` (method) `(self, value)`
- `featurelifted.And` (class) `(*parts: 'Trafaret')`
- `featurelifted.Forward` (class) `()`
- `featurelifted.Forward.set_type` (method) `(self, target: 'Trafaret') -> 'None'`
- `featurelifted.Forward.check` (method) `(self, value)`
- `featurelifted.DataError` (exception)

## Public Behaviors

- **B001**: `Dict`, `Key`, `Or`, `And`, and `Forward` compose validation rules.
- **B002**: `DataError` carries a path tuple for nested validation failures.
- **B003**: `Forward.set_type` enables recursive schemas.
- **B004**: The package exposes the required task API paths `featurelifted.Int`, `featurelifted.String`, `featurelifted.Dict`, `featurelifted.Dict.check`, `featurelifted.Key`, `featurelifted.Or`, `featurelifted.Or.check`, `featurelifted.And`, `featurelifted.Forward`, `featurelifted.Forward.set_type`, `featurelifted.Forward.check`, `featurelifted.DataError` with the kinds and callable signatures listed in this contract.

## Tests

### `public_tests/test_public_contract.py::test_dict_validates_schema`

- mapping: `B001`
- API: `featurelifted.Dict, featurelifted.Int, featurelifted.String`
- risk: `none`
- A001 `assert` L7: `schema.check({'name': 'Ada', 'age': 2}) == {'name': 'Ada', 'age': 2}`

### `hidden_tests/test_hidden_contract.py::test_or_composition`

- mapping: `B001`
- API: `featurelifted.And, featurelifted.And.check, featurelifted.Int, featurelifted.Or, featurelifted.String`
- risk: `none`
- A001 `assert` L9: `validator.check('x') == 'x'`
- A002 `assert` L10: `validator.check(1) == 1`
- A003 `assert` L11: `And(String(), String()).check('hi') == 'hi'`

### `hidden_tests/test_hidden_contract.py::test_key_optional_and_dataerror_path`

- mapping: `B002`
- API: `featurelifted.DataError, featurelifted.Dict, featurelifted.String`
- risk: `exception_semantics, filesystem_resource`
- A001 `raises` L16: `pytest.raises(DataError)`
- A002 `assert` L18: `exc.value.path == ('name',)`

### `hidden_tests/test_hidden_contract.py::test_forward_recursion`

- mapping: `B003`
- API: `featurelifted.Dict, featurelifted.Forward, featurelifted.Int, featurelifted.Or, featurelifted.String`
- risk: `none`
- A001 `assert` L25: `node.check(data)['next']['next'] == 'done'`

### `hidden_tests/test_required_api_surface.py::test_required_api_surface`

- mapping: `B004`
- API: `featurelifted.And, featurelifted.DataError, featurelifted.Dict, featurelifted.Forward, featurelifted.Int, featurelifted.Key, featurelifted.Or, featurelifted.String`
- risk: `none`
- A001 `assert` L16: `isinstance(Int, type)`
- A002 `assert` L17: `isinstance(String, type)`
- A003 `assert` L18: `isinstance(Dict, type)`
- A004 `assert` L19: `hasattr(Dict, 'check')`
- A005 `assert` L20: `isinstance(Key, type)`
- A006 `assert` L21: `isinstance(Or, type)`
- A007 `assert` L22: `hasattr(Or, 'check')`
- A008 `assert` L23: `isinstance(And, type)`
- A009 `assert` L24: `isinstance(Forward, type)`
- A010 `assert` L25: `hasattr(Forward, 'set_type')`
- A011 `assert` L26: `hasattr(Forward, 'check')`
- A012 `assert` L27: `issubclass(DataError, BaseException)`

## Dependency / Oracle Evidence

- allowed dependencies: `none`
- forbidden imports: `trafaret`
- source entrypoints: `trafaret.Dict, trafaret.Or, trafaret.Forward`
- oracle source files: `repo/trafaret/base.py, repo/trafaret/dataerror.py`
- runtime dependencies: `none`
- oracle notes: Composable validation subset.

## Machine Issues

- hidden_tests/test_hidden_contract.py uses undeclared API reference featurelifted.And.check
