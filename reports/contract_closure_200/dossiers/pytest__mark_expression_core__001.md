# pytest__mark_expression_core__001

- release: `frozen_python150`
- lift: `Adapted`
- coupling: `unknown`
- strict validation: `FAIL`
- tests/assertions: `5/12`

## Required API

- `featurelifted.Expression` (class) `(code: 'types.CodeType') -> 'None'`
- `featurelifted.Expression.compile` (method) `(input: 'str') -> 'Expression'`
- `featurelifted.ParseError` (exception)
- `featurelifted.expression` (module)
- `featurelifted.expression.Scanner` (class) `(input: 'str') -> 'None'`
- `featurelifted.expression.Scanner.current` (attribute)
- `featurelifted.expression.TokenType` (class) `(*values)`
- `featurelifted.expression.TokenType.IDENT` (attribute)

## Public Behaviors

- **B001**: The extracted feature must support this observable behavior: parse and compile mark expressions with and/or/not. Required observable cases include kwargs matcher.
- **B002**: The extracted feature must support this observable behavior: evaluate expressions against a matcher callback. Required observable cases include and or logic; kwargs matcher; expression module scanner.
- **B003**: The extracted feature must support this observable behavior: support identifier kwargs syntax for parameterized markers. Required observable cases include kwargs matcher.
- **B004**: The extracted feature must support this observable behavior: empty expression evaluates to False. Required observable cases include empty expression is false; and or logic; expression module scanner.
- **B005**: The package exposes the required task API paths `featurelifted.Expression`, `featurelifted.Expression.compile`, `featurelifted.ParseError`, `featurelifted.expression`, `featurelifted.expression.Scanner`, `featurelifted.expression.Scanner.current`, `featurelifted.expression.TokenType`, `featurelifted.expression.TokenType.IDENT` with the kinds and callable signatures listed in this contract.

## Tests

### `public_tests/test_public_api.py::test_empty_expression_is_false`

- mapping: `B004`
- API: `featurelifted.Expression, featurelifted.Expression.compile, featurelifted.Expression.evaluate`
- risk: `none`
- A001 `assert` L5: `not Expression.compile('').evaluate(lambda name: True)`

### `public_tests/test_public_api.py::test_and_or_logic`

- mapping: `B002, B004`
- API: `featurelifted.Expression, featurelifted.Expression.compile, featurelifted.Expression.evaluate`
- risk: `none`
- A001 `assert` L10: `Expression.compile('fast and not slow').evaluate(matcher)`

### `hidden_tests/test_hidden_behavior.py::test_kwargs_matcher`

- mapping: `B001, B002, B003`
- API: `featurelifted.Expression, featurelifted.Expression.compile, featurelifted.Expression.evaluate`
- risk: `none`
- A001 `assert` L9: `Expression.compile('req(version=2)').evaluate(matcher)`

### `hidden_tests/test_hidden_behavior.py::test_expression_module_scanner`

- mapping: `B002, B004`
- API: `featurelifted.expression`
- risk: `none`
- A001 `assert` L16: `scanner.current.type is TokenType.IDENT`

### `hidden_tests/test_required_api_surface.py::test_required_api_surface`

- mapping: `B005`
- API: `featurelifted.Expression, featurelifted.ParseError, featurelifted.expression`
- risk: `none`
- A001 `assert` L11: `isinstance(Expression, type)`
- A002 `assert` L12: `hasattr(Expression, 'compile')`
- A003 `assert` L13: `issubclass(ParseError, BaseException)`
- A004 `assert` L14: `expression is not None`
- A005 `assert` L15: `isinstance(getattr(expression, 'Scanner'), type)`
- A006 `assert` L16: `getattr(expression, 'Scanner') is not None`
- A007 `assert` L17: `isinstance(getattr(expression, 'TokenType'), type)`
- A008 `assert` L18: `getattr(expression, 'TokenType') is not None`

## Dependency / Oracle Evidence

- allowed dependencies: `none`
- forbidden imports: `pytest, _pytest`
- source entrypoints: `_pytest.mark.expression.Expression, _pytest.mark.expression.Expression.compile, _pytest.mark.expression.Expression.evaluate`
- oracle source files: `none`
- runtime dependencies: `none`
- oracle notes: Standalone mark expression module only.

## Machine Issues

- public_tests/test_public_api.py uses undeclared API reference featurelifted.Expression.evaluate
- hidden_tests/test_hidden_behavior.py uses undeclared API reference featurelifted.Expression.evaluate
