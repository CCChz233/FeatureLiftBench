# FeatureLift Task: ORM query builder and SQL AST

Extract VibeShop's mini Query-to-SQL AST compiler as a standalone package.

## Target API

- Import: `from featurelifted import Query, compile_query; from featurelifted.state import GLOBAL_STATE, reset_state`
- Callable: `featurelifted.compile_query`
- Signature: `compile_query(query: Query) -> str`

## Excluded Behavior

- Flask-ish routes and HTTP handlers
- YAML bootstrap, pricing, CSV, and session modules
- compile_query_v1 and build_query_legacy wrong helpers
- database drivers and runtime query execution
- original project tests and CLI entrypoints

## Constraints

- Output package: `featurelifted`
- Network access: `false`
- Forbidden upstream imports: `vibe_app`

<!-- featureliftbench:behavior-clauses:start -->
## Public Behavior Contract

The stable clause IDs below define the public behavior contract. Hidden tests may exercise
these clauses but do not introduce additional requirements.

- **B001** — build SELECT queries with columns, FROM table, WHERE predicates, and INNER joins
- **B002** — materialize immutable SQL AST nodes from Query.build_ast
- **B003** — compile AST nodes and Query objects to parameterized SQL strings
- **B004** — track compiled query AST payloads in GLOBAL_STATE
- **B005** — support eq/neq/gt/gte/lt/lte comparison operators in WHERE clauses
- **B006** — the declared target API remains importable and preserves upstream-observable semantics within the included and excluded feature scope
- **B007** — the submitted package does not import forbidden upstream packages: vibe_app
<!-- featureliftbench:behavior-clauses:end -->
