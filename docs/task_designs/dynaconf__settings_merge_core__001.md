# Task Design: dynaconf__settings_merge_core__001

Status: agent-calibrated

## Module Probes

| Probe | Remove module | Hidden test(s) that must fail |
| --- | --- | --- |
| object_merge | `utils/__init__.py` | `test_object_merge_list_shallow` |
| TOML loader | `loaders/toml_loader.py` | `test_layered_toml_environments` |
| env loader | `loaders/env_loader.py` | `test_dynaconf_toml_and_env_override` |

## Manual Oracle Closure Plan

| Check | Target | Result |
| --- | --- | --- |
| Public tests | pass | |
| Hidden tests | pass | |
| ExtractionRatio | 0.20 – 0.60 | |
| Copy-All delta | ≥ 0.25 | |
