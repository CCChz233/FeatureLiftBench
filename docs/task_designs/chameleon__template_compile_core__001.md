# Task Design: chameleon__template_compile_core__001

Status: agent-calibrated (B-tier exception promote)

## Module Probes

| Probe | Remove module | Hidden test(s) that must fail |
| --- | --- | --- |
| TAL compiler | `tal.py` | `test_tal_repeat_and_condition` |
| TALES | `tales.py` | `test_render_python_expression` |
| ZPT program | `zpt/program.py` | `test_tal_attributes_replace` |

## Manual Oracle Closure Plan

| Check | Target | Result |
| --- | --- | --- |
| Public tests | pass | |
| Hidden tests | pass | |
| ExtractionRatio | 0.20 – 0.60 | |
| Copy-All delta | ≥ 0.25 | |
