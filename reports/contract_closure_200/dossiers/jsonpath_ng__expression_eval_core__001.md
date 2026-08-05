# jsonpath_ng__expression_eval_core__001

- release: `frozen_python150`
- lift: `Direct`
- coupling: `unknown`
- strict validation: `PASS`
- tests/assertions: `11/16`

## Required API

- `featurelifted.parse` (function) `(path, debug=False)`
- `featurelifted.exceptions` (module)
- `featurelifted.exceptions.JsonPathLexerError` (exception)
- `featurelifted.exceptions.JsonPathParserError` (exception)

## Public Behaviors

- **B001**: The extracted feature must support this observable behavior: parse JSONPath strings into expression objects. Required observable cases include parse find simple path; root child fields; filter expression selects items; invalid expression raises.
- **B002**: The extracted feature must support this observable behavior: find matching values in dict/list document trees. Required observable cases include parse find simple path; wildcard array find; root child fields; update nested path.
- **B003**: The extracted feature must support this observable behavior: update values at matching paths in place. Required observable cases include update value in place; update nested path.
- **B004**: The extracted feature must support this observable behavior: filter expressions with comparison operators. Required observable cases include filter expression selects items; invalid expression raises.
- **B005**: The extracted feature must support this observable behavior: array slices and wildcard/index segments. Required observable cases include wildcard array find; bracket slice selects range; negative index selects last.
- **B006**: The package exposes the required task API paths `featurelifted.parse`, `featurelifted.exceptions`, `featurelifted.exceptions.JsonPathLexerError`, `featurelifted.exceptions.JsonPathParserError` with the kinds and callable signatures listed in this contract.

## Tests

### `public_tests/test_public_api.py::test_parse_find_simple_path`

- mapping: `B001, B002`
- API: `featurelifted.parse`
- risk: `filesystem_resource`
- A001 `assert` L11: `[m.value for m in matches] == ['ada']`

### `public_tests/test_public_api.py::test_wildcard_array_find`

- mapping: `B002, B005`
- API: `featurelifted.parse`
- risk: `none`
- A001 `assert` L17: `[m.value for m in matches] == [1, 2]`

### `public_tests/test_public_api.py::test_update_value_in_place`

- mapping: `B003`
- API: `featurelifted.parse`
- risk: `state_mutation`
- A001 `assert` L24: `doc['count'] == 9`

### `public_tests/test_public_api.py::test_root_child_fields`

- mapping: `B001, B002`
- API: `featurelifted.parse`
- risk: `none`
- A001 `assert` L30: `sorted((m.value for m in matches)) == [1, 2]`

### `hidden_tests/test_hidden_behavior.py::test_filter_expression_selects_items`

- mapping: `B001, B004`
- API: `featurelifted.exceptions, featurelifted.parse`
- risk: `none`
- A001 `assert` L16: `len(matches) == 1`
- A002 `assert` L17: `matches[0].value['price'] == 5`

### `hidden_tests/test_hidden_behavior.py::test_bracket_slice_selects_range`

- mapping: `B005`
- API: `featurelifted.exceptions, featurelifted.parse`
- risk: `none`
- A001 `assert` L23: `[m.value for m in matches] == [20, 30]`

### `hidden_tests/test_hidden_behavior.py::test_update_nested_path`

- mapping: `B002, B003`
- API: `featurelifted.exceptions, featurelifted.parse`
- risk: `filesystem_resource, state_mutation`
- A001 `assert` L30: `doc['store']['book'][1]['price'] == 99`

### `hidden_tests/test_hidden_behavior.py::test_negative_index_selects_last`

- mapping: `B005`
- API: `featurelifted.exceptions, featurelifted.parse`
- risk: `none`
- A001 `assert` L36: `[m.value for m in matches] == ['c']`

### `hidden_tests/test_hidden_behavior.py::test_invalid_expression_raises`

- mapping: `B001, B004`
- API: `featurelifted.exceptions, featurelifted.parse`
- risk: `exception_semantics`
- A001 `raises` L40: `pytest.raises((JsonPathLexerError, JsonPathParserError, Exception))`

### `hidden_tests/test_hidden_behavior.py::test_no_jsonpath_ng_import_surface`

- mapping: `B007`
- API: `featurelifted.__file__, featurelifted.exceptions`
- risk: `filesystem_resource`
- A001 `assert` L50: `name not in exports`
- A002 `assert` L56: `not import_pattern.search(text)`

### `hidden_tests/test_required_api_surface.py::test_required_api_surface`

- mapping: `B006`
- API: `featurelifted.exceptions, featurelifted.parse`
- risk: `none`
- A001 `assert` L10: `callable(parse)`
- A002 `assert` L11: `exceptions is not None`
- A003 `assert` L12: `issubclass(getattr(exceptions, 'JsonPathLexerError'), BaseException)`
- A004 `assert` L13: `issubclass(getattr(exceptions, 'JsonPathParserError'), BaseException)`

## Dependency / Oracle Evidence

- allowed dependencies: `ply`
- forbidden imports: `jsonpath_ng`
- source entrypoints: `jsonpath_ng.ext.parse, jsonpath_ng.jsonpath.JSONPath.find, jsonpath_ng.jsonpath.JSONPath.update, jsonpath_ng.parser.JsonPathParser, jsonpath_ng.lexer.JsonPathLexer`
- oracle source files: `jsonpath_ng/jsonpath.py, jsonpath_ng/parser.py, jsonpath_ng/lexer.py, jsonpath_ng/exceptions.py, jsonpath_ng/ext/parser.py, jsonpath_ng/ext/filter.py, jsonpath_ng/ext/arithmetic.py, jsonpath_ng/ext/iterable.py, jsonpath_ng/ext/string.py`
- runtime dependencies: `ply`
- oracle notes: Oracle omits vendored _ply and bin/; patches lexer/parser to use system ply.
