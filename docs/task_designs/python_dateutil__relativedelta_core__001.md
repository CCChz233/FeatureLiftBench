# Task Design: `python_dateutil__relativedelta_core__001`

Status: agent-calibrated (B-tier exception promote)

## Why This Task

`relativedelta` is the calendar-aware counterpart to `timedelta`: month/year rollovers, absolute field replacement, weekday setpos, and fractional normalization. Unlike the sibling `rrule` task (recurrence iteration), this slice targets **date offset arithmetic** used by billing cycles, subscription renewals, and schedulers such as croniter. Hidden tests stress normalization cascades, two-date diff mode, yearday/leapday rules, and nth-weekday jumps that timedelta-only stubs miss.

## Practical reuse（必填）

1. **Reuse module** — Standalone **calendar offset engine**: add/subtract months and years with end-of-month clamping, replace day-of-month, and jump to nth weekday (e.g. “first Monday”, “last Friday”).
2. **Who imports it** — Backend services computing invoice due dates, license renewals, payroll periods, or cron-style “next run” without pulling recurrence (`rrule`), timezone databases, or general date string parsers.
3. **Why not copy-all** — Full dateutil bundles `rrule` (RFC recurrence), `parser`, `tz`/`zoneinfo`, and platform tzwin helpers unrelated to relative date math. A compact closure is what croniter-like consumers actually need.

**Different reuse angle vs `python_dateutil__rrule_core__001`:** rrule answers “what are all future occurrences of this repeating rule?”; relativedelta answers “what is this date plus one billing period?” — orthogonal slices from the same upstream repo.

## Source

| Field | Value |
| --- | --- |
| Source repo | https://github.com/dateutil/dateutil |
| Commit | `1ae807774053c071acc9e7d3d27778fba0a7773e` (2.9.0.post0) |
| Repo snapshot | Trimmed: relativedelta + parser + easter + utils (no rrule/tz/zoneinfo) |
| License | Apache-2.0 |
| Language | Python |
| Difficulty | hard |
| Tags | batch-1, date-arithmetic, functional-discriminator, data_model_coupling, multi-task-repo |

## Entanglement

```json
{
  "level": "high",
  "types": ["data_model_coupling", "implicit_dependency_coupling"],
  "primary": "data_model_coupling",
  "description": "Relative date arithmetic couples absolute vs relative field ordering, month-end clamping, weekday setpos jumps, fractional normalization cascades, and two-date diff iteration.",
  "signals": [
    "absolute day/month/year replace before relative add",
    "weekday MO(n) jumps after day replacement",
    "normalized() cascades fractional units through _fix",
    "diff mode iterates months until timedelta remainder fits"
  ]
}
```

## Target Feature

### Source entrypoints

- `dateutil.relativedelta.relativedelta`
- `dateutil._common.weekday`

### Output API

```python
from featurelifted import relativedelta, MO, TU, WE, TH, FR, SA, SU
```

## Included Behaviors

- Construct relativedelta with relative (months, days, …) and absolute (day=1, month=3, …) fields
- Add/subtract to datetime/date with month/year rollover and month-end clamping
- Weekday constants MO..SU with nth setpos (MO(+1), FR(-1))
- `normalized()` for fractional day/hour/minute cascading
- `relativedelta(dt1, dt2)` difference decomposition
- yearday / nlyearday and leapdays post-February adjustment

## Excluded Behaviors

- `rrule`, `rruleset`, `rrulestr`, `easter`
- `dateutil.parser`, `dateutil.tz`, `zoneinfo`, `tzwin`
- Original `dateutil` import at runtime

## Public Tests

- Add months to datetime
- Add days and hours
- Weekday constant repr and `.weekday`
- Absolute `day=` replacement

## Hidden Tests

- `normalized()` fractional cascade (days=1.5, hours=2)
- First Monday via `day=1, weekday=MO(1)`
- Two-date diff mode months/days
- Last Friday via `day=31, weekday=FR(-1)`
- yearday conversion
- leapdays after February in leap year
- Subtract relativedelta
- Reject non-integer years/months
- No `dateutil` import surface

## Module Probes

| Probe | Remove module | Hidden test(s) that must fail |
| --- | --- | --- |
| Probe-1 | `featurelifted/_common.py` | `test_weekday_nth_first_monday` |
| Probe-2 | `featurelifted/relativedelta.py` | `test_normalized_fractional_days` |
| Probe-3 | `featurelifted/relativedelta.py` | `test_relativedelta_diff_months` |

## Manual Oracle Closure Plan

| Check | Target | Result |
| --- | --- | --- |
| Public tests | pass | pass (oracle, copy_all, naive) |
| Hidden tests | pass | pass (oracle, copy_all); **fail** (naive) |
| Forbidden import check | pass | pass |
| Oracle LOC | ~500–900 | 564 (3 files) |
| ExtractionRatio | 0.20 – 0.60 | oracle **0.259** |
| Copy-All ExtractionRatio | > oracle + 0.25 | **1.002** (Δ=0.743) |
| Naive hidden fail | yes | yes (normalized/weekday/diff) |
| Module probes | ≥3 verified | 3/3 OK |

Expected closure shape:

```text
featurelifted/
  __init__.py
  _common.py
  relativedelta.py
```

## Go / No-Go Criteria

- Reuse narrative distinct from rrule task (offset arithmetic vs recurrence).
- Oracle passes public + hidden; naive fails hidden on normalization/weekday/diff semantics.
- ≥3 module probes verified after Step 5.
- Copy-all extraction clearly above oracle.

## Agent Calibration

| Run | Model | Passed | ExtractionRatio | final_score | Notes |
| --- | --- | --- | ---: | ---: | --- |
| | | | | | |
