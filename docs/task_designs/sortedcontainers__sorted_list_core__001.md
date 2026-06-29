# Task Design: `sortedcontainers__sorted_list_core__001`

Status: agent-calibrated

## Why This Task

SortedList is a reusable ordered-sequence building block (scheduling windows, leaderboard ranks, duplicate-tolerant indexes). Its performance model depends on sublist load factors, a segment index for O(log n) positional access, and delete-merge invariants—stronger discrimination than flat-list + bisect shims.

## Practical reuse

1. **Reuse module** — Standalone sorted mutable sequence with fast bisect, slice-like reads, and duplicate-aware count/index.
2. **Who imports it** — Services needing in-memory sorted runs (metrics buffers, game leaderboards, interval tables) without vendoring SortedDict/SortedSet.
3. **Why not copy-all** — Upstream bundles SortedKeyList/SortedDict/SortedSet and benchmark harnesses; compact closure keeps the list core only.

## Source

| Field | Value |
| --- | --- |
| Source repo | https://github.com/grantjenks/python-sortedcontainers |
| Commit | `a1f52d6713dd2c2713a881d4f4d86ed68ff71cab` (v2.4.0) |
| License | Apache-2.0 |
| Difficulty | hard |
| Tags | batch-1, functional-discriminator, data_model_coupling |

## Module Probes

| Probe | Remove module | Hidden test(s) that must fail |
| --- | --- | --- |
| Index tree | `featurelifted/_index.py` | `test_hidden_bisect_with_small_load` |
| Delete merge | `featurelifted/_delete_ops.py` | `test_hidden_delete_random_invariants` |
| Invariants | `featurelifted/_invariants.py` | `test_hidden_check_invariants` |

## Public Tests

- add/update preserves sorted order
- bisect_left/right and count on duplicates
- discard vs remove semantics

## Hidden Tests

- bisect after `_reset(17)` with duplicate ranges
- irange inclusive tuple bounds and reverse islice
- random delete with `_check` under small load
- index windows on duplicate runs with negative start
- sublist `_lists`/`_maxes` invariants after growth
- no runtime `sortedcontainers` import surface

## Manual Oracle Closure Plan

| Check | Target | Result |
| --- | --- | --- |
| Public tests | pass | pass (oracle, copy_all, naive) |
| Hidden tests | pass | pass (oracle, copy_all); **fail** (naive) |
| Forbidden import check | pass | pass |
| Oracle LOC | ~1200+ | 1212 |
| Source repo Python LOC | ~8300 (snapshot incl. tests) | 8291 |
| ExtractionRatio | 0.20 – 0.60 | oracle **0.146** (compact — below band) |
| Copy-All ExtractionRatio | > oracle + margin | **0.349** (Δ=0.203) |
| Module probes | ≥3 verified | **3/3 OK** |

Expected closure shape:

```text
featurelifted/
  __init__.py
  _index.py
  _delete_ops.py
  _invariants.py
  sortedlist.py
```

## Agent Calibration

| Run | Model | Passed | ExtractionRatio | final_score | Notes |
| --- | --- | --- | ---: | ---: | --- |
| `sortedcontainers__sorted_list_core__001-flash-001` | deepseek_v4_flash | no (hidden fail) | 0.130 | 0.0 | **A-tier:** pub pass / hidden fail on `_reset`+`bisect` |

## Go / No-Go Criteria

- Oracle compact vs copy-all separation on extraction
- Naive flat-list baseline fails hidden (islice/irange/invariants)
- Module probes verified
- Flash calibration pending (not run in this staging pass)
