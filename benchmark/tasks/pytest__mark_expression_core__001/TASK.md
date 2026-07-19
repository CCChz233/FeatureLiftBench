# FeatureLift Task: pytest mark expression evaluator

Extract pytest -m mark expression compile/evaluate logic as a standalone package.

## Target API

- Import: `from featurelifted import Expression, ParseError; from featurelifted import expression; from featurelifted.expression import Scanner, TokenType`
- Callable: `featurelifted.Expression.compile`
- Signature: `compile(input: str) -> Expression`

## Excluded Behavior

- full pytest collection and test running
- keyword -k matching
- marker registration and strict markers
- CLI, original tests, docs, packaging metadata

## Constraints

- Output package: `featurelifted`
- Network access: `false`
- Forbidden upstream imports: `pytest`, `_pytest`

<!-- featureliftbench:behavior-clauses:start -->
## Public Behavior Contract

The stable clause IDs below define the public behavior contract. Hidden tests may exercise
these clauses but do not introduce additional requirements.

- **B001** — parse and compile mark expressions with and/or/not
- **B002** — evaluate expressions against a matcher callback
- **B003** — support identifier kwargs syntax for parameterized markers
- **B004** — empty expression evaluates to False
- **B005** — the declared target API remains importable and preserves upstream-observable semantics within the included and excluded feature scope
- **B006** — the submitted package does not import forbidden upstream packages: pytest, _pytest
<!-- featureliftbench:behavior-clauses:end -->
