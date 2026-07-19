# FeatureLift Task: JSON logic evaluator

Extract jsonLogic into `featurelifted`.

<!-- featureliftbench:behavior-clauses:start -->
## Public Behavior Contract

The stable clause IDs below define the public behavior contract. Hidden tests may exercise
these clauses but do not introduce additional requirements.

- **B001** — jsonLogic evaluation
- **B002** — var paths
- **B003** — short-circuit and/or
- **B004** — the declared target API remains importable and preserves upstream-observable semantics within the included and excluded feature scope
- **B005** — the submitted package does not import forbidden upstream packages: json_logic
<!-- featureliftbench:behavior-clauses:end -->
