# json_logic__evaluator_core__hard3_001

- release: `frozen_python150`
- lift: `Direct`
- coupling: `unknown`
- strict validation: `PASS`
- tests/assertions: `7/9`

## Required API

- `featurelifted.jsonLogic` (function) `(tests, data=None)`

## Public Behaviors

- **B001**: When jsonLogic evaluates supported arithmetic, comparison, conditional, collection, and boolean rules, it returns the corresponding JSON-compatible result.
- **B002**: When a var rule uses dotted paths or a default, jsonLogic resolves nested data and returns the default for missing paths.
- **B003**: When and/or rules are evaluated, operands short-circuit in order and return the same operand-style result as the upstream semantics.
- **B004**: The package exposes the required task API paths `featurelifted.jsonLogic` with the kinds and callable signatures listed in this contract.

## Tests

### `public_tests/test_public_contract.py::test_simple_comparison_and_var`

- mapping: `B002`
- API: `featurelifted.jsonLogic`
- risk: `none`
- A001 `assert` L6: `jsonLogic(rule, {'x': 1}) is True`
- A002 `assert` L7: `jsonLogic(rule, {'x': 2}) is False`

### `public_tests/test_public_contract.py::test_numeric_plus`

- mapping: `B001`
- API: `featurelifted.jsonLogic`
- risk: `none`
- A001 `assert` L10: `jsonLogic({'+': [1, '2', 3]}, {}) == 6`

### `public_tests/test_public_contract.py::test_if_operator`

- mapping: `B001`
- API: `featurelifted.jsonLogic`
- risk: `none`
- A001 `assert` L14: `jsonLogic(rule, {}) == 'yes'`

### `hidden_tests/test_hidden_contract.py::test_short_circuit_and`

- mapping: `B001, B003`
- API: `featurelifted.jsonLogic`
- risk: `none`
- A001 `assert` L6: `jsonLogic(rule, {}) is False`

### `hidden_tests/test_hidden_contract.py::test_nested_var_path_and_missing`

- mapping: `B002`
- API: `featurelifted.jsonLogic`
- risk: `none`
- A001 `assert` L11: `jsonLogic(rule, {'user': {'name': 'Ada'}}) == 'Ada'`
- A002 `assert` L12: `jsonLogic(rule, {}) is None`

### `hidden_tests/test_hidden_contract.py::test_or_short_circuit`

- mapping: `B003`
- API: `featurelifted.jsonLogic`
- risk: `none`
- A001 `assert` L16: `jsonLogic({'or': [True, {'/': [1, 0]}]}, {}) is True`

### `hidden_tests/test_required_api_surface.py::test_required_api_surface`

- mapping: `B004`
- API: `featurelifted.jsonLogic`
- risk: `none`
- A001 `assert` L9: `callable(jsonLogic)`

## Dependency / Oracle Evidence

- allowed dependencies: `none`
- forbidden imports: `json_logic`
- source entrypoints: `json_logic.jsonLogic`
- oracle source files: `repo/json_logic/__init__.py`
- runtime dependencies: `none`
- oracle notes: jsonLogic core
