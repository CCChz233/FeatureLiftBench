# FeatureLift Task: ORM query builder and SQL AST

Extract a task-scoped subset of `vibe_app` into a standalone `featurelifted` package.

The submitted implementation must not import the upstream package or read from `repo/` at runtime, must not use the network, and must not depend on external services. Use only the standard library unless the task lockfile allows otherwise.

## Target API

```python
from featurelifted import (
    compile_query,
    Query,
    state,
)
```

## Required API Details

- `Query(_columns: 'list[str]' = <factory>, _table: 'str | None' = None, _where: 'list[tuple[str, str, Any]]' = <factory>, _joins: 'list[tuple[str, str, str, str]]' = <factory>) -> None` class constructor
  - `Query.build_ast(self) -> 'SelectNode'`
- `compile_query(query: 'Query') -> 'str'`
- `state` module must be importable
  - `state.GLOBAL_STATE` constant must exist
  - `state.reset_state() -> 'None'`

## Required Behavior

- The extracted feature must support this observable behavior: build SELECT queries with columns, FROM table, WHERE predicates, and INNER joins. Required observable cases include simple select where; build ast records columns and predicates; join and multiple predicates.
- The extracted feature must support this observable behavior: materialize immutable SQL AST nodes from Query.build_ast. Required observable cases include compile query updates last sql.
- The extracted feature must support this observable behavior: compile AST nodes and Query objects to parameterized SQL strings. Required observable cases include compile query updates last sql.
- The extracted feature must support this observable behavior: track compiled query AST payloads in GLOBAL_STATE. Required observable cases include build ast tracks global state.
- The extracted feature must support this observable behavior: support eq/neq/gt/gte/lt/lte comparison operators in WHERE clauses. Required observable cases include join and multiple predicates.
- The package exposes the required task API paths `featurelifted.Query`, `featurelifted.Query.build_ast`, `featurelifted.compile_query`, `featurelifted.state`, `featurelifted.state.GLOBAL_STATE`, `featurelifted.state.reset_state` with the kinds and callable signatures listed in this contract.

## Constraints

- Forbidden imports: `vibe_app`.
- Do not implement Flask-ish routes and HTTP handlers.
- Do not implement YAML bootstrap, pricing, CSV, and session modules.
- Do not implement compile_query_v1 and build_query_legacy wrong helpers.
- Do not implement database drivers and runtime query execution.
- Do not implement original project tests and CLI entrypoints.

## Public vs Hidden Tests

Benchmark evaluator tests remain private. Each evaluator test maps to the public behaviors above and only deepens examples, boundaries, or combinations within those declared behaviors.

<!-- featureliftbench:behavior-clauses:start -->
## Public Behavior Contract

The stable clause IDs below define the public behavior contract. Hidden tests may exercise these clauses but do not introduce additional requirements.

- **B001** — The extracted feature must support this observable behavior: build SELECT queries with columns, FROM table, WHERE predicates, and INNER joins. Required observable cases include simple select where; build ast records columns and predicates; join and multiple predicates.
- **B002** — The extracted feature must support this observable behavior: materialize immutable SQL AST nodes from Query.build_ast. Required observable cases include compile query updates last sql.
- **B003** — The extracted feature must support this observable behavior: compile AST nodes and Query objects to parameterized SQL strings. Required observable cases include compile query updates last sql.
- **B004** — The extracted feature must support this observable behavior: track compiled query AST payloads in GLOBAL_STATE. Required observable cases include build ast tracks global state.
- **B005** — The extracted feature must support this observable behavior: support eq/neq/gt/gte/lt/lte comparison operators in WHERE clauses. Required observable cases include join and multiple predicates.
- **B006** — The package exposes the required task API paths `featurelifted.Query`, `featurelifted.Query.build_ast`, `featurelifted.compile_query`, `featurelifted.state`, `featurelifted.state.GLOBAL_STATE`, `featurelifted.state.reset_state` with the kinds and callable signatures listed in this contract.
- **B007** — the submitted package does not import forbidden upstream packages: vibe_app.
<!-- featureliftbench:behavior-clauses:end -->
