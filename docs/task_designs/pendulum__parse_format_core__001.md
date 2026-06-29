# Task Design: `pendulum__parse_format_core__001`

> Machine-readable task spec: [TASK_FORMAT.md](../TASK_FORMAT.md). This file is the human design note.

Status: agent-calibrated

## Why This Task

Pendulum bundles ISO8601 parsing, custom format tokens, and calendar-aware Duration types into a datetime library tightly coupled to timezone and locale machinery. This slice tests whether an agent can extract the parse/format/duration core without vendoring tzdata or dozens of locale packs.

## Practical reuse（必填）

1. **Reuse module** — A standalone datetime parse/format helper: ISO8601 + common datetime strings, Pendulum-style format tokens, and duration construction/parsing.
2. **Who imports it** — Services that need Pendulum-like `parse()` / `.format()` without pulling the full library, tzdata bundle, or humanize stack.
3. **Why not copy-all** — Full Pendulum includes ~30 locales, tzdata traversal, interval/humanize/testing helpers; the reusable slice is the parser + formatter + duration stack with UTC/fixed offsets only.

## Source

| Field | Value |
| --- | --- |
| Source repo | `https://github.com/sdispater/pendulum` |
| Commit | `b99bd1468b5562f045c90d851c4fab0072b26df8` |
| License | MIT |
| Language | Python |
| Difficulty | hard |
| Tags | batch-1, datetime, parse-format, parser_state_coupling |

## Entanglement

```json
{
  "level": "high",
  "types": ["parser_state_coupling", "data_model_coupling", "implicit_dependency_coupling"],
  "primary": "parser_state_coupling",
  "description": "Parse/format couples ISO8601 regex grammars, duration normalization, formatter token tables, and DateTime/Duration data-model arithmetic shared across modules.",
  "signals": [
    "iso8601 parser handles classic, ordinal, and week-calendar date forms",
    "duration parsing splits Y/M/D and T-segment components with validation",
    "Formatter token expansion shares locale lookups and escape brackets",
    "DateTime.format delegates to Formatter with timezone offset tokens"
  ]
}
```

## Target Feature

### Source entrypoints

- `pendulum.parse`
- `pendulum.parser.parse`
- `pendulum.parsing.iso8601.parse_iso8601`
- `pendulum.formatting.Formatter`
- `pendulum.duration.Duration`
- `pendulum.datetime.DateTime.format`

### Output API

```python
from featurelifted import parse, datetime, duration, DateTime, Duration, ParserError, UTC
```

Primary callable:

```python
featurelifted.parse(text, **options)
```

## Included Behaviors

- ISO8601 date/datetime/duration parsing with Z or numeric offsets
- Common `YYYY-MM-DD` / `HH:mm:ss` combinations with `day_first`
- DateTime construction and Pendulum format tokens
- Duration components (years, months, weeks, days, hours, minutes, seconds)

## Excluded Behaviors

- Bundled tzdata / IANA timezone database usage in tests
- Named timezone scheduling (`Europe/Paris`, etc.)
- Humanize, diff-for-humans, non-English locales
- Interval iteration, `now()` / time travel, CLI
- Original `pendulum` import at runtime

## Environment

```json
{
  "python": "3.11",
  "network": false,
  "timeout_seconds": 60,
  "dependency_lock": "requirements.lock",
  "allowed_dependencies": ["python-dateutil"],
  "forbidden_dependencies": ["pendulum"],
  "forbidden_imports": ["pendulum"]
}
```

## Public Tests

- Parse ISO date `2024-06-15`
- Parse Zulu datetime `2024-06-15T10:30:45Z`
- Format `YYYY-MM-DD HH:mm:ss`
- Duration constructor `total_seconds()`
- Parse simple ISO duration `P1DT12H`

## Hidden Tests

- ISO week calendar `2016-W05-5`
- Duration weeks `P2W` and full `P1Y2M3DT4H5M6S`
- Format literal brackets `YYYY [MM] DD`
- Fixed offset `+0530` without colon
- Common parser `day_first=True`
- Subsecond truncation to microseconds
- Duration rejects float years/months
- ParserError on invalid input
- Forbidden `pendulum` import surface check

## Module Probes

| Probe | Remove module | Hidden test(s) that must fail |
| --- | --- | --- |
| Probe-iso8601 | `parsing/iso8601.py` | `test_parse_iso_week_calendar_date`, `test_parse_duration_weeks_component` |
| Probe-formatter | `formatting/formatter.py` | `test_format_literal_brackets` |
| Probe-duration | `duration.py` | `test_parse_duration_full_components`, `test_duration_years_months_not_float` |

## Manual Oracle Closure Plan

| Check | Target | Result |
| --- | --- | --- |
| Public tests | pass | pass (oracle, copy_all, naive) |
| Hidden tests | pass | pass (oracle, copy_all); **fail** (naive) |
| Forbidden import check | pass | pass |
| Oracle LOC | | 4976 |
| Source repo Python LOC | 11783 | 11783 |
| ExtractionRatio | 0.20–0.60 | 0.422 |
| Copy-All functional gate | 1.0 | 1.0 |
| Copy-All ExtractionRatio | ≥ 0.85 | 0.966 |
| Module probes | all verified | 3/3 OK |

Expected closure shape:

```text
featurelifted/
  parser.py
  parsing/
  formatting/
  duration.py
  datetime.py
  date.py
  time.py
  tz/timezone.py
  locales/en/
```

## Agent Calibration

| Run | Model | Passed | ExtractionRatio | Tokens | Notes |
| --- | --- | --- | --- | --- | --- |
| | | | | | |

## Go / No-Go Criteria

- Practical reuse story credible for offline datetime helpers
- Oracle compact vs copy-all separation on ExtractionRatio
- ≥3 module probes verified
- Naive baseline passes public, fails hidden on ISO week/duration/format edges
