# `<task_id>` Go Task Design

**Status:** draft
**Language:** Go
**Spec:** [../GO_V2_MINI_SPEC.md](../GO_V2_MINI_SPEC.md)

## 1. Source

- Repo:
- URL:
- Commit:
- License:
- Go module path:
- Source entrypoints:

## 2. Practical Reuse

Describe the standalone module a user would actually want after extraction.

Good:

- "A semver constraint checker usable without the rest of the upstream CLI."
- "A bounded worker pool usable inside a service without importing the original app."

Bad:

- "Copy the package."
- "Make tests pass."
- "Expose the whole upstream library."

## 3. Feature Boundary

Included behavior:

-

Excluded behavior:

-

Expected public API:

```go
// Fill exact symbols the extracted package must expose.
```

## 4. Entanglement

Primary entanglement:

-

Secondary Go tags:

-

Why this is hard:

-

## 5. Tests

Public tests should check:

-

Hidden tests should check:

-

Concurrency/stress/race checks, if any:

-

Flake risks and mitigations:

-

## 6. Forbidden Rules

Forbidden imports:

```text

```

Forbidden modules:

```text

```

Allowed external modules:

```text

```

Special `replace` or vendor policy:

-

## 7. Baselines

Oracle strategy:

-

Naive baseline:

-

Expected naive failure:

- public fail
- hidden fail
- forbidden import/module fail
- build fail

Copy-all baseline:

-

Expected extraction relationship:

```text
oracle_extraction_ratio < copy_all_extraction_ratio
```

## 8. Docker / Offline Notes

- Expected Go version:
- Needs cgo:
- Needs race detector:
- Needs external modules:
- Should pass with `GOPROXY=off`:

## 9. Agent Calibration Notes

Expected difficulty label:

- A-tier: strong agent fails functional gate
- B-tier: strong agent passes but may be copy-heavy
- C-tier: too easy or too small; replace unless it has strong diagnostic value

What would count as a useful failure:

-

What would make this task too easy:

-

## 10. Decision

Decision:

- promote
- hold
- reject

Required fixes before promote:

-

Exceptions:

-
