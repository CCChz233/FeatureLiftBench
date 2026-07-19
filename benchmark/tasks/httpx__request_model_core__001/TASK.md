# FeatureLift Task: HTTP request model and offline request builder

Extract HTTPX request data model (URL, QueryParams, Headers, Cookies, Request) and client/default merge semantics for building requests without network I/O.

## Target API

- Import: `import featurelifted; from featurelifted import URL, QueryParams, Headers, Cookies, Request, build_request, InvalidURL`
- Callable: `featurelifted.build_request`
- Signature: `build_request(method, url, *, base_url='', params=None, headers=None, cookies=None, default_params=None, default_headers=None, default_cookies=None, content=None, data=None, json=None)`

## Excluded Behavior

- network I/O, transports, connection pools, proxies, redirects
- Client.send, AsyncClient, response parsing and streaming
- authentication flows beyond request header construction
- original httpx package import at runtime
- CLI, docs, CI, and original tests

## Constraints

- Output package: `featurelifted`
- Network access: `false`
- Forbidden upstream imports: `httpx`

<!-- featureliftbench:behavior-clauses:start -->
## Public Behavior Contract

The stable clause IDs below define the public behavior contract. Hidden tests may exercise
these clauses but do not introduce additional requirements.

- **B001** — construct and join URL objects with base URL and query parameters
- **B002** — preserve query parameter ordering and duplicate keys in QueryParams
- **B003** — case-insensitive header lookup with raw header preservation
- **B004** — merge default and per-request headers, query params, and cookies
- **B005** — build Request objects with content, data, and json body helpers
- **B006** — raise compatible errors for invalid URL and request input
- **B007** — the declared target API remains importable and preserves upstream-observable semantics within the included and excluded feature scope
- **B008** — the submitted package does not import forbidden upstream packages: httpx
<!-- featureliftbench:behavior-clauses:end -->
