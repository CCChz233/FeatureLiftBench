# Task Design: semver__version_parse_core__001 (Go)

Status: gold_verified_calibration

## Why This Task

Semantic version parsing/comparison is a reusable library feature embedded in Masterminds/semver with internal normalization helpers.

## Practical reuse

1. **Reuse module** — standalone semver comparison for release tooling
2. **Who imports it** — CLI release tools, package managers, CI gates
3. **Why not copy-all** — only parse/compare core is needed offline

## Target API

```go
featurelifted.Parse("1.2.3")
featurelifted.Compare("1.0.0", "1.0.1")
```

## Go/No-Go

Decision: promote_calibration (OpenHands + `deepseek/deepseek-v4-flash`, 2026-07-05).

Flash passed public+hidden with the same extraction footprint as the oracle
(`0.574468`), so this remains useful as Go pipeline calibration but is not
hard paper-ready evidence.
