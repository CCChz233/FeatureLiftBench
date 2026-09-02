# FeatureLiftBench Reports

> **Status: reference index · Last verified: 2026-08-29**
> Current release numbers and blockers are maintained in [docs/STATUS.md](../docs/STATUS.md).

`reports/` contains small, reviewable audits and derived analyses. Raw model runs belong under
`experiments/`. Generated summaries never override per-task `run.json` and `eval/result.json`.

Hard-50 Flash 校准原料在
[`experiments/validation/hard50/`](../experiments/validation/hard50)；
agentic-evidence 小结在 [agentic_evidence/](agentic_evidence/README.md)。

## Current Release Audits

| Path | Role |
| --- | --- |
| [Python-200 balance](audits/python200_balance_design.md) | External selection balance and replacements |
| [v3 Main readiness](audits/v3_main_readiness.md) | Frozen baseline task readiness |
| [v3 Oracle revalidation](audits/v3_oracle_revalidation/summary.md) | Repeated Docker reference evidence |
| [Adversarial canaries](audits/v3_adversarial_canaries.json) | Isolation and compactness canaries |
| [Task lifecycle](audits/task_lifecycle_report.md) | Package lifecycle status |
| [New protocol readiness](audits/new_protocol_readiness.md) | Contract/evaluation engineering gates |
| [Python-200 contract audit v1](contract_closure_200/README.md) | Full 200-task closure verdicts and remediation queue |
| [Contract v2 P0 closure](contract_closure_v2_p0/README.md) | Reviewed repair evidence for all 15 contradictory tasks |

Machine authorities include the active baseline freeze, Python-200 suite selection and source
registries under `artifacts/` and `benchmark/`.

## Paper-Candidate Result Audits

| Path | Condition |
| --- | --- |
| [Current Python-200 cross-model Main](../artifacts/research_analysis/current_results/python200_cross_model_main_20260818.json) | **Superseded** 150+Ext50 按题号合并；不是 Python-200' 主表 |
| [Current Qwen V1 vs Main](../artifacts/research_analysis/current_results/qwen_v1_vs_main_20260818.json) | Qwen3.6-35B V1-200；E50 干净切片；不是 Lite 协议 |
| [Current DeepSeek Main vs retired Lite V1 protocol](../artifacts/research_analysis/current_results/deepseek_main_vs_lite_v1_20260817.json) | DeepSeek 方法对比；不是当前 V1 |
| [Current V1 method spec](../docs/METHOD_V1.md) | V1 = Main + 2M cap |
| [Agent runtime ablation](../docs/METHOD_AGENT_RUNTIME.md) | DeepSeek Harness / Codex；不是 Official Main；尚无正式分数 |
| [Paper analysis index](paper_analysis/README.md) | 历史 mixed-snapshot 分析已不在树中 |

Only results classified in [docs/STATUS.md](../docs/STATUS.md) may enter current paper tables.
Historical pass counts must not be relabeled as current Main.

## Historical Model and Process Evidence

| Path | Boundary |
| --- | --- |
| `python150_compliant_20260726/` | mixed-snapshot candidate suites |
| [Failure attribution](failure_attribution_20260720/README.md) | historical trajectory failure analysis |
| [Token efficiency](token_efficiency_20260720/README.md) | historical token/context/process analysis |
| [Repo graph phase 1](repo_graph_phase1/README.md) | infrastructure evidence |
| [Repo graph phase 2](repo_graph_phase2/README.md) | smoke and A/B evidence |
| [Repo graph phase 3](repo_graph_phase3/README.md) | prototype evidence |
| `archive/` | old construction, freeze and run provenance |

Historical classification methods may be reused; absolute results remain tied to their original
task snapshots and experiment conditions.

## New Report Requirements

A paper-candidate report must record:

- suite/task-set and freeze/selection IDs;
- model revision, agent profile, arm and attempt policy;
- agent/evaluator image identities;
- Functional Pass Rate separately from agent completion/run status;
- pass-conditioned RRES，包括 eligible/available coverage 和 paired-subset policy;
- 互斥首败阶段与 `stage_evidence_unavailable`;
- exact missing, context, rate-limit, infra and rerun ledger;
- compactness and cost metrics with completeness caveats;
- source archive or suite checksum and reproducible analysis command.

Experiment policy and reporting requirements are defined in
[docs/EVALUATION.md](../docs/EVALUATION.md); current interpretation is maintained in
[docs/STATUS.md](../docs/STATUS.md).
