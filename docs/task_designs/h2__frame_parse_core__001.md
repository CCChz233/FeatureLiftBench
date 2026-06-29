# Task Design: `h2__frame_parse_core__001`

Status: agent-calibrated (B-tier exception promote)

## Practical reuse

1. **Reuse module** — Extract hyperframe HTTP/2 frame serialization and h2 FrameBuffer reassembly without connection/stream state machines.
2. **Who imports it** — Teams building HTTP/2 tooling, proxies, or protocol tests without vendoring full h2 connection state machines.
3. **Why not copy-all** — Curated snapshot includes full h2/ and hyperframe/ trees; compact closure keeps frame parse + buffer only.

## Module Probes

| Probe | Remove module | Hidden test(s) that must fail |
| --- | --- | --- |
| hyperframe frames | `featurelifted/hyperframe/frame.py` | `test_ping_stream_id_must_be_zero` |
| FrameBuffer | `featurelifted/h2/frame_buffer.py` | `test_continuation_reassembly` |
| h2 exceptions | `featurelifted/h2/exceptions.py` | `test_frame_buffer_rejects_bad_preamble` |

## Manual Oracle Closure Plan

| Check | Target | Result |
| --- | --- | --- |
| Public tests | pass | pass |
| Hidden tests | pass | pass |
| ExtractionRatio | 0.20 – 0.60 | 0.20 |
| Copy-All delta | ≥ 0.25 | 0.81 |

## Agent Calibration

| Run | Model | Passed | ExtractionRatio | final_score | Notes |
| --- | --- | --- | ---: | ---: | --- |
| oracle | — | yes | 0.20 | 0.80 | Step 5 promote batch-1 #47 |
| naive | — | pub/hid | 0.018 | — | hidden fail |
| copy-all | — | yes | 1.009 | — | Δ≈0.81 |
| | | | | | Flash deferred |
