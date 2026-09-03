# Hidden provenance Gate 0 / Flash-33 check — 2026-09-02

> **Do not treat any of the following as gold.** No full dual-Agent Flash-33
> run was launched in this pass.
>
> **Outcome of this pass:** Gate 0 re-run (R5), root cause found, runner
> termination accounting added, and Gate 0 **closed as passed** under an amended
> protocol. Gate 1 is unblocked but **deliberately not run** — Hidden provenance
> remains a declared limitation.

Protocol: [HIDDEN_CONTRACT_PROVENANCE.md](../../docs/HIDDEN_CONTRACT_PROVENANCE.md),
Gate 0–2 in [07_top_conference_readiness_plan.md](../../docs/paper/07_top_conference_readiness_plan.md).
Raw runs live in the gitignored workspace
`experiments/validation/agentic_evidence/`.

## Gate 0 (distlib smoke)

Artifact still on disk:
`experiments/validation/agentic_evidence/runs/flash33-distlib-tool-smoke-r4_20260826/`

| Check | Observed |
| --- | --- |
| `audit_record.json` | present |
| independent `validation.json` / `record_valid` | **true** (`verdict=explicit`) |
| `source_tree_unchanged` | **true** |
| early stop | `early_stop_count=0` |
| Agent normal exit | `agent_exited_normally=false`, `returncode=3` |
| 24-step budget | `audit_max_agent_steps=24` |

The smoke produced a schema-valid record and left the source tree unchanged.
It did **not** meet the readiness-plan exit condition (early stop **or**
normal write-then-exit). The paper DoD checkbox for Gate 0 stays open.
Do not widen the case set or raise the budget to paper over that.

### R5 re-run (2026-09-02) — same outcome, root cause identified

`experiments/validation/agentic_evidence/runs/flash33-distlib-tool-smoke-r5_20260902/`,
same config as R4 (`deepseek/deepseek-v4-flash`, `audit_max_agent_steps=24`,
final prompt enabled). Result is **identical to R4**: `record_valid=true`,
`verdict=underdetermined`, `source_tree_unchanged=true`,
`early_stop_count=0`, `normal_exit_count=0`, `returncode=3`. Reproducible
across two runs seven days apart, so this is not run-to-run noise.

**Root cause.** The agent spends all 24 steps investigating and only writes the
record in the forced final action, then mini-swe-agent exits 3 because the step
limit is consumed. Both accounted exit paths are therefore unreachable:

- the adapter's early-stop poll only evaluates `completion_check` **while the
  child process is alive** (`agent_adapters.py`: `process.wait()` succeeding
  breaks the supervision loop before the check runs), so a record that becomes
  valid in the last action is never observed as a completion artifact;
- `returncode == 3` is mini-swe-agent's step-limit signal, which
  `agent_exited_normally` cannot distinguish from a crash.

**Runner fix (2026-09-02).** `run_agentic_evidence_canaries.py` now emits a
`termination_path` per case and a `termination_paths` histogram per run, so the
report states which path a run actually took instead of only that two specific
paths were not taken. `agent_exited_normally` semantics are unchanged and the
shared adapter is untouched (changing `completion_detected` globally would alter
main-suite run accounting). Recomputed over the runs on disk:

| Run | n | valid | termination paths |
| --- | ---: | ---: | --- |
| `flash33-distlib-tool-smoke-r4_20260826` | 1 | 1 | `budget_exhausted_with_valid_record` 1 |
| `flash33-distlib-tool-smoke-r5_20260902` | 1 | 1 | `budget_exhausted_with_valid_record` 1 |
| `flash33-gate1-wave3-auditor-a_20260826` | 3 | 3 | `early_stop_after_valid_record` 3 |
| `flash33-gate1-wave3-auditor-b_20260826` | 3 | 3 | `early_stop_after_valid_record` 3 |
| `flash33-gate1-wave10-auditor-a_20260826` | 10 | 9 | `early_stop_after_valid_record` 9, `timeout` 1 |
| `flash33-gate1-wave10-auditor-b_20260826` | 10 | 9 | `early_stop_after_valid_record` 9, `budget_exhausted_without_record` 1 |

Two consequences that the R4-only report could not show:

1. **The early-stop mechanism is not broken.** It fired on 24 of 26 Gate 1
   cases. distlib is an outlier the auditor cannot close inside 24 steps.
2. **The fail-closed requirement is empirically satisfied.**
   `flash33-gate1-wave10-auditor-b` has one `budget_exhausted_without_record`
   case: it is counted invalid, its returncode is nonzero, and it is not
   reported as a normal exit — exactly the readiness-plan condition for
   "24 steps with no record".

### Decision (2026-09-02): Gate 0 closed as passed

