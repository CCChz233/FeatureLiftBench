# Task Design: `voluptuous__schema_validate_core__001`

Status: agent-calibrated (B-tier exception promote)

## Why This Task

Voluptuous is a compact declarative validation library used in config pipelines. Its schema compiler, marker semantics, composed validators, and `MultipleInvalid` path aggregation are tightly coupled—ideal for testing whether agents extract a reusable validation core rather than copy the whole package.

## Practical reuse

1. **Reuse module** — Standalone config/document validator: declare schemas and validate nested dict payloads offline.
2. **Who imports it** — Teams embedding schema checks in CLI tools, ETL loaders, or service bootstraps without pulling full Voluptuous + humanize/CLI surface.
3. **Why not copy-all** — Upstream bundles humanize helpers, Email/Url/File validators, and string transforms; compact closure keeps schema compilation + core composed validators.

## Source

| Field | Value |
| --- | --- |
| Source repo | https://github.com/alecthomas/voluptuous |
| Commit | `87825d6dbdab8830fcc6d559ecb3b88bdf68af6d` (v0.16.0) |
| License | BSD-3-Clause |
| Difficulty | hard |
| Tags | batch-1, functional-discriminator, data_model_coupling |

## Target API

```python
from featurelifted import Schema, Required, Optional, All, Any, In, Coerce, MultipleInvalid
```

## Module Probes

| Probe | Remove module | Hidden test(s) that must fail |
| --- | --- | --- |
| Schema compilation | `featurelifted/schema_builder.py` | `test_nested_schema_validation` |
| Composed validators | `featurelifted/validators.py` | `test_all_any_in_and_coerce` |
| Error aggregation | `featurelifted/error.py` | `test_multiple_invalid_error_paths` |

## Public Tests

- `Required` marker rejects missing keys
- `Optional` allows absent keys
- Basic dict schema type validation

## Hidden Tests

- Nested schema graphs
- `All` / `Any` / `In` with `Coerce`
- `MultipleInvalid.errors[0].path` for nested list failures
- No runtime `voluptuous` import surface

## Manual Oracle Closure Plan

| Check | Target | Result |
| --- | --- | --- |
| Public tests | pass | pass (oracle, copy_all, naive) |
| Hidden tests | pass | pass (oracle, copy_all); **fail** (naive) |
| Forbidden import check | pass | pass |
| Oracle LOC | ~1300 | 1308 |
| Source repo Python LOC | ~4000 (incl. upstream tests in snapshot) | 4001 |
| ExtractionRatio | 0.20 – 0.60 | oracle **0.327** |
| Copy-All ExtractionRatio | > oracle + margin | **0.577** (Δ=0.250) |
| Module probes | ≥3 verified | **3/3 OK** |

Expected closure shape:

```text
featurelifted/
  __init__.py
  error.py
  schema_builder.py
  validators.py   # trimmed Coerce/All/Any/In only
```

## Agent Calibration

| Run | Model | Passed | ExtractionRatio | final_score | Notes |
| --- | --- | --- | ---: | ---: | --- |
| `voluptuous__schema_validate_core__001-flash-001` | deepseek_v4_flash | yes (all tests) | 0.546 | 0.454 | **B-tier:** 近 oracle ext 0.327；hidden 未挡住 |
