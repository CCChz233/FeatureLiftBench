# FeatureLift Task: pytest skipif condition evaluator

Extract pytest skipif/xfail condition evaluation semantics as a standalone package.

## Target API

- Import: `from featurelifted import Mark, EvalContext, evaluate_condition`
- Callable: `featurelifted.evaluate_condition`
- Signature: `evaluate_condition(context: EvalContext, mark: Mark, condition: object) -> tuple[bool, str]`

## Excluded Behavior

- full skip/xfail mark application during test run
- pytest item/collector integration
- xfail strict/run/raises handling
- CLI, original tests, docs, packaging metadata

## Constraints

- Output package: `featurelifted`
- Network access: `false`
- Forbidden upstream imports: `pytest`, `_pytest`

<!-- featureliftbench:behavior-clauses:start -->
## Public Behavior Contract

The stable clause IDs below define the public behavior contract. Hidden tests may exercise
these clauses but do not introduce additional requirements.

- **B001** — evaluate string conditions via compile/eval with allowed globals
- **B002** — evaluate boolean conditions directly
- **B003** — merge markeval_namespace mappings into eval globals
- **B004** — return (result, reason) tuple with default reason for string conditions
- **B005** — the declared target API remains importable and preserves upstream-observable semantics within the included and excluded feature scope
- **B006** — the submitted package does not import forbidden upstream packages: pytest, _pytest
<!-- featureliftbench:behavior-clauses:end -->
