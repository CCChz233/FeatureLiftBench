# FeatureLift Task: unidiff patch hunk

Extract a task-scoped subset of `unidiff` into a standalone `featurelifted` package.

The submitted implementation must not import the upstream package or read from `repo/` at runtime, must not use the network, and must not depend on external services. Use only the standard library unless the task lockfile allows otherwise.

## Target API

```python
from featurelifted import (
    Hunk,
    LINE_TYPE_ADDED,
    LINE_TYPE_CONTEXT,
    LINE_TYPE_REMOVED,
    PatchedFile,
    PatchSet,
    UnidiffParseError,
)
```

## Required API Details

- `PatchSet` class must be importable
- `PatchedFile` class must be importable
- `Hunk` class must be importable
- `UnidiffParseError` class must be importable
- `LINE_TYPE_ADDED` constant must exist
- `LINE_TYPE_REMOVED` constant must exist
- `LINE_TYPE_CONTEXT` constant must exist

## Required Behavior

- PatchSet parses unified-diff text into an ordered collection of PatchedFile objects whose path omits the a/ or b/ prefix and whose entries are Hunk objects; patches containing multiple files produce one PatchedFile per file.
- Iterating a Hunk yields line objects whose line_type equals LINE_TYPE_ADDED, LINE_TYPE_REMOVED, or LINE_TYPE_CONTEXT according to the unified-diff prefix and whose value retains the line content.
- PatchSet accepts consecutive file sections in one diff, but raises UnidiffParseError when a hunk body does not satisfy the source and target lengths declared by its header.
- PatchedFile exposes added/removed counts.
- The package exposes PatchSet/PatchedFile/Hunk/UnidiffParseError/LINE_TYPE_* with the kinds listed in this contract.
- the submitted package does not import forbidden upstream packages: unidiff.

## Constraints

- Forbidden imports: `unidiff`.
- Do not implement git apply.
- Do not implement binary diffs.
- Do not implement original unidiff import at runtime.

<!-- featureliftbench:behavior-clauses:start -->
## Public Behavior Contract

The stable clause IDs below define the public behavior contract. Hidden tests may exercise these clauses but do not introduce additional requirements.

- **B001** — PatchSet parses unified-diff text into an ordered collection of PatchedFile objects whose path omits the a/ or b/ prefix and whose entries are Hunk objects; patches containing multiple files produce one PatchedFile per file.
- **B002** — Iterating a Hunk yields line objects whose line_type equals LINE_TYPE_ADDED, LINE_TYPE_REMOVED, or LINE_TYPE_CONTEXT according to the unified-diff prefix and whose value retains the line content.
- **B003** — PatchSet accepts consecutive file sections in one diff, but raises UnidiffParseError when a hunk body does not satisfy the source and target lengths declared by its header.
- **B004** — PatchedFile exposes added/removed counts.
- **B005** — The package exposes PatchSet/PatchedFile/Hunk/UnidiffParseError/LINE_TYPE_* with the kinds listed in this contract.
- **B006** — the submitted package does not import forbidden upstream packages: unidiff.
<!-- featureliftbench:behavior-clauses:end -->
