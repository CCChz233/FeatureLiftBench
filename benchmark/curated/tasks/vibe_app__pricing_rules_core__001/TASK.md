# FeatureLift Task: Pricing rules engine

Extract a task-scoped subset of `vibe_app` into a standalone `featurelifted` package.

The submitted implementation must not import the upstream package or read from `repo/` at runtime, must not use the network, and must not depend on external services. Use only the standard library unless the task lockfile allows otherwise.

## Target API

```python
from featurelifted import (
    compute_line_price,
    PricingContext,
)
```

## Required API Details

- `PricingContext(is_member: 'bool' = False, customer_tier: 'str | None' = None, config: 'dict[str, Any] | None' = None) -> None` class constructor
  - `PricingContext.is_member` attribute must exist on instances
- `compute_line_price(unit_price: 'float', quantity: 'int', category: 'str', *, context: 'PricingContext | None' = None) -> 'float'`

## Required Behavior

- The extracted feature must support this observable behavior: compute line totals from unit price, quantity, and category. Required observable cases include unknown category falls back to default.
- The extracted feature must support this observable behavior: apply category multipliers from pricing config. Required observable cases include category multiplier applied; unknown category falls back to default.
- The extracted feature must support this observable behavior: apply highest applicable quantity tier multiplier. Required observable cases include tier boundary uses highest applicable.
- The extracted feature must support this observable behavior: apply membership discount when PricingContext.is_member is true. Required observable cases include member discount with tier; unknown category falls back to default.
- The extracted feature must support this observable behavior: round totals using configured decimal precision. Required observable cases include unknown category falls back to default.
- The package exposes the required task API paths `featurelifted.PricingContext`, `featurelifted.PricingContext.is_member`, `featurelifted.compute_line_price` with the kinds and callable signatures listed in this contract.

## Constraints

- Forbidden imports: `vibe_app`.
- Do not implement Flask-ish routes and HTTP handlers.
- Do not implement YAML bootstrap and config merge.
- Do not implement CSV import pipeline.
- Do not implement legacy calc_price_v1 and calc_price_legacy helpers.
- Do not implement global app factory and middleware clutter.
- Do not implement original project tests and CLI entrypoints.

## Public vs Hidden Tests

Benchmark evaluator tests remain private. Each evaluator test maps to the public behaviors above and only deepens examples, boundaries, or combinations within those declared behaviors.

<!-- featureliftbench:behavior-clauses:start -->
## Public Behavior Contract

The stable clause IDs below define the public behavior contract. Hidden tests may exercise these clauses but do not introduce additional requirements.

- **B001** — The extracted feature must support this observable behavior: compute line totals from unit price, quantity, and category. Required observable cases include unknown category falls back to default.
- **B002** — The extracted feature must support this observable behavior: apply category multipliers from pricing config. Required observable cases include category multiplier applied; unknown category falls back to default.
- **B003** — The extracted feature must support this observable behavior: apply highest applicable quantity tier multiplier. Required observable cases include tier boundary uses highest applicable.
- **B004** — The extracted feature must support this observable behavior: apply membership discount when PricingContext.is_member is true. Required observable cases include member discount with tier; unknown category falls back to default.
- **B005** — The extracted feature must support this observable behavior: round totals using configured decimal precision. Required observable cases include unknown category falls back to default.
- **B006** — The package exposes the required task API paths `featurelifted.PricingContext`, `featurelifted.PricingContext.is_member`, `featurelifted.compute_line_price` with the kinds and callable signatures listed in this contract.
- **B007** — the submitted package does not import forbidden upstream packages: vibe_app.
<!-- featureliftbench:behavior-clauses:end -->
