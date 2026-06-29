# Task Design: `parso__python_parse_core__001`

Status: agent-calibrated (B-tier exception promote)

## Practical reuse

1. **Reuse module** — Lightweight Python parser for tooling/linters.
2. **Who imports it** — Jedi-like tools needing parso grammar without full jedi.
3. **Why not copy-all** — diff/pep8 modules add weight beyond parse core.

## Module Probes

| Probe | Remove module | Hidden test(s) that must fail |
| --- | --- | --- |
| Grammar loader | `featurelifted/grammar.py` | `test_parse_version_39` |
| Python parser | `featurelifted/python/parser.py` | `test_iter_errors_multiple` |
| Tree nodes | `featurelifted/python/tree.py` | `test_get_code_roundtrip` |

## Manual Oracle Closure Plan

| Check | Target | Result |
| --- | --- | --- |
| Public tests | pass | |
| Hidden tests | pass | |
| ExtractionRatio | 0.20 – 0.60 | |
| Copy-All delta | ≥ 0.25 | |

## Agent Calibration

| Run | Model | Passed | ExtractionRatio | final_score | Notes |
| --- | --- | --- | ---: | ---: | --- |
| | | | | | Flash deferred |
