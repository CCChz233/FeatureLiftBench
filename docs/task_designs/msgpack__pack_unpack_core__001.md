# Task Design: `msgpack__pack_unpack_core__001`

Status: agent-calibrated (B-tier exception promote)

## Why This Task

MessagePack is a common wire format for RPC caches and event pipelines. The Python implementation couples buffer cursor state, header dispatch tables, extension timestamp codecs, and hook-driven container construction—more than a JSON-with-bytes wrapper.

## Practical reuse

1. **Reuse module** — Standalone pure-Python MessagePack codec for services that need offline-safe serialization without vendoring Cython wheels.
2. **Who imports it** — Teams embedding pack/unpack in workers, IPC bridges, or test harnesses where `msgpack` wheels are unavailable.
3. **Why not copy-all** — Upstream ships Cython accelerators, benchmarks, docker, and 1900+ LOC of tests; compact fallback closure documents the real decode state machine.

## Source

| Field | Value |
| --- | --- |
| Source repo | https://github.com/msgpack/msgpack-python |
| Commit | `2de627311fb17b1a942d052447c3777cd58b162d` |
| License | Apache-2.0 |
| Difficulty | hard |
| Tags | batch-1, functional-discriminator, parser_state_coupling |

## Entanglement

```json
{
  "level": "high",
  "types": ["parser_state_coupling", "data_model_coupling", "implicit_dependency_coupling"],
  "primary": "parser_state_coupling",
  "description": "Unpacker buffer checkpoints, header table dispatch, and extension hooks are tightly coupled across nested containers."
}
```

## Target Feature

### Source entrypoints

- `msgpack.packb` / `msgpack.unpackb`
- `msgpack.Packer` / `msgpack.Unpacker`
- `msgpack.ext.Timestamp` / `msgpack.ext.ExtType`
- `msgpack.fallback` (pure-Python path)

### Output API

```python
from featurelifted import packb, unpackb, Packer, Unpacker, ExtType, Timestamp, ExtraData, FormatError
```

## Included Behaviors

- packb/unpackb for nil, bool, int, str, bytes, list, dict
- Packer/Unpacker streaming via `feed` + `unpack`
- Timestamp and ExtType extension types
- `strict_map_key`, `ext_hook`, `ExtraData`, `FormatError`

## Excluded Behaviors

- Cython `_cmsgpack` accelerated path
- Benchmarks, docker, docs, upstream tests
- Original `msgpack` import at runtime

## Public Tests

- None/bool/int roundtrip
- String, bytes, list, dict roundtrip
- Packer/Unpacker streaming
- dumps/loads aliases

## Hidden Tests

- Timestamp pack/unpack
- ExtType roundtrip
- `strict_map_key=False` with int map keys
- `ExtraData` on trailing bytes
- Custom `ext_hook`
- `FormatError` on invalid prefix
- `unpack` from file-like stream
- No runtime `msgpack` import surface

## Module Probes

| Probe | Remove module | Hidden test(s) that must fail |
| --- | --- | --- |
| Probe-1 | `featurelifted/ext.py` | `test_timestamp_roundtrip` |
| Probe-2 | `featurelifted/fallback.py` | `test_extra_data_raises` |
| Probe-3 | `featurelifted/exceptions.py` | `test_format_error_on_invalid_bytes` |

## Manual Oracle Closure Plan

| Check | Target | Result |
| --- | --- | --- |
| Public tests | pass | pass (oracle, copy_all, naive) |
| Hidden tests | pass | pass (oracle, copy_all); **fail** (naive) |
| Forbidden import check | pass | pass |
| Oracle LOC | ~900+ | 1019 |
| Source repo Python LOC | ~2400+ | 2473 |
| ExtractionRatio | 0.20 – 0.60 | oracle **0.412** |
| Copy-All functional gate | 1.0 | pass |
| Copy-All ExtractionRatio | > oracle + 0.25 | **0.997** (Δ=0.585) |
| Module probes | all verified | 3/3 OK |

Expected closure shape:

```text
featurelifted/
  __init__.py
  exceptions.py
  ext.py
  fallback.py
```

## Agent Calibration

| Run | Model | Passed | ExtractionRatio | Tokens | Notes |
| --- | --- | --- | --- | --- | |

## Go / No-Go Criteria

- Practical reuse narrative credible for serialization slice.
- Oracle vs copy-all extraction gap ≥ 0.25.
- Naive passes public, fails hidden on extension/timestamp semantics.
- ≥3 module probes verified.
