# Task Design: `environs__typed_env_core__001`

Status: agent-calibrated (B-tier exception promote)

## Why This Task

Environs is a widely used typed environment-variable loader. Its core couples marshmallow field deserialization, string preprocessing for composite types, variable expansion, prefix scoping, and deferred validation—stronger discrimination than a thin `os.environ` wrapper for agents that only implement basic casts.

## Practical reuse

1. **Reuse module** — Standalone typed env loader for services and CLIs: cast env vars to Python types with validators, defaults, and batch validation.
2. **Who imports it** — Teams decoupling config bootstrap from dotenv file I/O or Django URL helpers while keeping marshmallow validation semantics.
3. **Why not copy-all** — Upstream bundles dotenv loading, FileAwareEnv, django URL parsers, and a large upstream test suite; compact closure keeps parsing core only.

## Source

| Field | Value |
| --- | --- |
| Source repo | https://github.com/sloria/environs |
| Commit | `97f9b7065c753b763949a8d61ec2fee880458d4a` (v15.0.1) |
| License | MIT |
| Difficulty | hard |
| Tags | batch-1, functional-discriminator, config_environment_coupling |

## Target API

```python
from featurelifted import Env, EnvError, EnvValidationError, validate
```

## Module Probes

| Probe | Remove module | Hidden test(s) that must fail |
| --- | --- | --- |
| Custom timedelta field | `featurelifted/fields.py` | `test_timedelta_gep2257_duration` |
| Env parsing core | `featurelifted/env.py` | `test_list_subcast_int` |
| Exception types | `featurelifted/exceptions.py` | `test_deferred_seal_aggregates_errors` |

## Public Tests

- `int` / `bool` casting from env strings
- `str` default when unset
- Missing required var raises `EnvError` in eager mode

## Hidden Tests

- `list` with `subcast=int`
- `dict` with `subcast_values=int`
- `expand_vars` default substitution and multi-var string expansion
- Marshmallow `validate.Range` on `int`
- `eager=False` + `seal()` aggregates multiple field errors
- GEP-2257 `timedelta` duration string
- `prefixed` context manager for key names
- No runtime `environs` import surface

## Manual Oracle Closure Plan

| Check | Target | Result |
| --- | --- | --- |
| Public tests | pass | pass (oracle, copy_all, naive) |
| Hidden tests | pass | pass (oracle, copy_all); **fail** (naive) |
| Forbidden import check | pass | pass |
| Oracle LOC | ~900+ | 778 |
| Source repo Python LOC | ~2700 | 2193 |
| ExtractionRatio | 0.20 – 0.60 | oracle **0.355** |
| Copy-All ExtractionRatio | ≥ 0.85 | **0.877** (Δ=0.522 vs oracle) |
| Module probes | all verified | **3/3 OK** |

Expected closure shape:

```text
featurelifted/
  __init__.py
  env.py
  exceptions.py
  types.py
  fields.py
```

## Go / No-Go Criteria

- Practical reuse narrative credible for config/bootstrap modules.
- Oracle compact; copy-all high extraction; naive passes public, fails hidden.
- ≥3 module probes verified.