Gate 0 as originally written admitted only early stop or normal write-then-exit.
The distlib case reproducibly lands on a third path,
`budget_exhausted_with_valid_record`. The maintainer decision is to **recognise
that path as a legitimate pass**, on these conditions, now written into
[07_top_conference_readiness_plan.md](../../docs/paper/07_top_conference_readiness_plan.md)
§3 Gate 0:

- the record must be independently valid and `source_tree_unchanged=true`;
- the path must be accounted separately and **must not** be folded into
  `normal_exit_count`;
- the fail-closed branch (`budget_exhausted_without_record` → invalid, nonzero
  returncode, not a normal exit) still holds, and is empirically demonstrated by
  `flash33-gate1-wave10-auditor-b`.

Recognising path 3 does **not** raise the 24-step budget and does **not**
replace the distlib case, so it does not paper over the failure the plan warns
about. What changed is that the runner now reports which accounted path a run
took, instead of only that two particular paths were not taken.

**The Gate 0 DoD checkbox is now checked.** The R5 run is the referenced
evidence.

## Gate 1 (partial only; not Flash-33)

Existing dual-auditor waves, `gold=false`:

| Wave | n | `agent_consensus` | unresolved / coverage / conflict |
| --- | ---: | ---: | --- |
| `flash33-gate1-wave3-consensus_20260826` | 3 | 1 | citation_mismatch 2 |
| `flash33-gate1-wave10-consensus_20260826` | 10 | 5 | citation_mismatch 2, conflict 1, coverage_failure 2 |

No `flash33_agent_labels_consensus.json` for 33/33 under
`artifacts/research_analysis/hidden_provenance/`. Completing Gate 1 and Gate 2
needs API budget; this pass did not start that.

### Gate 1 readiness inventory (2026-09-02)

Everything except the API spend is in place:

| Prerequisite | State |
| --- | --- |
| Full 33-case suite | ready, `experiments/validation/agentic_evidence/flash33_suite_v1/cases` (33 dirs) |
| Audit runner | works, `harness/scripts/archive/run_agentic_evidence_canaries.py` (see note below) |
| Agent binary + API key | present (`miniswe/bin/mini`, `FEATURELIFTBENCH_API_KEY` from `.env`) |
| Multi-reviewer aggregation | **done** — `aggregate_flash33_audit_labels.py` takes repeated `--run-dir`/`--reviewer`, and `flash33_aggregate.py` is explicitly "without severity override", emitting per-assertion reviewer verdict, validity, confidence, citation status, consensus status and abstain reason, with `coverage_failure` for invalid/missing records |
| Gate 1 outputs wired | `flash33_agent_labels_consensus.json` + `flash33_agreement.json` |

So the readiness plan's "必须改造" list for Gate 1 is already satisfied; the
remaining work is purely the 33 × 2 auditor runs.

**Cost estimate from wave10 actuals:** median 148 s (auditor A) / 126 s
(auditor B) per case; 10 cases took 46.4 min and 23.0 min respectively.
Extrapolating, 33 cases × 2 auditors is roughly **3.5–4 h wall clock**
sequential. The 13 wave3/wave10 cases could be reused via the runner's
`--resume`, but that mixes 2026-08-26 and later records under one reviewer id;
a single-dated fresh 33 is cleaner provenance.

**Decision (2026-09-02): not launched.** Gate 0 is now closed, so Gate 1 is
unblocked, but the maintainer chose not to spend the API budget in this pass.
Until 33/33 exists, Hidden provenance stays a **declared limitation**: the
Flash-33 initial labels are replayable and `gold=false`, and no Hidden-fairness
claim may be stated as gold. Everything needed to start is listed above, so this
is a budget decision, not an engineering gap.

### Note on runner location

`run_agentic_evidence_canaries.py` sits in `harness/scripts/archive/` and is
listed there under "killed-method / one-shot comparators". That
classification is wrong: it is the live runner for Gate 0 and Gate 1, which are
open paper DoD items. It is not in either script README's inventory. Left in
place because its sibling `retry_invalid_agentic_evidence_cases.py` resolves it
as a same-directory path; the archive README now records that Gate 0/1 depend
on it.

## Flash-33 initial labels (replayable, not gold)

| Artifact | Status |
| --- | --- |
| `harness/config/experiments/hidden_provenance_flash33_v1.txt` | 33 IDs |
| `artifacts/research_analysis/hidden_provenance/flash33_packets.json` | n=33, IDs match the task file |
| `artifacts/research_analysis/hidden_provenance/flash33_labels.json` | n=33, IDs match; `gold=false` |
| Distribution | Explicit 11 / Recoverable 4 / Ambiguous 0 / Underdetermined 18 |
| `python200_prime_candidate_rejudgement_20260831.json` | maintainer AI-assisted; `gold=false`; not independent human review |

The initial labels can be replayed from the packets and codebook. They must
not be written as paper gold. The 2026-08-31 rejudgement closes a candidate
blocker list; it does not replace Gate 1 consensus.
