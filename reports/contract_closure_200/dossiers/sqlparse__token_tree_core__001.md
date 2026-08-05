# sqlparse__token_tree_core__001

- release: `frozen_python150`
- lift: `Adapted`
- coupling: `unknown`
- strict validation: `FAIL`
- tests/assertions: `5/20`

## Required API

- `featurelifted.parse` (function) `(sql: str, encoding: str | None = None) -> tuple[Statement, ...]`
- `featurelifted.parsestream` (function) `(stream: Union[str, IO[str]], encoding: str | None = None) -> collections.abc.Generator[Statement, None, None]`
- `featurelifted.sql` (module)
- `featurelifted.tokens` (module)

## Public Behaviors

- **B001**: The extracted feature must support this observable behavior: parse SQL text into Statement token trees. Required observable cases include parse returns statement tokens; token tree basics; token navigation and ancestor relationships.
- **B002**: The extracted feature must support this observable behavior: support token tree traversal and identifier helpers. Required observable cases include token tree basics; cte aliases and identifier helpers.
- **B003**: The extracted feature must support this observable behavior: preserve parent/ancestor relationships and comparison navigation. Required observable cases include token navigation and ancestor relationships.
- **B004**: The extracted feature must support this observable behavior: extract identifiers, aliases, and CTE structure from parsed statements. Required observable cases include cte aliases and identifier helpers.
- **B005**: The extracted feature must support this observable behavior: Identifier.get_name/get_real_name/get_alias and token ancestor navigation within Where clauses. Required observable cases include token navigation and ancestor relationships.
- **B006**: The package exposes the required task API paths `featurelifted.parse`, `featurelifted.parsestream`, `featurelifted.sql`, `featurelifted.tokens` with the kinds and callable signatures listed in this contract.

## Tests

### `public_tests/test_public_api.py::test_parse_returns_statement_tokens`

- mapping: `B001`
- API: `featurelifted.parse, featurelifted.sql, featurelifted.sql.Statement, featurelifted.tokens, featurelifted.tokens.Keyword, featurelifted.tokens.Keyword.DML`
- risk: `state_mutation`
- A001 `assert` L11: `isinstance(statement, sql.Statement)`
- A002 `assert` L12: `statement.get_type() == 'SELECT'`
- A003 `assert` L14: `flattened[0].value == 'select'`
- A004 `assert` L15: `flattened[0].ttype is T.Keyword.DML`
- A005 `assert` L16: `[token.value for token in flattened[:5]] == ['select', 'id', ',', 'name', 'from']`

### `public_tests/test_public_api.py::test_token_tree_basics`

- mapping: `B001, B002`
- API: `featurelifted.parse`
- risk: `none`
- A001 `assert` L22: `statement.tokens`
- A002 `assert` L23: `any((token.value.lower() == 'select' for token in statement.flatten()))`

### `hidden_tests/test_hidden_behavior.py::test_cte_aliases_and_identifier_helpers`

- mapping: `B002, B004`
- API: `featurelifted.parse, featurelifted.sql, featurelifted.sql.Identifier`
- risk: `none`
- A001 `assert` L13: `statement.get_type() == 'SELECT'`
- A002 `assert` L19: `('cte AS (SELECT id FROM users)', 'cte', 'cte', None) in identifiers`
- A003 `assert` L20: `('cte.id AS user_id', 'user_id', 'id', 'user_id') in identifiers`
- A004 `assert` L21: `('logs', 'logs', 'logs', None) in identifiers`

### `hidden_tests/test_hidden_behavior.py::test_token_navigation_and_ancestor_relationships`

- mapping: `B001, B003, B005`
- API: `featurelifted.parse, featurelifted.sql, featurelifted.sql.Comparison, featurelifted.sql.Where`
- risk: `none`
- A001 `assert` L30: `index == 2`
- A002 `assert` L31: `isinstance(comparison, sql.Comparison)`
- A003 `assert` L32: `comparison.value == 'id = 1'`
- A004 `assert` L33: `comparison.within(sql.Where)`
- A005 `assert` L34: `comparison.has_ancestor(where)`

### `hidden_tests/test_required_api_surface.py::test_required_api_surface`

- mapping: `B006`
- API: `featurelifted.parse, featurelifted.parsestream, featurelifted.sql, featurelifted.tokens`
- risk: `none`
- A001 `assert` L12: `callable(parse)`
- A002 `assert` L13: `callable(parsestream)`
- A003 `assert` L14: `sql is not None`
- A004 `assert` L15: `tokens is not None`

## Dependency / Oracle Evidence

- allowed dependencies: `none`
- forbidden imports: `sqlparse`
- source entrypoints: `sqlparse.parse, sqlparse.parsestream, sqlparse.sql.Token, sqlparse.sql.TokenList, sqlparse.sql.Statement, sqlparse.sql.Identifier, sqlparse.sql.IdentifierList, sqlparse.tokens`
- oracle source files: `none`
- runtime dependencies: `none`
- oracle notes: Parse and token-tree navigation closure. Formatter filters, CLI, tests, docs, and packaging metadata are excluded.

## Machine Issues

- public_tests/test_public_api.py uses undeclared API reference featurelifted.sql.Statement
- public_tests/test_public_api.py uses undeclared API reference featurelifted.tokens.Keyword
- public_tests/test_public_api.py uses undeclared API reference featurelifted.tokens.Keyword.DML
- hidden_tests/test_hidden_behavior.py uses undeclared API reference featurelifted.sql.Comparison
- hidden_tests/test_hidden_behavior.py uses undeclared API reference featurelifted.sql.Identifier
- hidden_tests/test_hidden_behavior.py uses undeclared API reference featurelifted.sql.Where
