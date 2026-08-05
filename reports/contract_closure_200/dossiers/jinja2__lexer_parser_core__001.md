# jinja2__lexer_parser_core__001

- release: `frozen_python150`
- lift: `Adapted`
- coupling: `unknown`
- strict validation: `FAIL`
- tests/assertions: `6/19`

## Required API

- `featurelifted.Environment` (class) `(block_start_string: 'str' = '{%', block_end_string: 'str' = '%}', variable_start_string: 'str' = '{{', variable_end_string: 'str' = '}}', comment_start_string: 'str' = '{#', comment_end_string: 'str' = '#}', line_statement_prefix: 't.Optional[str]' = None, line_comment_prefix: 't.Optional[str]' = None, trim_blocks: 'bool' = False, lstrip_blocks: 'bool' = False, newline_sequence: '"te.Literal[\'\\\\n\', \'\\\\r\\\\n\', \'\\\\r\']"' = '\n', keep_trailing_newline: 'bool' = False) -> 'None'`
- `featurelifted.Environment.parse` (method) `(self, source: 'str', name: 't.Optional[str]' = None, filename: 't.Optional[str]' = None) -> 'nodes.Template'`
- `featurelifted.nodes` (module)
- `featurelifted.lexer` (module)
- `featurelifted.lexer.Lexer` (class) `(environment: 'Environment') -> None`
- `featurelifted.lexer.Lexer.tokenize` (method) `(self, source: str, name: Optional[str] = None, filename: Optional[str] = None, state: Optional[str] = None) -> TokenStream`
- `featurelifted.parser` (module)
- `featurelifted.parser.Parser` (class) `(environment: 'Environment', source: str, name: Optional[str] = None, filename: Optional[str] = None, state: Optional[str] = None) -> None`

## Public Behaviors

- **B001**: The extracted feature must support this observable behavior: tokenize template source into token streams. Required observable cases include lex returns token types; parser module required for if elif.
- **B002**: The extracted feature must support this observable behavior: parse templates into AST node trees. Required observable cases include parse variable output; parse for loop structure; parser module required for if elif.
- **B003**: The extracted feature must support this observable behavior: support block, variable, comment, and statement delimiters. Required observable cases include lexer module required for raw blocks.
- **B004**: The extracted feature must support this observable behavior: preserve syntax error reporting with line numbers. Required observable cases include parser module required for if elif.
- **B005**: The package exposes the required task API paths `featurelifted.Environment`, `featurelifted.Environment.parse`, `featurelifted.nodes`, `featurelifted.lexer`, `featurelifted.lexer.Lexer`, `featurelifted.lexer.Lexer.tokenize`, `featurelifted.parser`, `featurelifted.parser.Parser` with the kinds and callable signatures listed in this contract.

## Tests

### `public_tests/test_public_api.py::test_parse_variable_output`

- mapping: `B002`
- API: `featurelifted.Environment, featurelifted.nodes, featurelifted.nodes.Name, featurelifted.nodes.Output, featurelifted.nodes.Template`
- risk: `none`
- A001 `assert` L8: `isinstance(tree, nodes.Template)`
- A002 `assert` L9: `len(tree.body) == 1`
- A003 `assert` L11: `isinstance(output, nodes.Output)`
- A004 `assert` L12: `any((isinstance(node, nodes.Name) and node.name == 'name' for node in output.nodes))`

### `public_tests/test_public_api.py::test_lex_returns_token_types`

- mapping: `B001`
- API: `featurelifted.Environment`
- risk: `none`
- A001 `assert` L19: `'block_begin' in types`
- A002 `assert` L20: `'name' in types`

### `hidden_tests/test_hidden_behavior.py::test_parse_for_loop_structure`

- mapping: `B002`
- API: `featurelifted.Environment, featurelifted.lexer, featurelifted.nodes, featurelifted.nodes.For, featurelifted.nodes.Output, featurelifted.parser`
- risk: `none`
- A001 `assert` L11: `isinstance(for_node, nodes.For)`
- A002 `assert` L12: `isinstance(for_node.body[0], nodes.Output)`

### `hidden_tests/test_hidden_behavior.py::test_lexer_module_required_for_raw_blocks`

- mapping: `B003`
- API: `featurelifted.Environment, featurelifted.lexer, featurelifted.parser`
- risk: `none`
- A001 `assert` L20: `'{{ x }}' in values`

### `hidden_tests/test_hidden_behavior.py::test_parser_module_required_for_if_elif`

- mapping: `B001, B002, B004`
- API: `featurelifted.Environment, featurelifted.lexer, featurelifted.nodes, featurelifted.nodes.If, featurelifted.parser`
- risk: `none`
- A001 `assert` L27: `isinstance(if_node, nodes.If)`
- A002 `assert` L28: `len(if_node.elif_) == 1`

### `hidden_tests/test_required_api_surface.py::test_required_api_surface`

- mapping: `B005`
- API: `featurelifted.Environment, featurelifted.lexer, featurelifted.nodes, featurelifted.parser`
- risk: `none`
- A001 `assert` L12: `isinstance(Environment, type)`
- A002 `assert` L13: `hasattr(Environment, 'parse')`
- A003 `assert` L14: `nodes is not None`
- A004 `assert` L15: `lexer is not None`
- A005 `assert` L16: `isinstance(getattr(lexer, 'Lexer'), type)`
- A006 `assert` L17: `hasattr(getattr(lexer, 'Lexer'), 'tokenize')`
- A007 `assert` L18: `parser is not None`
- A008 `assert` L19: `isinstance(getattr(parser, 'Parser'), type)`

## Dependency / Oracle Evidence

- allowed dependencies: `MarkupSafe`
- forbidden imports: `jinja2, jinja`
- source entrypoints: `jinja2.lexer.Lexer, jinja2.lexer.TokenStream, jinja2.parser.Parser, jinja2.environment.Environment.lex, jinja2.environment.Environment.parse, jinja2.nodes`
- oracle source files: `none`
- runtime dependencies: `none`
- oracle notes: Lexer/parser closure only. Compiler, runtime, loaders, filters excluded.

## Machine Issues

- public_tests/test_public_api.py uses undeclared API reference featurelifted.nodes.Name
- public_tests/test_public_api.py uses undeclared API reference featurelifted.nodes.Output
- public_tests/test_public_api.py uses undeclared API reference featurelifted.nodes.Template
- hidden_tests/test_hidden_behavior.py uses undeclared API reference featurelifted.nodes.For
- hidden_tests/test_hidden_behavior.py uses undeclared API reference featurelifted.nodes.If
- hidden_tests/test_hidden_behavior.py uses undeclared API reference featurelifted.nodes.Output
