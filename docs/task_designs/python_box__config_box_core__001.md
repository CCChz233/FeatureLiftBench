# Task Design: `python_box__config_box_core__001`

Status: agent-calibrated (B-tier exception promote)

## Practical reuse

1. **Reuse module** — Typed config dict with dot access for twelve-factor apps and CLI defaults.
2. **Who imports it** — Teams using ConfigBox-style env/config parsing without file converters.
3. **Why not copy-all** — Full python-box bundles YAML/TOML converters, BoxList, and file loaders.

## Module Probes

| Probe | Remove module | Hidden test(s) that must fail |
| --- | --- | --- |
| Case fold | `featurelifted/config_box.py` | `test_case_insensitive_key_lookup` |
| List mod | `featurelifted/config_box.py` | `test_list_with_mod_callback` |
| Box access | `featurelifted/box.py` | `test_dot_access` |

## Manual Oracle Closure Plan

| Check | Target | Result |
| --- | --- | --- |
| Public tests | pass | |
| Hidden tests | pass | |
| ExtractionRatio | 0.20 – 0.60 | |
| Copy-All delta | ≥ 0.25 | |
