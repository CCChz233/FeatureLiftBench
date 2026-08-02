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

- The extracted feature must support this observable behavior: PatchSet parses unified diffs into PatchedFile/Hunk. Required observable cases include parse patchset.
- The extracted feature must support this observable behavior: hunk lines expose added/removed/context types. Required observable cases include hunk lines; context lines.
- The extracted feature must support this observable behavior: UnidiffParseError on short hunks and multi-file patches. Required observable cases include parse error short hunk; multiple files.
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

- **B001** — The extracted feature must support this observable behavior: PatchSet parses unified diffs into PatchedFile/Hunk. Required observable cases include parse patchset.
- **B002** — The extracted feature must support this observable behavior: hunk lines expose added/removed/context types. Required observable cases include hunk lines; context lines.
- **B003** — The extracted feature must support this observable behavior: UnidiffParseError on short hunks and multi-file patches. Required observable cases include parse error short hunk; multiple files.
- **B004** — PatchedFile exposes added/removed counts.
- **B005** — The package exposes PatchSet/PatchedFile/Hunk/UnidiffParseError/LINE_TYPE_* with the kinds listed in this contract.
- **B006** — the submitted package does not import forbidden upstream packages: unidiff.
<!-- featureliftbench:behavior-clauses:end -->
