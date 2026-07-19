# FeatureLift Task: Pricing rules engine

Extract VibeShop line-item pricing rules (category, tier, membership) as a standalone package.

## Target API

- Import: `from featurelifted import PricingContext, compute_line_price`
- Callable: `featurelifted.compute_line_price`
- Signature: `compute_line_price(unit_price: float, quantity: int, category: str, *, context: PricingContext | None = None) -> float`

## Excluded Behavior

- Flask-ish routes and HTTP handlers
- YAML bootstrap and config merge
- CSV import pipeline
- legacy calc_price_v1 and calc_price_legacy helpers
- global app factory and middleware clutter
- original project tests and CLI entrypoints

## Constraints

- Output package: `featurelifted`
- Network access: `false`
- Forbidden upstream imports: `vibe_app`

<!-- featureliftbench:behavior-clauses:start -->
## Public Behavior Contract

The stable clause IDs below define the public behavior contract. Hidden tests may exercise
these clauses but do not introduce additional requirements.

- **B001** — compute line totals from unit price, quantity, and category
- **B002** — apply category multipliers from pricing config
- **B003** — apply highest applicable quantity tier multiplier
- **B004** — apply membership discount when PricingContext.is_member is true
- **B005** — round totals using configured decimal precision
- **B006** — the declared target API remains importable and preserves upstream-observable semantics within the included and excluded feature scope
- **B007** — the submitted package does not import forbidden upstream packages: vibe_app
<!-- featureliftbench:behavior-clauses:end -->
