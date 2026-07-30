# 当前研究入口

**更新时间：** 2026-07-30

## 一句话

Benchmark 工程已经闭环；正式主线仍是 v3 Full-Repository / No-Hint baseline。  
方法侧：干净 **Exec-Contract clean3** 在 alembic+click focus 两题皆 public✓（Functional 仍 0/2）；**Self-Authored Contract** 首跑闸门绿但 formal 0/2（弱于 clean3）。TD-Cognition 为负对照。  
操作：[`exec_contract_pilot`](../experiments/exec_contract_pilot/) · [`self_contract_pilot`](../experiments/self_contract_pilot/) · 故事：[METHOD_EXEC_CONTRACT.md](METHOD_EXEC_CONTRACT.md) · [METHOD_SELF_CONTRACT.md](METHOD_SELF_CONTRACT.md)。

## 当前判断

FeatureLiftBench 测量 Agent 能否在完整真实仓库和完整功能契约下，自主定位
实现、恢复 API/行为/依赖闭包，并交付独立且紧凑的功能模块。

Python-150 已满足八条核心原则：

- 150/150 完整公开契约；
- 150/150 No-Hint；
- 150/150 canonical full-repository input；
- 150/150 reference-relative compactness records；
- 450/450 Docker Oracle；
- 12/12 adversarial isolation canaries；
- source/spec/reference/evaluator/environment 已内容寻址冻结。

现有四模型结果使用 `mixed_snapshot_v1`，可以支持早期失败模式分析，但不能
回答 v3 Full-Repository / No-Hint 下的最终性能。

## 下一步

| 优先级 | 工作 | 完成标准 |
| --- | --- | --- |
| P0 | v3 baseline | 每个目标模型完整 150 题、attempt=1、freeze/image/protocol 可审计 |
| P1 | v3 结果分析 | Functional Pass@1、compactness、token、step、latency、failure taxonomy |
| P2 | 难度重校准 | 基于首轮 v3 empirical success，不把旧 hard 标签当实证结论 |
| P3 | 方法研究 | Focus 最佳干净模板臂 = **exec clean3**；self_contract focus 0/2 未增益、协议未改前不扩。TD 4/12 零翻盘 |

## Focus 方法快照（alembic + click，2026-07-30）

| Arm | alembic | click | 备注 |
| --- | --- | --- | --- |
| Main `compare-20260728-155516/main` | p✗ h✗ | p✗ h✗ | 基线 |
| **exec clean3** | **p✓ h✗** | **p✓ h✗** | 当前最佳干净模板 |
| exec clean4 | p✗ h✗ | p✓ h✗ | B006 → `"base"` 过度泛化 |
| self_contract `…-140322` | p✗ h✗ | p✗ h✗ | 闸门绿；base 泛化 + 漏 invoke |

详表：[CLEAN_FOCUS.md](../experiments/exec_contract_pilot/CLEAN_FOCUS.md) · [FOCUS_RESULTS.md](../experiments/self_contract_pilot/FOCUS_RESULTS.md)  
导出：`exports/flb-useful-focus-expts-20260730-144258.tar.gz`

## Exec-Contract 试点快照

| 项 | 状态 |
| --- | --- |
| 模型 | `deepseek/deepseek-v4-flash` |
| 12 题对照 Main | `compare-20260728-155516/main` → **4/12** |
| Focus 最佳 | `exec-contract-clean3-20260729-214504` |
| 故事 | [METHOD_EXEC_CONTRACT.md](METHOD_EXEC_CONTRACT.md) |
| 操作 | [exec_contract pilot](../experiments/exec_contract_pilot/README.md) |

## Self-Authored Contract 快照

| 项 | 状态 |
| --- | --- |
| 臂 | `--arm self_contract` |
| Focus | **0/2** Functional；[FOCUS_RESULTS.md](../experiments/self_contract_pilot/FOCUS_RESULTS.md) |
| 故事 | [METHOD_SELF_CONTRACT.md](METHOD_SELF_CONTRACT.md) |

