# FeatureLift Task: SQL token tree navigation core

Extract sqlparse's SQL parsing and token tree traversal behavior as a standalone package.

## Target API

- Import: `from featurelifted import parse, parsestream; from featurelifted import sql, tokens`
- Callable: `featurelifted.parse`
- Signature: `parse(sql: str, encoding: str | None = None) -> tuple[Statement, ...]`

## Excluded Behavior

- multi-statement script splitting
- SQL formatting and formatter filters
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
- **B002** — support token tree traversal and identifier helpers
- **B003** — preserve parent/ancestor relationships and comparison navigation
- **B004** — extract identifiers, aliases, and CTE structure from parsed statements
- **B005** — Identifier.get_name/get_real_name/get_alias and token ancestor navigation within Where clauses
- **B006** — the declared target API remains importable and preserves upstream-observable semantics within the included and excluded feature scope
- **B007** — the submitted package does not import forbidden upstream packages: sqlparse
<!-- featureliftbench:behavior-clauses:end -->
