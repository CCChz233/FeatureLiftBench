# Task Design Spike: `httpx__request_model_core__001`

> Machine-readable task spec will be created only if this spike passes review. This is a pre-staging design spike, not an oracle-verified task.

Status: agent-calibrated

## Spike Decision

**Recommendation: GO for staging spike, with hard gate checks before promotion.**

This should not be a small `URL` utility extraction. The candidate is only worth doing if the target feature includes the interaction between `URL`, `QueryParams`, `Headers`, `Cookies`, `Request`, and client/default merge semantics. A task that only asks for `URL` parsing is too light for batch-1 mainboard.

## Why This Task

HTTPX is a real HTTP client library, but a substantial part of its value before network I/O is the request data model: normalize URLs, merge query params, preserve header semantics, merge cookies, and build a request object consistently. That slice is useful outside HTTPX itself, for SDK generators, API clients, signing middleware, proxy/gateway test harnesses, and offline request canonicalization.

The difficulty comes from extracting this request-building core from a client stack that also contains transports, streaming, auth, redirects, timeout handling, response decoding, and async/sync runtime concerns. The useful package should not include networking.

## Practical reuse

1. **Reuse module** — `featurelifted` represents an offline HTTP request model and builder: URL normalization, query/header/cookie containers, and request construction/merge rules.
2. **Who imports it** — A team building API SDK tooling, request signing, cache-key generation, mock servers, contract tests, or proxy/gateway validation could import this without depending on HTTPX transports.
3. **Why not copy-all** — Copying all of HTTPX brings networking transports, sync/async clients, response streaming, auth, proxy, timeout, and optional dependency surface that are irrelevant to offline request canonicalization.

## Source

| Field | Value |
| --- | --- |
| Source repo | `https://github.com/encode/httpx` |
| Commit | `326b9431c761e1ef1e00b9f760d1f654c8db48c6` (HTTPX 0.27.0) |
| License | BSD-3-Clause |
| Language | Python |
| Difficulty | hard |
| Tags | `batch-1`, `request-model`, `hard-first`, `functional-discriminator`, `no-network` |

## Entanglement

```json
{
  "level": "high",
  "types": [
    "data_model_coupling",
    "parser_state_coupling",
    "config_environment_coupling",
    "implicit_dependency_coupling"
  ],
  "primary": "data_model_coupling",
  "description": "HTTP request model behavior is spread across model containers, URL parsing, client defaults, request construction, content helpers, and exception/type utilities. The reusable slice must preserve request semantics while excluding transports and network execution.",
  "signals": [
    "URL, QueryParams, Headers, Cookies, and Request interact rather than acting as isolated helpers",
    "client-level defaults are merged into per-request values",
    "case-insensitive header behavior must preserve raw/canonical forms",
    "query parameter ordering, duplicate keys, escaping, and removal semantics matter",
    "the source package contains large unrelated sync/async transport and response machinery"
  ]
}
```

## Target Feature

### Source entrypoints

Verify exact module paths after pinning the HTTPX commit. Expected entrypoints:

- `httpx.URL`
- `httpx.QueryParams`
- `httpx.Headers`
- `httpx.Cookies`
- `httpx.Request`
- `httpx.Client.build_request`
- `httpx._client.BaseClient._merge_url`
- `httpx._client.BaseClient._merge_headers`
- `httpx._client.BaseClient._merge_cookies`
- `httpx._client.BaseClient._merge_queryparams`
- Supporting source modules likely include `_models.py`, `_urls.py`, `_client.py`, `_content.py`, `_types.py`, `_exceptions.py`, and `_utils.py`.

### Output API

Proposed external API:

```python
from featurelifted import Cookies, Headers, QueryParams, Request, URL, build_request
```

Primary callable:

```python
featurelifted.build_request(
    method,
    url,
    *,
    base_url="",
    params=None,
    headers=None,
    cookies=None,
    default_params=None,
    default_headers=None,
    default_cookies=None,
    content=None,
    data=None,
    json=None,
)
```

The function should model the relevant behavior of HTTPX request construction without exposing `Client`, network transports, `send`, response handling, or async APIs.

## Included Behaviors

