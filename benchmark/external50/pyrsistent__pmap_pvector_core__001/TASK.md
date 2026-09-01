# FeatureLift Task: pyrsistent pmap pvector

Extract a task-scoped subset of `pyrsistent` into a standalone `featurelifted` package.

The submitted implementation must not import the upstream package or read from `repo/` at runtime, must not use the network, and must not depend on external services. Use only the standard library unless the task lockfile allows otherwise.

## Target API

```python
from featurelifted import (
    PMap,
    pmap,
    PVector,
    pvector,
)
```

## Required API Details

- `pmap(initial=None) -> PMap`
- `pvector(initial=()) -> PVector`
- `PMap` class must be importable
- `PMap.set(self, key, value) -> PMap`
- `PMap.get(self, key, default=None)`
- `PVector` class must be importable
- `PVector.append(self, value) -> PVector`
- `PVector.extend(self, iterable) -> PVector`
- `PVector.set(self, index, value) -> PVector`

## Required Behavior

- `pmap` accepts an initial mapping, and `PMap.set(key, value)` returns a distinct map in which existing entries remain readable and the new entry is available through indexing or `get`, without adding that entry to the original map.
- `PVector.set(index, value)` returns a distinct vector with that position replaced while the original vector retains its previous sequence.
- `PVector.extend(iterable)` returns a vector containing the original sequence followed by the iterable's values.
- `PVector.append(value)` and the other vector update methods return distinct vectors and leave their input vectors unchanged.
- The package exposes pmap/pvector/PMap/PVector with the kinds listed in this contract.
- the submitted package does not import forbidden upstream packages: pyrsistent.

## Constraints

- Forbidden imports: `pyrsistent`.
- Do not implement pset/pdeque/pclass.
- Do not implement original pyrsistent import at runtime.

<!-- featureliftbench:behavior-clauses:start -->
## Public Behavior Contract

The stable clause IDs below define the public behavior contract. Hidden tests may exercise these clauses but do not introduce additional requirements.

- **B001** — `pmap` accepts an initial mapping, and `PMap.set(key, value)` returns a distinct map in which existing entries remain readable and the new entry is available through indexing or `get`, without adding that entry to the original map.
- **B002** — `PVector.set(index, value)` returns a distinct vector with that position replaced while the original vector retains its previous sequence.
- **B003** — `PVector.extend(iterable)` returns a vector containing the original sequence followed by the iterable's values.
- **B004** — `PVector.append(value)` and the other vector update methods return distinct vectors and leave their input vectors unchanged.
- **B005** — The package exposes pmap/pvector/PMap/PVector with the kinds listed in this contract.
- **B006** — the submitted package does not import forbidden upstream packages: pyrsistent.
<!-- featureliftbench:behavior-clauses:end -->
