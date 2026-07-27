# 当前研究入口

**更新时间：** 2026-07-27

## 一句话

Benchmark 工程已经闭环；当前最高优先级是按 frozen Full-Repository /
No-Hint Python-150 跑正式 baseline，而不是继续改题、恢复人工审核或推进
旧方法线。

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
| P3 | 方法研究 | 在冻结 v3 子集上验证 Contract/API closure recovery |

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
| Contract/API closure recovery | 下一方法候选 |
| Repository Fact Graph 基础设施 | 保留 |
| RSG start-here/support retrieval | 降级为历史基线 |
| ECSM / 强制 task-closure 状态机 | 废弃 |
| 独立人工审核门禁 | 取消 |

废弃路线的规划文档和取消的审核包已经从当前文档树移除；原始实验结果仍保留
在 `experiments/` / `reports/`，用于复查而非指导当前路线。

## 今天只读

- [设计原则](BENCHMARK_DESIGN_PRINCIPLES.md)
- [当前状态](STATUS.md)
- [实验清单](EXPERIMENTS.md)
- [服务器运行手册](SERVER_RUNBOOK_PYTHON150.md)
- [报告索引](REPORTS_INDEX.md)
