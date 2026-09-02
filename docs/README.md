# FeatureLiftBench 文档入口

> **Status: current · Last verified: 2026-09-02**

日常只从这里进入。**数字只看 [STATUS.md](STATUS.md)**，方法结论只看
[FINDINGS.md](FINDINGS.md)。论文主套件是冻结 Python-150 + Hard-50（Python-200′）。

## 权威

| 需要 | 文档 |
| --- | --- |
| 规模、freeze、可用结果、blocker | [STATUS.md](STATUS.md) |
| 方法结论 | [FINDINGS.md](FINDINGS.md) |
| Main 条件、指标、正式实验臂 | [EVALUATION.md](EVALUATION.md) |
| 出题规则 | [TASK_DESIGN_RULES.md](TASK_DESIGN_RULES.md) |
| 题目验证 / 三态打标（筛题暂停） | [BENCHMARK_VALIDATION_GATE.md](BENCHMARK_VALIDATION_GATE.md) |
| 失败分析与人工标注 | [FAILURE_ANALYSIS_PROTOCOL.md](FAILURE_ANALYSIS_PROTOCOL.md) |
| 当前 cost arm：V1 = Main + 2M | [METHOD_V1.md](METHOD_V1.md) |
| 构念 | [BENCHMARK_DESIGN.md](BENCHMARK_DESIGN.md) |
| source / freeze 政策 | [BENCHMARK_DESIGN_PRINCIPLES.md](BENCHMARK_DESIGN_PRINCIPLES.md) · [FULL_REPOSITORY_SOURCE_POLICY.md](FULL_REPOSITORY_SOURCE_POLICY.md) |

## 运行

| 需要 | 文档 |
| --- | --- |
| 本地跑实验 | [RUN.md](../RUN.md) |
| 服务器跑 Python-200′ | [SERVER_RUNBOOK_PYTHON200.md](SERVER_RUNBOOK_PYTHON200.md) |
| 可选 DeepSeek Harness / Codex | [METHOD_AGENT_RUNTIME.md](METHOD_AGENT_RUNTIME.md) |
| 脚本哪些能用 | [scripts/README.md](../scripts/README.md) |
| 仓库结构 | [benchmark/](../benchmark/README.md) · [agent/](../agent/README.md) · [method/](../method/README.md) · [harness/](../harness/README.md) |
| 整理仓库 | [REPOSITORY_MAINTENANCE.md](REPOSITORY_MAINTENANCE.md) |

正式入口只有 `./scripts/run_benchmark.sh`（或 `featureliftbench` CLI）。
`--benchmark python200_hard`。不要用 `run_python200_paper.sh` 写新主表。

## 论文与参考

| 需要 | 文档 |
| --- | --- |
| 论文稿 | [paper/](paper/README.md) |
| schema、生命周期、Go/Python 轨道 | [reference/](reference/README.md) · [06_task_schema.md](reference/06_task_schema.md) · [07_incremental_task_rules.md](reference/07_incremental_task_rules.md) |
| 已停方法、完成的计划、组会稿 | [archive/](archive/README.md) |

`HIDDEN_CONTRACT_PROVENANCE.md` 仍留在本目录：freeze 钉住了这个路径，不要改内容。
它不是活的审计入口；可复跑检查见 [BENCHMARK_VALIDATION_GATE.md](BENCHMARK_VALIDATION_GATE.md)。

写完文档后运行：

```bash
python3.12 scripts/check_docs.py --warnings-as-errors
```
