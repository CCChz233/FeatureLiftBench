# FeatureLiftBench 实验清单

> **Status: archived · Last verified: 2026-08-04**
> 本文是合并前快照；当前结果资格见 [STATUS.md](../../STATUS.md)。
> 当前规模和 readiness 只在 [STATUS.md](../../STATUS.md) 维护。

## Official Condition

论文主条件是 Full-Repository / No-Hint Main：benchmark tests 不可见、source hints
不可见、标准 prompt、一次 task attempt、无失败重试、agent 与 evaluator 均在记录
identity 的 Docker image 中运行。完整定义见
[Experiment Protocol](../specs/04_experiment_protocol.md) 和 [Experiment Arms](../specs/EXPERIMENT_ARMS.md)。

## Result Sets

| Result set | Completeness | Classification | Source |
| --- | --- | --- | --- |
| Frozen Python baseline: GPT-OSS 120B | complete | core candidate after environment resolution | historical audit `reports/paper_analysis/python150_frozen_20260803/` |
| Frozen Python baseline: Qwen3.5 122B | complete | core candidate after context/environment resolution | historical audit `reports/paper_analysis/python150_frozen_20260803/` |
| Frozen Python baseline: Qwen3.6 35B | complete union of three shards | core candidate after context/environment resolution | historical audit `reports/paper_analysis/python150_frozen_20260803/` |
| Frozen Python baseline: DeepSeek V4 Flash | partial | supporting evidence only | historical audit `reports/paper_analysis/python150_frozen_20260803/` |
| Balanced External extension | not yet complete | required for Python-200 model tables | [suite definition](../../../benchmark/selection/python200_suite.json) |
| Older mixed-snapshot suites | historical | not comparable with current Main | [reports](../../../reports/README.md) |

Do not copy pass counts from bundle `MANIFEST.md`, `summary.json`, or agent completion
status. Primary results come from per-task evaluator Functional score, cross-checked with
`eval/result.json`.

## Joining Baseline and Extension

Baseline and External results may be combined only when all of the following match:

- exact model revision and endpoint behavior;
- agent adapter/profile and prompt condition;
- task attempt and retry policy;
- agent image identity;
- evaluator image identity and scoring code;
- Main information boundary.

Keep the two suites immutable and merge by task ID in analysis. A missing submission is a
valid Functional failure in the denominator. Shards over disjoint task sets are partitions,
not repeated samples.

## Required Artifacts

Every paper-candidate run must retain:

- exact task IDs and suite/task-set hash;
- freeze/selection identifiers;
- model, profile, arm and attempt policy;
- agent/evaluator image IDs;
- per-task `run.json`, `eval/result.json`, submission and usage/context audit;
- infra, context, rate-limit and rerun exception ledger;
- generated analysis with Functional and completion status reported separately.

## Reporting

- Primary: Functional Pass@1 with uncertainty.
- Paired model comparisons: per-task contingency table and paired test.
- Secondary: build/public/hidden/isolation gates, compactness, tokens, API calls, steps and time.
- Diagnostic only: agent completion status, shard-level rates and unaudited copy heuristics.

Interpretation snapshot: [FINDINGS_20260804.md](FINDINGS_20260804.md); evidence locations are indexed in
[reports/README.md](../../../reports/README.md).
