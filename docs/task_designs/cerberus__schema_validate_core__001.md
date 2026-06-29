# Task Design: `cerberus__schema_validate_core__001`

Status: agent-calibrated (B-tier exception promote)

## Why This Task

Cerberus is a lightweight dict-validation library used in APIs and config pipelines. Its nested schema compilation, coercion side effects, and error-tree rewriting across `validator`, `schema`, and `errors` are tightly coupled—stronger hidden discrimination than voluptuous (B-tier Flash) for agents that only implement shallow type checks.

## Practical reuse

1. **Reuse module** — Standalone document validator: declare nested schemas, coerce inputs, and surface structured field errors offline.
2. **Who imports it** — Teams embedding request/config validation in microservices or CLIs without vendoring Cerberus benchmarks, registries, or docs.
3. **Why not copy-all** — Upstream bundles registry indirection, benchmark harnesses, and packaging metadata; compact closure keeps validation + error formatting core.

## Source

| Field | Value |
| --- | --- |
| Source repo | https://github.com/pyeve/cerberus |
| Commit | `f2221c5a901bbf8618efb694ef9364bd0882ac9a` (v1.3.8) |
| License | ISC |
| Difficulty | hard |
| Tags | batch-1, functional-discriminator, data_model_coupling |

## Target API

```python
from featurelifted import Validator, DocumentError, SchemaError
```

## Module Probes

| Probe | Remove module | Hidden test(s) that must fail |
| --- | --- | --- |
| Schema compilation | `featurelifted/schema.py` | `test_nested_schema_validation` |
| Coerce + rule dispatch | `featurelifted/validator.py` | `test_coerce_updates_document` |
| Error tree formatting | `featurelifted/errors.py` | `test_nested_list_error_paths` |

## Public Tests

- `required` rule rejects missing keys
- `type` rule rejects wrong types
- `validate` returns boolean success flag

## Hidden Tests

- Nested dict schema with required subfields
- `coerce` updates `document` with converted values
- Nested list-of-dict error trees (`errors['items'][0][0]['id']`)
- Deep nested list + coerce + `min` constraint combo
- No runtime `cerberus` import surface

## Manual Oracle Closure Plan

| Check | Target | Result |
| --- | --- | --- |
| Public tests | pass | pass (oracle, copy_all, naive) |
| Hidden tests | pass | pass (oracle, copy_all); **fail** (naive) |
| Forbidden import check | pass | pass |
| Oracle LOC | ~2500+ | 2550 |
| Source repo Python LOC | ~7500 (incl. upstream tests in snapshot) | 5914 |
| ExtractionRatio | 0.20 – 0.60 | oracle **0.431** |
| Copy-All ExtractionRatio | > oracle + margin | **0.492** (Δ=0.061 — yellow zone) |
| Module probes | ≥3 verified | **3/3 OK** |

Expected closure shape:

```text
featurelifted/
  __init__.py
  platform.py
  utils.py
  errors.py
  schema.py
  validator.py
```

## Agent Calibration

| Run | Model | Passed | ExtractionRatio | final_score | Notes |
| --- | --- | --- | ---: | ---: | --- |
| `cerberus__schema_validate_core__001-flash-001` | deepseek_v4_flash | yes (all tests) | 0.434 | 0.566 | **B-tier:** 近 oracle ext 0.431；hidden 未挡住 |
