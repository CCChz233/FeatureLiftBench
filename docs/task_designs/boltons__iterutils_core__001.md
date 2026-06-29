# Task Design: `boltons__iterutils_core__001`

Status: agent-calibrated

## Practical reuse

1. **Reuse module** — Standalone iterator/chunking/remap utilities for ETL and config tree walks.
2. **Who imports it** — Pipelines needing boltons-style `chunked`/`remap` without vendoring all boltons modules.
3. **Why not copy-all** — Curated snapshot includes sibling boltons modules; compact closure keeps iterutils only.

## Module Probes

| Probe | Remove module | Hidden test(s) that must fail |
| --- | --- | --- |
| Chunked fill | `featurelifted/iterutils.py` | `test_chunked_fill_padding` |
| Unique key | `featurelifted/iterutils.py` | `test_unique_key_preserves_first_of_length` |
| Bucketize transform | `featurelifted/iterutils.py` | `test_bucketize_value_transform` |

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
| | | | | | Flash deferred (B-tier exception batch) |
