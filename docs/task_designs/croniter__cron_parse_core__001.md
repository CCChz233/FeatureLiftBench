# Task Design: `croniter__cron_parse_core__001`

Status: agent-calibrated (B-tier exception promote)

## Agent Calibration

| Run | Model | Passed | ExtractionRatio | final_score | Notes |
| --- | --- | --- | ---: | ---: | --- |
| `croniter__cron_parse_core__001-flash-001` | deepseek_v4_flash | yes (all tests) | 0.197 | 0.803 | **B-tier:** compact pass beats oracle ext 0.242; hidden 未挡住 |

## Why This Task

Cron scheduling is a common embedded need (job runners, workflow engines). `croniter` packs field parsing, expansion, and calendar walking into one module tightly coupled to `dateutil.relativedelta`. Hidden tests stress step/range fields and DOM/DOW union—behaviors a naive cron parser typically misses.

## Practical reuse（必填）

1. **Reuse module** — A standalone cron rule iterator: parse expressions and walk next/prev fire times for naive datetimes.
2. **Who imports it** — Backend teams vendoring schedule evaluation into workers, ETL orchestrators, or admin consoles without pulling APScheduler/Celery.
3. **Why not copy-all** — Upstream bundles hash expanders, `croniter_range`, DST branches, and test-only surface; a compact closure keeps the 5-field iterator core.

## Source

| Field | Value |
| --- | --- |
| Source repo | https://github.com/pallets-eco/croniter |
| Commit | `dc04395e2291b44a74507919d27a13f922b7f77d` (release 2.0.7) |
| License | MIT |
| Language | Python |
| Difficulty | hard |
| Tags | batch-1, functional-discriminator, parser_state_coupling |

## Entanglement

```json
{
  "level": "high",
  "types": ["parser_state_coupling", "config_environment_coupling", "implicit_dependency_coupling"],
  "description": "Croniter couples regex field parsing, expansion tables, calendar arithmetic, DOM/DOW union logic, and iterator state.",
  "signals": ["field expanders", "day_or DOM/DOW union", "_calc rollover", "relativedelta month steps"]
}
```

## Target Feature

### Source entrypoints

- `croniter.croniter`
- `croniter.croniter.croniter.get_next` / `get_prev`
- `croniter.croniter.datetime_to_timestamp`

### Output API

```python
from featurelifted import croniter, CroniterBadCronError
```

## Included Behaviors

- 5-field cron parse and next/prev on naive `datetime(2024, 1, 15, 12, 0, 0)`
- Step and range fields (`*/15`, `9-17`)
- Invalid field rejection (`CroniterBadCronError`)
- DOM/DOW union (`day_or=True`)

## Excluded Behaviors

- `croniter_range`, hash `H()`/`r()` expanders, `match_range` / `is_valid`
- Original `croniter` import; DST/timezone scheduling (tests are naive-only)
- Upstream tests in oracle closure

## Public Tests

- Daily noon next/prev from fixed base
- Hourly minute tick and weekday field

## Hidden Tests

- Step + hour range combined
- Invalid minute field error type
- Alternating next/prev on list fields (`8,20`)
- DOM/DOW union next
- No `croniter` import surface in `featurelifted`

## Module Probes

| Probe | Remove module | Hidden test(s) that must fail |
| --- | --- | --- |
| Probe-1 | `featurelifted/constants.py` | `test_step_and_range_fields` |
| Probe-2 | `featurelifted/errors.py` | `test_invalid_minute_raises` |
| Probe-3 | `featurelifted/iterator.py` | `test_combined_next_prev_walk` |

## Manual Oracle Closure Plan

| Check | Target | Result |
| --- | --- | --- |
| Public tests | pass | pass (oracle, copy_all, naive) |
| Hidden tests | pass | pass (oracle, copy_all); **fail** (naive) |
| Forbidden import check | pass | pass |
| Oracle LOC | ~800+ | 765 |
| Source repo Python LOC | ~3800 (incl. upstream tests in snapshot) | 3167 |
| ExtractionRatio | 0.20 – 0.60 | oracle **0.242** |
| Copy-All functional gate | 1.0 | pass |
| Copy-All ExtractionRatio | > oracle + margin | **0.279** (Δ=0.037 only — yellow zone) |
| Module probes | all verified | 3/3 OK (python3.12) |

Expected closure shape:

```text
featurelifted/
  __init__.py
  constants.py
  errors.py
  utils.py
  iterator.py
```

## Go / No-Go Criteria

- Practical reuse narrative holds for job-scheduler embedding.
- Oracle passes public + hidden; naive fails hidden on step/union semantics.
- ≥3 module probes verified after Step 5.
- ExtractionRatio in band; copy-all penalized vs compact oracle.
