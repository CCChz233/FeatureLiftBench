# FeatureLiftBench Docs

文档入口。数字状态见 [STATUS.md](STATUS.md)；研究优先级见 [CURRENT_RESEARCH.md](CURRENT_RESEARCH.md)。

**规格迁移进度（2026-07-24）：** **150/150 engineering-compliant** · 0 legacy · 迁移后 Oracle 证据 150/150 · 手册 [CONSTITUTION_MIGRATION.md](CONSTITUTION_MIGRATION.md)

---

## 先读这四份（2026-07-24 起）

| 顺序 | 文档 | 内容 |
| --- | --- | --- |
| 1 | [BENCHMARK_DESIGN.md](BENCHMARK_DESIGN.md) | **整体思路**：测什么、信息分层、打分、方法优先级 |
| 2 | [TASK_DESIGN_RULES.md](TASK_DESIGN_RULES.md) | **规格宪法**：public_spec、API/behavior、门禁 |
| 3 | [CONSTITUTION_MIGRATION.md](CONSTITUTION_MIGRATION.md) | **迁移手册**：CLI、compliant/legacy 分报、试点 |
| 4 | [EXPERIMENT_ARMS.md](EXPERIMENT_ARMS.md) | **实验臂**：test-blind Main / Public-feedback / Short-prompt |

冲突时以以上四份 + [CURRENT_RESEARCH.md](CURRENT_RESEARCH.md) 为准。

---

## 按意图导航

| 我想… | 从这里开始 |
| --- | --- |
| 理解整个 benchmark 设计 | [BENCHMARK_DESIGN.md](BENCHMARK_DESIGN.md) |
| 迁规格 / 跑 validate | [CONSTITUTION_MIGRATION.md](CONSTITUTION_MIGRATION.md) · [TASK_DESIGN_RULES.md](TASK_DESIGN_RULES.md) |
| 做 Public-feedback 等对照 | [EXPERIMENT_ARMS.md](EXPERIMENT_ARMS.md) · [../RUN.md](../RUN.md) §1.5 |
| 看当前优先级与下一步 | [CURRENT_RESEARCH.md](CURRENT_RESEARCH.md) |
| 看规模 / Oracle / 合规计数 | [STATUS.md](STATUS.md) · `reports/constitution/spec_compliance_150_20260724.csv` |
| 跑实验 | [SERVER_RUNBOOK_COMPLIANT150.md](SERVER_RUNBOOK_COMPLIANT150.md) · [../RUN.md](../RUN.md) · [EXPERIMENTS.md](EXPERIMENTS.md) |
| 看结果解读 | [FINDINGS.md](FINDINGS.md) |
| 生命周期 / promote | [07_incremental_task_rules.md](07_incremental_task_rules.md) |
| 包布局 schema | [06_task_schema.md](06_task_schema.md) |

---

## 文档分层地图

```text
叙事与优先级
  BENCHMARK_DESIGN.md      ← 整体思路
  CURRENT_RESEARCH.md      ← 今天做什么
  STATUS.md / FINDINGS.md / EXPERIMENTS.md

出题与评测规范（权威）
  TASK_DESIGN_RULES.md     ← 宪法
  CONSTITUTION_MIGRATION.md ← 迁移操作（CLI / 分报）
  EXPERIMENT_ARMS.md       ← 实验臂
  01_task_definition.md … 07_incremental_task_rules.md

编号核心文档（部分内容可能滞后于宪法）
  00_overview … 05_failure_taxonomy, 02_RQs, 04_protocol
  → 与宪法冲突时回修并向宪法对齐

方法线（降级 / 历史）
  research_analysis/REPOSITORY_SEMANTIC_GRAPH_*   ← RSG 基线
  research_analysis/ECSM_*                       ← 已废弃
```

---

## Core Docs

| File | Purpose |
| --- | --- |
| [BENCHMARK_DESIGN.md](BENCHMARK_DESIGN.md) | 整体设计思路 |
| [TASK_DESIGN_RULES.md](TASK_DESIGN_RULES.md) | 规格宪法 |
| [CONSTITUTION_MIGRATION.md](CONSTITUTION_MIGRATION.md) | 规格迁移手册 |
| [EXPERIMENT_ARMS.md](EXPERIMENT_ARMS.md) | 实验臂 |
| [CURRENT_RESEARCH.md](CURRENT_RESEARCH.md) | 研究入口 |
| [STATUS.md](STATUS.md) | 状态摘要 |
| [SERVER_RUNBOOK_COMPLIANT150.md](SERVER_RUNBOOK_COMPLIANT150.md) | 最新 Python-150 服务器正式运行流程 |
| [06_task_schema.md](06_task_schema.md) | 任务包布局 |
| [07_incremental_task_rules.md](07_incremental_task_rules.md) | 生命周期 |
| [limitations.md](limitations.md) | 已知局限 |

## Task Design Notes

- [task_designs/](task_designs/) · [go_task_designs/](go_task_designs/) — maintainer 笔记，**不是** Agent 可见规格  
- **Compliant 题：** Agent 可见契约 = `render(public_spec)`  
- **Legacy 题：** 当前 Python main 为 0；历史 legacy runs 仍须按旧口径单独报告

## Research & Methods

| 状态 | 文档 |
| --- | --- |
| **当前主线** | Python-150 独立人工 paper-gold 审核 + compliant core-100 校准 |
| **下一方法候选** | Contract/API closure recovery（compliant 子集上验证） |
| **降级** | RSG start-here |
| **废弃** | ECSM |

## Operational

| Location | Purpose |
| --- | --- |
| [../RUN.md](../RUN.md) | 运行速查（含 `./run_experiment.sh`） |
| `harness/featureliftbench/cli.py` | validate / migrate / render / annotate |
| [../.agents/skills/](../.agents/skills/) | create / validate / promote / run-eval |

## 维护规则

1. **宪法优先**：宪法 / 迁移 / 臂 变更后，回修 `00–07` 与 STATUS。  
2. **Living status**：合规计数变时更新 STATUS + `spec_compliance.csv`。  
3. **分报**：legacy 与 compliant 实验不得混报 headline。  
4. **Historical**：旧报告不 retro-edit；加 banner 说明 legacy 口径。
