# Task Design: `intervaltree__interval_tree_core__001`

Status: agent-calibrated

## Why This Task

Interval trees are widely reused for scheduling, genomics, and resource allocation. The upstream package couples Interval half-open semantics, SortedDict boundary indexing, and self-balancing Node mutations—more than a list scan wrapper.

## Practical reuse

1. **Reuse module** — Standalone mutable interval index supporting overlap queries and range edits.
2. **Who imports it** — Services indexing time ranges, memory segments, or annotation spans without vendoring upstream tests/benchmarks.
3. **Why not copy-all** — Upstream bundles extensive test matrices and optimality harnesses; compact closure keeps the four runtime modules only.

## Source

| Field | Value |
| --- | --- |
| Source repo | https://github.com/chaimleib/intervaltree |
| Commit | `1bc406e1f441577c4e421fc51aba2ab67fbd97fb` |
| License | Apache-2.0 |
| Difficulty | hard |
| Tags | batch-1, functional-discriminator, data_model_coupling |

## Module Probes

| Probe | Remove module | Hidden test(s) that must fail |
| --- | --- | --- |
| Node search | `featurelifted/node.py` | `test_complex_point_query` |
| Chop mutation | `featurelifted/intervaltree.py` | `test_chop_datafunc` |
| Interval semantics | `featurelifted/interval.py` | `test_distinct_data_same_range` |

## Public Tests

- Add intervals and point overlap query
- Remove by Interval object
- Range overlap boolean and set query

## Hidden Tests

- `chop` splits and optional `datafunc` relabeling
- `remove_overlap` with multiple intersecting intervals
- `envelop` vs `overlap` distinction
- Distinct data on identical ranges (set semantics)
- `remove_envelop` partial deletion
- Complex multi-interval point query
- No runtime `intervaltree` import surface

## Manual Oracle Closure Plan

| Check | Target | Result |
| --- | --- | --- |
| Public tests | pass | pass |
| Hidden tests | pass | pass |
| Forbidden import check | pass | pass |
| ExtractionRatio | 0.20 – 0.60 | 0.312 |
| Copy-All ExtractionRatio | > oracle + margin | 0.998 (Δ=0.686) |
| Module probes | ≥3 verified | 3/3 OK |

## Agent Calibration

| Run | Model | Passed | ExtractionRatio | final_score | Notes |
| --- | --- | --- | ---: | ---: | --- |
| | | | | | |
