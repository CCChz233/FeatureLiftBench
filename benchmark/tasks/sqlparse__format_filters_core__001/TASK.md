# FeatureLift Task: SQL format and filters core

Extract sqlparse's SQL formatting behavior composed from filter-stack modules as a standalone package.

## Target API

- Import: `from featurelifted import format; from featurelifted.exceptions import SQLParseError`
- Callable: `featurelifted.format`
- Signature: `format(sql: str, encoding: str | None = None, **options) -> str`

## Excluded Behavior

- SQL parsing into navigable token trees
- multi-statement script splitting
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

- **B001** — format common SQL with keyword case, identifier case, comment stripping, reindentation, indentation width, and operator spacing
- **B002** — preserve original formatter behavior for comments, whitespace, string literals, aliases, and nested expressions
- **B003** — validate formatter options and reject invalid values
- **B004** — the declared target API remains importable and preserves upstream-observable semantics within the included and excluded feature scope
- **B005** — the submitted package does not import forbidden upstream packages: sqlparse
<!-- featureliftbench:behavior-clauses:end -->
