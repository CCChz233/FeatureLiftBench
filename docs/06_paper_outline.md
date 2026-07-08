# Paper Outline

## Candidate Titles

- FeatureLiftBench: Evaluating Repository-Level Feature Extraction in Code Agents
- Can Code Agents Extract Reusable Features from Entangled Repositories?

## Abstract Sketch

Current code-agent benchmarks focus heavily on code generation, code completion, or issue repair inside an existing repository. Real software reuse often requires a different capability: extracting a reusable feature from an entangled codebase into a standalone package while preserving behavior and avoiding unnecessary copying. FeatureLiftBench evaluates this capability with source repository snapshots, feature specifications, public and hidden tests, forbidden import checks, and compactness-aware scoring. The benchmark is organized as language splits under one task definition, with Python as the current mature split and Go as an in-progress split designed to stress static type and package-boundary closure.

TODO: add verified headline results only after the official run protocol is frozen.

## 1. Introduction

Motivation:

- Existing benchmarks often ask agents to generate code or patch an existing repository.
- Software reuse, migration, and modularization require extracting features from existing code.
- Feature extraction is difficult because implementations are entangled with dependencies, configuration, framework state, resources, and language-specific runtime or type systems.
- FeatureLiftBench tests whether agents can produce standalone, compact, behavior-preserving packages.

Key contrast:

- SWE-bench: issue repair in the original repo.
- FeatureLiftBench: feature extraction out of the original repo.

## 2. Task Definition

Describe:

- Source repository snapshot.
- Feature specification.
- Target API.
- Public tests and hidden tests.
- Standalone `submission/` package.
- Forbidden imports and path leakage.
- Compactness requirement.

Emphasize that Python and Go are language splits under this definition.

## 3. Benchmark Construction

Describe:

- Repository selection criteria.
- Feature type selection.
- Task metadata.
- Public and hidden test design.
- Oracle, naive, and copy-all construction when available.
- Difficulty rubric.
- Language-specific construction notes.

Python construction should discuss dynamic dependency recovery, runtime behavior, and hidden-test fidelity. Go construction should discuss type closure, package boundaries, `go.mod`, interfaces, and compile-time failure modes.

## 4. Experimental Setup

Describe:

- Agents and models.
- Standard, hint, oracle-locate, and copy-all settings.
- Evaluator and Docker or clean environment.
- Metrics: install/build pass, public pass, hidden pass, functional gate, final score, LOC/extraction ratio, forbidden import rate, public-hidden gap.

## 5. Results Organized by RQs

### RQ1: Overall Performance

Report whether current agents can perform FeatureLift. Use one table per stable language split or a split column if both are mature.

### RQ2: Failure Analysis

Report failure taxonomy distribution and representative case studies.

### RQ3: Localization Ablation

Compare standard, hint, and oracle-locate settings.

### RQ4: Compactness

Compare pass rate with final score and copy-all baseline. Show that functional tests alone overestimate extraction quality.

### RQ5: Task Difficulty

Analyze performance against task properties such as files, dependency depth, feature type, dynamic behavior, global state, package boundaries, and type closure.

## 6. Related Work

Discuss:

- SWE-bench and SWE-Bench Pro.
- RepoBench and repository-level code understanding.
- LiveCodeBench and code generation benchmarks.
- Automated benchmark generation.
- Refactoring, program slicing, software modularization, and library extraction.
- Program repair and agent-based software engineering benchmarks.

## 7. Limitations

Potential limitations:

- Hidden tests are incomplete approximations of full behavior.
- Compactness metrics can penalize legitimate closures or miss semantic over-copy.
- Python split may overrepresent parser, validator, and config-loader style features.
- Go split is still under calibration until paper-ready hard tasks are verified.
- Evaluator safety and path leakage checks may need expansion.
- Benchmark tasks are curated and may not represent all extraction scenarios.

## 8. Conclusion

FeatureLiftBench introduces a repository-level feature extraction benchmark for code agents. It measures whether agents can recover dependency closure, preserve behavior, package standalone code, and avoid copy-heavy shortcuts. The benchmark complements issue-repair benchmarks by testing a practical software reuse capability that current agents may not reliably possess.

## TODO

- Insert official dataset table after Python and Go split status is frozen.
- Replace abstract TODO with verified results.
- Add examples only from audited task designs and experiment artifacts.
- Align paper scoring notation with the evaluator version used for official runs.
