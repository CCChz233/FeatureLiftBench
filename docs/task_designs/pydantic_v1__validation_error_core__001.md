# Task Design Spike: `pydantic_v1__validation_error_core__001`

> Machine-readable task spec will be created in staging. Pre-staging design spike.

Status: agent-calibrated (B-tier exception promote)

## Spike Decision

**Recommendation: GO for staging spike, with strict API boundary.**

Target is **not** full Pydantic v1. The reusable slice is `BaseModel` field parsing, `@validator` / `@root_validator`, model `Config`, and structured `ValidationError` trees (loc/type/msg). JSON Schema export, networks, settings, dataclasses bridge, and mypy plugin are excluded.

## Why This Task

Pydantic v1 is widely embedded in legacy services for request/config validation. Teams often need only the model parsing + error reporting core without dragging in schema generation, URL/email types, or settings machinery. Extracting this slice tests decoupling across metaclass construction, field descriptors, validator registries, and error flattening.

## Practical reuse

1. **Reuse module** — `featurelifted` is a standalone schema validation core: declare models, run `parse_obj`/`__init__` validation, and consume structured `ValidationError.errors()`.
2. **Who imports it** — API gateways, ETL pipelines, config loaders, and SDK codegen tools that need typed dict→model validation with nested error paths, without full Pydantic distribution surface.
3. **Why not copy-all** — Full Pydantic v1 adds JSON Schema (`schema.py`), mypy plugin, network types, env settings, color parsing, and hypothesis hooks irrelevant to validation-error core.

## Source

| Field | Value |
| --- | --- |
| Source repo | `https://github.com/pydantic/pydantic` |
| Commit | `5ebcdc13b83fba5da34ad9b0f008f7b4faf89396` (v1.10.18) |
| License | MIT |
| Language | Python |
| Difficulty | hard |
| Tags | `batch-1`, `validation`, `hard-first`, `functional-discriminator`, `framework-coupling` |

## Entanglement

```json
{
  "level": "high",
  "types": [
    "data_model_coupling",
    "framework_coupling",
    "global_state_registry_coupling",
    "implicit_dependency_coupling"
  ],
  "primary": "framework_coupling",
  "description": "Model validation couples metaclass field setup, validator registries, config inheritance, nested model graphs, and ValidationError flattening across multiple internal modules.",
  "signals": [
    "ModelMetaclass builds fields and validator groups at class creation",
    "nested BaseModel errors require loc prefix merging",
    "root_validator runs after field validation with different error semantics",
    "Config.extra and error_msg_templates change validation behavior"
  ]
}
```

## Target Feature

### Source entrypoints

- `pydantic.BaseModel`
- `pydantic.ValidationError`
- `pydantic.validator`
- `pydantic.root_validator`
- `pydantic.Field`
- `pydantic.config.Extra`
- `pydantic.error_wrappers.flatten_errors`

### Output API

```python
from featurelifted import BaseModel, Field, ValidationError, validator, root_validator, Extra
```

Primary callable:

```python
featurelifted.BaseModel.parse_obj(data)
```

### Included behaviors

- Declare `BaseModel` subclasses with typed fields and defaults.
- Parse dict input via constructor / `parse_obj`, raising `ValidationError` on failure.
- `@validator` field validators (`pre`, `each_item`, `always`).
- `@root_validator` whole-model checks.
- `Config.extra = Extra.forbid` and nested model validation.
- `ValidationError.errors()` returns list of dicts with `loc`, `msg`, `type` (and optional `ctx`).
- Nested errors include full loc paths (e.g. `('items', 0, 'qty')`).

### Excluded behaviors

- JSON Schema generation (`schema`, `schema_json`, `schema.py`).
- Network/email/DSN types (`networks.py`).
- `BaseSettings` / env loading.
- `dataclasses` integration, `validate_arguments`, generics, mypy plugin.
- Original `pydantic` import at runtime.

## Environment

```json
{
  "python": "3.11",
  "network": false,
  "timeout_seconds": 60,
  "dependency_lock": "requirements.lock",
  "allowed_dependencies": ["typing_extensions"],
  "forbidden_dependencies": ["pydantic"],
  "forbidden_imports": ["pydantic"]
}
```

## Public Tests

- Simple model field coercion (`str`, `int`, `bool`).
- Missing required field raises `ValidationError`.
- `@validator` normalizes a field value.
- `errors()[0]['loc']` and `errors()[0]['type']` present on failure.

## Hidden Tests

- Nested model/list loc paths for invalid nested items.
- `@root_validator` failure surfaces at `__root__` or field loc.
- `Config.extra = Extra.forbid` rejects unknown keys.
- `validator(pre=True)` runs before type coercion.
- Multiple errors returned in one `ValidationError`.
- Assert error `type` codes, not full message strings (avoid flaky text).
- No `pydantic` import in package sources; no `schema()` on public API.

## Module Probes

| Probe | Remove module | Hidden test(s) that must fail |
| --- | --- | --- |
| Probe-1 | `featurelifted/error_wrappers.py` | `test_nested_validation_error_loc_paths` |
| Probe-2 | `featurelifted/class_validators.py` | `test_root_validator_rejects_invalid_combo` |
| Probe-3 | `featurelifted/fields.py` | `test_extra_forbid_rejects_unknown_keys` |
| Probe-4 | `featurelifted/validators.py` | `test_validator_pre_runs_before_type_check` |

## Manual Oracle Closure Plan

| Check | Target | Result |
| --- | --- | --- |
| Public tests | pass | pass |
| Hidden tests | pass | pass |
| Forbidden import check | pass | pass |
| Oracle LOC | 1200-3500 preferred | ~5836 (15 modules) |
| Source repo Python LOC | ~13226 | 13226 |
| ExtractionRatio | 0.20-0.60 | 0.567 |
| Copy-All functional gate | 1.0 | 1.0 |
| Copy-All ExtractionRatio | >= 0.95 | 0.991 |
| Naive/shallow baseline | hidden fail | hidden fail (nested loc paths) |
| Module probes | all verified | 4/4 OK |

Expected closure shape:

```text
featurelifted/
  __init__.py
  main.py
  fields.py
  class_validators.py
  config.py
  error_wrappers.py
  errors.py
  validators.py
  types.py
  typing.py
  utils.py
  json.py
  datetime_parse.py
  version.py
  annotated_types.py
```

## Go / No-Go Criteria

**Go** if oracle is 1200-7500 LOC, extraction 0.20-0.60, hidden tests discriminate naive implementations, and Flash fails hidden while passing some public tests.

**No-go** if closure requires schema/networks/settings modules, or error assertions are message-flaky.

## Agent Calibration

| Run | Model | Passed | ExtractionRatio | Tokens | Notes |
| --- | --- | --- | --- | --- | --- |
| `pydantic_v1__validation_error_core__001-flash-001` | deepseek_v4_flash | yes (hidden pass) | 0.558 | 1.83M | copy-heavy closure (~20 files); final_score≈0.44; consider stronger hidden vs bulk-copy in future |

**Promote decision (2026-06-27):** GO — oracle/naive/copy-all layering clear; module probes verified. Flash achieved functional pass via near-oracle-sized copy; scoring penalizes extraction but hidden discrimination is weaker than httpx pilot.
