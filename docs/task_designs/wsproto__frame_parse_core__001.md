# Task Design: `wsproto__frame_parse_core__001`

Status: agent-calibrated (B-tier exception promote)

## Practical reuse

1. **Reuse module** — Extract wsproto RFC6455 frame parsing, masking, fragmentation, and control frames without HTTP handshake or connection lifecycle.
2. **Who imports it** — WebSocket middleware, protocol fuzzers, and frame-level test harnesses without full wsproto connection state.
3. **Why not copy-all** — Curated snapshot bundles wsproto + h11; compact closure keeps frame_protocol (+ minimal events/utilities glue).

## Module Probes

| Probe | Remove module | Hidden test(s) that must fail |
| --- | --- | --- |
| Frame fragmentation | `featurelifted/frame_protocol.py` | `test_fragmented_message_reassembly` |
| Frame masking rules | `featurelifted/frame_protocol.py` | `test_role_masking_validation` |
| Masked server decode | `featurelifted/frame_protocol.py` | `test_server_decodes_masked_client_frame` |

## Manual Oracle Closure Plan

| Check | Target | Result |
| --- | --- | --- |
| Public tests | pass | pass |
| Hidden tests | pass | pass |
| ExtractionRatio | 0.20 – 0.60 | 0.317 |
| Copy-All delta | ≥ 0.25 | 0.668 |

## Agent Calibration

| Run | Model | Passed | ExtractionRatio | final_score | Notes |
| --- | --- | --- | ---: | ---: | --- |
| oracle | — | yes | 0.317 | 0.683 | Step 5 promote batch-1 #49 |
| naive | — | pub/hid | 0.015 | — | hidden fail |
| copy-all | — | yes | 0.985 | — | Δ≈0.668 |
| | | | | | Flash deferred |
