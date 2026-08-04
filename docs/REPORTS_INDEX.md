# Reports index

数字状态以 [STATUS.md](STATUS.md) 为准。`reports/` 保存机器审计、结果摘要和
历史证据；大体积原始运行保存在本地 `experiments/`，默认不提交。

## v3 当前权威证据

| 路径 | 内容 |
| --- | --- |
| [`reports/audits/v3_main_readiness.md`](../reports/audits/v3_main_readiness.md) | Python-150 × 八原则逐题验收 |
| [`reports/audits/v3_main_readiness.json`](../reports/audits/v3_main_readiness.json) | 机器可读 readiness |
| [`reports/audits/v3_oracle_revalidation/summary.md`](../reports/audits/v3_oracle_revalidation/summary.md) | 150 × 3 Docker Oracle 稳定性 |
| [`reports/audits/v3_adversarial_canaries.json`](../reports/audits/v3_adversarial_canaries.json) | 12 个 isolation/compactness 对抗样例 |
| [`benchmark/sources/registry.json`](../benchmark/sources/registry.json) | 126 external repos / 132 snapshots / 150 task mappings |
| [`artifacts/research_analysis/v3/current_benchmark_freeze.json`](../artifacts/research_analysis/v3/current_benchmark_freeze.json) | active v3 source/spec/reference/evaluator/environment freeze |
| [`reports/audits/task_lifecycle_report.md`](../reports/audits/task_lifecycle_report.md) | task package lifecycle |
| [`reports/audits/new_protocol_readiness.md`](../reports/audits/new_protocol_readiness.md) | 公开契约与 evaluation mapping 工程门禁 |
| [`docs/LIFT_TAXONOMY.md`](LIFT_TAXONOMY.md) | Direct / Adapted / Composite 定义 |
| [`reports/lift_taxonomy/`](../reports/lift_taxonomy/) | 150 题 lift_type 标注进度（seeded≠final） |
| [`reports/contract_closure_audit/`](../reports/contract_closure_audit/) | contract-closure 审计与问题族 |

旧的 source/no-hint 预审、Pilot-16 计划和整改 checklist 已被
`v3_main_readiness` 与 active freeze 取代，不再保留为并列入口。

## 当前模型结果

v3 Full-Repository / No-Hint baseline 尚未运行。

| 路径 | 口径 |
| --- | --- |
| [`reports/python150_compliant_20260726/`](../reports/python150_compliant_20260726/) | `mixed_snapshot_v1` 四模型 candidate；非 v3 |
| [`reports/archive/v1_mixed_snapshot_runs_20260712.md`](../reports/archive/v1_mixed_snapshot_runs_20260712.md) | 2026-07-12 更早冻结 run 集；历史复现 |
| [`reports/paper_analysis/`](../reports/paper_analysis/) | 上述 2026-07-12 run set 的生成分析；历史 |

## 历史失败与成本分析

| 路径 | 作用 |
| --- | --- |
| [`reports/failure_attribution_20260720/`](../reports/failure_attribution_20260720/) | 550-run failure attribution |
| [`reports/token_efficiency_20260720/`](../reports/token_efficiency_20260720/) | token/context/process analysis |
| [`docs/research_analysis/TRAJECTORY_FINDINGS.md`](research_analysis/TRAJECTORY_FINDINGS.md) | 轨迹案例与机制线索 |

这些报告来自 v1/mixed conditions。分类方法可复用，绝对数字不能当作 v3
结果。

## 已降级方法证据

| 路径 | 状态 |
| --- | --- |
| [`reports/repo_graph_phase1/`](../reports/repo_graph_phase1/) | RSG 基础设施检查 |
| [`reports/repo_graph_phase2/`](../reports/repo_graph_phase2/) | RSG smoke/hard A/B；未见 hidden-pass 增益 |
| [`reports/repo_graph_phase3/`](../reports/repo_graph_phase3/) | 关系族原型 |

RSG 不再是当前提分主线；ECSM 已废弃。旧方法规划文档已删除，原始实验结果
保留用于复查。

## 归档

[`reports/archive/`](../reports/archive/) 只保存仍有 provenance 价值的历史
材料：

- `batch3_202607/`：100→150 的构造、materialization 和 promotion 快照；
- `v1_mixed_snapshot_runs_20260712.md`：旧 paper run freeze。

完成的 sprint 和迁移计划不应重新链接为当前操作说明。

## 新结果入库规则

一个新的 v3 report 至少要记录：

- active benchmark freeze ID；
- model/agent/profile/arm；
- agent/eval image digests；
- exact task set 和 attempt policy；
- evaluator Functional Pass@1；
- agent completion/status mismatch；
- compactness vector；
- token/step/latency；
- context/rerun/infra exception ledger；
- suite checksum 和数据质量结果。

运行流程见
[SERVER_RUNBOOK_PYTHON150.md](SERVER_RUNBOOK_PYTHON150.md)，实验口径见
[EXPERIMENTS.md](EXPERIMENTS.md)。
