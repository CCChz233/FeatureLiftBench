# FeatureLiftBench Overview

## Benchmark Goal

FeatureLiftBench evaluates whether code agents can extract compact, standalone, behavior-preserving reusable features from real-world repositories.

给定一个 pinned source repository snapshot 和一个 feature specification，Agent 需要理解目标功能在原仓库中的实现、恢复必要的 dependency closure，并把功能封装成可独立安装和测试的 standalone package。核心能力不是写新代码，而是从已有耦合代码中做 feature extraction、behavior preservation 和 compactness tradeoff。

## Core Difference from SWE-bench

SWE-bench asks agents to modify a repository; FeatureLiftBench asks agents to separate a reusable capability from a repository.

| Dimension | SWE-bench style issue repair | FeatureLiftBench |
|---|---|---|
| Input | GitHub issue and source repo | Feature specification and source repo snapshot |
| Output | Patch applied to the original repo | New standalone package under `submission/` |
| Main skill | Locate and fix issue in place | Locate, extract, decouple, package, and preserve behavior |
| Runtime dependency | Original repo remains the target | Extracted package must run without importing the original repo |
| Anti-gaming | Tests | Tests plus forbidden import, path leakage checks, and compactness |

FeatureLiftBench is not a bug-fixing benchmark, code completion benchmark, or greenfield coding benchmark. It is a repository-level feature extraction benchmark.

## Current Scope

FeatureLiftBench is one benchmark with multiple language splits. Python and Go are language splits, not independent benchmarks, and they share the same task semantics, research questions, evaluator philosophy, and reporting concepts.

- Python split: current implemented main split. Local metadata scan on 2026-07-06 finds 100 tasks in `benchmark/tasks/`, 75 unique sources, all marked `hard`.
- Go split: work in progress. The repo contains Go smoke, seed, and calibration task directories under `benchmark/go/`, but current Go planning docs still distinguish calibration or seed tasks from paper-ready hard gold tasks.
- Future splits should reuse the same core task definition instead of creating separate RQ, scoring, or experiment protocols.

## Expected Output of Agents

Agents produce a standalone package under `submission/`.

Python submissions currently target:

```text
submission/
  pyproject.toml
  featurelifted/
    ...
```

Go submissions currently target:

```text
submission/
  go.mod
  *.go
```

The exact package layout is language-specific, but the invariant is shared: the submitted package must expose the required target API and must not import, vendor wholesale, symlink to, or rely on the original source repository at runtime.

## Evaluation Philosophy

FeatureLiftBench evaluates two axes together:

1. Functional success: the package installs or builds, exposes the target API, avoids forbidden imports and dependencies, and passes public plus hidden tests.
2. Extraction quality: the package is compact relative to the source repository or reference closure, rather than being a copy-heavy solution.

Public tests guide the visible API and common behaviors. Hidden tests check behavior preservation, edge cases, dynamic dependency recovery, and overfitting. Compactness prevents a copy-all strategy from being scored as a high-quality feature extraction.

## Current Status / TODO

- Canonical core docs are now organized as `docs/00_*` through `docs/06_*`.
- Python-specific design docs live under `docs/python/`.
- Go-specific design docs live under `docs/go/`.
- Legacy documents remain in `docs/` for implementation details, historical notes, and runbooks.
- TODO: decide whether older root-level docs should be cross-linked from `docs/README.md` to this canonical structure.
- TODO: keep result claims out of paper-facing docs until the exact run protocol, model versions, and harness commit are frozen.
