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
- `PMap.set` callable must exist
- `PMap.get` callable must exist
- `PVector` class must be importable
- `PVector.append` callable must exist
- `PVector.extend` callable must exist
- `PVector.set` callable must exist

## Required Behavior

- The extracted feature must support this observable behavior: pmap/PMap.set/get returns new maps without mutating originals. Required observable cases include pmap set get; pmap immutability.
- The extracted feature must support this observable behavior: pvector/PVector.append returns new vectors. Required observable cases include pvector append; factory types.
- The extracted feature must support this observable behavior: PVector.set/extend produce new vectors. Required observable cases include pvector set; pvector extend.
- Original pmap/pvector instances remain unchanged after updates.
- The package exposes pmap/pvector/PMap/PVector with the kinds listed in this contract.
- the submitted package does not import forbidden upstream packages: pyrsistent.

## Constraints

- Forbidden imports: `pyrsistent`.
- Do not implement pset/pdeque/pclass.
- Do not implement original pyrsistent import at runtime.

<!-- featureliftbench:behavior-clauses:start -->
## Public Behavior Contract

The stable clause IDs below define the public behavior contract. Hidden tests may exercise these clauses but do not introduce additional requirements.

- **B001** — The extracted feature must support this observable behavior: pmap/PMap.set/get returns new maps without mutating originals. Required observable cases include pmap set get; pmap immutability.
- **B002** — The extracted feature must support this observable behavior: pvector/PVector.append returns new vectors. Required observable cases include pvector append; factory types.
- **B003** — The extracted feature must support this observable behavior: PVector.set/extend produce new vectors. Required observable cases include pvector set; pvector extend.
- **B004** — Original pmap/pvector instances remain unchanged after updates.
- **B005** — The package exposes pmap/pvector/PMap/PVector with the kinds listed in this contract.
- **B006** — the submitted package does not import forbidden upstream packages: pyrsistent.
<!-- featureliftbench:behavior-clauses:end -->
