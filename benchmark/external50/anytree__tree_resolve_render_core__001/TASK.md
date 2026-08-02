# FeatureLift Task: anytree tree resolve render

Extract a task-scoped subset of `anytree` into a standalone `featurelifted` package.

The submitted implementation must not import the upstream package or read from `repo/` at runtime, must not use the network, and must not depend on external services. Use only the standard library unless the task lockfile allows otherwise.

## Target API

```python
from featurelifted import (
    ChildResolverError,
    findall,
    Node,
    PreOrderIter,
    RenderTree,
    Resolver,
    ResolverError,
)
```

## Required API Details

- `Node` class must be importable
  - `Node.name` attribute must exist on instances
  - `Node.parent` attribute must exist on instances
  - `Node.children` attribute must exist on instances
- `Resolver` class must be importable
  - `Resolver.get` callable must exist
- `RenderTree` class must be importable
  - `RenderTree.__iter__` callable must exist
- `PreOrderIter` callable must exist
- `findall` callable must exist
- `ChildResolverError` class must be importable
- `ResolverError` class must be importable

## Required Behavior

- The extracted feature must support this observable behavior: build parent/child trees and PreOrderIter. Required observable cases include build and preorder.
- The extracted feature must support this observable behavior: Resolver path get and ChildResolverError. Required observable cases include resolver get.
- The extracted feature must support this observable behavior: RenderTree yields Row(pre, fill, node) and findall filters. Required observable cases include render and findall.
- parent assignment mutates children relationships.
- The package exposes Node/Resolver/RenderTree/PreOrderIter/findall/ChildResolverError/ResolverError with the kinds listed in this contract.
- the submitted package does not import forbidden upstream packages: anytree.

## Constraints

- Forbidden imports: `anytree`.
- Do not implement dot export.
- Do not implement dict attachment persistence.
- Do not implement original anytree import at runtime.

<!-- featureliftbench:behavior-clauses:start -->
## Public Behavior Contract

The stable clause IDs below define the public behavior contract. Hidden tests may exercise these clauses but do not introduce additional requirements.

- **B001** — The extracted feature must support this observable behavior: build parent/child trees and PreOrderIter. Required observable cases include build and preorder.
- **B002** — The extracted feature must support this observable behavior: Resolver path get and ChildResolverError. Required observable cases include resolver get.
- **B003** — The extracted feature must support this observable behavior: RenderTree yields Row(pre, fill, node) and findall filters. Required observable cases include render and findall.
- **B004** — parent assignment mutates children relationships.
- **B005** — The package exposes Node/Resolver/RenderTree/PreOrderIter/findall/ChildResolverError/ResolverError with the kinds listed in this contract.
- **B006** — the submitted package does not import forbidden upstream packages: anytree.
<!-- featureliftbench:behavior-clauses:end -->
