# Go Repository Selection Criteria

## Goal

Go repository selection should prioritize real reusable library slices that stress standalone module extraction, type closure, package boundaries, and hidden behavior. The Go split should not become a set of toy `Add` functions or file-copy exercises.

## Ideal Repository Properties

- Real Go OSS library or curated legacy-style module.
- Clear license and pinned commit or tag.
- Builds with a stable Go version, currently Go 1.22 in existing Go task metadata.
- Has `go.mod` or a straightforward module boundary.
- Has a feature that can be imported as a standalone package.
- No external service requirement.
- No cgo requirement in early phases.
- Contains target and non-target code close enough that compact extraction requires judgment.
- Supports deterministic `go test` public and hidden tests.
- Has interface, type, package, or module structure that makes extraction nontrivial.

## Repository Scoring Rubric

| Criterion | Score |
|---|---:|
| Module/build stability | 0-2 |
| Testability with offline `go test` | 0-2 |
| Clear reusable symbol or behavior boundary | 0-2 |
| Type/package closure complexity | 0-2 |
| Hidden-test and copy-all discriminator feasibility | 0-2 |

Interpretation:

- 8-10: high priority.
- 6-7: candidate.
- 4-5: use only if feature is excellent.
- 0-3: reject.

## Exclusion Rules

Reject repositories or slices that:

- Require network, database, browser, cloud service, or privileged runtime.
- Require cgo during the initial Go split.
- Are mostly code generation outputs.
- Have a target feature already isolated as one clean package that can be copied wholesale.
- Only expose CLI behavior with no useful importable API.
- Require vendoring most of the source module.
- Hide target selection in filenames or comments.
- Cannot produce meaningful hidden tests beyond public happy paths.

## Recommended Repo Mining Workflow

1. Build a shortlist of real Go libraries with importable reusable features.
2. Check license, commit/tag stability, and `go test` offline viability.
3. Identify a symbol or behavior boundary, not a file boundary.
4. Write a boundary plan before generating task files.
5. Create public tests that specify the API without revealing file locations.
6. Create hidden tests for edge cases, interfaces, errors, reflection, or package/module semantics.
7. Build oracle, naive, and copy-all baselines.
8. Run mechanical gates and classify as paper-ready hard, calibration, redesign, or drop.

## Practical Reuse Questions

Before a Go repo enters the candidate backlog, answer:

- What reusable package would `featurelifted` represent?
- Who would import it and in what production or tooling scenario?
- Why is compact closure better than vendoring or copy-all?

## Current Go Split Notes

Existing planning docs indicate that some Go tasks have reached calibration status, but paper-ready hard Go tasks still require stricter evidence. The current `benchmark/go/tasks/` tree also contains seed or placeholder tasks whose metadata still describes `sample.Add`; those should not be counted as hard paper-ready FeatureLift tasks.

## Open work

- Reconcile `benchmark/go/tasks/` contents with Go planning docs and promote only verified hard tasks.
- Add one source-level repo pool row per accepted Go hard task after verification.
- Decide whether calibration tasks remain in `benchmark/go/tasks/` or move to a separate calibration directory.
