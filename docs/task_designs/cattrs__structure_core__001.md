# Task Design: `cattrs__structure_core__001`

Status: agent-calibrated (B-tier exception promote)

## Why This Task

cattrs is the standard companion to attrs for dict↔object conversion in services and config pipelines. Its Converter couples attrs/dataclass introspection, multi-strategy hook dispatch, and generated dict hooks across several modules—distinct from the existing `attrs__validators_core__001` slice (field validation only).

## Practical reuse

1. **Reuse module** — Standalone structure/unstructure converter: turn nested dict payloads into attrs/dataclass instances and back for APIs, jobs, or config loaders.
2. **Who imports it** — Teams embedding serialization without vendoring cattrs preconf codecs (orjson/ujson/msgpack), strategy registries, or GenConverter codegen.
3. **Why not copy-all** — Upstream bundles preconf adapters, union/subclass strategy explosion, and validation helpers; compact closure keeps Converter + gen dict hooks core.

## Source

| Field | Value |
| --- | --- |
| Source repo | https://github.com/python-attrs/cattrs |
| Commit | `5dc43b3f3887f443a58c61d7c89650357c236d51` (v23.2.3) |
| License | MIT |
| Difficulty | hard |
| Tags | batch-1, functional-discriminator, data_model_coupling |

## Target API

```python
from featurelifted import Converter, structure, unstructure
from featurelifted.gen import make_dict_structure_fn, make_dict_unstructure_fn, override
from featurelifted.errors import ClassValidationError, ForbiddenExtraKeysError
```

## Module Probes

| Probe | Remove module | Hidden test(s) that must fail |
| --- | --- | --- |
| Hook dispatch | `featurelifted/dispatch.py` | `test_nested_attrs_and_dataclass` |
| Generated dict hooks | `featurelifted/gen/__init__.py` | `test_structure_hook_rename_override` |
| Type compatibility layer | `featurelifted/_compat.py` | `test_unstructure_omit_if_default` |

## Public Tests

- attrs class round-trip via `Converter`
- dataclass round-trip
- module-level `structure` / `unstructure` helpers

## Hidden Tests

- Nested attrs container holding dataclass list elements
- `make_dict_structure_fn` + `override(rename=...)`
- `make_dict_unstructure_fn` + `override(omit_if_default=True)`
- `forbid_extra_keys` → `ClassValidationError` / `ForbiddenExtraKeysError`
- Optional `None` field round-trip
- No runtime `cattrs` import surface

## Manual Oracle Closure Plan

| Check | Target | Result |
| --- | --- | --- |
| Public tests | pass | pass (oracle, copy_all, naive) |
| Hidden tests | pass | pass (oracle, copy_all); **fail** (naive) |
| Forbidden import check | pass | pass |
| Oracle LOC | ~1200–3500 | **2978** |
| Source repo Python LOC | | **10716** |
| ExtractionRatio | 0.20 – 0.60 | oracle **0.278** |
| Copy-All ExtractionRatio | > oracle + margin | **0.361** (Δ=0.083 — yellow zone) |
| Module probes | ≥3 verified | **3/3 OK** |

Expected closure shape:

```text
featurelifted/
  __init__.py
  _compat.py
  _generics.py
  converters.py
  disambiguators.py
  dispatch.py
  errors.py
  fns.py
  gen/
    __init__.py
    _consts.py
    _shared.py
    _generics.py
    _lc.py
    typeddicts.py
```

## Go / No-Go Criteria

- Oracle compact closure passes public + hidden; copy-all passes with higher extraction.
- Naive baseline passes public but fails hidden on hooks / omit / rename semantics.
- ≥3 module probes verified.

## Agent Calibration

| Run | Model | Passed | ExtractionRatio | final_score | Notes |
| --- | --- | --- | ---: | ---: | --- |
| `cattrs__structure_core__001-flash-001` | deepseek_v4_flash | yes (all tests) | 0.226 | 0.774 | **B-tier: 全过，ext≈0.23 vs oracle 0.28** |
