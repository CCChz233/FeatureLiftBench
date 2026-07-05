# Task Design: humanize__bytes_format_core__001 (Go)

Status: gold_verified_calibration

## Why This Task

Byte-size formatting is a reusable utility embedded in dustin/go-humanize alongside unrelated formatters (time, comma numbers, SI prefixes).

## Practical reuse

1. **Reuse module** — standalone `Bytes` / `IBytes` / `ParseBytes` for logs, dashboards, and CLI output
2. **Who imports it** — observability tools, storage UIs, backup CLIs
3. **Why not copy-all** — only the bytes slice is needed; time/comma formatters are dead weight

## Source

| Field | Value |
| --- | --- |
| Source repo | https://github.com/dustin/go-humanize |
| Commit | v1.0.1 |
| License | MIT |
| Language | **Go** |
| Difficulty | medium / calibration |
| Tags | formatter, parser |

## Entanglement

```json
{
  "level": "medium",
  "types": ["data_model_coupling", "parser_state_coupling"],
  "description": "Format and parse paths share suffix tables, rounding thresholds, and unit constants.",
  "signals": ["bytesSizeTable", "humanateBytes", "comma stripping"]
}
```

## Target API

```go
featurelifted.Bytes(82854982)       // "83 MB"
featurelifted.IBytes(82854982)      // "79 MiB"
featurelifted.ParseBytes("42 MB")   // 42000000, nil
```

## Included Behaviors

- SI (`Bytes`) and IEC (`IBytes`) formatting with correct rounding
- `ParseBytes` with spaced/compact suffixes and comma-stripped decimals
- Overflow guard for values above `math.MaxUint64`

## Excluded Behaviors

- `Time`, `Comma`, `SI` float helpers
- CLI / main
- Original module import

## Test Plan

### Public

- `Bytes(1 MiB)` → `"1.0 MB"`
- `IBytes(1 MiB)` → `"1.0 MiB"`
- `ParseBytes("42 MB")` → `42000000`

### Hidden

- Comma decimal: `"1,005.03 MB"`
- Compact IEC suffix: `"42mib"`
- Rounding without spurious decimal: `Bytes(9999)` → `"10 kB"`
- Overflow error: `"16 EiB"`

## Baseline Expectations

| Variant | Public | Hidden | Extraction |
| --- | --- | --- | --- |
| oracle | pass | pass | 0.09–0.60 |
| naive | pass | **fail** | ≤0.10 |
| copy_all | pass | pass | ≥0.85, Δ≥0.25 vs oracle |

## Oracle Closure Estimate

- ~3 `.go` files (`bytes_common`, `bytes_format`, `bytes_parse`), ~110 LOC
- Excluded repo noise: `times.go`, `comma.go`, padding stubs

## Go/No-Go

Decision: promote_calibration (OpenHands + `deepseek/deepseek-v4-flash`, 2026-07-05).

Flash passed public+hidden with the same extraction footprint as the oracle
(`0.323944`), so this remains useful as Go pipeline calibration but is not
hard paper-ready evidence.

## References

- [GO_PILOT_PLAYBOOK.md](../GO_PILOT_PLAYBOOK.md)
- [GO_QUALITY_RUBRIC.md](../GO_QUALITY_RUBRIC.md)