- Construct and compare `URL` objects from strings, bytes-compatible input, relative paths, and base URL joins.
- Preserve query parameter ordering and duplicate keys where HTTPX does.
- Support `QueryParams` construction from strings, mappings, list-of-pairs, and mixed scalar/list values.
- Support header case-insensitive lookup while preserving raw header values for iteration and request construction.
- Merge request-specific headers over default headers using HTTPX-compatible semantics.
- Merge default query params with per-request query params.
- Merge cookies from defaults and per-request cookies into a request cookie header.
- Build `Request` objects with normalized method, URL, headers, cookies, and body content for common `content`, `data`, and `json` cases.
- Raise compatible exception types for invalid URL and invalid request input.

## Excluded Behaviors

- Network I/O, transports, connection pools, proxies, redirects, retries, HTTP/2, TLS, sockets.
- `Client.send`, `AsyncClient`, response parsing/decoding, streaming response APIs.
- Authentication flows except any minimal header interactions required by request construction.
- Multipart file upload internals unless required for ordinary form data behavior.
- Original package import at runtime.
- CLI, docs, CI, original tests, packaging metadata.

## Environment

```json
{
  "python": "3.11",
  "network": false,
  "timeout_seconds": 60,
  "dependency_lock": "requirements.lock",
  "allowed_dependencies": ["idna"],
  "forbidden_dependencies": ["httpx"],
  "forbidden_imports": ["httpx"]
}
```

Open question: prefer empty `requirements.lock` if the pinned source can be copied with no third-party runtime dependency for the selected API. If `idna` is required for IDNA hostname behavior, keep it explicitly allowed and pinned.

## Public Tests

Public tests should establish the API and main path without revealing every merge edge:

- Construct `URL` with path, query, fragment, and base URL behavior.
- Construct `QueryParams` from mapping and list-of-pairs; assert stable string output for simple cases.
- Construct `Headers`; assert case-insensitive lookup and override behavior.
- Construct `Cookies`; assert cookie header generation for simple defaults.
- Use `build_request` with default headers/params/cookies and per-request overrides.
- Verify no network APIs are present or needed.

## Hidden Tests

Hidden tests must distinguish a real extraction from a shallow public-test implementation:

- Duplicate query keys and ordered updates:
  - list-of-pairs with repeated keys,
  - overriding one key while preserving unrelated duplicates,
  - empty value vs missing value.
- URL joining and escaping:
  - base URL with path prefix,
  - relative path with existing query,
  - percent-encoded path/query components,
  - IDNA hostname if dependency is allowed.
- Header semantics:
  - repeated headers,
  - mixed casing,
  - raw value preservation,
  - comma-join behavior only where HTTPX does it.
- Cookie merge semantics:
  - default cookies plus per-request cookies,
  - override same cookie name,
  - request-supplied `Cookie` header interaction.
- Request body helpers:
  - `content=b"bytes"`,
  - `data={"a": "b"}`,
  - `json={"x": 1}`,
  - content-type header defaults and explicit override behavior.
- Error compatibility:
  - invalid URL forms,
  - unsupported data/content combinations,
  - invalid header values.
- Negative decoupling checks:
  - importing `featurelifted` must not import `httpx`,
  - no `Client.send`, `AsyncClient`, transport classes, or response streaming API.

## Testability Plan

This candidate is acceptable only if the behavior can be evaluated with deterministic offline pytest tests.

Evaluation design:

- Compare concrete request-model outputs: `str(request.url)`, `request.method`, ordered query pairs, header lookup/raw iteration, cookie header, and body bytes.
- Avoid real network, DNS, proxy, TLS, sockets, or async runtime.
- Avoid wall-clock time and platform-specific environment behavior.
- If IDNA behavior is included, pin `idna` in `requirements.lock` and use fixed domains in tests.
- For error tests, assert exception classes and stable structural fields before asserting exact full messages.
- Include one deliberately shallow baseline during staging review:
  - naive `URL=str`, `Headers=dict`, `QueryParams=dict` implementation should pass some public tests but fail hidden duplicate/order/raw-header/cookie/body interactions.
- Include copy-all as a functional pass but high-extraction baseline.

No-go if the only meaningful tests require making actual requests, exercising transports, relying on installed HTTPX, or comparing highly version-specific internals that are not part of the intended output API.

