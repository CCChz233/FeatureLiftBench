# FeatureLiftBench useful focus experiments

## Scorecard (alembic + click)

| Arm | alembic | click |
|---|---|---|
| Main | p✗ h✗ | p✗ h✗ |
| exec clean3 | p✓ h✗ | p✓ h✗ |
| exec clean4 | p✗ h✗ | p✓ h✗ |
| self_contract | p✗ h✗ | p✗ h✗ |

## Contents

- `baselines/main-compare-20260728-155516/` — Main arm, focus 2 tasks only
- `runs/exec-contract-clean3-20260729-214504/` — **best exec_contract so far** (both p✓ h✗)
- `runs/exec-contract-clean4-20260730-121739/` — B006 over-generalize regression (alembic p✗)
- `runs/self-contract-focus-20260730-140322/` — model-authored contracts pilot
- `docs/` — CLEAN_FOCUS, contamination notes, method docs
- `logs/` — suite logs

## Notes

- `workspace/repo/` stripped (recover from benchmark tasks).
- clean3 is the strongest clean template baseline on this focus.
- self_contract alembic failed public on `get_revision("base")` over-generalization (same family as clean4).
- Do **not** treat contaminated v2c as primary evidence (see CONTAMINATED doc).
