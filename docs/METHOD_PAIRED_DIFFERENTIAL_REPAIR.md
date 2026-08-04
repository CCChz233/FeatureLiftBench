# Paired Differential Repair (PDR)

**Status:** held-out clean-6 negative; do not expand  
**Base candidate:** Exec-Contract clean3  
**Visibility:** Full-Repository / No-Hint / test-blind

## Motivation

The earlier trajectories separate two problems:

1. clean3 executable contracts improve public behavior but leave part of the
   behavioral closure unresolved;
2. free-form differential probing can find a real upstream/candidate mismatch,
   but a local truth can be generalized into a public regression.

PDR treats dynamic repair as a two-oracle debugging problem:

- **upstream oracle:** what the target behavior should become;
- **baseline oracle:** what adjacent behavior must continue to do.

The method adds one small tool, `flb_diff.py`, rather than a debugger suite.

## Protocol

1. Start from the frozen clean3 submission and contracts.
2. Run the same observation-only probe against upstream, immutable baseline,
   and mutable candidate.
3. Before a useful mismatch is found, a small number of reconnaissance probes
   may be discarded. The first probe with:
   - `target_matches_upstream = false`, and
   - `control_preserved_from_baseline = true`
   
   becomes the frozen counterexample.
4. Repair only that target. The patch may be refined only when the same frozen
   control exposes a regression.
5. Accept only when target and control are both true, the immutable baseline
   hash is unchanged, and the frozen clean3 contracts pass.
6. Run formal evaluation once, after the submission is frozen.

For symbolic or overloaded values, the control is domain-complete: every
special value named by TASK is also registered as ordinary user data. Exact
registered data must win before symbolic fallback.

## Admission rules

The upstream implementation is not automatically the task contract. A target
is admissible only when TASK requires the distinguished behavior.

- Exception observations are normalized to the coarsest TASK-declared type.
  An upstream-only subtype is not a valid target.
- Exact wording and casing are ignored unless TASK declares them.
- Ordering is observed only when the task contract makes it meaningful.
- Probes contain no assertions, expected values, evaluator references, or
  test-framework imports.

## Focus development result

| Task | clean3 | PDR | Interpretation |
| --- | --- | --- | --- |
| Alembic RevisionMap | p✓ h✗ | **p✓ h✓** | Frozen `head` target plus registered `head/heads/base` control caught and corrected an over-general repair |
| Click LazyCommandCollection | p✓ h✗ | p✓ h✗ | Agent aligned an upstream-only exception subtype; TASK did not require it, and the uncontracted casing failure remained |

On these two development tasks, Functional changes from clean3 **0/2** to
PDR **1/2**. This is mechanism evidence, not a held-out result: the focus tasks
and the symbolic-id collision rule were already part of method development.

The detailed trajectory and artifact paths are in
[`experiments/dpr_pilot/RESULTS_20260730.md`](../experiments/dpr_pilot/RESULTS_20260730.md).

## Held-out clean-6 result

A deterministic six-task sample was frozen before model calls and run as
Main vs clean3 vs PDR. All PDR candidates were frozen before formal
unblinding.

| Arm | Public | Hidden | Functional |
| --- | ---: | ---: | ---: |
| Main | 4/6 | 2/6 | **2/6** |
| clean3 | 4/6 | 2/6 | **2/6** |
| PDR with abstention | 4/6 | 2/6 | **2/6** |

PDR certified two repairs and abstained on four tasks. Neither certified
repair produced a Functional flip; the fallback prevented regressions. The
PDR phase alone used 16.99M tokens and 341 API calls, more than twice the
clean3 tokens, for zero lift.

The run also found that upstream collection failed on all six clean3 tasks,
leaving zero trace events and non-substantive contracts while the structural
contract invocation still passed. PDR then accepted one TASK-undeclared
Pyramid target and spent four tasks' budgets up to the OpenHands step limit.

Full frozen results and trajectory analysis:
[`RESULTS_20260731.md`](../experiments/pdr_clean6_20260730/RESULTS_20260731.md).

## Decision

The useful core is small:

- immutable-candidate fallback as the outer regression boundary;
- upstream target oracle;
- immutable baseline conservation oracle;
- fail-closed evidence and TASK-clause admission.

The free-form reconnaissance loop and second full agent call are not supported:
they were expensive, selected peripheral behavior, and did not improve the
held-out Functional count.

The next method should first make Exec-Contract fail closed: prepare upstream
dependencies, require passing selected upstream tests plus nonzero substantive
trace evidence, cover all TASK APIs/signatures, bind every observation to a
public clause, and use one implementation call. Validate that smaller mechanism
on the now-open clean-6 development tasks before drawing another untouched
cohort.
