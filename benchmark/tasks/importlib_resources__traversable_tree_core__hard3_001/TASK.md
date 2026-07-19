# FeatureLift Task: Traversable resource tree and text/binary reader

Extract a task-scoped subset of `importlib_resources` package resource traversal into a standalone `featurelifted` package.

The implementation must not import `importlib_resources`, must not read from `repo/`, must not use the network, and must not depend on external services. Use only the standard library.

## Target API

```python
from featurelifted import MemoryTraversable, TraversalError, files, read_binary, read_text

files(anchor) -> Traversable
read_text(anchor, resource, encoding="utf-8", errors="strict") -> str
read_binary(anchor, resource) -> bytes
```

The returned Traversable must support:

- `name`
- `iterdir()`
- `is_dir()`
- `is_file()`
- `joinpath(*descendants)`
- `/` child traversal
- `open("r" | "rb", encoding=..., errors=...)`
- `read_text(...)`
- `read_bytes()`

## Required Behavior

- `anchor` may be a module object or a module name string.
- For filesystem packages, traversal starts at the package root.
- `joinpath` accepts multiple path segments and slash-separated nested resource names.
- `read_text` defaults to UTF-8 and honors explicit encodings.
- `read_binary` preserves byte payloads.
- Parent traversal with `..` must be rejected with `TraversalError`.
- Missing resources must raise `TraversalError`.
- `MemoryTraversable` should provide the same read/traversal contract for in-memory trees.

## Constraints

- Forbidden imports: `importlib_resources`.
- Forbidden path access: `repo/`, `importlib_resources/`.
- Do not implement zip adapters, `as_file`, deprecated `contents`, or deprecated `path`.
- Do not expose host-specific absolute source paths in API results.

## Public vs Hidden Tests

Public tests cover module anchors, string anchors, basic `files()` traversal, nested text reads, and binary reads.
Hidden tests cover multiple joinpath segments, slash-separated nested resource paths, encoding behavior, binary mode open, parent traversal rejection, missing resources, and MemoryTraversable compatibility.

<!-- featureliftbench:behavior-clauses:start -->
## Public Behavior Contract

The stable clause IDs below define the public behavior contract. Hidden tests may exercise
these clauses but do not introduce additional requirements.

- **B001** — module object and string anchor resolution
- **B002** — filesystem-backed Traversable root
- **B003** — MemoryTraversable test tree
- **B004** — iterdir, is_file, is_dir, name, open, read_bytes, read_text
- **B005** — joinpath and / traversal
- **B006** — read_text and read_binary helpers
- **B007** — TraversalError for parent traversal and missing resources
- **B008** — the declared target API remains importable and preserves upstream-observable semantics within the included and excluded feature scope
- **B009** — the submitted package does not import forbidden upstream packages: importlib_resources
<!-- featureliftbench:behavior-clauses:end -->
