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

- The extracted feature must support this observable behavior: chunked splits iterables and first returns the first element. Required observable cases include chunked and first.
- The extracted feature must support this observable behavior: unique_everseen deduplicates preserving order. Required observable cases include unique everseen; unique everseen key.
- The extracted feature must support this observable behavior: consume advances iterators and windowed yields sliding tuples. Required observable cases include consume and windowed; windowed fillvalue; consume all.
- chunked strict=True raises ValueError when the iterable length is not divisible by n.
- The package exposes chunked/first/unique_everseen/consume/windowed with the kinds listed in this contract.
- the submitted package does not import forbidden upstream packages: more_itertools.

## Constraints

- Forbidden imports: `more_itertools`.
- Do not implement full more_itertools catalog.
- Do not implement original more_itertools import at runtime.

<!-- featureliftbench:behavior-clauses:start -->
## Public Behavior Contract

The stable clause IDs below define the public behavior contract. Hidden tests may exercise these clauses but do not introduce additional requirements.

- **B001** — The extracted feature must support this observable behavior: chunked splits iterables and first returns the first element. Required observable cases include chunked and first.
- **B002** — The extracted feature must support this observable behavior: unique_everseen deduplicates preserving order. Required observable cases include unique everseen; unique everseen key.
- **B003** — The extracted feature must support this observable behavior: consume advances iterators and windowed yields sliding tuples. Required observable cases include consume and windowed; windowed fillvalue; consume all.
- **B004** — chunked strict=True raises ValueError when the iterable length is not divisible by n.
- **B005** — The package exposes chunked/first/unique_everseen/consume/windowed with the kinds listed in this contract.
- **B006** — the submitted package does not import forbidden upstream packages: more_itertools.
<!-- featureliftbench:behavior-clauses:end -->
