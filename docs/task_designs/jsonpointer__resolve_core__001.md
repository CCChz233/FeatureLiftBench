# Task Design: `jsonpointer__resolve_core__001`

Status: agent-calibrated (B-tier exception promote)

## Why This Task

JSON Pointer (RFC 6901) is embedded in JSON Patch, JSON Schema `$ref`, and document mutation tooling. The upstream library packs escape parsing, sequence vs mapping dispatch, EndOfList semantics, and in-place mutation into one module. Hidden tests stress tilde/slash escapes, `-` append, and invalid index rules that naive path splitters miss.

## Practical reuse（必填）

1. **Reuse module** — A standalone JSON document navigator: resolve and set values by RFC 6901 pointer strings.
2. **Who imports it** — Teams vendoring pointer logic into config patchers, schema validators, or API gateways without pulling full jsonpatch stacks.
3. **Why not copy-all** — Upstream bundles doctest-heavy tests, setup/doc scaffolding; compact closure keeps pointer core only.

## Source

| Field | Value |
| --- | --- |
| Source repo | https://github.com/stefankoegl/python-json-pointer |
| Commit | `5998f951dcc5ace60f67f35afe6778c445401a07` |
| License | Modified BSD License |
| Language | Python |
| Difficulty | hard |
| Tags | batch-1, functional-discriminator, parser_state_coupling |

## Entanglement

```json
{
  "level": "high",
  "types": ["parser_state_coupling", "data_model_coupling"],
  "description": "JSON Pointer couples token unescaping, sequence vs mapping dispatch, EndOfList sentinel handling, and in-place deepcopy mutation paths.",
  "signals": ["RFC 6901 unescape at parse time", "walk/get_part Mapping vs Sequence", "set handles '-' append", "invalid ~ escapes rejected"]
}
```

## Target Feature

### Source entrypoints

- `jsonpointer.JsonPointer`
- `jsonpointer.resolve_pointer`
- `jsonpointer.set_pointer`
- `jsonpointer.escape` / `jsonpointer.unescape`

### Output API

```python
from featurelifted import JsonPointer, JsonPointerException, resolve_pointer, set_pointer, escape, unescape
```

## Included Behaviors

- Resolve nested dict/list documents by pointer
- Set values in-place and out-of-place; append via `-`
- Escape/unescape `~` and `/` in token names
- Default values for missing paths; invalid escape rejection

## Excluded Behaviors

- JSON Patch diff/patch operations
- Upstream tests, docs, CLI (`bin/jsonpointer`)
- Original `jsonpointer` import at runtime

## Public Tests

- Root pointer resolves to document
- Nested dict and array index resolution
- In-place set updates document
- JsonPointer path round-trip for simple paths

## Hidden Tests

- RFC 6901 escape round-trip and `from_parts`
- Invalid `~` escape raises `JsonPointerException`
- `EndOfList` for `-` on arrays; reject `/foo/-/1`
- Reject leading-zero array indices (`/01`)
- `set_pointer` append via `-`; out-of-place deepcopy
- Missing path default; pointer join (`/`) and containment
- No `jsonpointer` import surface in submission

## Module Probes

| Probe | Remove module | Hidden test(s) that must fail |
| --- | --- | --- |
| Probe-1 | `featurelifted/_escape.py` | `test_escape_round_trip_paths` |
| Probe-2 | `featurelifted/_errors.py` | `test_end_of_list_marker` |
| Probe-3 | `featurelifted/_pointer.py` | `test_array_index_rejects_leading_zero` |

## Manual Oracle Closure Plan

| Check | Target | Result |
| --- | --- | --- |
| Public tests | pass | pass (oracle, copy_all, naive) |
| Hidden tests | pass | pass (oracle, copy_all); **fail** (naive) |
| Forbidden import check | pass | pass |
| Oracle LOC | ~300+ | 225 |
| Source repo Python LOC | ~1056 | 604 |
| ExtractionRatio | 0.20 – 0.60 | oracle **0.373** |
| Copy-All functional gate | 1.0 | pass |
| Copy-All ExtractionRatio | > oracle + margin | **1.003** (Δ=0.630) |
| Module probes | all verified | 3/3 OK |

Expected closure shape:

```text
featurelifted/
  __init__.py
  _escape.py
  _errors.py
  _pointer.py
```

## Go / No-Go Criteria

- Practical reuse narrative holds for JSON document tooling.
- Oracle passes public + hidden; naive fails hidden on escape/index/append semantics.
- ≥3 module probes verified after Step 5.
- Copy-all extraction clearly above oracle.

## Agent Calibration

| Run | Model | Passed | ExtractionRatio | final_score | Notes |
| --- | --- | --- | ---: | ---: | --- |
| `jsonpointer__resolve_core__001-flash-001` | deepseek_v4_flash | yes (all tests) | 0.255 | 0.745 | **B-tier: 全过，ext≈0.25 vs oracle 0.37** |
