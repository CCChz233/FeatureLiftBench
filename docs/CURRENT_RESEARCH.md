# 当前研究入口

更新时间：2026-07-23

这是论文创新、当前实验结果和下一轮实验的**唯一入口**。原始运行、审计材料和历史 sprint 仍保留，但日常讨论不再从那些目录逐个查找。

## 一句话结论

FeatureLiftBench 当前最有潜力的论文创新是 **Budgeted Executable Closure State Machine（Budgeted ECSM）**：把功能解耦建模为 obligation–artifact–evidence 的闭包过程，用可执行证据、freshness/invalidation 和单位 token 的 hidden-risk reduction 决定 expand、probe、prune 与 stop。

2026-07-23 修订的 [Repository Semantic Graph Final Design v1.1](research_analysis/REPOSITORY_SEMANTIC_GRAPH_DESIGN.md) 是 ECSM 的可插拔仓库数据与工具层：静态骨架解决候选依赖，task/submission overlay 解决闭包对照，evidence ledger 解决 freshness。RSG tool augmentation 与原生 ECSM enforcement 分开实验；V1 不启用跨任务长期记忆。

RSG Phase 1 离线实现已通过 checkpoint：Python-150 为 150/150 build、0 parse error、definition/import recall 100%、source-entrypoint mapping 96.73%；host/container digest 一致，exact-edge 分层 provenance 抽样为 100/100。Phase 2/3 现已接入 opt-in runner、三类 Agent、task closure、submission delta、claim/evidence/freshness 和 FeatureLiftAgent native stopping guard。详见 [Phase 1 checkpoint](../reports/repo_graph_phase1/README.md) 与 [实现计划](research_analysis/REPOSITORY_SEMANTIC_GRAPH_IMPLEMENTATION_PLAN.md)。

Phase 4 已在 2026-07-23 启动真实 OpenHands 付费门控，但 `rsg-pilot-v1-20260723-clean1` 在 2/12 cells 后停止：P3 只采用了 final `submission-check`，没有采用初始 `task-closure`。这说明 CLI 可用性不等于 Agent 采用率；当前必须先将两个操作暴露为 OpenHands 原生 tools，并通过新的 mechanism smoke，才恢复剩余 Pilot。该门控不提供 RSG 增益或退化的因果结论。

Token efficiency 应作为方法的第二目标，而不是单独的“上下文压缩”贡献。

## 当前证据

- Python 主榜：150 个 hard tasks。
- 当前分析：550 个 model-task runs，225 个 formal passes。
- Verified tokens：1,092,030,197，其中 98.65% 是 prompt。
- 63.72% tokens 消耗在最终没有 formal pass 的运行上。
- 65.27% runs 出现重复文件读取。
- 现有 OpenHands **已经有通用上下文压缩**：288/550 runs 触发 552 次 `Condensation`。

因此研究问题不是“要不要加入 summary”，而是：**带可执行证据和失效规则的状态压缩，能否优于 OpenHands 默认 `LLMSummarizingCondenser`？**

## 今天只需要读的文件

| 目的 | 文件 |
| --- | --- |
| 看当前结论和实验设计 | [`reports/token_efficiency_20260720/README.md`](../reports/token_efficiency_20260720/README.md) |
| 复现 550-run 分析 | [`reports/token_efficiency_20260720/token_efficiency_analysis.ipynb`](../reports/token_efficiency_20260720/token_efficiency_analysis.ipynb) |
| 看数据质量与结论边界 | [`reports/token_efficiency_20260720/validation.md`](../reports/token_efficiency_20260720/validation.md) |
| 看创新定位 | [`research_analysis/ICLR_INNOVATION_ROADMAP.md`](research_analysis/ICLR_INNOVATION_ROADMAP.md) |
| 看 ECSM 方法定义 | [`research_analysis/ECSM_METHOD_SPEC.md`](research_analysis/ECSM_METHOD_SPEC.md) |
| 看仓库语义骨架图设计 | [`research_analysis/REPOSITORY_SEMANTIC_GRAPH_DESIGN.md`](research_analysis/REPOSITORY_SEMANTIC_GRAPH_DESIGN.md) |
| 看仓库语义图实现路线 | [`research_analysis/REPOSITORY_SEMANTIC_GRAPH_IMPLEMENTATION_PLAN.md`](research_analysis/REPOSITORY_SEMANTIC_GRAPH_IMPLEMENTATION_PLAN.md) |
| 看 RSG Phase 1 验收 | [`reports/repo_graph_phase1/README.md`](../reports/repo_graph_phase1/README.md) |
| 看最新 RSG 付费门控 | [EXPERIMENTS.md §4.1](EXPERIMENTS.md#41-openhands-rsg-pilot-门控) |
| 看实验 arms 与范围 | [`research_analysis/EXPERIMENT_SCOPE_AND_ARM_RATIONALE.md`](research_analysis/EXPERIMENT_SCOPE_AND_ARM_RATIONALE.md) |
| 看扩展/停止门禁 | [`research_analysis/PILOT_DECISION_RULES.md`](research_analysis/PILOT_DECISION_RULES.md) |

## 两条实验线的下一步

### RSG：先恢复工具采用门

当前不继续 clean1 的剩余 10 cells。先把 `task-closure` 与
`submission-check` 注册为 OpenHands 原生 tools，运行新的真实 mechanism
smoke；只有两次必需调用均进入 query audit、freshness 正确且无 protocol /
context violation，才使用新的 experiment ID 恢复 12-run Pilot。

### ECSM：后续 resource gate

先做 16-cell resource gate，不直接启动大规模多臂实验：

| Arm | 作用 |
| --- | --- |
| Default OpenHands condenser | 当前强基线，已经具备 generic summarization |
| Tuned generic condenser | 分离“更早/更强摘要”带来的收益 |
| Executable Evidence Memory | 测试 hash、freshness、invalidation 与证据复用 |
| ECSM + Evidence Memory | 测试完整状态控制和 evidence-gain-per-token 决策 |

统一使用 4 个冻结任务、同一模型/工具/温度、3M token guard、1 seed。只有 hidden correctness 不退步且 median verified tokens 至少下降 20%，才扩展到 Pilot-10。

## 目录职责

| 目录 | 放什么 |
| --- | --- |
| `docs/` | 长期规范、当前入口和人类可读研究设计 |
| `reports/token_efficiency_20260720/` | 当前可复现分析 |
| `reports/paper_analysis/` | 冻结论文结果表、切片和案例 |
| `reports/audits/` | task lifecycle、integrity 和 repo audit |
| `reports/archive/` | 已完成 sprint 的历史快照 |
| `artifacts/research_analysis/` | 脚本生成的 JSON/CSV 审计证据 |
| `experiments/registry/` | 全部实验的统一机器索引 |
| `experiments/python/openhands/` | Python agent 原始运行，路径保持不动 |
| `experiments/ecsm_pilot/` | ECSM 机制实验配置与 runner |

## 明确不作为入口的内容

- `reports/archive/`：历史过程记录，不代表当前结论。
- `artifacts/research_analysis/`：机器证据，不适合从这里开始阅读。
- `docs/task_designs/`：逐题维护笔记，不是论文分析文档。
- `experiments/python/openhands/`：原始证据，不手工浏览；优先通过 `experiments/registry/` 和分析 notebook 使用。
