# Workflow extraction pilot — 2026-09-12

This is a new construction study, not a change to the frozen Python-150 or
Hard-50 suites. It tests whether useful multi-stage features produce genuine
functional difficulty under the existing Full-Repository / No-Hint protocol.

Current implementation and measured results: [RESULTS.md](RESULTS.md).
Private server-overlay instructions: [SERVER.md](SERVER.md).

## Acceptance criteria

1. A concrete standalone consumer and an upstream implementation already exist.
2. Public contracts specify all required API, input, output, error and state
   categories. Maintainer source locations stay in private provenance.
3. Reference behavior is checked against the pinned upstream independently of
   benchmark test expectations. No invented upstream semantics.
4. Basic and hidden tests share the contract; combinations deepen coverage.
5. Shallow baselines perform plausible useful work. Empty stubs and artificial
   copy-all padding are not difficulty evidence.
6. Functional correctness and reference-relative compactness stay separate.
7. Each materialized candidate requires local validation, isolated Linux replay,
   and fixed-budget strong-agent calibration before it is called hard.
8. Freeze contracts and evaluation inputs before calibration; preserve all
   failures. No hidden-test editing to reach a desired pass rate.

## Construction order

Start with end-to-end prototypes from pip, dbt-core and SQLGlot, and use their
measured closure and baseline evidence to select the rest of a 12-task pilot.
Do not manufacture twelve nominally different tasks from shared code just to
reach a count. SQLGlot overlaps the retired External-50 repository pool; this
must remain explicit in any eventual source-disjoint selection.

Generated candidate packages live under `benchmark/staging/`. Source acquisition
uses complete Git trees, with Git metadata omitted. Bulk source trees, wheels,
virtual environments and replay artifacts are local assets, not paper inputs.

## Environment observations

- Local Python 3.12.14 is available through the bundled runtime.
- Initial Docker probe found no running Linux engine.
- No project `.env` or configured local model runtime was present at inspection.
- Consequently local checks are development evidence; server Docker/agent runs
  must provide promotion-quality and empirical difficulty evidence.

No main membership, published result, or existing freeze is modified here.
