# Task Design: mapstructure__decode_core_hard__001 (Go)

Status: gold_verified_calibration (hard-readiness failed)

## Why This Task

The first Go mapstructure task was useful for pipeline calibration, but OpenHands + Flash extracted the oracle-sized target slice directly. This hard variant keeps the same practical feature while adding reflection behavior that is harder to recover by copying obvious files or implementing only the public examples.

## Practical reuse

1. **Reuse module** — standalone config map decoder for CLIs, services, and adapters
2. **Who imports it** — config loaders and API boundary code that need map-to-struct conversion
3. **Why not copy-all** — nearby cache/schema/registry helpers are unrelated to runtime decoding and should be excluded

## Target API

```go
featurelifted.Decode(map[string]any{...}, &dest)
featurelifted.NewDecoder(&featurelifted.DecoderConfig{...})
featurelifted.ComposeDecodeHookFunc(...)
featurelifted.StringToSliceHookFunc(",")
```

## Included Behaviors

- Basic map-to-struct decode via `mapstructure` tags
- Metadata key tracking and unused-key errors
- Weak string/float conversions into primitive target fields
- Nested pointer allocation and recursive struct decode
- Slice and map element decoding with weak conversions
- Decode hook composition in caller-provided order
- `encoding.TextUnmarshaler` support
- Squashed embedded struct handling with conflict detection

## Excluded Behaviors

- Field cache registry helpers
- Schema validation registry helpers
- Encoding or flattening helpers
- Original module import

## Test Plan

### Public

- Basic tagged struct decode
- Metadata key tracking

### Hidden

- Combined nested pointer, slice, and map decode
- Text unmarshalling behavior
- Hook composition order
- Squash conflict and unused metadata/error state

## Baseline Expectations

| Variant | Public | Hidden | Extraction |
| --- | --- | --- | --- |
| oracle | pass | pass | 0.09–0.60 |
| naive | pass | **fail** | ≤0.11 |
| copy_all | pass | pass | ≥0.85, Δ≥0.20 vs oracle |
| OpenHands Flash | pass | pass | 0.571253, equal to oracle |

## Go/No-Go

Decision: promote_calibration, not paper_ready_hard.

Mechanical gates passed after Docker review:

- oracle: public+hidden pass, extraction 0.571253
- naive: public pass, hidden fail, extraction 0.017199
- copy_all: public+hidden pass, extraction 1.0

OpenHands + `deepseek/deepseek-v4-flash` was run twice. Both runs selected the
same file footprint as oracle and passed hidden tests, so this task is useful as
a calibration/easy-B hardening attempt but does not provide hard research
evidence. The next redesign should avoid clean file-boundary extraction.
