# Task Design: `isodate__duration_parse_core__001`

Status: agent-calibrated

## Practical reuse

1. **Reuse module** — ISO8601 duration parser for APIs, media manifests, and billing intervals.
2. **Who imports it** — Services parsing XML Schema durations without the full isodate datetime stack.
3. **Why not copy-all** — Full isodate bundles date/time/tz parsers and strftime tables beyond duration core.

## Module Probes

| Probe | Remove module | Hidden test(s) that must fail |
| --- | --- | --- |
| Duration model | `featurelifted/duration.py` | `test_parse_duration_full_components` |
| Period regex | `featurelifted/isoduration.py` | `test_parse_duration_comma_decimal_hours` |
| Date combine | `featurelifted/isodates.py` | `test_duration_totimedelta_with_start` |

## Manual Oracle Closure Plan

| Check | Target | Result |
| --- | --- | --- |
| Public tests | pass | |
| Hidden tests | pass | |
| ExtractionRatio | 0.20 – 0.60 | |
| Copy-All delta | ≥ 0.25 | |
