# Task Design Spike: `python_dateutil__rrule_core__001`

Status: agent-calibrated (B-tier exception promote)

## Agent Calibration

| Run | Model | Passed | ExtractionRatio | final_score | Notes |
| --- | --- | --- | --- | --- | --- |
| `python_dateutil__rrule_core__001-flash-001` | deepseek_v4_flash | yes (hidden pass) | 0.276 | 0.724 | compact pass（5 files, ~1581 LOC）；hidden 未挡住 Flash，但 naive 仍 fail；标 `scoring-discriminator` |

**Promote decision (2026-06-27):** GO — Step 5 分层扎实（oracle 0.277 / naive hidden fail / copy-all 1.004）；Flash 为紧凑解而非 copy-heavy，final_score≈oracle，说明题可解且奖励正确解耦。

## Spike Decision

**Recommendation: GO for staging spike.**

Target is iCalendar RFC 5545 recurrence core: `rrule`, `rruleset`, and `rrulestr` (naive dates only). Exclude general date parsing, `relativedelta`, `tz`/`zoneinfo`, and Windows tz helpers.

## Practical reuse

1. **Reuse module** — standalone recurrence engine for calendars, billing cycles, job schedulers, and subscription renewals.
2. **Who imports it** — backend services that must expand RRULE/RRULESET offline without pulling full `python-dateutil` or timezone databases.
3. **Why not copy-all** — full dateutil adds parser, relativedelta, tz stack, zoneinfo rebuild, and platform-specific tzwin code unrelated to recurrence iteration.

## Source

| Field | Value |
| --- | --- |
| Source repo | `https://github.com/dateutil/dateutil` |
| Commit | `1ae807774053c071acc9e7d3d27778fba0a7773e` (2.9.0.post0) |
| License | Apache-2.0 |
| Difficulty | hard |
| Tags | `batch-1`, `recurrence`, `hard-first`, `functional-discriminator`, `parser_state_coupling` |

## Entanglement

```json
{
  "level": "high",
  "types": ["parser_state_coupling", "global_state_registry_coupling", "implicit_dependency_coupling"],
  "primary": "parser_state_coupling",
  "description": "Recurrence iteration couples RFC rule parsing, calendar masks, leap-year handling, weekday/setpos logic, cache state, and rruleset inclusion/exdate merging.",
  "signals": [
    "rrulestr parses RFC key/value grammar into constructor kwargs",
    "BYSETPOS + BYDAY interact on monthly/yearly masks",
    "BYEASTER requires orthogonal holiday computation",
    "rruleset merges multiple generators with exdate/rdate overrides"
  ]
}
```

## Target Feature

### Output API

```python
from featurelifted import rrule, rruleset, rrulestr, YEARLY, MONTHLY, WEEKLY, DAILY, MO, TU, WE, TH, FR, SA, SU
```

### Included behaviors

- Construct `rrule` with freq, interval, count/until, BY* filters.
- Iterate occurrences in order; respect count and until.
- `rruleset` with include rules, RDATE/EXDATE (naive).
- `rrulestr` for RRULE lines with naive `YYYYMMDD` / `YYYYMMDDTHHMMSS` dates (`ignoretz=True`).
- `BYEASTER` offsets via bundled easter helper.

### Excluded behaviors

- `dateutil.tz`, TZID parameters, `tzinfos`, `zoneinfo`.
- `relativedelta`, general `parser.parse` for arbitrary date strings.
- Original `dateutil` import at runtime.

## Public Tests

- Monthly rule yields expected three dates.
- Weekly `byweekday` filter.
- `count` stops iteration.
- `rrulestr` parses simple MONTHLY rule.

## Hidden Tests

- `BYSETPOS` + `BYDAY` (e.g. last Friday).
- `BYEASTER` offset occurrences.
- `rruleset` EXDATE removes occurrence.
- Invalid `interval=0` raises.
- Multiple errors / edge freq combinations.
- No `dateutil` import in sources; `__all__` excludes tz/parser.

## Module Probes

| Probe | Remove module | Hidden test(s) that must fail |
| --- | --- | --- |
| Probe-1 | `featurelifted/easter.py` | `test_byeaster_occurrence` |
| Probe-2 | `featurelifted/_common.py` | `test_bysetpos_last_weekday` |
| Probe-3 | `featurelifted/rrule.py` (partial: rruleset class) | `test_rruleset_exdate_skips` |

## Manual Oracle Closure Plan

| Check | Target | Result |
| --- | --- | --- |
| Public tests | pass | pass |
| Hidden tests | pass | pass |
| Oracle LOC | ~1800–3500 | ~1870 (3 modules) |
| ExtractionRatio | 0.20–0.60 | 0.277 |
| Copy-All vs oracle gap | ≥0.30 | 0.727 (copy-all 1.004) |
| Naive hidden fail | yes | yes (bysetpos/byeaster/exdate) |
| Module probes | ≥3 verified | 3/3 OK |

## Go / No-Go Criteria

**Go** if A-tier or strong Step-5 layering; hidden blocks naive; Flash does not pass with trivial thin wrapper.

**No-go** if oracle needs full tz/parser stack or tests drift on local tzdata.
