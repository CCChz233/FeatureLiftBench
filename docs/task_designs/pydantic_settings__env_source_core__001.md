# Task Design: pydantic_settings__env_source_core__001

Status: agent-calibrated (B-tier exception promote)

## Module Probes

| Probe | Remove module | Hidden test(s) that must fail |
| --- | --- | --- |
| Env source | `sources/providers/env.py` | `test_env_prefix_and_nested` |
| Settings main | `main.py` | `test_json_list_env` |
| sources utils | `sources/utils.py` | `test_case_sensitive_env` |

## Manual Oracle Closure Plan

| Check | Target | Result |
| --- | --- | --- |
| Public tests | pass | |
| Hidden tests | pass | |
| ExtractionRatio | 0.20 – 0.60 | |
| Copy-All delta | ≥ 0.25 | |
