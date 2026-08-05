# mako__lexer_expression_core__001

- release: `frozen_python150`
- lift: `Direct`
- coupling: `unknown`
- strict validation: `FAIL`
- tests/assertions: `12/40`

## Required API

- `featurelifted.Lexer` (class) `(text, filename=None, input_encoding=None, preprocessor=None)`
- `featurelifted.Lexer.parse` (method) `(self)`
- `featurelifted.parsetree` (module)
- `featurelifted.PythonCode` (class) `(code, **exception_kwargs)`
- `featurelifted.PythonFragment` (class) `(code, **exception_kwargs)`
- `featurelifted.PythonFragment.declared_identifiers` (attribute)
- `featurelifted.PythonFragment.undeclared_identifiers` (attribute)
- `featurelifted.SyntaxException` (exception)
- `featurelifted.CompileException` (exception)

## Public Behaviors

- **B001**: The extracted feature must support this observable behavior: lex template source into parsetree nodes (text, expression, control, tags). Required observable cases include parse text and expression; def tag parses; percent escape in template; unclosed tag raises syntax; expression filter escapes; invalid partial control raises compile.
- **B002**: The extracted feature must support this observable behavior: parse ${...} expressions and % control lines. Required observable cases include parse text and expression; parse control line; def tag parses; expression filter escapes; elif partial control identifiers; invalid partial control raises compile.
- **B003**: The extracted feature must support this observable behavior: analyze Python fragments for declared and undeclared identifiers. Required observable cases include python code undeclared; python fragment for loop; elif partial control identifiers.
- **B004**: The extracted feature must support this observable behavior: report SyntaxException and CompileException with line positions. Required observable cases include unclosed tag raises syntax.
- **B005**: The package exposes the required task API paths `featurelifted.Lexer`, `featurelifted.Lexer.parse`, `featurelifted.parsetree`, `featurelifted.PythonCode`, `featurelifted.PythonFragment`, `featurelifted.PythonFragment.declared_identifiers`, `featurelifted.PythonFragment.undeclared_identifiers`, `featurelifted.SyntaxException`, `featurelifted.CompileException` with the kinds and callable signatures listed in this contract.

## Tests

### `public_tests/test_public_api.py::test_parse_text_and_expression`

- mapping: `B001, B002`
- API: `featurelifted.Lexer, featurelifted.Lexer.parse, featurelifted.parsetree, featurelifted.parsetree.Expression, featurelifted.parsetree.TemplateNode, featurelifted.parsetree.Text`
- risk: `none`
- A001 `assert` L9: `isinstance(node, parsetree.TemplateNode)`
- A002 `assert` L10: `len(node.nodes) == 3`
- A003 `assert` L11: `isinstance(node.nodes[0], parsetree.Text)`
- A004 `assert` L12: `isinstance(node.nodes[1], parsetree.Expression)`
- A005 `assert` L13: `node.nodes[1].text == 'name'`
- A006 `assert` L14: `isinstance(node.nodes[2], parsetree.Text)`

### `public_tests/test_public_api.py::test_parse_control_line`

- mapping: `B002`
- API: `featurelifted.Lexer, featurelifted.Lexer.parse, featurelifted.parsetree, featurelifted.parsetree.ControlLine`
- risk: `none`
- A001 `assert` L19: `isinstance(node.nodes[0], parsetree.ControlLine)`
- A002 `assert` L20: `node.nodes[0].keyword == 'if'`
- A003 `assert` L21: `node.nodes[0].text == 'if flag:'`
- A004 `assert` L22: `isinstance(node.nodes[2], parsetree.ControlLine)`
- A005 `assert` L23: `node.nodes[2].isend is True`

### `public_tests/test_public_api.py::test_python_code_undeclared`

- mapping: `B003`
- API: `featurelifted.PythonCode`
- risk: `none`
- A001 `assert` L28: `parsed.undeclared_identifiers == {'x', 'y', 'z'}`
- A002 `assert` L29: `parsed.declared_identifiers == set()`

### `public_tests/test_public_api.py::test_def_tag_parses`

- mapping: `B001, B002`
- API: `featurelifted.Lexer, featurelifted.Lexer.parse, featurelifted.parsetree, featurelifted.parsetree.DefTag`
- risk: `none`
- A001 `assert` L35: `isinstance(tag, parsetree.DefTag)`
- A002 `assert` L36: `tag.keyword == 'def'`
- A003 `assert` L37: `tag.attributes['name'] == 'foo()'`

### `hidden_tests/test_hidden_behavior.py::test_percent_escape_in_template`

- mapping: `B001`
- API: `featurelifted.Lexer, featurelifted.Lexer.parse, featurelifted.parsetree, featurelifted.parsetree.ControlLine, featurelifted.parsetree.Text`
- risk: `none`
- A001 `assert` L13: `isinstance(node.nodes[0], parsetree.Text)`
- A002 `assert` L14: `node.nodes[0].content == '%'`
- A003 `assert` L15: `isinstance(node.nodes[2], parsetree.ControlLine)`
- A004 `assert` L16: `node.nodes[2].keyword == 'if'`

