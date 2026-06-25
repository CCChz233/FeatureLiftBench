# Task Design: coverage__config_merge_core__001

Status: oracle-verified

## Why This Task

Covers run-section configuration inheritance across rc formats, env vars, and kwargs without pulling in measurement or path remapping logic.

## Output API

```python
from featurelifted import CoverageConfig, read_run_config
```

## Module Probes

| Probe | Remove module | Hidden test(s) that must fail |
| --- | --- | --- |
| INI parser | `config.py` (`HandyConfigParser`) | `test_read_run_config_from_setup_cfg` |
| Env merge | `config.py` (`read_coverage_config`) | `test_read_run_config_env_data_file` |
| Multiline lists | `config.py` / `tomlconfig.py` list merge | `test_read_run_config_multiline_lists` |

## Manual Oracle Closure Plan

Expected closure: `env.py`, `exceptions.py`, `types.py`, `misc.py`, `config.py`, `tomlconfig.py`.
