# Task Design: `ruamel_yaml__roundtrip_core__001`

Status: agent-calibrated (B-tier exception promote)

## Practical reuse

1. **Reuse module** — Config round-trip preserving comments and ordering.
2. **Who imports it** — Tools needing ruamel-style YAML editing without full packaging stack.
3. **Why not copy-all** — Package is already compact; copy-all equals oracle for Python modules.

## Module Probes

| Probe | Remove module | Hidden test(s) that must fail |
| --- | --- | --- |
| Comments model | `featurelifted/comments.py` | `test_eol_comment_preserved` |
| Emitter | `featurelifted/emitter.py` | `test_flow_style_dump` |
| Scanner | `featurelifted/scanner.py` | `test_literal_block_scalar` |

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
