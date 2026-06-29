# Task Design: `yarl__url_model_core__001`

Status: agent-calibrated

## Why This Task

Yarl's `URL` is the canonical immutable URL model in the aiohttp ecosystem, but the parsing/join/query/path logic is reusable without HTTP I/O. Hidden tests stress MultiDict duplicate keys, semicolon-in-query handling, IDNA hosts, and RFC 3986 join/path normalization that naive `urllib.parse` wrappers miss.

## Practical reuse（必填）

1. **Reuse module** — A standalone immutable URL value type for config loaders, API clients, and routing helpers that need yarl-compatible URL semantics.
2. **Who imports it** — Teams extracting URL logic from aiohttp stacks or vendoring a compact URL model without the full yarl wheel/Cython build chain.
3. **Why not copy-all** — Upstream ships benchmarks, docs, CI, and a large test suite; compact closure keeps the URL model only.

## Source

| Field | Value |
| --- | --- |
| Source repo | https://github.com/aio-libs/yarl |
| Commit | `b0d27e478c543c28045296311a821f924729150f` |
| License | Apache-2.0 |
| Language | Python |
| Difficulty | hard |
| Tags | batch-1, functional-discriminator, parser_state_coupling |

## Entanglement

```json
{
  "level": "high",
  "types": ["parser_state_coupling", "data_model_coupling", "third_party_dependency_coupling"],
  "primary": "parser_state_coupling",
  "description": "URL behavior couples split/join parsing, quoters, MultiDict query serialization, path normalization, and IDNA host transforms.",
  "signals": ["split_url vs join composition", "duplicate query keys", "semicolon not a separator", "dot-segment path normalization", "IDNA host encode/decode"]
}
```

## Target Feature

### Source entrypoints

- `yarl.URL`
- `yarl._parse.split_url`
- `yarl._path.normalize_path`
- `yarl._query.get_str_query`
- `yarl._url.URL.join` / `with_query` / `update_query` / `joinpath`

### Output API

```python
from featurelifted import URL, Query, QueryVariable, SimpleQuery, cache_clear, cache_configure, cache_info
```

## Included Behaviors

- Parse/construct URLs; join absolute and relative URLs
- MultiDict query with duplicate keys and update_query
- Path normalization; default port omission
- IDNA host handling (pure-Python quoting fallback)

## Excluded Behaviors

- aiohttp, network I/O, Cython `_quoting_c` extension
- Upstream tests/docs at runtime; original `yarl` import

## Public Tests

- Basic parse components (scheme/host/port/path/query/fragment)
- Join absolute path; with_query kwargs; joinpath append

## Hidden Tests

- Duplicate query keys via MultiDict.getall
- Semicolon inside query value (not a separator)
- IDNA punycode host decode
- Relative join with `..`; joinpath dot-segment normalization
- Default HTTP port stripped from str; query no double-unquote
- update_query with MultiDict; join query-only relative URL
- No `yarl` import surface; join rejects non-URL type

## Module Probes

| Probe | Remove module | Hidden test(s) that must fail |
| --- | --- | --- |
| Probe-1 | `featurelifted/_parse.py` | `test_join_relative_parent_path` |
| Probe-2 | `featurelifted/_query.py` | `test_duplicate_query_keys_multidict` |
| Probe-3 | `featurelifted/_path.py` | `test_joinpath_normalizes_dot_segments` |

## Manual Oracle Closure Plan

| Check | Target | Result |
| --- | --- | --- |
| Public tests | pass | pass (oracle, copy_all, naive) |
| Hidden tests | pass | pass (oracle, copy_all); **fail** (naive) |
| Forbidden import check | pass | pass |
| Oracle LOC | ~2000+ | 1806 |
| Source repo Python LOC | ~9000+ | 7894 |
| ExtractionRatio | 0.20 – 0.60 | oracle **0.229** |
| Copy-All functional gate | 1.0 | pass |
| Copy-All ExtractionRatio | > oracle + margin | **0.865** (Δ=0.636) |
| Module probes | all verified | 3/3 OK |

Expected closure shape:

```text
featurelifted/
  __init__.py
  _parse.py
  _path.py
  _query.py
  _quoters.py
  _quoting.py
  _quoting_py.py
  _url.py
```

## Go / No-Go Criteria

- Practical reuse narrative holds for URL tooling without aiohttp.
- Oracle passes public + hidden; naive fails hidden on query/join/IDNA semantics.
- ≥3 module probes verified after Step 5.
- Copy-all extraction clearly above oracle.
