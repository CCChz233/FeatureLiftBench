# Task Design: `urllib3__retry_backoff_core__001`

Status: agent-calibrated (B-tier exception promote)

## Why This Task

HTTP client libraries embed retry policy as a standalone configuration object. urllib3's `Retry` couples counter semantics, backoff history, status/method allowlists, and redirect accounting—testable without sockets when exercised through `increment`/`is_retry`/`get_backoff_time`.

## Practical reuse（必填）

1. **Reuse module** — A vendored HTTP retry policy object for SDKs, API gateways, or job runners that need urllib3-compatible retry semantics without the full urllib3 stack.
2. **Who imports it** — Teams building thin HTTP wrappers or resilience middleware that must match urllib3 retry/backoff behavior in tests.
3. **Why not copy-all** — The util package bundles SSL, URL parsing, connection helpers, and wait primitives; compact closure keeps Retry + required exceptions only.

## Source

| Field | Value |
| --- | --- |
| Source repo | https://github.com/urllib3/urllib3 |
| Commit | `2f68c5363ef632d73dd4d9300289d7ce5ff275b4` (2.3.0) |
| License | MIT |
| Language | Python |
| Difficulty | hard |
| Tags | batch-1, functional-discriminator, config_environment_coupling |

## Entanglement

```json
{
  "level": "high",
  "types": ["config_environment_coupling", "data_model_coupling", "implicit_dependency_coupling"],
  "primary": "config_environment_coupling",
  "description": "Retry couples multi-counter config, backoff history, allowlists, redirect vs error branches, and MaxRetryError reasons.",
  "signals": ["total/connect/read/status interplay", "backoff reset on redirect", "status_forcelist AND allowed_methods", "RequestHistory growth", "parse_retry_after branches"]
}
```

## Target Feature

### Source entrypoints

- `urllib3.util.retry.Retry`
- `urllib3.util.retry.RequestHistory`
- `urllib3.exceptions.MaxRetryError`

### Output API

```python
from featurelifted import Retry, RequestHistory, MaxRetryError, ConnectTimeoutError, ReadTimeoutError, ResponseError, InvalidHeader
```

## Included Behaviors

- Retry defaults, `from_int`, counter decrement and exhaustion
- `status_forcelist` + `allowed_methods` conjunction
- Exponential backoff with cap; redirect resets consecutive error backoff
- `parse_retry_after` numeric/date parsing with cap
- `RequestHistory` on increment; `remove_headers_on_redirect` lowercasing

## Excluded Behaviors

- Connection pools, sockets, TLS, PoolManager
- Actual HTTP request/response I/O (tests use mock response objects)
- Original `urllib3` import at runtime

## Public Tests

- Defaults / `from_int`
- `is_retry` with status_forcelist
- Backoff progression on consecutive increments
- Connect timeout increment exhaustion

## Hidden Tests

- Total vs connect counter precedence
- allowed_methods AND status_forcelist
- Backoff reset after redirect
- parse_retry_after numeric and invalid header
- History accumulation; read timeout method gate
- remove_headers_on_redirect lowercasing
- Status-specific MaxRetryError message
- No urllib3 imports in submission

## Module Probes

| Probe | Remove module | Hidden test(s) that must fail |
| --- | --- | --- |
| Probe-1 | `featurelifted/exceptions.py` | `test_total_wins_over_connect` |
| Probe-2 | `featurelifted/util.py` | `test_read_timeout_requires_allowed_method` |
| Probe-3 | `featurelifted/retry.py` | `test_backoff_resets_after_redirect` |

## Manual Oracle Closure Plan

| Check | Target | Result |
| --- | --- | --- |
| Public tests | pass | pass (oracle, copy_all, naive) |
| Hidden tests | pass | pass (oracle, copy_all); **fail** (naive) |
| Forbidden import check | pass | pass |
| Oracle LOC | ~900+ | 648 |
| Source repo Python LOC | ~3300 (trimmed util snapshot) | 2347 |
| ExtractionRatio | 0.20 – 0.60 | oracle **0.276** |
| Copy-All functional gate | 1.0 | pass |
| Copy-All ExtractionRatio | > oracle + margin | **1.004** (Δ=0.728) |
| Module probes | all verified | 3/3 OK |

Expected closure shape:

```text
featurelifted/
  __init__.py
  exceptions.py
  util.py
  retry.py
```

## Go / No-Go Criteria

- Practical reuse narrative holds for HTTP SDK middleware.
- Oracle passes public + hidden; naive fails hidden on counter/backoff semantics.
- ≥3 module probes verified after Step 5.
- ExtractionRatio in band; copy-all penalized vs compact oracle.

## Agent Calibration

| Run | Model | Passed | ExtractionRatio | final_score | Notes |
| --- | --- | --- | ---: | ---: | --- |
| `urllib3__retry_backoff_core__001-flash-001` | deepseek_v4_flash | yes (all tests) | 0.159 | 0.842 | **B-tier: 全过，ext≈0.16 vs oracle 0.28** |
