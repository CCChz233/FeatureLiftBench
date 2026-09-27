# FeatureLiftBench construction evidence (anonymous local bundle)

Assembled on 2026-09-27 for the 150 Python tasks discussed in the manuscript.
This bundle is a retrospective evidence index, not a reconstruction of the
original candidate selection process or a newly executed benchmark run.

## Contents

- `selection/frozen_membership.jsonl`: the exact 150-task membership, immutable
  source IDs, commits and digests from the final freeze. `selection_evidence`
  explicitly distinguishes the seven tagged replacement tasks from the other
  143 tasks, for which no candidate-level decision ledger was located.
- `selection/replacement_candidate_declarations.json`: 21 candidate constants
  from the archived 2026-07-27 builder script. The original generated ledger
  and its popularity snapshot were not located. The declarations therefore
  show what the script encoded, not proof that the historical selection
  procedure was executed exactly as documented.
- `contracts/contract_test_mappings.jsonl`: the current public contracts,
  public/hidden test-node mappings and required-API coverage for all 150 tasks.
  Original generated `TASK.md`, `behavior_contract.json`, and public/hidden
  Python test files are included under `tasks/<task_id>/` so mappings can be
  inspected against the actual tests. The companion source files are byte-for-
  byte copies; `SHA256SUMS.json` lists their checksums.
- `reviews/historical_and_current_review_index.jsonl`: task-level review fields
  copied from current metadata and mapping records, alongside a new 2026-09-27
  structural recheck. Historical review types are preserved as recorded.
  The new check is conducted by Codex, not by an independent human reviewer.
- `reviews/author_statement_provenance.json`: an earlier author statement
  recorded in the paper workbench. It is an author report, not a task-level
  human-review ledger.
- `reviews/blinker_current_example_review.md`: present-day inspection of one
  contract/test example, including a limitation of its stored mapping.
- `reviews/human_semantic_review_template.csv`: one pending row per task for a
  genuine reviewer to record source, contract, test assertions, adaptations,
  mapping corrections, decision, date, and evidence notes. Blank cells are
  intentionally unfilled; the template is not a completed review ledger.
- `replays/recorded_reference_replays.jsonl`: 450 previously saved pass records
  for three source-free reference replays per retained task. No replay is run
  during this assembly.
- `summary.json` and `build_construction_evidence.py`: counts, limitations and
  a regeneration command. The builder reads the local benchmark files and
  regenerates this ZIP without calling external services.

## Interpretation

The current task metadata contains AI-assisted review entries for all 150
tasks. The separate behavior-contract records mark 143 as AI-assisted and seven
as maintainer-reviewed. These fields do not provide a complete, independently
verifiable per-task human review ledger for the full collection. Current
structural checks verify generated TASKs, hashes, declared behavior/API
coverage, mapping node IDs, static test API usage and companion mapping
agreement. They cannot prove that every hidden assertion is semantically fair.

The original 143-task candidate funnel, excluded candidate counts, and reviewer
identity/date/disagreement records are not present in the located materials.
Do not infer them from the final freeze or repository-selection guideline.

This bundle documents construction evidence. Full execution reproduction also
requires the evaluator, pinned source archives, dependency/runtime environment
and model-run artifacts; those are not embedded here. The anonymous access URL
for the eventual full replication package remains to be supplied.

## Local regeneration

From the repository root:

```bash
python -B docs/paper-workbench/replication/build_construction_evidence.py
```

`SHA256SUMS.json` allows verification of every included file except itself.
