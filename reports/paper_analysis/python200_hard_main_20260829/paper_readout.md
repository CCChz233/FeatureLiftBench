# Python-200′ DeepSeek V4 Flash Main — 2026-08-29

> **Status: current candidate evidence · Last verified: 2026-08-29**

## Technical summary

The received suite records **132/200 (66.0%)** functional passes on the Python-200′ selection, but it is not a complete eligible 200-task Main run. Seventeen Python-150 tasks were blocked before agent launch by freeze-spec mismatches, 16 Hard-50 evaluations failed because required offline dependencies were unavailable, and 59 runs exceeded the prompt allowance. The union is 84 tasks, so 132/200 is an **audit headline**, not a paper leaderboard result.

## The split rates are descriptive but infrastructure-confounded

| Split | Functional Pass | Rate | Wilson 95% interval |
| --- | ---: | ---: | ---: |
| Frozen Python-150 | 103/150 | 68.7% | 60.9%–75.5% |
| Hard-50 | 29/50 | 58.0% | 44.2%–70.6% |
| **Python-200′** | **132/200** | **66.0%** | **59.2%–72.2%** |

These raw split rates cannot be interpreted as a clean difficulty contrast: all 17 freeze-preflight blocks are in Python-150, while all 16 dependency installation failures are in Hard-50. The earlier independent Hard-50 calibration remains useful design evidence, but this received suite must be repaired before it supports a new main-table split comparison. Historical E50 runs also differ in date, runtime image, and endpoint.

## Infrastructure and model failures must be separated

| First functional outcome | Tasks | Share of 200 |
| --- | ---: | ---: |
| pass | 132 | 66.0% |
| missing_submission | 19 | 9.5% |
| build | 16 | 8.0% |
| public | 25 | 12.5% |
| hidden | 8 | 4.0% |

Of the 68 nominal non-passes, 17 are pre-agent freeze blocks and 16 are offline dependency failures. The model/output evidence is therefore 2 no-submission, 25 public-behavior, and 8 hidden-only failures. There are no isolation failures.

## Workflow status is not the paper metric

Only **47/200** runs have workflow status `passed`, while **132/200** pass the functional evaluator. The paper and leaderboard must use `final_score` / Functional Pass@1, not the agent-process status field.

## Provenance and robustness gate

- Task-set identity: 200/200 task IDs match; 0 extra and 0 missing.
- Source identity: 183 started tasks match the source registry; missing source IDs occur only where no run provenance was emitted.
- Runtime identity: agent and evaluator Docker image digests are recorded; network-isolated evaluator failures = 0.
- Preflight: 17 tasks never launched because their active spec hash disagreed with the freeze.
- Dependency environment: 16 tasks failed before behavioral tests because required offline wheels were absent.
- Context audit: 59 runs exceeded the configured prompt allowance at least once; 37 of them passed. This is the main eligibility blocker.
- The suite records no benchmark freeze identifier. The task set can be reconstructed from IDs and registry snapshots, but final paper provenance should explicitly bind the recorded run to the active freeze.

## What this adds to the paper

1. **RQ1 has an audit-ready candidate, not a completed cell.** The suite exposes exactly which tasks require clean replacement runs.
2. **Failure attribution improves materially.** Infrastructure blocks are no longer misreported as model failures.
3. **The taxonomy and compactness layers are ready.** They can be reused once the strict replacement set is complete.
4. **The result cannot enter the final leaderboard.** The current headline is useful for internal planning only.

## Recommended next steps

1. Use the frozen 84-task union: 59 context violations, 17 freeze-preflight blocks, and 16 dependency failures with overlap removed.
2. Repair/pin the offline wheel set before rerunning dependency failures.
3. Bind every replacement run to the active benchmark freeze and preserve the original candidate unchanged.
4. Keep the two genuine no-submission outcomes and 33 behavioral failures as observed evidence unless a preregistered full-repeat policy says otherwise.

## Further questions

- What is the eligible Functional Pass@1 after the fixed 84-task replacement set?
- How many context-violation outcomes change under strict enforcement?
- Are Hard-50 failures concentrated by lift type or feature family after multiple-comparison-aware uncertainty reporting?
