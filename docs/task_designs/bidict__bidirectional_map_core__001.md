# Task Design: `bidict__bidirectional_map_core__001`

Status: agent-calibrated (B-tier exception promote)

## Why This Task

Bidirectional mappings are a common embedded data structure (config key↔id tables, enum registries). bidict couples forward/inverse backing stores, duplicate policies, and ordered linked-list invariants—stronger than a dict-plus-reverse shim.

## Practical reuse

1. **Reuse module** — Standalone bidirectional map with inverse views and duplicate handling.
2. **Who imports it** — Services mapping stable keys to values in both directions without vendoring full bidict docs/tests.
3. **Why not copy-all** — Upstream bundles benchmarks and extensive test harnesses; compact closure keeps runtime package only.

## Source

| Field | Value |
| --- | --- |
| Source repo | https://github.com/jab/bidict |
| Commit | `393bcfdc8edb861514d23aae55839272b5bd52f8` |
| License | MPL-2.0 |
| Difficulty | hard |
| Tags | batch-1, functional-discriminator, data_model_coupling |

## Module Probes

| Probe | Remove module | Hidden test(s) that must fail |
| --- | --- | --- |
| Duplicate policy | `featurelifted/_dup.py` | `test_on_dup_raise_value_collision` |
| Ordered list | `featurelifted/_orderedbase.py` | `test_ordered_move_to_end` |
| Inverse sync | `featurelifted/_base.py` | `test_bidict_inverse_reflects_updates` |

## Public Tests

- Forward and inverse lookup on `bidict`
- Live inverse after mutation
- `frozenbidict` read-only surface

## Hidden Tests

- `ON_DUP_RAISE` value collision → `ValueDuplicationError`
- Key+value duplication → `KeyAndValueDuplicationError`
- `OrderedBidict.move_to_end` ordering
- `frozenbidict` hash stability
- `inverted()` iterator helper
- No runtime `bidict` import surface

## Manual Oracle Closure Plan

| Check | Target | Result |
| --- | --- | --- |
| Public tests | pass | TBD |
| Hidden tests | pass | TBD |
| Forbidden import check | pass | TBD |
| ExtractionRatio | 0.20 – 0.60 | TBD |
| Copy-All ExtractionRatio | > oracle + margin | TBD |
| Module probes | ≥3 verified | TBD |

## Agent Calibration

| Run | Model | Passed | ExtractionRatio | final_score | Notes |
| --- | --- | --- | ---: | ---: | --- |
| `bidict__bidirectional_map_core__001-flash-001` | deepseek_v4_flash | yes (all tests) | 0.310 | 0.690 | **B-tier: 全过，ext≈0.31 vs oracle 0.48** |
