# sqlglot__parse_transpile_core__001

- release: `external50`
- lift: `Composite`
- coupling: `parser_state_coupling`
- strict validation: `PASS`
- tests/assertions: `9/14`

## Required API

- `featurelifted.parse_one` (function) `(sql: str, read: str | None = None)`
- `featurelifted.parse` (function) `(sql: str, read: str | None = None)`
- `featurelifted.transpile` (function) `(sql: str, read: str | None = None, write: str | None = None, pretty: bool = False)`
- `featurelifted.exp.Select` (class)
- `featurelifted.exp.Column` (class)
- `featurelifted.errors.ParseError` (exception)

## Public Behaviors

- **B001**: The extracted feature must support this observable behavior: parse_one/parse into Select expressions and raise ParseError on invalid SQL. Required observable cases include parse one select; parse error; parse multiple.
- **B002**: The extracted feature must support this observable behavior: transpile across sqlite/postgres/mysql. Required observable cases include transpile sqlite to postgres; transpile mysql to sqlite; mysql dialect backticks.
- **B003**: The extracted feature must support this observable behavior: Expression.sql with pretty formatting. Required observable cases include pretty sql.
- **B004**: Frozen dialects for required tests are sqlite, postgres, and mysql only.
- **B005**: The package exposes the required task API paths `featurelifted.parse_one`, `featurelifted.parse`, `featurelifted.transpile`, `featurelifted.exp.Select`, `featurelifted.exp.Column`, `featurelifted.errors.ParseError` with the kinds listed in this contract.
- **B006**: the submitted package does not import forbidden upstream packages: sqlglot.

## Tests

### `public_tests/test_public_api.py::test_parse_one_select`

- mapping: `B001`
- API: `featurelifted.errors, featurelifted.exp, featurelifted.exp.Select, featurelifted.parse_one`
- risk: `none`
- A001 `assert` L9: `isinstance(node, exp.Select)`
- A002 `assert` L11: `rendered == 'SELECT a FROM t'`

### `public_tests/test_public_api.py::test_transpile_sqlite_to_postgres`

- mapping: `B002`
- API: `featurelifted.errors, featurelifted.transpile`
- risk: `none`
- A001 `assert` L16: `out == ['SELECT a FROM t']`

### `public_tests/test_public_api.py::test_parse_error`

- mapping: `B003`
- API: `featurelifted.errors, featurelifted.parse_one`
- risk: `none`
- A001 `assert` L22: `False`

### `hidden_tests/test_hidden_behavior.py::test_parse_multiple`

- mapping: `B001`
- API: `featurelifted.exp, featurelifted.exp.Select, featurelifted.parse`
- risk: `none`
- A001 `assert` L11: `len(nodes) == 2`
- A002 `assert` L12: `all((isinstance(n, exp.Select) for n in nodes))`

### `hidden_tests/test_hidden_behavior.py::test_mysql_dialect_backticks`

- mapping: `B002`
- API: `featurelifted.exp, featurelifted.exp.Select, featurelifted.parse_one`
- risk: `none`
- A001 `assert` L17: `isinstance(node, exp.Select)`
- A002 `assert` L19: `'a' in sql`

### `hidden_tests/test_hidden_behavior.py::test_pretty_sql`

- mapping: `B003`
- API: `featurelifted.parse_one`
- risk: `none`
- A001 `assert` L25: `'SELECT' in sql and 'FROM' in sql`

### `hidden_tests/test_hidden_behavior.py::test_transpile_mysql_to_sqlite`

- mapping: `B004`
- API: `featurelifted.transpile`
- risk: `none`
- A001 `assert` L30: `isinstance(out, list) and out and ('x' in out[0])`

### `hidden_tests/test_hidden_behavior.py::test_no_upstream_import_surface`

- mapping: `B006`
- API: `featurelifted.__file__`
- risk: `filesystem_resource`
- A001 `assert` L39: `not pattern.search(path.read_text(encoding='utf-8'))`

### `hidden_tests/test_required_api_surface.py::test_required_api_surface`

- mapping: `B005`
- API: `featurelifted.errors, featurelifted.exp, featurelifted.exp.Column, featurelifted.exp.Select, featurelifted.parse, featurelifted.parse_one, featurelifted.transpile`
- risk: `none`
- A001 `assert` L6: `callable(parse_one) and callable(parse) and callable(transpile)`
- A002 `assert` L7: `exp.Select is not None and exp.Column is not None`
- A003 `assert` L8: `issubclass(ParseError, Exception)`

## Dependency / Oracle Evidence

- allowed dependencies: `none`
- forbidden imports: `sqlglot`
- source entrypoints: `none`
- oracle source files: `sqlglot/__init__.py, sqlglot/expressions.py, sqlglot/dialects/`
- runtime dependencies: `none`
- oracle notes: parse/transpile for sqlite/postgres/mysql only.
- behavior contract lacks a completed review_status
- behavior contract schema_version missing or unsupported
