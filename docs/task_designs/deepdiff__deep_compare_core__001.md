# Task Design: `deepdiff__deep_compare_core__001`

Status: agent-calibrated (B-tier exception promote)

## Practical reuse

1. **Reuse module** — Structural diff for config/test assertions.
2. **Who imports it** — Pipelines needing DeepDiff path filters without search/delta stack.
3. **Why not copy-all** — search/delta/commands modules inflate copy-all closure.

## Module Probes

| Probe | Remove module | Hidden test(s) that must fail |
| --- | --- | --- |
| Diff engine | `featurelifted/diff.py` | `test_nested_dict_change` |
| Path parser | `featurelifted/path.py` | `test_exclude_paths_wildcard` |
| Model layer | `featurelifted/model.py` | `test_list_item_added` |

## Manual Oracle Closure Plan

| Check | Target | Result |
| --- | --- | --- |
| Public tests | pass | |
| Hidden tests | pass | |
| ExtractionRatio | 0.20 – 0.60 | |
| Copy-All delta | ≥ 0.25 | |

## Agent Calibration

| Run | Model | Passed | ExtractionRatio | final_score | Notes |
| --- | --- | --- | ---: | ---: | --- |
| | | | | | Flash deferred |
