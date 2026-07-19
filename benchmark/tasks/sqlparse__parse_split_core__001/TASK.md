# FeatureLift Task: SQL parse and split core

Extract sqlparse's SQL statement parsing and multi-statement splitting behavior as a standalone package.

## Target API

- Import: `from featurelifted import parse, parsestream, split, sql, tokens`
- Callable: `featurelifted.parse`
- Signature: `parse(sql: str, encoding: str | None = None) -> tuple[Statement, ...]`

## Excluded Behavior

- SQL formatting and formatter filters
- token tree navigation helpers beyond basic parse output
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
- **B003** — preserve statement-splitting behavior for semicolons inside quotes and comments
- **B004** — the declared target API remains importable and preserves upstream-observable semantics within the included and excluded feature scope
- **B005** — the submitted package does not import forbidden upstream packages: sqlparse
<!-- featureliftbench:behavior-clauses:end -->
