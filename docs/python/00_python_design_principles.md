# Python Design Principles

## Scope

This document defines Python-specific task design principles for FeatureLiftBench. It does not define separate Python RQs, scoring, or experiment protocol. Python is one language split of FeatureLiftBench.

## What Makes a Good Python FeatureLift Task

Good Python tasks require repository-level understanding:

- The feature entrypoint is easy to describe but not isolated in one trivial file.
- Correct extraction requires reading multiple modules, not only matching a function name.
- The source package contains unrelated code that a compact solution should prune.

Good tasks require dependency closure recovery:

- The agent must identify helper functions, constants, exceptions, decorators, data tables, resources, or transitive imports.
- Some dependencies may be dynamic, such as plugin registries, lazy imports, import-time initialization, or runtime dispatch tables.
- The closure should be bounded enough for a standalone package.

Good tasks require behavior preservation:

- Hidden tests should cover edge cases, error types, ordering, formatting, parser state, object identity, global state, or compatibility behavior.
- The public contract should specify the API and representative behavior without
  revealing source locations; benchmark public and hidden tests remain
  Agent-invisible in Main.
- The target should be a feature with stable observable behavior, not just internal structure.

Good tasks require compact extraction:

- Copying the whole package should be possible enough to expose the copy-all baseline, but obviously larger than a clean closure.
- Oracle or reference solutions should remove unrelated code.
- Task review should report functional pass and reference-relative compactness
  separately.

Good tasks require standalone packaging:

- The submission should install or import as `featurelifted`.
- Runtime imports must not refer to the original package.
- Tests should run in a clean environment without relying on source repo paths.

## Preferred Feature Types

- Config loader
- Parser / tokenizer
- Validator
- Serializer / deserializer
- Template renderer
- Rule engine
- Path resolver
- Metadata extractor
- CLI core logic

These feature families are useful because they often have real downstream reuse value, visible behavior, and nontrivial runtime dependencies.

## Avoided Task Types

- Trivial single-function extraction.
- Tasks requiring external services.
- Tasks depending on network access.
- Huge framework-level extraction.
- Tasks with unclear feature boundaries.
- Tasks where hidden tests introduce new requirements outside the stated feature.
- Tasks where the source package is already a clean standalone module and can be copied wholesale with no pruning judgment.
- Tasks whose expected behavior is mostly performance, concurrency, or integration with unavailable systems.

## Difficulty Criteria

| Dimension | Easy | Medium | Hard | Very Hard |
|---|---|---|---|---|
| Files involved | 1 | 2-3 | 4-6 | 7+ |
| Dependency depth | none | shallow | transitive | deep/dynamic |
| Behavior complexity | simple | edge cases | state/errors | dynamic/global |
| Packaging difficulty | low | moderate | high | high |
| Pruning difficulty | low | moderate | high | very high |

## Python-Specific Stressors

Dynamic dependency recovery:

- `importlib`, lazy imports, optional dependencies, runtime plugin loading.
- Decorator side effects and module-level registries.
- Data files or package resources used through runtime APIs.

Runtime behavior:

- Exception classes and message compatibility.
- Ordering of dict-like structures, sorted outputs, or parser tokens.
- Global state, caches, locale-like tables, and environment parsing.
- Monkeypatch-sensitive APIs and import-time initialization.

Hidden tests:

- Should cover behavior combinations and edge cases implied by the public
  contract but not exhaustively enumerated there.
- Should avoid hidden-only API requirements unless the API is clearly in the task spec.
- Should distinguish faithful extraction from narrow stubs.

## Review Questions

- Would a strong agent need to read source code rather than implement from the prompt alone?
- Is the dependency closure nontrivial but bounded?
- Does the public contract fully define the target API without source-location hints?
- Can copy-all remain functional while being clearly worse on the separately
  reported compactness metric?
- Does the task test Python runtime behavior rather than only file copying?

## Open work

- Add per-task difficulty annotations beyond the current all-`hard` metadata if the paper needs easy/medium/hard stratification.
- Audit hidden tests for hidden-only requirements.
- Record dynamic behavior tags consistently in metadata.
