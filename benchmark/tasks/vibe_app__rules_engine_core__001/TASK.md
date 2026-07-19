# FeatureLift Task: Business rules engine

Extract VibeShop rules evaluation (conditions, actions, priority) as a standalone package.

## Target API

- Import: `from featurelifted import Rule, RulesEngine, evaluate_rules; from featurelifted.state import GLOBAL_STATE, reset_state`
- Callable: `featurelifted.evaluate_rules`
- Signature: `evaluate_rules(facts: dict, rules: list[Rule]) -> dict`

## Excluded Behavior

- Flask-ish routes and HTTP handlers
- YAML bootstrap and pricing computation
- evaluate_rules_v1 and evaluate_rules_legacy wrong helpers
- CSV import pipeline and app factory clutter
- original project tests and CLI entrypoints

## Constraints

- Output package: `featurelifted`
- Network access: `false`
- Forbidden upstream imports: `vibe_app`

<!-- featureliftbench:behavior-clauses:start -->
## Public Behavior Contract

The stable clause IDs below define the public behavior contract. Hidden tests may exercise
these clauses but do not introduce additional requirements.

- **B001** — match field conditions with eq/gt/gte/in/contains operators
- **B002** — apply set/inc/append actions to facts mappings
- **B003** — evaluate rules in descending priority order
- **B004** — track evaluation count in GLOBAL_STATE registry
- **B005** — the declared target API remains importable and preserves upstream-observable semantics within the included and excluded feature scope
- **B006** — the submitted package does not import forbidden upstream packages: vibe_app
<!-- featureliftbench:behavior-clauses:end -->
