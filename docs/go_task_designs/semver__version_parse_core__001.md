# Task Design: semver__version_parse_core__001 (Go)

Status: oracle-verified

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

Decision: promote (pending Flash)
