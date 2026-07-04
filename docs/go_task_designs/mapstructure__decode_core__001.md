# Task Design: mapstructure__decode_core__001 (Go)

Status: oracle-verified

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

Decision: promote (pending gate)
