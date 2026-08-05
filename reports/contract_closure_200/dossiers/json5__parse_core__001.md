# json5__parse_core__001

- release: `frozen_python150`
- lift: `Direct`
- coupling: `unknown`
- strict validation: `PASS`
- tests/assertions: `6/8`

## Required API

- `featurelifted.loads` (function) `(s, encoding=None, cls=None, object_hook=None, parse_float=None, parse_int=None, parse_constant=None, object_pairs_hook=None, allow_duplicate_keys=True)`
- `featurelifted.load` (function) `(fp, encoding=None, cls=None, object_hook=None, parse_float=None, parse_int=None, parse_constant=None, object_pairs_hook=None, allow_duplicate_keys=True)`

## Public Behaviors

- **B001**: The extracted feature must support this observable behavior: parse JSON5 objects, arrays, strings, numbers, booleans, and null. Required observable cases include malformed input reports position.
- **B002**: The extracted feature must support this observable behavior: support unquoted keys, single-quoted strings, trailing commas, and comments. Required observable cases include loads parses unquoted keys and trailing comma; loads supports line comments; malformed input reports position.
- **B003**: The extracted feature must support this observable behavior: support hexadecimal and leading-plus numeric literals. Required observable cases include hex and plus numeric literals.
- **B004**: The extracted feature must support this observable behavior: raise ValueError with line/column context for malformed input. Required observable cases include malformed input reports position.
- **B005**: The extracted feature must support this observable behavior: optional duplicate-key rejection via allow_duplicate_keys=False. Required observable cases include duplicate keys rejected when disabled.
- **B006**: The package exposes the required task API paths `featurelifted.loads`, `featurelifted.load` with the kinds and callable signatures listed in this contract.

## Tests

### `public_tests/test_public_api.py::test_loads_parses_unquoted_keys_and_trailing_comma`

- mapping: `B002`
- API: `featurelifted.loads`
- risk: `none`
- A001 `assert` L9: `value == {'name': 'widget', 'qty': 2}`

### `public_tests/test_public_api.py::test_loads_supports_line_comments`

- mapping: `B002`
- API: `featurelifted.loads`
- risk: `none`
- A001 `assert` L23: `value['active'] is True`
- A002 `assert` L24: `value['tags'] == ['sale', 'new']`

### `hidden_tests/test_hidden_behavior.py::test_hex_and_plus_numeric_literals`

- mapping: `B003`
- API: `featurelifted.loads`
- risk: `none`
- A001 `assert` L9: `value == {'mask': 255, 'delta': 12}`

### `hidden_tests/test_hidden_behavior.py::test_duplicate_keys_rejected_when_disabled`

- mapping: `B005`
- API: `featurelifted.loads`
- risk: `exact_error_text, exception_semantics`
- A001 `raises` L13: `pytest.raises(ValueError, match='Duplicate key')`

### `hidden_tests/test_hidden_behavior.py::test_malformed_input_reports_position`

- mapping: `B001, B002, B004`
- API: `featurelifted.loads`
- risk: `exact_error_text, exception_semantics`
- A001 `raises` L18: `pytest.raises(ValueError, match='column \\d+')`

### `hidden_tests/test_required_api_surface.py::test_required_api_surface`

- mapping: `B006`
- API: `featurelifted.load, featurelifted.loads`
- risk: `none`
- A001 `assert` L10: `callable(loads)`
- A002 `assert` L11: `callable(load)`

## Dependency / Oracle Evidence

- allowed dependencies: `none`
- forbidden imports: `json5`
- source entrypoints: `json5.loads, json5.load, json5.parser.Parser`
- oracle source files: `json5/__init__.py, json5/lib.py, json5/parser.py, json5/version.py`
- runtime dependencies: `none`
- oracle notes: JSON5 loads/parser closure only. dump/dumps and CLI modules excluded.
