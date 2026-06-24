# Task Design: vibe_app__yaml_config_bootstrap__001

Status: oracle-verified

## Why This Task

Decouple layered YAML bootstrap from a legacy app where config loading mutates `GLOBAL_STATE` and a broken fast bootstrap shortcut coexists with the real merge path.

## Source

| Field | Value |
| --- | --- |
| Source repo | `sources/vibe_app/` |
| Commit | curated |
| License | MIT |
| Language | Python |
| Difficulty | hard |
| Tags | extreme, multi-task-repo, functional-discriminator, config_environment_coupling |

## Target Feature

### Source entrypoints

- `vibe_app.config_loader.bootstrap_config`
- `vibe_app.config_merge.merge_config_layers`

### Output API

```python
from featurelifted import bootstrap_config, merge_config_layers
```

## Public Tests

- Deep merge preserves nested keys while overriding leaves.
- Bootstrap loads bundled default/app/pricing/tiers layers from repo config dir.

## Hidden Tests

- `${ENV:-default}` expansion while loading YAML.
- Bootstrap records side effects in registry state.
- Merge does not mutate input dicts.

## Module Probes

| Probe | Remove module | Hidden test(s) that must fail |
| --- | --- | --- |
| Deep merge | `config_merge.py` | `test_merge_does_not_mutate_inputs` |
| Env expansion | `config_loader.py` | `test_env_placeholder_expansion` |

## Manual Oracle Closure Plan

Expected closure shape:

```text
featurelifted/
  __init__.py
  state.py
  config_merge.py
  config_loader.py
```
