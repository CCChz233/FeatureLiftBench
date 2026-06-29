# Task Design: `referencing__json_schema_refs_core__001`

Status: agent-calibrated (B-tier exception promote)

## Practical reuse

1. **Reuse module** — Extract referencing Registry/Resolver $ref, anchor, and fragment resolution for JSON Schema dialects without jsonschema validator implementations.
2. **Who imports it** — Schema tooling, OpenAPI/JSON Schema validators, and config merge pipelines needing portable $ref resolution.
3. **Why not copy-all** — Curated snapshot includes referencing tests tree; compact closure keeps _core + jsonschema dialect glue only.

## Module Probes

| Probe | Remove module | Hidden test(s) that must fail |
| --- | --- | --- |
| Registry core | `featurelifted/_core.py` | `test_unresolvable_external_ref` |
| JSON Schema dialect | `featurelifted/jsonschema.py` | `test_unknown_dialect_and_missing_anchor` |
| Exceptions | `featurelifted/exceptions.py` | `test_anchor_lookup` |

## Manual Oracle Closure Plan

| Check | Target | Result |
| --- | --- | --- |
| Public tests | pass | pass |
| Hidden tests | pass | pass |
| ExtractionRatio | 0.20 – 0.60 | 0.48 |
| Copy-All delta | ≥ 0.25 | 0.53 |

## Agent Calibration

| Run | Model | Passed | ExtractionRatio | final_score | Notes |
| --- | --- | --- | ---: | ---: | --- |
| oracle | — | yes | 0.48 | 0.52 | Step 5 promote batch-1 #48 |
| naive | — | pub/hid | 0.03 | — | hidden fail |
| copy-all | — | yes | 1.009 | — | Δ≈0.53; needs attrs+rpds in eval venv |
| | | | | | Flash deferred |