## TD-Cognition 归档快照（2026-07-28，负对照）

| 项 | 状态 |
| --- | --- |
| 干净 TD | `td-cognition-clean-20260728-220500` → **4/12**，相对 Main **零翻盘** |
| 结论 | 自编探针易锁死错误认知；不扩。尸检动机写入 Exec-Contract 文档 §2 |
| 故事 | [METHOD_TEST_DRIVEN_COGNITION.md](METHOD_TEST_DRIVEN_COGNITION.md) |

正式默认：

```text
OpenHands
+ specified model
+ Full-Repository / No-Hint Main
+ agent Docker
+ evaluator Docker
+ Python-150
+ one attempt per task
+ evaluator Functional Pass@1
```

操作见
[SERVER_RUNBOOK_PYTHON150.md](SERVER_RUNBOOK_PYTHON150.md)。

## 论文主线

1. **Benchmark contribution**：把 feature extraction 定义为完整仓库、
   完整公开契约、No-Hint、submission 后私有评测的独立任务。
2. **Dataset contribution**：150 External Main tasks、126 external
   repositories、132 immutable snapshots，以及独立 Curated-7 split。
3. **Evaluation contribution**：Functional Pass@1 与 reference-relative
   compactness 分离，并记录 isolation、copy/dependency footprint。
4. **Empirical contribution**：比较模型在正确性、紧凑性、成本和失败机制上
   的差异。
5. **Method contribution（后置）**：验证面向 API/behavior completion 的
   closure recovery 是否改善 Main，而不是只提升文件定位。

## 现有证据的边界

历史 `mixed_snapshot_v1` 四模型 evaluator Functional Pass@1 为
87/150、56/150、49/150、37/150。它们提示：

- 强模型和弱模型存在明显区分；
- 常见失败发生在 API/行为完成、依赖/资源遗漏和 copy-heavy；
- 单纯提供定位或 RSG start-here 尚未显示稳定 hard-task 增益；
- public-feedback 与 test-blind 条件不能混报。

这些是方向性证据。完整仓库会增加 localization 和上下文负担，No-Hint 会
去掉旧 entrypoints，因此 v3 通过率、token 和失败分布必须重新测量。

## 方法状态

| 路线 | 状态 |
| --- | --- |
| Benchmark v3 工程 | 完成 |
| Contract/API closure recovery | **主候选仍是 Exec-Contract（focus 上限 = clean3）**；Self-Authored 已试点无增益。TD 负对照 |
| Repository Fact Graph 基础设施 | 保留 |
| RSG start-here/support retrieval | 降级为历史基线 |
| ECSM / 强制 task-closure 状态机 | 废弃 |
| 独立人工审核门禁 | 取消 |

废弃路线的规划文档和取消的审核包已经从当前文档树移除；原始实验结果仍保留
在 `experiments/` / `reports/`，用于复查而非指导当前路线。

## 今天只读

- [设计原则](BENCHMARK_DESIGN_PRINCIPLES.md)
- [当前状态](STATUS.md)
- [方法故事：Exec-Contract](METHOD_EXEC_CONTRACT.md)
- [方法故事：Self-Authored Contract](METHOD_SELF_CONTRACT.md)
- [Exec-Contract focus 结果](../experiments/exec_contract_pilot/CLEAN_FOCUS.md)
- [Self-Contract focus 结果](../experiments/self_contract_pilot/FOCUS_RESULTS.md)
- [TD 负对照故事](METHOD_TEST_DRIVEN_COGNITION.md)
- [实验臂](EXPERIMENT_ARMS.md)
- [实验清单](EXPERIMENTS.md)
- [服务器运行手册](SERVER_RUNBOOK_PYTHON150.md)
- [报告索引](REPORTS_INDEX.md)
