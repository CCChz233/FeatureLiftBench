# Repository maintenance — 2026-08-29

> **Documentation status: reference · Maintenance pass complete**

## Baseline

- Start commit: `4da7f59cc97475f113cb9dadd1c18bcec605dbc5`
- Branch: `main`
- Active paper suite: `python200-hard-full-repository-no-hint-unreleased`
- Task set: 200 = frozen 150 + Hard-50
- Baseline freeze: `846b814726217623fa205cb7688bee61e6c21c43efda1ebd05e79b5ed8cb4fbd`
- Hard-50 selection: `hard50-expansion-20260827-v1-reviewed`
- Hard-50 release tree: `6b1cac758212025fe90481e4eaab353c8ab0812997b558fef28c74708177c351`
- Task-set SHA256: `a28c301e83bf62b831c007b7c5ebc4fd0f6e4c012496d812fa90d233dfe81ad3`
- Baseline status: 212 tracked modifications and 36,377 non-ignored untracked files before maintenance-file additions
- Pre-existing user work excluded from cleanup: 198 benchmark files, 9 integration files, method/AutoSaddler changes, and the maintenance-handbook edits
- Credentials: `.env` and local agent config were not read or added to Git

## Scope

- Included: rebuildable caches, misplaced agentic-evidence workspaces, root compatibility entrypoints, stopped method documentation, misplaced experiment bundles, asset inventory
- Excluded: all user task-contract and AutoSaddler functional edits
- High-risk approval: the maintainer explicitly approved the six point-named Hard-50 evidence moves after the initial safe maintenance pass; benchmark payloads and freeze/source identities were not moved or deleted

## Changes

### Removed as rebuildable cache

| Path | Approximate size before | Recovery |
| --- | ---: | --- |
| `integrations/autosaddler_featureliftbench/.venv` | 532 MB | Follow the `uv venv` and `uv pip install` commands in the integration README |
| `third_party/runtimes` | 865 MB | `./setup.sh` or `./harness/scripts/pin_runtime_agents.sh` |
| root pytest/ruff caches, `build/`, egg-info, `__pycache__`, `.DS_Store` | small | Recreated by build/test commands |

At least 1.4 GB of reproducible local state was removed. No benchmark payload or experiment result was deleted.

### Moved without content changes

| Source | Destination | Reason |
| --- | --- | --- |
| `artifacts/research_analysis/agentic_evidence/*` | `experiments/validation/agentic_evidence/` | Full repository audit workspaces are raw validation evidence, not small artifacts |
| raw directories under `reports/agentic_evidence/` | `experiments/validation/agentic_evidence/` | Reports now contain only reviewable calibration summaries |
| two result tarballs at `experiments/` root | `experiments/bundles/incoming/frozen-results/` | Restore the documented experiment top-level contract |
| four stopped method documents at `docs/` root | `docs/archive/methods/` | Keep one archived negative-result copy and remove false current entrypoints |
| six approved Hard-50 calibration directories at `experiments/` root | `experiments/validation/hard50/` | Keep referenced raw validation evidence under its canonical boundary |

Agentic-evidence destination tree digest after migration:
`0363d365b67aeaacf33e8c1ebcf04c40416a801104840ae5e29e0b3e295f2223`.
Historical completed run records were not rewritten, so embedded absolute paths remain provenance only.

Moved bundle identities:

- `d4b5303ccdaf1d5a188001e0b24de1694bf928af8647dacbae194db46cb6e28b` — `FeatureLiftBench-deepseek-v4-flash-150-20260805.tar.gz`
- `0d950fb1210a5a40ed746fe31eeedb40f1a3d53f1fca0badead6ad83f9612208` — `python200-deepseek-v4-flash-lite-v1-vllm-local-0813-001-results-latest.tar.gz`

### Entry and documentation policy

- Added `scripts/README.md` as the script ownership index.
- Added `scripts/reorganize_experiments.py` to the tracked maintenance-script whitelist and recorded bundle moves without replacing earlier ledger history.
- Kept `run_benchmark.sh` and `run_experiment.sh` as supported thin root forwarders.
- Marked ten historical root scripts deprecated; removal is deferred until the next maintenance review as required by the handbook.
- Archived Artifact-aware, Pre-submit audit, Spec-adversarial, and Verification-aware method documents and updated current links.
- Added tracked README boundaries for raw agentic-evidence validation and small agentic-evidence reports.

## Approved high-risk migration

The maintainer explicitly approved moving the following six current Hard-50
calibration directories. Each move stayed on the same filesystem, retained the
directory basename, and preserved the pre-move tree digest:

| Path | Approx. size | Tree digest |
| --- | ---: | --- |
| `experiments/validation/hard50/hard50_copyheavy_swap_flash_20260828` | 59 MB | `6752bd1d42948c06cc558a9d4277c8a271bcb69586b82d040443e842c39db2b9` |
| `experiments/validation/hard50/hard50_copyheavy_swaps_20260827` | 36 MB | `50a1ec62d11f57b3f687bb30e224d571b4d520933bbe6bd3a4e5a1d08b99122c` |
| `experiments/validation/hard50/hard50_pilot_flash_20260827` | 70 MB | `4e6876b63d528b3d72b56c58af4ce7d2d98ef74177c8a63a9c61bd369280831f` |
| `experiments/validation/hard50/hard50_pilot_flash_swaps_20260827` | 8 MB | `ecd5a8a279f208b0c32e876a472956523a2ace0bb61f8abe59754b8e8a897d0f` |
| `experiments/validation/hard50/hard50_pilot_gates_20260827` | 92 MB | `872b7c3a925801fdbb6f93c0f6ac9aa22c84289e383eaad87c0412a50170e72d` |
| `experiments/validation/hard50/hard50_remaining40_flash_20260827` | 344 MB | `65ea837c63d314ea7b24f5197a9f12b48807660fc0aa82efd5e6321aa032ef37` |

The two benchmark-selection scripts that directly referenced the old locations
were updated in the same change. The move is also part of the reusable
`scripts/reorganize_experiments.py` migration manifest.

The following benchmark paths were inventory-only: `benchmark/tasks/`, `benchmark/hard50/`, `benchmark/hard50_pilot/`, `benchmark/sources/`, `benchmark/vendor-wheels/`, references, selection files, and generated suite links.

## Unknown and deferred

- `archive/` remains about 1.7 GB. Its top-level tarballs are unique by SHA256 in this local tree, but the whole archive has not been proven redundant against canonical experiments.
- Top-level archive tarball SHA256 values:
  - `69f60a9ece66d3a547e98604dd8952d4faf0265db621fead1396091150ec9029` — mini-swe-agent Main Flash
  - `669425d41a3b5464e52ae8e8800ee22e331a9e47eb114807087989b2ad3b8be4` — OpenHands 100-hard suites
  - `66b28b18f5402d4c4fbafc18ee8c2a7a3c54c67e43e3088f923ddec20aac1632` — OpenHands Main Flash results
- `benchmark/hard50_pilot/` remains an untracked high-risk payload pending a separate canonical-copy and retention decision.
- The ignored `AutoSaddler/` checkout remains because related integration work is active; its recovery pin is commit `30e20ce`.

## Validation

- [x] Documentation check — 369 project documents, 0 broken links, 0 missing statuses, 0 unreachable current documents
- [x] Catalog check — suite, agent, method, and arm registries are consistent
- [x] Task lifecycle check — 217 task packages checked, 0 errors, 0 global issues
- [x] Relevant harness/integration tests — 34 maintenance-related harness tests and 10 AutoSaddler integration contract tests passed
- [x] End-to-end Docker smoke — `semver__version_core__001` reference submission passed build, Public, Hidden, isolation, and functional gates with final score 1.0; result: `experiments/smoke/repository-maintenance-20260829/semver-reference-docker/result.json`
- [x] Python-200′ and legacy Python-200 views each have 200 symlinks and no broken links
- [x] The maintenance pass did not edit suite/freeze/source identity files
- [x] Source and suite identity hashes recorded above
- [x] Experiment top-level check — only the documented canonical directories remain

## Completion

The approved Hard-50 move completed the experiment top-level contract. Remaining
Unknown items above require separate evidence and, where applicable, a new
point-named approval; they are not unfinished work from this maintenance pass.

## Follow-up — documentation alignment (same day)

No payload moves. Updated current entry documents so the on-disk layout matches
the paper suite:

- `benchmark/README.md` now names `python200_hard` as the paper root and marks
  `python200_tasks/` superseded.
- `RUN.md` and `docs/SERVER_RUNBOOK_PYTHON200.md` launch via
  `./scripts/run_benchmark.sh --benchmark python200_hard`.
- `docs/README.md` splits authority / run / screening / 组会 / plans.
- Dead `./logs/*.sh` wrappers were removed from current run docs.
- `PLAN_EXTERNAL50_TO_PYTHON150_QUALITY.md` marked reference (contract day done).
- `scripts/reorganize_experiments.py` uses `datetime.timezone.utc` so `python3.9`
  can `--check`.

Validation for this follow-up: `python3.12 scripts/check_docs.py --warnings-as-errors`.
Suite/freeze/source identity files were not edited.
