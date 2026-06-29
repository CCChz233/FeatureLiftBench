# Task Design: `humanize__naturaltime_core__001`

Status: agent-calibrated (B-tier exception promote)

## Practical reuse

1. **Reuse module** — Standalone relative-time phrasing for logs, UI timestamps, and audit trails.
2. **Who imports it** — Apps needing Django-style naturaltime without vendoring all humanize formatters.
3. **Why not copy-all** — Full humanize bundles filesize, lists, number, and locale packs beyond time core.

## Module Probes

| Probe | Remove module | Hidden test(s) that must fail |
| --- | --- | --- |
| Naturaltime future | `featurelifted/time.py` | `test_naturaltime_future_with_when` |
| Precisedelta suppress | `featurelifted/time.py` | `test_precisedelta_suppress_days` |
| Number intcomma years | `featurelifted/number.py` | `test_naturaldelta_long_month_granularity` |

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
