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

- `Node(name, parent=None, children=None, **kwargs)` class constructor
  - `Node.name` attribute must exist on instances
  - `Node.parent` attribute must exist on instances
  - `Node.children` attribute must exist on instances
- `Resolver(pathattr='name')` class constructor
  - `Resolver.get(self, node, path: str)`
- `RenderTree(node, style=None, childiter=list, maxlevel=None)` class constructor
  - `RenderTree.__iter__(self)`
- `PreOrderIter(node, filter_=None, stop=None, maxlevel=None)` class constructor
- `findall(node, filter_=None, stop=None, maxlevel=None, mincount=None, maxcount=None)`
- `ChildResolverError` class must be importable
- `ResolverError` class must be importable

## Required Behavior

- When nodes are linked through the `parent` constructor argument, iterating `PreOrderIter` from the root returns the root followed by its descendants in preorder.
- Given a tree and a `Resolver` configured for `name`, `get` resolves both root-qualified paths and child-relative paths to the existing node; requesting a missing child raises `ChildResolverError`, which is a `ResolverError`.
- For a tree, iterating `RenderTree` yields rows exposing `pre`, `fill`, and `node`, while `findall` returns a tuple of matching nodes in traversal order and returns an empty tuple when no node matches.
- When an existing node's `parent` attribute is assigned, that node appears in the new parent's `children` tuple and subsequent preorder traversal includes it beneath that parent.
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

- **B001** — When nodes are linked through the `parent` constructor argument, iterating `PreOrderIter` from the root returns the root followed by its descendants in preorder.
- **B002** — Given a tree and a `Resolver` configured for `name`, `get` resolves both root-qualified paths and child-relative paths to the existing node; requesting a missing child raises `ChildResolverError`, which is a `ResolverError`.
- **B003** — For a tree, iterating `RenderTree` yields rows exposing `pre`, `fill`, and `node`, while `findall` returns a tuple of matching nodes in traversal order and returns an empty tuple when no node matches.
- **B004** — When an existing node's `parent` attribute is assigned, that node appears in the new parent's `children` tuple and subsequent preorder traversal includes it beneath that parent.
- **B005** — The package exposes Node/Resolver/RenderTree/PreOrderIter/findall/ChildResolverError/ResolverError with the kinds listed in this contract.
- **B006** — the submitted package does not import forbidden upstream packages: anytree.
<!-- featureliftbench:behavior-clauses:end -->
