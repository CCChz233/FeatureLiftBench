# Task Design: `cachetools__cache_eviction_core__001`

Status: agent-calibrated (B-tier exception promote)

## Why This Task

Memoizing cache containers are a common embeddable utility (service response caches, rate-limit windows). cachetools couples eviction policy data structures, injectable timers for TTL, and decorator key hashing—harder than a dict with `functools.lru_cache`.

## Practical reuse

1. **Reuse module** — Standalone LRU/TTL/LFU cache types plus `cached` decorator key helpers.
2. **Who imports it** — Backend teams vendoring cache primitives without pulling async wrappers, CLI, or upstream test harnesses.
3. **Why not copy-all** — Upstream ships benchmarks, async variants, and `func.*` decorator shims; compact closure keeps eviction core only.

## Source

| Field | Value |
| --- | --- |
| Source repo | https://github.com/tkem/cachetools |
| Commit | `48284d73d0a8834c9c50f8d41bb99e6f93b2dfed` |
| License | MIT |
| Difficulty | hard |
| Tags | batch-1, functional-discriminator, data_model_coupling, parser_state_coupling |

## Module Probes

| Probe | Remove module | Hidden test(s) that must fail |
| --- | --- | --- |
| Eviction policies | `featurelifted/_caches.py` | `test_lru_eviction_order`, `test_ttl_expiry_with_mock_timer` |
| Key hashing | `featurelifted/keys.py` | `test_typedkey_distinguishes_value_types` |
| Cached wrapper | `featurelifted/_cached.py` | `test_cached_info_tracks_hits_and_misses` |

## Public Tests

- `LRUCache` basic get/set and length
- `TTLCache` stores values before expiry
- `cached` decorator memoizes on repeated calls

## Hidden Tests

- LRU touch order evicts least-recently-used keys
- LFU evicts lowest-frequency entry when full
- TTL expiry with injectable timer (monkeypatched fake clock)
- `maxsize` enforcement after many inserts
- `typedkey` distinguishes `int` vs `float` arguments
- `cached(..., info=True)` reports hits/misses via `cache_info()`
- No runtime `cachetools` import surface

## Manual Oracle Closure Plan

| Check | Target | Result |
| --- | --- | --- |
| Public tests | pass | pass (oracle, copy_all, naive) |
| Hidden tests | pass | pass (oracle, copy_all); **fail** (naive) |
| Forbidden import check | pass | pass |
| ExtractionRatio | 0.20 – 0.60 | **0.238** (oracle) |
| Copy-All ExtractionRatio | > oracle + margin | **1.000** |
| Module probes | ≥3 verified | 3/3 verified |

Expected closure shape:

```text
featurelifted/
  __init__.py
  _caches.py
  keys.py
  _cached.py
```

## Agent Calibration

| Run | Model | Passed | ExtractionRatio | final_score | Notes |
| --- | --- | --- | ---: | ---: | --- |
| `cachetools__cache_eviction_core__001-flash-001` | deepseek_v4_flash | yes (all tests) | 0.175 | 0.825 | **B-tier: 全过，ext≈0.18 vs oracle 0.24** |

## Go / No-Go Criteria

- Oracle compact closure passes; copy-all clearly higher extraction.
- Naive shallow LRU fails hidden TTL/LFU/typedkey/info tests.
- Module probes verified for `_caches.py`, `keys.py`, `_cached.py`.
