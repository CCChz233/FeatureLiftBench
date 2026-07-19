# FeatureLift Task: SQL parse, split, and format core

Extract sqlparse's SQL statement parsing, splitting, token tree, and common formatting behavior as a standalone package.

## Target API

- Import: `from featurelifted import parse, parsestream, split, format, sql, tokens; from featurelifted.exceptions import SQLParseError`
- Callable: `featurelifted.parse`
- Signature: `parse(sql: str, encoding: str | None = None) -> tuple[Statement, ...]`

## Excluded Behavior

- command line interface
- original project tests
- documentation and release tooling
- packaging metadata from the original project
- dialect-perfect SQL validation

## Constraints

- Output package: `featurelifted`
- Network access: `false`
- Forbidden upstream imports: `sqlparse`

<!-- featureliftbench:behavior-clauses:start -->
## Public Behavior Contract

The stable clause IDs below define the public behavior contract. Hidden tests may exercise
these clauses but do not introduce additional requirements.

- **B001** — parse SQL text into Statement token trees
- **B002** — split multi-statement SQL scripts while respecting strings, comments, and nesting
- **B003** — support common token tree traversal and identifier helpers
- **B004** — format common SQL with keyword case, identifier case, comment stripping, reindentation, indentation width, and operator spacing
- **B005** — preserve original behavior for comments, whitespace, string literals, aliases, functions, nested expressions, CTEs, CASE expressions, and common DDL/DML
- **B006** — the declared target API remains importable and preserves upstream-observable semantics within the included and excluded feature scope
- **B007** — the submitted package does not import forbidden upstream packages: sqlparse
<!-- featureliftbench:behavior-clauses:end -->
