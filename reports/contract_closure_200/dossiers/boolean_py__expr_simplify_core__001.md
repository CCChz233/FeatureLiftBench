# boolean_py__expr_simplify_core__001

- release: `external50`
- lift: `Composite`
- coupling: `parser_state_coupling`
- strict validation: `PASS`
- tests/assertions: `8/18`

## Required API

- `featurelifted.BooleanAlgebra` (class)
- `featurelifted.BooleanAlgebra.parse` (method)
- `featurelifted.BooleanAlgebra.Symbol` (attribute)
- `featurelifted.BooleanAlgebra.TRUE` (attribute)
- `featurelifted.BooleanAlgebra.FALSE` (attribute)
- `featurelifted.BooleanAlgebra.parse` (method)
- `featurelifted.ParseError` (class)
- `featurelifted.Symbol` (class)
- `featurelifted.Expression` (class)
- `featurelifted.Expression.simplify` (method)
- `featurelifted.Expression.subs` (method)

## Public Behaviors

- **B001**: The extracted feature must support this observable behavior: parse and simplify boolean expressions. Required observable cases include parse and simplify.
- **B002**: The extracted feature must support this observable behavior: expression.subs with simplify. Required observable cases include subs.
- **B003**: The extracted feature must support this observable behavior: simplified equality and ParseError on bad input. Required observable cases include equality; parse error.
- **B004**: NOT/TRUE/FALSE constants simplify as upstream.
- **B005**: The package exposes BooleanAlgebra/parse/ParseError/Symbol with the kinds listed in this contract.
- **B006**: the submitted package does not import forbidden upstream packages: boolean.

## Tests

### `public_tests/test_public_api.py::test_parse_and_simplify`

- mapping: `B001`
- API: `featurelifted.BooleanAlgebra`
- risk: `exact_error_text`
- A001 `assert` L10: `simplified == algebra.parse('~c | (a & b)') or str(simplified) == '~c|(a&b)'`

### `public_tests/test_public_api.py::test_subs`

- mapping: `B002`
- API: `featurelifted.BooleanAlgebra`
- risk: `exact_error_text`
- A001 `assert` L18: `subbed == algebra.parse('b | ~c') or str(subbed) == 'b|~c'`

### `public_tests/test_public_api.py::test_equality`

- mapping: `B003`
- API: `featurelifted.BooleanAlgebra`
- risk: `none`
- A001 `assert` L25: `left.simplify() == right.simplify()`

### `hidden_tests/test_hidden_behavior.py::test_parse_error`

- mapping: `B001, B004`
- API: `featurelifted.BooleanAlgebra, featurelifted.ParseError`
- risk: `none`
- A001 `assert` L10: `False`

### `hidden_tests/test_hidden_behavior.py::test_not_and_constants`

- mapping: `B002`
- API: `featurelifted.BooleanAlgebra`
- risk: `none`
- A001 `assert` L18: `expr.simplify() == algebra.FALSE`

### `hidden_tests/test_hidden_behavior.py::test_symbol_roundtrip`

- mapping: `B003`
- API: `featurelifted.BooleanAlgebra`
- risk: `none`
- A001 `assert` L25: `expr.subs({sym: algebra.TRUE}) == algebra.TRUE`

### `hidden_tests/test_hidden_behavior.py::test_no_upstream_import_surface`

- mapping: `B006`
- API: `featurelifted.__file__`
- risk: `filesystem_resource`
- A001 `assert` L39: `not pattern.search(path.read_text(encoding='utf-8'))`

### `hidden_tests/test_required_api_surface.py::test_required_api_surface`

- mapping: `B005`
- API: `featurelifted.BooleanAlgebra, featurelifted.Expression, featurelifted.Expression.simplify, featurelifted.Expression.subs`
- risk: `none`
- A001 `assert` L5: `hasattr(featurelifted, 'BooleanAlgebra')`
- A002 `assert` L6: `hasattr(featurelifted, 'Expression')`
- A003 `assert` L7: `hasattr(featurelifted, 'ParseError')`
- A004 `assert` L8: `hasattr(featurelifted, 'Symbol')`
- A005 `assert` L10: `callable(instance_0.parse)`
- A006 `assert` L11: `hasattr(instance_0, 'Symbol')`
- A007 `assert` L12: `hasattr(instance_0, 'TRUE')`
- A008 `assert` L13: `hasattr(instance_0, 'FALSE')`
- A009 `assert` L14: `callable(instance_0.parse)`
- A010 `assert` L15: `callable(featurelifted.Expression.simplify)`
- A011 `assert` L16: `callable(featurelifted.Expression.subs)`

## Dependency / Oracle Evidence

- allowed dependencies: `none`
- forbidden imports: `boolean`
- source entrypoints: `none`
- oracle source files: `boolean/boolean.py, boolean/__init__.py`
- runtime dependencies: `none`
- oracle notes: Composite BooleanAlgebra.parse + expression.simplify/subs (not algebra.simplify).
- behavior contract lacks a completed review_status
- behavior contract schema_version missing or unsupported
