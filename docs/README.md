# Documentation Index

**FeatureLiftBench** — repository-level **feature decoupling** benchmark (not issue/patch repair).

当前主榜：**100 Python hard**（batch-0 五十题冻结 + batch-1 新增五十题）。实际数量以 `benchmark/tasks/` 为准。

---

## 我该读哪一份？

| 你想… | 读这个 |
| --- | --- |
| **第一次了解项目在测什么** | [CONCEPTS.md](CONCEPTS.md) |
| **跑实验 / 部署服务器** | [SERVER_DEPLOY.md](SERVER_DEPLOY.md) · [SETUP.md](SETUP.md) · 速查 [RUN.md](../RUN.md) |
| **Docker / 安全边界 / 验收** | [SECURITY_HARDENING_TODO.md](SECURITY_HARDENING_TODO.md) · [SECURITY_ACCEPTANCE.md](SECURITY_ACCEPTANCE.md) |
| **写论文 / 复现指标与流程** | [BENCHMARK_SPEC.md](BENCHMARK_SPEC.md) · [PAPER_OUTLINE.md](PAPER_OUTLINE.md) |
| **用 OpenHands 跑 benchmark / 上服务器** | [OPENHANDS_SERVER_RUNBOOK.md](OPENHANDS_SERVER_RUNBOOK.md) · [OPENHANDS_RUN_PITFALLS.md](OPENHANDS_RUN_PITFALLS.md) · [OPENHANDS_BENCHMARK_TODO.md](OPENHANDS_BENCHMARK_TODO.md) · [FEATURELIFT_AGENT_DESIGN.md](FEATURELIFT_AGENT_DESIGN.md) · [FEATURELIFT_AGENT_TODO.md](FEATURELIFT_AGENT_TODO.md) |
| **加题、扩到 100** | [BATCH1_PLAYBOOK.md](../BATCH1_PLAYBOOK.md)（七步执行标准）· [BATCH1_REPO_SELECTION.md](BATCH1_REPO_SELECTION.md)（仓库池）· [BATCH1_QUALITY_RUBRIC.md](BATCH1_QUALITY_RUBRIC.md)（质量评审）· [EXPANSION.md](EXPANSION.md) · 台账 [candidate_backlog.md](candidate_backlog.md) |
| **规划 Go v2 benchmark** | [GO_FEATURELIFTBENCH_DESIGN.md](../GO_FEATURELIFTBENCH_DESIGN.md)（总体设计）· [GO_V2_MINI_SPEC.md](GO_V2_MINI_SPEC.md)（任务/eval 契约）· [GO_PILOT_PLAYBOOK.md](GO_PILOT_PLAYBOOK.md)（5 题 pilot 执行）· 模板 [go_task_designs/TEMPLATE.md](go_task_designs/TEMPLATE.md) |
| **单题文件长什么样** | [TASK_FORMAT.md](TASK_FORMAT.md) · 笔记 [task_designs/TEMPLATE.md](task_designs/TEMPLATE.md) |
| **查题目列表与 CLI** | [benchmark_tasks.md](benchmark_tasks.md) |
| **看 baseline、缺口、优先级** | [BENCHMARK_STATUS.md](BENCHMARK_STATUS.md) |
| **看已跑实验数字** | [EXPERIMENT_RESULTS.md](EXPERIMENT_RESULTS.md) |
| **已知 bug / 局限** | [limitations.md](limitations.md) |
| **仓库目录与 harness** | [ARCHITECTURE.md](ARCHITECTURE.md) |

工程 backlog（非文档导航）：根目录 [TODO.md](../TODO.md) · 扩题执行 [BATCH1_PLAYBOOK.md](../BATCH1_PLAYBOOK.md)。

---

## 文档分层（避免重复读）

```text
概念层     CONCEPTS          测什么、怎么评分（人读）
契约层     BENCHMARK_SPEC    复现协议、指标、论文口径
格式层     TASK_FORMAT       metadata + 目录（出题用）
运营层     SETUP + RUN + SERVER_DEPLOY   环境、跑 suite、服务器清单
Agent层    OPENHANDS_SERVER_RUNBOOK + OPENHANDS_BENCHMARK_TODO + FEATURELIFT_AGENT_DESIGN + FEATURELIFT_AGENT_TODO      OpenHands 主测 agent、服务器执行、上下文审计、FeatureLiftAgent 对照协议
安全层     SECURITY_*        Docker eval/agent 边界与验收
数据层     benchmark_tasks   题目清单
状态层     BENCHMARK_STATUS  baseline + 待办优先级
实验层     EXPERIMENT_RESULTS  run 结果表
扩题层     BATCH1_PLAYBOOK + BATCH1_REPO_SELECTION + BATCH1_QUALITY_RUBRIC + EXPANSION   50→100 执行 + 仓库池 + 质量评审 + 政策
Go v2层    GO_FEATURELIFTBENCH_DESIGN + GO_V2_MINI_SPEC + GO_PILOT_PLAYBOOK + go_task_designs/TEMPLATE   Go 方向设计 + pilot 契约 + 5 题执行 + 单题模板
参考层     ARCHITECTURE      目录与脚本
缺陷层     limitations
```

**不要**把 `BENCHMARK_STATUS` 和 `EXPERIMENT_RESULTS` 当入门文档；**不要**把 `task_designs/*.md`（50+ 单题笔记）当导航入口。

---

## `task_designs/` 目录

每道正式题的**人类设计笔记**（可 speculative）。机器规范以 [TASK_FORMAT.md](TASK_FORMAT.md) 为准。新题用 [TEMPLATE.md](task_designs/TEMPLATE.md)。
