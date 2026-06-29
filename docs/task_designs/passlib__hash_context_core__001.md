# Task Design: passlib__hash_context_core__001

Status: agent-calibrated (B-tier exception promote)

## Module Probes

| Probe | Remove module | Hidden test(s) that must fail |
| --- | --- | --- |
| CryptContext | `context.py` | `test_context_verify_and_update_roundtrip` |
| pbkdf2 handler | `utils/handlers.py` | `test_context_hash_includes_rounds` |
| registry | `registry.py` | `test_context_hash_includes_rounds` |

## Manual Oracle Closure Plan

| Check | Target | Result |
| --- | --- | --- |
| Public tests | pass | pass |
| Hidden tests | pass | pass |
| ExtractionRatio | 0.20 – 0.60 | 0.249 |
| Copy-All delta | ≥ 0.25 | 0.364 |
