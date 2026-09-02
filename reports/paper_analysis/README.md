# Paper analysis

> **Status: current index · Last verified: 2026-09-01**

Current candidate evidence:

- `python200_hard_main_20260829/`: DeepSeek V4 Flash OpenHands Main on the
  Python-200′ (frozen Python-150 + Hard-50) task set. Start with
  `offline_closure_checklist.md` and `paper_readout.md`; `summary.json`,
  `provenance_attestation.json`, `context_audit.json`, and `failure_audit.json`
  are the reusable machine-readable layers. The received 132/200 headline is
  blocked: 17 tasks did not launch, 16 stopped at offline dependency install,
  and the frozen strict replacement union contains 84 task IDs. For failure
  causality, read `failure_process_analysis.md` and then the stricter
  `contract_clarity_vs_exploration.md`; the latter separates model exploration
  failures from TASK exact-oracle gaps on the 19 first-pass aligned failures.
  `clause_narrowing/clause_narrowing.md` then narrows to the 8 Hidden-first
  failures and asks whether each obligation was recoverable from the public
  contract at all, which bounds how much any agent-side method can win;
  `clause_narrowing/evidence_packets.md` carries the per-task evidence.

- `benchmark_tiers/`: **v1 provisional** two-state labels (`meets_standard` /
  `violates`) and the 163-task list they produced. Superseded pending v2
  adjudication; do not treat 163/37 as the paper analysis set.
- `benchmark_tiers_v2_candidate/`: protocol v2 three-state candidate labels.
  Official `python200_hard_standard_suite.json` is written only after
  `undetermined = 0` and an explicit `--write-selection`.
  Protocol: [BENCHMARK_VALIDATION_GATE.md](../../docs/BENCHMARK_VALIDATION_GATE.md) §13.

Exploratory historical evidence:

- `python150_exploratory_20260830/`: reproducible four-model analysis of the
  frozen Python-150 matrix, including an executed notebook, exact CSV tables,
  and seven PNG/PDF figures. Use it to develop analysis and figure designs, not
  as the final Python-200′ leaderboard.

Historical v1 note: `mixed_snapshot_v1` is no longer present. Do not use its
150-task figures as Full-Repository / No-Hint Main. Current result status lives
in [docs/STATUS.md](../../docs/STATUS.md) and
[docs/FINDINGS.md](../../docs/FINDINGS.md).
