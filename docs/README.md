# Documentation Index

**FeatureLiftBench** — repository-level **feature decoupling** benchmark (not issue/patch repair).

当前主榜：**100 Python hard**（batch-0 五十题冻结 + batch-1 新增五十题）。实际数量以 `benchmark/tasks/` 为准。

---

## 我该读哪一份？

| 你想… | 读这个 |
| --- | --- |
| **第一次了解项目在测什么** | [CONCEPTS.md](CONCEPTS.md) |
| **跑实验 / 部署服务器** | [SERVER_DEPLOY.md](SERVER_DEPLOY.md) · [SETUP.md](SETUP.md) · 速查 [RUN.md](../RUN.md) |
| **Windows 本机跑实验** | [WINDOWS.md](WINDOWS.md)（WSL + Docker Desktop） |
| **长跑中断续跑** | [RUN.md §4](../RUN.md#4-续跑完整主榜) · [BENCHMARK_STATUS.md §续跑](BENCHMARK_STATUS.md#续跑与失败重试) |
| **Docker / 安全边界 / 验收** | [SECURITY_HARDENING_TODO.md](SECURITY_HARDENING_TODO.md) · [SECURITY_ACCEPTANCE.md](SECURITY_ACCEPTANCE.md) |
| **写论文 / 复现指标与流程** | [BENCHMARK_SPEC.md](BENCHMARK_SPEC.md) |
| **Python 加题（batch-1，已满 100）** | [BATCH1_PLAYBOOK.md](../BATCH1_PLAYBOOK.md) · [BATCH1_REPO_SELECTION.md](BATCH1_REPO_SELECTION.md) · [BATCH1_QUALITY_RUBRIC.md](BATCH1_QUALITY_RUBRIC.md) · [EXPANSION.md](EXPANSION.md) · [candidate_backlog.md](candidate_backlog.md) |
| **Go track（10 gold → 100）** | [GO_BENCHMARK_TODO.md](GO_BENCHMARK_TODO.md) · [GO_EXPANSION.md](GO_EXPANSION.md) · [GO_PILOT_PLAYBOOK.md](GO_PILOT_PLAYBOOK.md) · [GO_EXPERIMENT_PROTOCOL.md](GO_EXPERIMENT_PROTOCOL.md) · [GO_HARNESS_PLAN.md](GO_HARNESS_PLAN.md) · [GO_TASK_FORMAT.md](GO_TASK_FORMAT.md) · [GO_QUALITY_RUBRIC.md](GO_QUALITY_RUBRIC.md) · [GO_REPO_SELECTION.md](GO_REPO_SELECTION.md) · [go_candidate_backlog.md](go_candidate_backlog.md) |
| **单题文件长什么样** | Python：[TASK_FORMAT.md](TASK_FORMAT.md) · [task_designs/TEMPLATE.md](task_designs/TEMPLATE.md) · Go：[GO_TASK_FORMAT.md](GO_TASK_FORMAT.md) · [go_task_designs/TEMPLATE.md](go_task_designs/TEMPLATE.md) |
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
安全层     SECURITY_*        Docker eval/agent 边界与验收
数据层     benchmark_tasks   题目清单
状态层     BENCHMARK_STATUS  baseline + 待办优先级
实验层     EXPERIMENT_RESULTS  run 结果表
扩题层     Python: BATCH1_* + EXPANSION (100 hard)  |  Go: GO_* + go_candidate_backlog (10 gold → 100)
参考层     ARCHITECTURE      目录与脚本
缺陷层     limitations
```

**不要**把 `BENCHMARK_STATUS` 和 `EXPERIMENT_RESULTS` 当入门文档；**不要**把 `task_designs/*.md`（50+ 单题笔记）当导航入口。

---

## `task_designs/` 与 `go_task_designs/` 目录

每道正式题的**人类设计笔记**（可 speculative）。机器规范：Python [TASK_FORMAT.md](TASK_FORMAT.md)、Go [GO_TASK_FORMAT.md](GO_TASK_FORMAT.md)。新题模板见各目录 `TEMPLATE.md`。

Go 正式题目录：`benchmark/go/tasks/`（**10 目录 / 3 真 gold**，见 [go_pilot_acceptance_report.md](go_pilot_acceptance_report.md)）。Agent 实验：`experiments/go-openhands/`（[GO_EXPERIMENT_PROTOCOL.md](GO_EXPERIMENT_PROTOCOL.md)）。
