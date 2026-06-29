# Task Design: `dataclasses_json__serde_core__001`

Status: agent-calibrated (B-tier exception promote)

## Why This Task

dataclasses-json is widely used to attach JSON serde to stdlib dataclasses. The useful slice couples field metadata, letter-case transforms, exclusion predicates, nested decode, and undefined-parameter handling across several modules—distinct from `cattrs__structure_core__001` (attrs hook dispatch) and pydantic validation.

## Practical reuse

1. **Reuse module** — Standalone dataclass JSON mapper for APIs and config payloads with field rename, exclusion, and nested object decode.
2. **Who imports it** — Services that want `@dataclass_json` ergonomics without vendoring marshmallow schema generation or upstream packaging.
3. **Why not copy-all** — Upstream bundles mm.py schema builder, CatchAll undefined modes tied to marshmallow, and test/docs trees irrelevant to runtime serde.

## Source

| Field | Value |
| --- | --- |
| Source repo | https://github.com/lidatong/dataclasses-json |
| Commit | `dc63902eeb5e1c5ce1ea4e078c50e0eb9bc1a541` |
| License | MIT |
| Difficulty | hard |
| Tags | batch-1, functional-discriminator, data_model_coupling |

## Module Probes

| Probe | Remove module | Hidden test(s) that must fail |
| --- | --- | --- |
| Core decode/encode | `featurelifted/core.py` | `test_nested_dataclass_roundtrip` |
| Letter case helpers | `featurelifted/stringcase.py` | `test_field_level_camel_case` |
| Undefined handling | `featurelifted/undefined.py` | `test_undefined_raise_on_extra_keys` |

## Public Tests

- Basic `to_json` / `from_json` round-trip
- `to_dict` / `from_dict` round-trip
- Class-level `LetterCase.CAMEL`
- `config(field_name=...)` alias

## Hidden Tests

- Field-level `LetterCase.CAMEL`
- `Exclude.ALWAYS` and custom exclude predicate
- Nested dataclass encode/decode
- `Undefined.RAISE` rejects unknown keys
- Duplicate letter-case key collision raises `ValueError`
- `global_config` encoder/decoder registration
- No runtime `dataclasses_json` imports

## Manual Oracle Closure Plan

| Check | Target | Result |
| --- | --- | --- |
| Public tests | pass | pass (oracle, copy_all, naive) |
| Hidden tests | pass | pass (oracle, copy_all); **fail** (naive) |
| Forbidden import check | pass | pass |
| Oracle LOC | ~1000–1400 | **1014** |
| Source repo Python LOC | | **3858** |
| ExtractionRatio | 0.20 – 0.60 | oracle **0.263** |
| Copy-All ExtractionRatio | > oracle + margin | **0.913** (Δ=0.651) |
| Module probes | ≥3 verified | **3/3 OK** |

Expected closure shape:

```text
featurelifted/
  __init__.py
  api.py
  cfg.py
  core.py
  stringcase.py
  undefined.py
  utils.py
  __version__.py
```

## Go / No-Go Criteria

- Oracle compact closure passes public + hidden; copy-all passes with higher extraction.
- Naive baseline passes public but fails hidden on letter case / exclude / nested / undefined.
- ≥3 module probes verified.

## Agent Calibration

| Run | Model | Passed | ExtractionRatio | final_score | Notes |
| --- | --- | --- | ---: | ---: | --- |
| | | | | | |
