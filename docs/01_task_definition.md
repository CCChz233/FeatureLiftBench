# FeatureLift Task Definition

## Task Summary

A FeatureLift task asks an agent to extract one reusable feature from an entangled repository snapshot and package it as an independent library. The target behavior already exists in the source repository; the agent's job is to recover and decouple the minimal useful closure.

## Input

Each task provides a language-specific workspace with the following logical inputs:

- Source repository snapshot: a pinned commit or curated snapshot mounted as read-only task input.
- Feature specification: natural-language description of included and excluded behavior.
- Target API requirement: package name, import path, callable or type surface, and expected signature.
- Public tests: visible tests that exercise the intended API and representative behaviors.
- Packaging requirement: instructions for an installable or buildable package under `submission/`.
- Metadata: machine-readable task information such as language, source, dependency lock, timeout, forbidden imports, and test command.

Hidden tests, oracle manifests, and scoring references are evaluation artifacts, not agent-visible input.

## Output

The agent must create a standalone package under `submission/`.

For Python, the current output package is usually:

```text
submission/
  pyproject.toml
  featurelifted/
```

For Go, the current output package is usually:

```text
submission/
  go.mod
  *.go
```

Language-specific docs define exact layout expectations. The core benchmark requirement is unchanged across languages: the output must be independent from the source repo and must expose the target API.

## Constraints

- Must not import the original repository or its top-level package.
- Must not depend on source repository paths, symlinks, hidden tests, evaluator files, or local machine paths.
- Must not use network access.
- Must pass hidden tests during evaluation.
- Must be compact rather than copy-heavy.
- Must honor the public target API rather than exposing only an internal helper.
- Must not add hidden-only behavior by reading test files or evaluator artifacts.

## Functional Success Criteria

A submission is functionally successful only when all required gates pass:

- It installs, imports, or builds in a clean evaluation environment.
- The target API is importable and callable by tests.
- Public tests pass.
- Hidden tests pass.
- Forbidden import and forbidden dependency checks pass.
- No direct reliance on the source repo path is detected by the evaluator.

Functional success is binary. Compactness is scored separately and then combined with the functional gate.

## Difference from Issue Repair

Issue repair modifies the original repository to satisfy a bug report or feature request. FeatureLift produces a new package and leaves the original repository unchanged. The difficult step is not merely finding a line to edit; it is deciding which parts of the original implementation are necessary, which coupling must be removed, and how to preserve runtime behavior outside the original environment.

## Difference from Code Generation

Greenfield code generation can implement behavior from a specification alone. FeatureLift requires reading the existing source implementation and preserving its observable behavior, including edge cases, parser state, exception behavior, global state, or dependency semantics that may not be fully specified in the prompt.

## Difference from Code Completion

Code completion predicts local code in an existing context. FeatureLift is repository-level: it requires cross-file understanding, dependency closure recovery, import rewriting, packaging, and verification in a clean runtime environment.

## Stable Contract

Task semantics must remain stable across language splits. Python and Go may differ in packaging, dependency metadata, and build tooling, but they should not define separate versions of FeatureLift, separate scoring concepts, or separate RQs.
