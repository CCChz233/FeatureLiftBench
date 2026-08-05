# pygments__lexer_core__001

- release: `frozen_python150`
- lift: `Direct`
- coupling: `unknown`
- strict validation: `FAIL`
- tests/assertions: `6/17`

## Required API

- `featurelifted.lex` (function) `(code, lexer)`
- `featurelifted.get_lexer_by_name` (function) `(_alias, **options)`
- `featurelifted.PythonLexer` (class) `(*args, **kwds)`
- `featurelifted.token` (module)

## Public Behaviors

- **B001**: The extracted feature must support this observable behavior: tokenize Python source with PythonLexer and lex(). Required observable cases include python lexer keywords and names; get lexer by name returns python lexer; triple quoted string and operator tokens.
- **B002**: The extracted feature must support this observable behavior: resolve lexers by alias with get_lexer_by_name. Required observable cases include get lexer by name returns python lexer; triple quoted string and operator tokens.
- **B003**: The extracted feature must support this observable behavior: emit Token types for keywords, strings, comments, numbers, operators, and names. Required observable cases include string and comment tokens are distinct; triple quoted string and operator tokens.
- **B004**: The extracted feature must support this observable behavior: honor lexer options such as stripall and ensurenl. Required observable cases include stripall option removes whitespace tokens.
- **B005**: The extracted feature must support this observable behavior: support modeline and encoding helpers used by lexer lookup. Required observable cases include triple quoted string and operator tokens.
- **B006**: The package exposes the required task API paths `featurelifted.lex`, `featurelifted.get_lexer_by_name`, `featurelifted.PythonLexer`, `featurelifted.token` with the kinds and callable signatures listed in this contract.

## Tests

### `public_tests/test_lexer_public.py::test_python_lexer_keywords_and_names`

- mapping: `B001`
- API: `featurelifted.PythonLexer, featurelifted.lex, featurelifted.token, featurelifted.token.Keyword, featurelifted.token.Name, featurelifted.token.Name.Function`
- risk: `none`
- A001 `assert` L11: `token.Keyword in kinds`
- A002 `assert` L12: `token.Name.Function in kinds`
- A003 `assert` L13: `token.Name in kinds`

### `public_tests/test_lexer_public.py::test_get_lexer_by_name_returns_python_lexer`

- mapping: `B001, B002`
- API: `featurelifted.get_lexer_by_name, featurelifted.lex`
- risk: `none`
- A001 `assert` L19: `lexer.name == 'Python'`
- A002 `assert` L20: `list(lex('x = 1', lexer))`

### `hidden_tests/test_lexer_hidden.py::test_string_and_comment_tokens_are_distinct`

- mapping: `B003`
- API: `featurelifted.PythonLexer, featurelifted.lex, featurelifted.token, featurelifted.token.Comment, featurelifted.token.Comment.Single, featurelifted.token.Literal, featurelifted.token.Literal.String, featurelifted.token.Literal.String.Single`
- risk: `none`
- A001 `assert` L13: `token.Comment.Single in types`
- A002 `assert` L14: `token.Literal.String.Single in types`
- A003 `assert` L15: `'abc' in values`

### `hidden_tests/test_lexer_hidden.py::test_stripall_option_removes_whitespace_tokens`

- mapping: `B004`
- API: `featurelifted.PythonLexer, featurelifted.lex, featurelifted.token, featurelifted.token.Text`
- risk: `none`
- A001 `assert` L22: `all((ttype is not token.Text for ttype, _ in pairs))`
- A002 `assert` L23: `[value for _, value in pairs if value.strip()] == ['x', '=', '1']`

### `hidden_tests/test_lexer_hidden.py::test_triple_quoted_string_and_operator_tokens`

- mapping: `B001, B002, B003, B005`
- API: `featurelifted.PythonLexer, featurelifted.lex, featurelifted.token, featurelifted.token.Number, featurelifted.token.Number.Integer, featurelifted.token.Operator, featurelifted.token.String, featurelifted.token.String.Double`
- risk: `none`
- A001 `assert` L31: `token.String.Double in types`
- A002 `assert` L32: `token.Operator in types`
- A003 `assert` L33: `token.Number.Integer in types`

### `hidden_tests/test_required_api_surface.py::test_required_api_surface`

- mapping: `B006`
- API: `featurelifted.PythonLexer, featurelifted.get_lexer_by_name, featurelifted.lex, featurelifted.token`
- risk: `none`
- A001 `assert` L12: `callable(lex)`
- A002 `assert` L13: `callable(get_lexer_by_name)`
- A003 `assert` L14: `isinstance(PythonLexer, type)`
- A004 `assert` L15: `token is not None`

## Dependency / Oracle Evidence

- allowed dependencies: `none`
- forbidden imports: `pygments`
- source entrypoints: `pygments.lex, pygments.lexer.Lexer, pygments.lexer.RegexLexer, pygments.lexers.get_lexer_by_name, pygments.lexers.python.PythonLexer, pygments.token`
- oracle source files: `none`
- runtime dependencies: `none`

## Machine Issues

- public_tests/test_lexer_public.py uses undeclared API reference featurelifted.token.Keyword
- public_tests/test_lexer_public.py uses undeclared API reference featurelifted.token.Name
- public_tests/test_lexer_public.py uses undeclared API reference featurelifted.token.Name.Function
- hidden_tests/test_lexer_hidden.py uses undeclared API reference featurelifted.token.Comment
- hidden_tests/test_lexer_hidden.py uses undeclared API reference featurelifted.token.Comment.Single
- hidden_tests/test_lexer_hidden.py uses undeclared API reference featurelifted.token.Literal
- hidden_tests/test_lexer_hidden.py uses undeclared API reference featurelifted.token.Literal.String
- hidden_tests/test_lexer_hidden.py uses undeclared API reference featurelifted.token.Literal.String.Single
- hidden_tests/test_lexer_hidden.py uses undeclared API reference featurelifted.token.Number
- hidden_tests/test_lexer_hidden.py uses undeclared API reference featurelifted.token.Number.Integer
- hidden_tests/test_lexer_hidden.py uses undeclared API reference featurelifted.token.Operator
- hidden_tests/test_lexer_hidden.py uses undeclared API reference featurelifted.token.String
- hidden_tests/test_lexer_hidden.py uses undeclared API reference featurelifted.token.String.Double
- hidden_tests/test_lexer_hidden.py uses undeclared API reference featurelifted.token.Text
