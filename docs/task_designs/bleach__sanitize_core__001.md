# Task Design: `bleach__sanitize_core__001`

Status: agent-calibrated (B-tier exception promote)

## Practical reuse

1. **Reuse module** — Standalone HTML fragment sanitizer for user-generated content pipelines.
2. **Who imports it** — Apps needing bleach-style `clean()` without vendoring linkifier stack.
3. **Why not copy-all** — Curated snapshot includes linkifier/callbacks; compact closure keeps sanitizer + html5lib shim.

## Module Probes

| Probe | Remove module | Hidden test(s) that must fail |
| --- | --- | --- |
| Sanitizer core | `featurelifted/sanitizer.py` | `test_strip_disallowed_script` |
| Html5lib shim | `featurelifted/html5lib_shim.py` | `test_strip_mode_removes_tag` |
| Vendor parse | `featurelifted/_vendor/parse.py` | `test_javascript_href_stripped` |

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
