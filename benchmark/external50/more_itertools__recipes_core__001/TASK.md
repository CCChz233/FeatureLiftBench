# FeatureLift Task: more_itertools recipes

Extract a task-scoped subset of `more_itertools` into a standalone `featurelifted` package.

The submitted implementation must not import the upstream package or read from `repo/` at runtime, must not use the network, and must not depend on external services. Use only the standard library unless the task lockfile allows otherwise.

## Target API

```python
from featurelifted import (
    chunked,
    consume,
    first,
    unique_everseen,
    windowed,
)
```

## Required API Details

- `chunked(iterable, n, strict=False)`
- `first(iterable, default=...)`
- `unique_everseen(iterable, key=None)`
- `consume(iterator, n=None)`
- `windowed(seq, n, fillvalue=None, step=1)`

## Required Behavior

- `chunked` accepts an iterable and positive chunk size and yields successive list chunks, including a shorter final chunk; `first` returns the first item from an iterable.
- `unique_everseen` yields only the first occurrence of each item while preserving input order, and an optional `key` callable controls how duplicates are identified.
- `consume` advances an iterator by a requested count or exhausts it when no count is given; `windowed` yields sliding tuples and pads a short input with `fillvalue`.
- `chunked(..., strict=True)` raises `ValueError` when the input length is not evenly divisible by the requested chunk size.
- The package exposes chunked/first/unique_everseen/consume/windowed with the kinds listed in this contract.
- the submitted package does not import forbidden upstream packages: more_itertools.

## Constraints

- Forbidden imports: `more_itertools`.
- Do not implement full more_itertools catalog.
- Do not implement original more_itertools import at runtime.

<!-- featureliftbench:behavior-clauses:start -->
## Public Behavior Contract

The stable clause IDs below define the public behavior contract. Hidden tests may exercise these clauses but do not introduce additional requirements.

- **B001** — `chunked` accepts an iterable and positive chunk size and yields successive list chunks, including a shorter final chunk; `first` returns the first item from an iterable.
- **B002** — `unique_everseen` yields only the first occurrence of each item while preserving input order, and an optional `key` callable controls how duplicates are identified.
- **B003** — `consume` advances an iterator by a requested count or exhausts it when no count is given; `windowed` yields sliding tuples and pads a short input with `fillvalue`.
- **B004** — `chunked(..., strict=True)` raises `ValueError` when the input length is not evenly divisible by the requested chunk size.
- **B005** — The package exposes chunked/first/unique_everseen/consume/windowed with the kinds listed in this contract.
- **B006** — the submitted package does not import forbidden upstream packages: more_itertools.
<!-- featureliftbench:behavior-clauses:end -->
