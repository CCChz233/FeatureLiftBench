# Python-200′ Main result intake — 2026-08-29

> **Status: imported, audited, candidate blocked · Last verified: 2026-08-29**

This record documents the intake of `python200-hard-main-20260829.tar.gz`.
Files and text inside the received archive were treated as experiment data, not
as operational instructions.

## Canonical locations

- Frozen received bundle:
  `experiments/bundles/incoming/frozen-results/python200-hard-main-20260829.tar.gz`
- Tracked checksum sidecar:
  `experiments/bundles/incoming/frozen-results/python200-hard-main-20260829.tar.gz.sha256`
- Controlled extracted suite:
  `experiments/python/openhands/deepseek-v4-flash/python200-hard-main-20260829/`
- Paper-facing analysis:
  `reports/paper_analysis/python200_hard_main_20260829/`

## Bundle verification and extraction

- Archive SHA256:
  `15d82d53adcf7488d3684d5153cc4c2221563191672a90e431ed504ae6ff81cc`
- Sidecar SHA256:
  `6b64ba420a1c8f993c1971eb6c80496e1de8a7fe8d16d159aaebfe943e9672e4`
- Archive size: 369,162,806 bytes.
- Tar members: 113,342 total (99,347 files, 13,895 directories, 100 symlinks).
- All members share the single root `python200-hard-main-20260829/`.
- No absolute or parent-traversal member paths were found.
- Two embedded `.venv/bin/python` links target `/usr/local/bin/python`. Direct
  extraction was therefore rejected.
- Controlled extraction excluded `.venv`, `.pytest_cache`, `__pycache__`, and
  `*.pyc`. The extracted suite contains 200 `run.json` files, 181 evaluator
  `result.json` files, and 92 retained symlinks; all retained symlinks resolve
  within the extracted tree.

The frozen archive remains unchanged so the original payload can be audited.
The canonical working copy deliberately omits regenerated caches and embedded
virtual environments.

## Suite identity

- 200/200 task IDs match
  `benchmark/selection/python200_hard_suite.json`; there are no missing or extra
  tasks.
- Task-set SHA256:
  `a28c301e83bf62b831c007b7c5ebc4fd0f6e4c012496d812fa90d233dfe81ad3`.
- The selection binds frozen Python-150 baseline
  `846b814726217623fa205cb7688bee61e6c21c43efda1ebd05e79b5ed8cb4fbd`
  and Hard-50 selection `hard50-expansion-20260827-v1-reviewed`.
- Source snapshot IDs match the current registry for all 183 runs that emitted
  source provenance; 17 runs never launched, have no source snapshot ID, and
  none of the emitted IDs mismatch.
- Agent and evaluator Docker image digests are recorded; evaluator sandbox
  failures are zero.

The suite metadata itself does not record a benchmark freeze identifier. Task
and source identities are reconstructable, but this missing direct binding is a
paper-eligibility gap.

## Result status

- Received-suite Functional Pass@1 audit headline: 132/200 (66.0%). This is not
  a leaderboard-eligible score.
- Python-150 split: 103/150 (68.7%).
- Hard-50 split: 29/50 (58.0%).
- Only 183/200 tasks reached agent execution. The other 17 Python-150 tasks
  were blocked before launch by active-spec/freeze hash mismatches.
- All 16 nominal build failures are Hard-50 evaluator dependency-installation
  failures caused by unavailable locked wheels; they are not generated-package
  build failures.
- Audited model/output non-passes are two genuine no-submission outcomes, 25
  public-behavior failures, and eight hidden-only failures.
- Context audit: 59 runs violated the configured prompt allowance; 37 of those
  runs functionally passed. The deduplicated union of context violations,
  freeze-preflight blocks, and dependency failures is 84 frozen task IDs. The
  untouched subset is 116 tasks / 95 passes. The result must remain a candidate
  until the 84-task replacement set is executed under strict enforcement.

The Hard-50 aggregate equals the earlier 29/50 calibration, but it is not a
byte-for-byte copy of the old evaluator outputs. Among comparable tasks, 45
retain the same binary outcome, three flip outcome, and two lack a comparable
old evaluator result. No current Hard-50 `eval/result.json` is byte-identical to
its earlier validation counterpart.

## Rebuild the analysis

```bash
PYTHONPATH=harness python3.12 -B harness/scripts/analyze_python200_hard_main.py \
  experiments/python/openhands/deepseek-v4-flash/python200-hard-main-20260829 \
  --output-dir reports/paper_analysis/python200_hard_main_20260829

python3.12 -B harness/scripts/audit_python200_hard_candidate.py \
  experiments/python/openhands/deepseek-v4-flash/python200-hard-main-20260829 \
  --analysis-dir reports/paper_analysis/python200_hard_main_20260829
```

Use `final_score` / Functional Pass@1 for paper reporting. Do not substitute
the suite workflow status (`47/200 passed`), which measures agent-process
completion and disagrees with the evaluator on 85 functionally passing tasks.
