# Task Design: `websockets__handshake_parse_core__001`

Status: agent-calibrated

## Spike Decision

**GO for staging** with ExtractionRatio blocker noted below.

HTTP upgrade handshake parsing (header grammars + HTTP/1.1 request parse + validation) without socket I/O; distinct from full websockets client/server stacks.

## Blockers

1. **ExtractionRatio 0.100** — Oracle closure is ~1,240 LOC vs full pinned repo ~12,456 LOC. Handshake slice is inherently small relative to the full websockets package (async/sync transports, framing, extensions). Copy-all discrimination is strong (final_score 0.040 vs oracle 0.900), but ratio is below the 0.20 staging floor. Mitigation options before promote: widen closure (e.g. response-side validation + legacy handshake helpers) or accept yellow-zone justification in design review.

2. **Flash calibration** — Not run (per batch instructions).

## Practical reuse

1. **Reuse module** — Standalone WebSocket handshake header parser for gateways, proxies, and protocol test harnesses.
2. **Who imports it** — API gateways, WS middleware, security scanners validating upgrade requests offline.
3. **Why not copy-all** — Full websockets includes async/sync transports, framing, extensions, and CLI; compact closure keeps header/HTTP parsing only.

## Source

| Field | Value |
| --- | --- |
| Source repo | `https://github.com/python-websockets/websockets` |
| Commit | `d4303a5d3e373fc8c34177c3dec1a9c75c8865fa` (v16.0) |
| License | BSD-3-Clause |
| Difficulty | hard |
| Tags | `batch-1`, `websockets`, `hard-first`, `functional-discriminator`, `parser_state_coupling`, `no-network` |

## Target API

```python
from featurelifted import Headers, Request, validate_handshake_request, accept_key
from featurelifted.headers import parse_connection, parse_upgrade, parse_extension, parse_subprotocol
from featurelifted.exceptions import InvalidHeaderFormat, InvalidUpgrade
```

## Module Probes

| Probe | Remove module | Hidden test(s) that must fail |
| --- | --- | --- |
| Probe-1 | `featurelifted/headers.py` | `test_parse_extension_with_quoted_params` |
| Probe-2 | `featurelifted/http11.py` | `test_parse_request_invalid_method` |
| Probe-3 | `featurelifted/handshake.py` | `test_validate_handshake_rejects_bad_upgrade` |

## Manual Oracle Closure Plan

| Check | Target | Result |
| --- | --- | --- |
| Public tests | pass | **pass** |
| Hidden tests | pass | **pass** |
| ExtractionRatio | 0.20–0.60 | **0.100** (below floor — see blockers) |
| Naive hidden fail | yes | **pass** (public pass, hidden fail on extension parse) |
| Copy-all vs oracle | ≥0.30 higher | **pass** (0.960 vs 0.100; Δ=0.860) |
| Module probes | ≥3 | **3/3 pass** |

## Agent Calibration

| Run | Model | Passed | ExtractionRatio | final_score | Notes |
| --- | --- | --- | ---: | ---: | --- |
| `websockets__handshake_parse_core__001-flash-001` | deepseek_v4_flash | yes (all tests) | 0.066 | 0.934 | **B-tier:** 紧凑实现通过全部 hidden |
