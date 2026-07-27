# FeatureLift Task: Business rules engine

Extract a task-scoped subset of `vibe_app` into a standalone `featurelifted` package.

The submitted implementation must not import the upstream package or read from `repo/` at runtime, must not use the network, and must not depend on external services. Use only the standard library unless the task lockfile allows otherwise.

## Target API

```python
from featurelifted import (
    evaluate_rules,
    Rule,
    RulesEngine,
    state,
)
```

## Required API Details

- `Rule(name: 'str', conditions: 'list[dict[str, Any]]', actions: 'list[dict[str, Any]]', priority: 'int' = 0) -> None` class constructor
- `RulesEngine(rules: 'list[Rule]' = <factory>) -> None` class constructor
  - `RulesEngine.evaluate(self, facts: 'dict[str, Any]') -> 'dict[str, Any]'`
- `evaluate_rules(facts: 'dict[str, Any]', rules: 'list[Rule]') -> 'dict[str, Any]'`
- `state` module must be importable
  - `state.GLOBAL_STATE` constant must exist
  - `state.reset_state() -> 'None'`

## Required Behavior

- The extracted feature must support this observable behavior: match field conditions with eq/gt/gte/in/contains operators. Required observable cases include contains operator matches list membership.
- The extracted feature must support this observable behavior: apply set/inc/append actions to facts mappings. Required observable cases include rule applies set action when condition matches; inc action accumulates counter.
- The extracted feature must support this observable behavior: evaluate rules in descending priority order. Required observable cases include multiple rules apply in priority order; rules engine updates global state counter.
- The extracted feature must support this observable behavior: track evaluation count in GLOBAL_STATE registry. Required observable cases include rules engine updates global state counter.
- The package exposes the required task API paths `featurelifted.Rule`, `featurelifted.RulesEngine`, `featurelifted.RulesEngine.evaluate`, `featurelifted.evaluate_rules`, `featurelifted.state`, `featurelifted.state.GLOBAL_STATE`, `featurelifted.state.reset_state` with the kinds and callable signatures listed in this contract.

## Constraints

- Forbidden imports: `vibe_app`.
- Do not implement Flask-ish routes and HTTP handlers.
- Do not implement YAML bootstrap and pricing computation.
- Do not implement evaluate_rules_v1 and evaluate_rules_legacy wrong helpers.
- Do not implement CSV import pipeline and app factory clutter.
- Do not implement original project tests and CLI entrypoints.

## Public vs Hidden Tests

Benchmark evaluator tests remain private. Each evaluator test maps to the public behaviors above and only deepens examples, boundaries, or combinations within those declared behaviors.

<!-- featureliftbench:behavior-clauses:start -->
## Public Behavior Contract

The stable clause IDs below define the public behavior contract. Hidden tests may exercise these clauses but do not introduce additional requirements.

- **B001** — The extracted feature must support this observable behavior: match field conditions with eq/gt/gte/in/contains operators. Required observable cases include contains operator matches list membership.
- **B002** — The extracted feature must support this observable behavior: apply set/inc/append actions to facts mappings. Required observable cases include rule applies set action when condition matches; inc action accumulates counter.
- **B003** — The extracted feature must support this observable behavior: evaluate rules in descending priority order. Required observable cases include multiple rules apply in priority order; rules engine updates global state counter.
- **B004** — The extracted feature must support this observable behavior: track evaluation count in GLOBAL_STATE registry. Required observable cases include rules engine updates global state counter.
- **B005** — The package exposes the required task API paths `featurelifted.Rule`, `featurelifted.RulesEngine`, `featurelifted.RulesEngine.evaluate`, `featurelifted.evaluate_rules`, `featurelifted.state`, `featurelifted.state.GLOBAL_STATE`, `featurelifted.state.reset_state` with the kinds and callable signatures listed in this contract.
- **B006** — the submitted package does not import forbidden upstream packages: vibe_app.
<!-- featureliftbench:behavior-clauses:end -->