## Module Probes

| Probe | Remove module | Hidden test(s) that must fail |
| --- | --- | --- |
| Probe-1 | `featurelifted/_urls.py` | `test_base_url_join_and_duplicate_query_params` |
| Probe-2 | `featurelifted/_models.py` | `test_headers_cookie_merge_and_request_object` |
| Probe-3 | `featurelifted/_client_merge.py` | `test_build_request_merges_client_defaults` |
| Probe-4 | `featurelifted/_content.py` | `test_request_content_data_json_headers` |

## Manual Oracle Closure Plan

| Check | Target | Result |
| --- | --- | --- |
| Public tests | pass | **pass** |
| Hidden tests | pass | **pass** |
| Forbidden import check | pass | **pass** |
| Oracle LOC | 1200-3500 preferred | **2322** |
| Source repo Python LOC | TBD after snapshot | **7296** |
| ExtractionRatio | 0.20-0.55 | **0.318** |
| Copy-All functional gate | 1.0 | **pass** |
| Copy-All ExtractionRatio | >= 0.95 | **0.908** |
| Naive/shallow baseline | hidden fail | **pass** (public pass, hidden fail) |
| Module probes | all verified | **4/4 pass** |
| Flash calibration | discriminative | **pass** (public pass, hidden fail, extraction 0.17) |

Expected closure shape:

```text
featurelifted/
  __init__.py
  _client_merge.py
  _content.py
  _exceptions.py
  _models.py
  _types.py
  _urls.py
  _utils.py
```

Do not accept a closure that includes transports, clients capable of network I/O, response decoders, async runtime adapters, proxy handling, or TLS/certificate utilities unless a specific request-building behavior demonstrably needs a tiny helper.

## Spike Work Plan

1. Pin an HTTPX commit and snapshot it under `benchmark/staging/httpx__request_model_core__001/repo/`.
2. Inspect imports from `_models.py`, `_urls.py`, `_client.py`, `_content.py`, `_types.py`, `_exceptions.py`, `_utils.py`.
3. Build a throwaway oracle closure by copying only request-model modules and extracting merge helpers from `Client`/`BaseClient` into `_client_merge.py`.
4. Draft public/hidden tests before finalizing metadata.
5. Build a naive/shallow baseline and confirm hidden tests fail for meaningful reasons.
6. Run oracle eval and compute extraction ratio.
7. Run module probe removals.
8. If closure is too small, expand only with behavior that is still useful request-model behavior; if closure is too large, narrow the API or drop the candidate.

## Go / No-Go Criteria

**Go to staging if all hold:**

- The useful module is an offline request builder, not merely a URL parser.
- Oracle closure spans multiple interacting modules and is not a one-file copy.
- Expected oracle extraction ratio lands roughly between 0.20 and 0.55.
- Hidden tests can force interactions across URL, query params, headers, cookies, and request body helpers.
- Tests are deterministic, offline, and fail with clear functional causes.
- Naive/shallow baseline fails hidden while oracle passes.
- At least three module probes trigger distinct hidden failures.
- The output package has no network-capable API surface.

**No-go / redesign if any hold:**

- The closure collapses to a thin wrapper around `_urls.py` and `_models.py` with little merge logic.
- Preserving behavior requires copying most of HTTPX.
- Hidden tests mostly duplicate public tests or only check simple container construction.
- Hidden failures are flaky, depend on network/environment/time, or mostly assert fragile internal strings.
- Module probes only cause broad import errors rather than targeted behavior failures.
- Agent can pass by implementing a naive dict/string wrapper without honoring duplicate query params, header raw preservation, cookie merge, or body/header interactions.
- The task becomes a networking client task instead of a request model task.

## Agent Calibration

| Run | Model | Passed | ExtractionRatio | Tokens | Notes |
| --- | --- | --- | --- | --- | --- |
| `httpx__request_model_core__001-flash-002` | deepseek_v4_flash | no (hidden fail) | 0.169 | 4.57M | public pass; compact submission missing merge/header/cookie semantics |

Target for this task: strong agents should fail if they implement only the public API shell, and should score poorly if they copy all HTTPX. A good passing solution should be compact but not trivial.
