# FeatureLiftBench 当前状态

**最后更新：** 2026-07-27

## 结论

Python External-150 已完成 Full-Repository / No-Hint v3 hardened 工程闭环，
**可以开始正式模型实验**。当前缺的不是 benchmark 修复，而是按 active v3 freeze 从头运行
baseline。

已有模型结果全部来自 `mixed_snapshot_v1`，不能改标签进入 v3 主表。

## v3 release gate

| 项 | 状态 |
| --- | --- |
| Python Main tasks | **150/150 ready** |
| 完整公开契约 | **150/150** |
| No-Hint Agent workspace | **150/150** |
| Canonical source mapping | **150/150** |
| Full source snapshots | **132/132 ready** |
| Reference-relative compactness records | **150/150** |
| Docker Oracle revalidation | **450/450**（150 × 3） |
| Stable tasks / quarantine | **150 / 0** |
| Source-free functional capsules | **150/150** |
| Adversarial isolation canaries | **12/12** |
| v3 strict readiness audit | **150/150 pass** |
| Harness tests | **344 passed, 7 skipped**（最近完整回归） |

权威证据：

- [v3 Main readiness](../reports/audits/v3_main_readiness.md)
- [v3 Oracle revalidation](../reports/audits/v3_oracle_revalidation/summary.md)
- [adversarial canaries](../reports/audits/v3_adversarial_canaries.json)
- [source registry](../benchmark/sources/registry.json)
- [active benchmark freeze](../artifacts/research_analysis/v3/current_benchmark_freeze.json)

## Active freeze

```text
policy:
  featureliftbench.full_repository_no_hint_main.v3
freeze_pointer:
  artifacts/research_analysis/v3/current_benchmark_freeze.json
tasks:
  150
primary_metric:
  evaluator Functional Pass@1
secondary_metric:
  reference-relative compactness vector
```

冻结覆盖 source registry、task/spec、reference、evaluator、环境与 vendor
wheels。任何结果若没有记录并匹配该 freeze，都不能进入 v3 headline。旧
v2 freeze 仅保留为不可变历史 provenance。

## Benchmark 规模

| Split | 数量 | 说明 |
| --- | ---: | --- |
| Python v3 External Main | 150 | 当前论文主榜 |
| Python Curated | 7 | 扩展 split；不进入 headline |
| Python smoke | 3 | harness smoke |
| Go tasks | 12 | seed/calibration；非 paper-ready Main |

Python source registry：

- 126 个真实外部仓库；
- 0 个本地 curated source 进入 Main；
- 126 repositories；
- 132 immutable snapshots；
- 150 task mappings；
- 132 ready，0 pending。

原 7 道 `vibe_app` 题位于 `benchmark/curated/tasks/`，不参与 External-150
headline。`metadata.source.name` 不能直接当作 canonical repository 数。
详细分布见
[Python Repository and Task Inventory](python/02_python_repo_task_inventory.md)。

## 当前实验结果

### v3 Full-Repository / No-Hint

**尚无模型 baseline。** 下一步应对每个指定模型运行一次完整 Python-150
Pass@1。默认配置见
[Server Runbook](SERVER_RUNBOOK_PYTHON150.md)。

### 历史 `mixed_snapshot_v1`

2026-07-26 的四个 OpenHands/test-blind candidate suites 各覆盖 150 题。
按当前论文主指标 `evaluation.functional_gate`：

| Model | Evaluator Functional Pass@1 | Agent-completion pass | 备注 |
| --- | ---: | ---: | --- |
| DeepSeek-V4-Flash-DSpark | **87/150（58.0%）** | 84/150 | 1 context violation |
| Qwen3.5-122B-A10B-FP8 | **56/150（37.3%）** | 56/150 | 1 次 fail→fail post-hoc rerun 说明 |
| Qwen3.6-35B-A3B-FP8 | **49/150（32.7%）** | 47/150 | 4 context violations |
| gpt-oss-120b | **37/150（24.7%）** | 37/150 | compact bundle audit clean |

`Agent-completion pass` 会把 step-limit 后残留 submission 的 evaluator pass
判为失败；它是过程指标，不是 benchmark 的 Functional Pass@1。五条
agent/evaluator 状态不一致记录必须单独披露。

完整审计见
[`reports/python150_compliant_20260726/`](../reports/python150_compliant_20260726/)。
这些结果仍有 context、rerun 和 exact provenance caveat，且源码条件不是
v3 full-repository，因此只作历史/消融证据。

更早的 2026-07-12 run set 已移入
[reports/archive/v1_mixed_snapshot_runs_20260712.md](../reports/archive/v1_mixed_snapshot_runs_20260712.md)。

## 现在需要做什么

1. 在服务器 checkout 当前代码并物化/校验 canonical sources。
2. 构建固定 agent/eval Docker images。
3. 用正式配置跑 1 题 end-to-end smoke。
4. 对每个目标模型运行 Python-150 一次，保持 `attempt=1`。
5. 保存 suite、逐题 run/eval、usage、image digest 和 benchmark freeze。
6. 统一生成 v3 leaderboard、失败归因、token/step/latency 和 compactness 表。

## 当前不需要做什么

- 不需要重写 150 道题；
- 不需要恢复独立人工审核门禁；
- 不需要再跑 Flash 100 次证明 benchmark 合格；
- 不需要把旧 source slices 或 entrypoint-conditioned 结果包装成 v3；
- 不需要在首轮 baseline 前扩更多仓库或继续 RSG/ECSM 方法实验。

## 入口

- 核心原则：[BENCHMARK_DESIGN_PRINCIPLES.md](BENCHMARK_DESIGN_PRINCIPLES.md)
- 完整设计：[BENCHMARK_DESIGN.md](BENCHMARK_DESIGN.md)
- 当前研究：[CURRENT_RESEARCH.md](CURRENT_RESEARCH.md)
- 实验清单：[EXPERIMENTS.md](EXPERIMENTS.md)
- 运行手册：[SERVER_RUNBOOK_PYTHON150.md](SERVER_RUNBOOK_PYTHON150.md)
- 报告索引：[REPORTS_INDEX.md](REPORTS_INDEX.md)
