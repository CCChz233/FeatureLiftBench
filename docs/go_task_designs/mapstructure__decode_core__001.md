# Task Design: mapstructure__decode_core__001 (Go)

Status: gold_verified_calibration

## Why This Task

Map-to-struct decoding is a reusable config/JSON bridge embedded in go-viper/mapstructure with reflection, hooks, and tag rules.

## Practical reuse

1. **Reuse module** — standalone `Decode` for config loaders and API adapters
2. **Who imports it** — microservices, CLI tools, viper/cobra stacks
3. **Why not copy-all** — only decode slice needed; cache/helpers are dead weight

## Target API

```go
featurelifted.Decode(map[string]any{...}, &dest)
featurelifted.NewDecoder(&featurelifted.DecoderConfig{...})
```

## Go/No-Go

Decision: promote_calibration (OpenHands + `deepseek/deepseek-v4-flash`, 2026-07-05).

Flash passed public+hidden with the same extraction footprint as the oracle
(`0.597633`), so this remains useful as Go pipeline calibration but is not
hard paper-ready evidence. The hard follow-up is
`mapstructure__decode_core_hard__001`.
