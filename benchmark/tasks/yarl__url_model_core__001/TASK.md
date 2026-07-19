# FeatureLift Task: URL parse, join, query, and path model

Extract yarl.URL immutable URL data model with RFC 3986 parsing, relative join, query MultiDict semantics, path normalization, and IDNA host handling without aiohttp or network I/O.

## Target API

- Import: `import featurelifted; from featurelifted import URL, Query, QueryVariable, SimpleQuery, cache_clear, cache_configure, cache_info`
- Callable: `featurelifted.URL`
- Signature: `URL(val='', *, encoded=False, **kwargs)`

## Excluded Behavior

- aiohttp, network I/O, HTTP client/server integration
- Cython _quoting_c extension build (pure-Python quoting fallback only)
- upstream test suite, docs, CI, and packaging metadata at runtime
- original yarl package import at runtime

## Constraints

- Output package: `featurelifted`
- Network access: `false`
- Forbidden upstream imports: `yarl`, `aiohttp`

<!-- featureliftbench:behavior-clauses:start -->
## Public Behavior Contract

The stable clause IDs below define the public behavior contract. Hidden tests may exercise
these clauses but do not introduce additional requirements.

- **B001** — parse and construct URL objects with scheme, host, port, path, query, fragment
- **B002** — join absolute and relative URLs preserving query and fragment rules
- **B003** — MultiDict query with duplicate keys, ordering, and semicolon-in-value handling
- **B004** — path normalization for dot and dot-dot segments
- **B005** — IDNA host encoding and decoding; default port omission in string form
- **B006** — with_query, update_query, and joinpath helpers
- **B007** — the declared target API remains importable and preserves upstream-observable semantics within the included and excluded feature scope
- **B008** — the submitted package does not import forbidden upstream packages: yarl, aiohttp
<!-- featureliftbench:behavior-clauses:end -->
