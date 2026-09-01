# Paper analysis

> **Status: current index · Last verified: 2026-08-29**

Current candidate evidence:

- `python200_hard_main_20260829/`: DeepSeek V4 Flash OpenHands Main on the
  Python-200′ (frozen Python-150 + Hard-50) task set. Start with
  `offline_closure_checklist.md` and `paper_readout.md`; `summary.json`,
  `provenance_attestation.json`, `context_audit.json`, and `failure_audit.json`
  are the reusable machine-readable layers. The received 132/200 headline is
  blocked: 17 tasks did not launch, 16 stopped at offline dependency install,
  and the frozen strict replacement union contains 84 task IDs.

Exploratory historical evidence:

- `python150_exploratory_20260830/`: reproducible four-model analysis of the
  frozen Python-150 matrix, including an executed notebook, exact CSV tables,
  and seven PNG/PDF figures. Use it to develop analysis and figure designs, not
  as the final Python-200′ leaderboard.

Historical v1 note: `mixed_snapshot_v1` is no longer present. Do not use its
150-task figures as Full-Repository / No-Hint Main. Current result status lives
in [docs/STATUS.md](../../docs/STATUS.md) and
[docs/FINDINGS.md](../../docs/FINDINGS.md).
