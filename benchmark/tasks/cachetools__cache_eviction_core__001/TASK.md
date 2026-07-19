# FeatureLift Task: Cache eviction core

Extract LRUCache, TTLCache, and LFUCache eviction policies, TTL expiry with injectable timers, and cached decorator key helpers without importing cachetools.

## Target API

- Import: `import featurelifted; from featurelifted import LRUCache, TTLCache, LFUCache, cached, hashkey, typedkey`
- Callable: `featurelifted.LRUCache`
- Signature: `LRUCache(maxsize, getsizeof=None)`

## Excluded Behavior

- async caches, cachedmethod, func.lru_cache wrappers, and TLRUCache
- upstream benchmarks, docs, tests, and packaging metadata
- original cachetools import at runtime

## Constraints

- Output package: `featurelifted`
- Network access: `false`
- Forbidden upstream imports: `cachetools`

<!-- featureliftbench:behavior-clauses:start -->
## Public Behavior Contract

The stable clause IDs below define the public behavior contract. Hidden tests may exercise
these clauses but do not introduce additional requirements.

- **B001** — LRU eviction order with touch-on-get and maxsize enforcement
- **B002** — LFU frequency buckets and least-frequent eviction
- **B003** — TTL expiry with injectable timer and doubly-linked expiry list
- **B004** — cached decorator memoization with optional cache_info hits/misses
- **B005** — hashkey and typedkey cache key functions for decorator kwargs and types
- **B006** — the declared target API remains importable and preserves upstream-observable semantics within the included and excluded feature scope
- **B007** — the submitted package does not import forbidden upstream packages: cachetools
<!-- featureliftbench:behavior-clauses:end -->
