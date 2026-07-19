# FeatureLift Task: Retry backoff policy core

Extract urllib3 Retry configuration, exponential backoff, status_forcelist matching, redirect accounting, and increment/history semantics without importing urllib3 or performing HTTP I/O.

## Target API

- Import: `import featurelifted; from featurelifted import Retry, RequestHistory, ConnectTimeoutError, ReadTimeoutError, MaxRetryError, ResponseError, InvalidHeader`
- Callable: `featurelifted.Retry`
- Signature: `Retry(total=10, connect=None, read=None, redirect=None, status=None, other=None, **kw)`

## Excluded Behavior

- HTTP connection pools, sockets, TLS, and actual request/response I/O
- PoolManager and connectionpool integration
- upstream test suite and dummyserver
- original urllib3 import at runtime

## Constraints

- Output package: `featurelifted`
- Network access: `false`
- Forbidden upstream imports: `urllib3`

<!-- featureliftbench:behavior-clauses:start -->
## Public Behavior Contract

The stable clause IDs below define the public behavior contract. Hidden tests may exercise
these clauses but do not introduce additional requirements.

- **B001** — Retry defaults and from_int coercion
- **B002** — connect/read/status/redirect/other counter decrement and exhaustion
- **B003** — status_forcelist and allowed_methods conjunction
- **B004** — exponential backoff with max cap and redirect reset
- **B005** — Retry-After header parsing with numeric and HTTP-date forms
- **B006** — RequestHistory accumulation on increment
- **B007** — remove_headers_on_redirect lowercasing
- **B008** — the declared target API remains importable and preserves upstream-observable semantics within the included and excluded feature scope
- **B009** — the submitted package does not import forbidden upstream packages: urllib3
<!-- featureliftbench:behavior-clauses:end -->
