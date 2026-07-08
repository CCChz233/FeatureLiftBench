# Evaluator and Scoring

## Evaluation Pipeline

The evaluator should remain shared across language splits at the concept level, with language-specific build/test adapters.

Pipeline:

1. Create a clean evaluation environment.
2. Mount or copy the source repository as task input, not as runtime dependency.
3. Run the agent in an agent workspace that hides hidden tests and scoring artifacts.
4. Collect `submission/`.
5. Install or build the submission.
6. Check the target API.
7. Check forbidden imports and forbidden dependencies.
8. Check for direct source repo path reliance where the evaluator supports it.
9. Run public tests.
10. Run hidden tests.
11. Compute LOC and compactness metrics.
12. Write result JSON and logs.

Python uses `pytest` and package installation/import checks. Go uses `go test`, `go.mod`, and static Go import/module checks. These are adapters under the same evaluator semantics.

## Functional Gate

The current implemented scoring contract in `harness/featureliftbench/scoring.py` is:

```text
FunctionalGate = BuildPass and TestPass and OriginalImportPass
```

Where:

- `BuildPass`: submission installs/imports or builds in the clean eval environment.
- `TestPass`: public and hidden tests pass.
- `OriginalImportPass`: forbidden imports/dependencies/modules are not used, and the submission is not inside the source repo.

Functional gate is binary:

```text
functional_gate = 1.0 if all functional gates pass else 0.0
```

## Compactness

The current implemented compactness proxy is extraction ratio:

```text
ExtractionRatio = SubmittedRuntimeLOC / SourceRepoRuntimeLOC
```

For Python, runtime LOC counts Python source while excluding tests according to the harness metrics. For Go, runtime LOC should count submitted Go runtime files and exclude tests; Go LOC details must stay synchronized with the Go evaluator implementation.

Lower extraction ratio is better. A whole-repo copy can pass tests but should score near zero.

## Final Score

The current implemented formula is:

```text
FinalScore = FunctionalGate * max(0, 1 - ExtractionRatio)
```

If `FunctionalGate = 0`, final score is `0` regardless of compactness.

This formula is canonical for current documents because it matches the evaluator. Any future reference-LOC formula, such as `min(1, (alpha * reference_LOC + beta) / submitted_LOC)`, must be introduced only with a synchronized evaluator change, migration note, and paper metric definition.

## Reported Metrics

Core metrics:

- Install or build pass
- Public pass
- Hidden pass
- Pass@1
- Functional gate
- Final score
- Submitted LOC
- Source LOC
- Extraction ratio or LOC ratio
- Forbidden import rate
- Forbidden dependency or forbidden module rate
- Public-hidden gap

Optional or future metrics:

- Path leakage rate if implemented as a distinct detector.
- Copy-heavy pass rate.
- Compact pass rate under a declared extraction threshold.
- Environment failure rate separated from model failure.

## Result JSON Shape

Illustrative result fields:

```json
{
  "task_id": "example__feature_core__001",
  "language": "python",
  "build_pass": true,
  "test_pass": true,
  "public_pass": true,
  "hidden_pass": true,
  "original_import_pass": true,
  "scores": {
    "functional_gate": 1.0,
    "extraction_ratio": 0.25,
    "final_score": 0.75
  },
  "metrics": {
    "loc": 500,
    "source_loc": 2000
  },
  "errors": []
}
```

Exact field names should be read from current evaluator output before paper tables are generated.

## Scoring Invariants

- RQ, scoring, and evaluator concepts must not be duplicated into Python and Go variants.
- Language splits may have different build/test adapters but must report comparable conceptual metrics.
- Hidden tests are part of functional success, not a separate bonus.
- Compactness should penalize copy-heavy success without rewarding tiny incorrect submissions.

## TODO

- Audit current Python and Go evaluator output fields and align table-generation scripts with this document.
- Decide whether to expose `path_leakage` as an explicit result field.
- Document how symlinks, vendored modules, generated files, and test files count toward LOC in each language.