### `hidden_tests/test_hidden_behavior.py::test_unclosed_tag_raises_syntax`

- mapping: `B001, B004`
- API: `featurelifted.Lexer, featurelifted.Lexer.parse, featurelifted.SyntaxException`
- risk: `exception_semantics`
- A001 `raises` L20: `pytest.raises(SyntaxException)`

### `hidden_tests/test_hidden_behavior.py::test_python_fragment_for_loop`

- mapping: `B003`
- API: `featurelifted.PythonFragment`
- risk: `none`
- A001 `assert` L26: `parsed.declared_identifiers == {'item'}`
- A002 `assert` L27: `parsed.undeclared_identifiers == {'items'}`

### `hidden_tests/test_hidden_behavior.py::test_expression_filter_escapes`

- mapping: `B001, B002`
- API: `featurelifted.Lexer, featurelifted.Lexer.parse, featurelifted.parsetree, featurelifted.parsetree.Expression`
- risk: `none`
- A001 `assert` L33: `isinstance(expr, parsetree.Expression)`
- A002 `assert` L35: `'value' in undeclared`
- A003 `assert` L36: `'h' not in undeclared`
- A004 `assert` L37: `'trim' not in undeclared`

### `hidden_tests/test_hidden_behavior.py::test_elif_partial_control_identifiers`

- mapping: `B002, B003`
- API: `featurelifted.PythonFragment`
- risk: `none`
- A001 `assert` L42: `'cond' in parsed.undeclared_identifiers`
- A002 `assert` L43: `'other' in parsed.undeclared_identifiers`

### `hidden_tests/test_hidden_behavior.py::test_invalid_partial_control_raises_compile`

- mapping: `B001, B002`
- API: `featurelifted.CompileException, featurelifted.PythonFragment`
- risk: `exception_semantics`
- A001 `raises` L47: `pytest.raises(CompileException)`

### `hidden_tests/test_hidden_behavior.py::test_no_mako_import_surface`

- mapping: `B006`
- API: `featurelifted.__file__`
- risk: `filesystem_resource`
- A001 `assert` L64: `not import_pattern.search(text)`

### `hidden_tests/test_required_api_surface.py::test_required_api_surface`

- mapping: `B005`
- API: `featurelifted.CompileException, featurelifted.Lexer, featurelifted.PythonCode, featurelifted.PythonFragment, featurelifted.SyntaxException, featurelifted.parsetree`
- risk: `none`
- A001 `assert` L14: `isinstance(Lexer, type)`
- A002 `assert` L15: `hasattr(Lexer, 'parse')`
- A003 `assert` L16: `parsetree is not None`
- A004 `assert` L17: `isinstance(PythonCode, type)`
- A005 `assert` L18: `isinstance(PythonFragment, type)`
- A006 `assert` L19: `PythonFragment is not None`
- A007 `assert` L20: `PythonFragment is not None`
- A008 `assert` L21: `issubclass(SyntaxException, BaseException)`
- A009 `assert` L22: `issubclass(CompileException, BaseException)`

## Dependency / Oracle Evidence

- allowed dependencies: `MarkupSafe`
- forbidden imports: `mako`
- source entrypoints: `mako.lexer.Lexer, mako.lexer.Lexer.parse, mako.parsetree, mako.ast.PythonCode, mako.ast.PythonFragment, mako.ast.FunctionDecl, mako.pyparser.parse`
- oracle source files: `mako/exceptions.py, mako/compat.py, mako/util.py, mako/_ast_util.py, mako/pyparser.py, mako/ast.py, mako/filters.py, mako/pygen.py, mako/parsetree.py, mako/lexer.py`
- runtime dependencies: `MarkupSafe`
- oracle notes: Oracle copies lexer/parsetree/ast/pyparser closure only; excludes template, codegen, runtime, lookup, cache, and ext plugins.

## Machine Issues

- public_tests/test_public_api.py uses undeclared API reference featurelifted.parsetree.ControlLine
- public_tests/test_public_api.py uses undeclared API reference featurelifted.parsetree.DefTag
- public_tests/test_public_api.py uses undeclared API reference featurelifted.parsetree.Expression
- public_tests/test_public_api.py uses undeclared API reference featurelifted.parsetree.TemplateNode
- public_tests/test_public_api.py uses undeclared API reference featurelifted.parsetree.Text
- hidden_tests/test_hidden_behavior.py uses undeclared API reference featurelifted.parsetree.ControlLine
- hidden_tests/test_hidden_behavior.py uses undeclared API reference featurelifted.parsetree.Expression
- hidden_tests/test_hidden_behavior.py uses undeclared API reference featurelifted.parsetree.Text
