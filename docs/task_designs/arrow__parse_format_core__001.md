# Task Design: `arrow__parse_format_core__001`

Status: agent-calibrated (B-tier exception promote)

## Practical reuse

1. **Reuse module** — Arrow-style datetime parse/format/humanize for APIs and logging.
2. **Who imports it** — Services needing Arrow ergonomics without 60+ locale files.
3. **Why not copy-all** — Full Arrow bundles locales.py (~6k LOC) and factory extras beyond English core.

## Module Probes

| Probe | Remove module | Hidden test(s) that must fail |
| --- | --- | --- |
| Parser ordinal | `featurelifted/parser.py` | `test_parse_ordinal_day_token` |
| Formatter literals | `featurelifted/formatter.py` | `test_format_literal_brackets` |
| English humanize | `featurelifted/locales.py` | `test_humanize_relative_hours` |

## Manual Oracle Closure Plan

| Check | Target | Result |
| --- | --- | --- |
| Public tests | pass | |
| Hidden tests | pass | |
| ExtractionRatio | 0.20 – 0.60 | |
| Copy-All delta | ≥ 0.25 | |
