# 文档索引

**以 [RUN.md](../RUN.md) 跑实验，以 [ARCHITECTURE.md](ARCHITECTURE.md) 理解实现。** 两篇冲突时以它们为准。

## 当前必读

| 需求 | 文档 |
|------|------|
| 跑 OpenHands 实验 | [../RUN.md](../RUN.md) |
| 项目如何实现 | [ARCHITECTURE.md](ARCHITECTURE.md) |
| 项目概述 | [../README.md](../README.md) |
| 环境 / 系统要求 | [SETUP.md](SETUP.md) |
| Benchmark 测什么 | [CONCEPTS.md](CONCEPTS.md) |
| 评测契约 | [BENCHMARK_SPEC.md](BENCHMARK_SPEC.md) |
| 单题格式 | [TASK_FORMAT.md](TASK_FORMAT.md) |
| 题目列表 | [benchmark_tasks.md](benchmark_tasks.md) |
| 排错 | [OPENHANDS_RUN_PITFALLS.md](OPENHANDS_RUN_PITFALLS.md) |
| 局限 | [limitations.md](limitations.md) |

## 实验主线（一句话）

```text
flb.local.toml → featureliftbench → OpenHands (agent Docker) → submission → eval Docker → suite.json
```

## 已合并 / 仅作跳转

下列文档已并入 [RUN.md](../RUN.md)，保留文件只为旧链接：

- [OPENHANDS_SERVER_RUNBOOK.md](OPENHANDS_SERVER_RUNBOOK.md)
- [SERVER_DEPLOY.md](SERVER_DEPLOY.md)

## 参考（非日常跑题）

| 文档 | 说明 |
|------|------|
| [OPENHANDS_BENCHMARK_TODO.md](OPENHANDS_BENCHMARK_TODO.md) | OpenHands 加固待办 |
| [EXPERIMENT_RESULTS.md](EXPERIMENT_RESULTS.md) | 历史 mini/vLLM 结果 |
| [BENCHMARK_STATUS.md](BENCHMARK_STATUS.md) | 旧状态笔记 |
| [FEATURELIFT_AGENT_DESIGN.md](FEATURELIFT_AGENT_DESIGN.md) | 仓内 control scaffold |

## 出题 / 数据集

| 文档 | 用途 |
|------|------|
| [../BATCH1_PLAYBOOK.md](../BATCH1_PLAYBOOK.md) | Batch-1 出题流程 |
| [EXPANSION.md](EXPANSION.md) | 50→100 扩展 |
| [docs/task_designs/](task_designs/) | 单题设计笔记（非机器真相源） |

## Go 探索（非 Python 主线）

[GO_FEATURELIFTBENCH_DESIGN.md](../GO_FEATURELIFTBENCH_DESIGN.md)、[GO_PILOT_PLAYBOOK.md](GO_PILOT_PLAYBOOK.md)
