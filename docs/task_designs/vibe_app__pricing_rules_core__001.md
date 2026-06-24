# Task Design: vibe_app__pricing_rules_core__001

Status: oracle-verified

## Why This Task

Extract canonical pricing from a vibe-coded shop app where three similar helpers exist in `utils.py` but only `compute_line_price` matches production semantics tied to tier/category YAML rules.

## Source

| Field | Value |
| --- | --- |
| Source repo | `sources/vibe_app/` |
| Commit | curated |
| License | MIT |
| Language | Python |
| Difficulty | hard |
| Tags | extreme, multi-task-repo, functional-discriminator, legacy_vibe_clutter |

## Target Feature

### Source entrypoints

- `vibe_app.utils.compute_line_price`
- `vibe_app.pricing.rules.PricingContext`

### Output API

```python
from featurelifted import PricingContext, compute_line_price
```

## Public Tests

- Category multiplier adjusts line totals.
- Member discount combines with tier multiplier.

## Hidden Tests

- Tier boundary selects highest applicable multiplier.
- Unknown categories fall back to default multiplier.

## Module Probes

| Probe | Remove module | Hidden test(s) that must fail |
| --- | --- | --- |
| Tier lookup | `pricing/tiers.py` | `test_tier_boundary_uses_highest_applicable` |
| Category discounts | `pricing/discounts.py` | `test_unknown_category_falls_back_to_default` |

## Manual Oracle Closure Plan

Expected closure shape:

```text
featurelifted/
  __init__.py
  helpers/money.py
  pricing/
    rules.py
    tiers.py
    discounts.py
```
