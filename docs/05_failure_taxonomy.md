# Failure Taxonomy

## Labeling Policy

Each failed or low-quality submission should receive one primary failure label and, when useful, one secondary label. Automatic checks should assign mechanical labels where possible; human review is needed for locate failure, dependency closure failure, behavior drift, and test gaming.

## 1. Locate Failure

- Definition: the agent does not find the source files, symbols, or behavior region that implements the target feature.
- Typical symptoms: irrelevant files copied, target API stubbed from scratch, public tests fail on basic behavior, trajectory searches unrelated modules.
- How to detect: trajectory review, missing expected source entrypoints, oracle-locate improvement.
- Example placeholder: TODO: add example from experiments.

## 2. Dependency Closure Failure

- Definition: the agent finds the main entrypoint but misses required helpers, constants, resources, runtime registration, types, interfaces, or transitive dependencies.
- Typical symptoms: import errors, missing attributes, partial behavior, hidden-only failures, Go compile errors for undefined types.
- How to detect: stack traces, missing closure files, public pass plus hidden fail, module probes.
- Example placeholder: TODO: add example from experiments.

## 3. Packaging Failure

- Definition: the submitted package cannot be installed, imported, built, or called through the required target API.
- Typical symptoms: missing `pyproject.toml`, wrong package name, wrong Go module path, invalid `go.mod`, bad import path, missing exported symbol.
- How to detect: install/build logs and target API import checks.
- Example placeholder: TODO: add example from experiments.

## 4. Behavior Drift

- Definition: the submission implements a similar but not behavior-preserving version of the feature.
- Typical symptoms: public tests pass but hidden tests fail on edge cases, exception types, ordering, parser state, formatting, global state, or interface semantics.
- How to detect: public-hidden gap, hidden failure diff, targeted behavior probes.
- Example placeholder: TODO: add example from experiments.

## 5. Over-Copy

- Definition: the submission passes functional gates by copying a large amount of unrelated source code.
- Typical symptoms: high extraction ratio, broad package copy, many unused files, final score near zero despite passing tests.
- How to detect: LOC metrics, copied file audit, copy-all baseline comparison.
- Example placeholder: TODO: add example from experiments.

## 6. Forbidden Import

- Definition: the submission directly imports the original repository, original package, forbidden dependency, or forbidden Go module.
- Typical symptoms: `import original_package`, dependency on upstream package in `pyproject.toml` or `go.mod`, `replace` directive pointing to original module.
- How to detect: static forbidden import/dependency/module checks and build logs.
- Example placeholder: TODO: add example from experiments.

## 7. Path Leakage

- Definition: the submission relies on source repo paths, local absolute paths, symlinks, hidden evaluator locations, or environment-specific files.
- Typical symptoms: works in agent workspace but fails in clean eval, opens `/workspace/repo/...`, reads source snapshots at runtime, uses absolute developer paths.
- How to detect: static string scan, runtime import guard, clean eval workspace, explicit path leakage detector if implemented.
- Example placeholder: TODO: add example from experiments.

## 8. Test Gaming

- Definition: the submission overfits visible tests or hardcodes examples instead of preserving the feature behavior.
- Typical symptoms: public pass with brittle branch logic, exact fixture constants, missing generalization, hidden tests fail on small variants.
- How to detect: hidden tests, trajectory review, code review for fixture-specific logic.
- Example placeholder: TODO: add example from experiments.

## 9. Environment Failure

- Definition: failure caused primarily by infrastructure, dependency installation, Docker, resource limits, or unsupported platform assumptions rather than the agent's extraction logic.
- Typical symptoms: Docker unavailable, dependency index failure, timeout before agent acts, OOM in evaluator, missing toolchain.
- How to detect: run logs, infra error fields, repeated reproduction with oracle or no-op baseline.
- Example placeholder: TODO: add example from experiments.

## Language-Specific Notes

Python failures often cluster around dynamic dependency recovery, runtime behavior, hidden edge cases, import rewriting, module-level globals, and behavior that is only visible through execution.

Go failures often cluster around type closure, package boundary mistakes, missing interfaces, invalid `go.mod`, forbidden module references, and compile-time errors before tests can run.

These are not separate taxonomies. They are language-specific manifestations of the same FeatureLift failure types.
