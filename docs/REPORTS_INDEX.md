# Reports index（可提交版）

`reports/` 目录在 `.gitignore` 中（本地生成物）。本文件是**可进 git 的索引**，指向本地 `reports/` 路径与 docs 内权威文档。

数字型当前状态以 [STATUS.md](STATUS.md) 为准，不以 sprint 报告为准。

## 规格宪法（2026-07-24）

| 本地路径 | 内容 |
| --- | --- |
| `reports/constitution/spec_compliance_150_20260724.csv` | 主榜 `spec_status` 分列（150 compliant / 0 legacy） |
| `reports/constitution/pilot_rejudgement_20260724.md` | 试点三题 hidden failure 重判 |
| `reports/constitution/hard50_migration_20260724.md` | hard-50 宪法迁移、审核来源与 Oracle 复验 |
| `reports/constitution/compliant150_migration_20260724.md` | Python-150 全量工程合规验收 |
| `reports/audits/new_protocol_readiness.md` | Test-blind 新协议内容就绪度与逐题修订队列 |
| `experiments/ablation/hard50-compliant-deepseek-v4-flash-20260724/paired-analysis.md` | compliant hard-50 可见性配对；旧 Main=现 Public-feedback，旧 No-public=现 test-blind Main |
| [CONSTITUTION_MIGRATION.md](CONSTITUTION_MIGRATION.md) | 迁移 CLI 与 rebaseline 手册 |

## 当前分析

| 本地路径 | 内容 |
| --- | --- |
| `reports/token_efficiency_20260720/README.md` | 550-run token / 过程分析（历史文中或仍提 ECSM，以 [CURRENT_RESEARCH.md](CURRENT_RESEARCH.md) 为准） |
| `reports/token_efficiency_20260720/token_efficiency_analysis.ipynb` | 550-run 可复现分析 |
| `reports/token_efficiency_20260720/validation.md` | 数据质量、spot checks 与结论边界 |

## RSG mechanism evidence

| 路径 | 内容 |
| --- | --- |
| `experiments/rsg_pilot/openhands/deepseek-v4-flash/rsg-pilot-v1-20260723-clean1/` | 干净的 2-cell P0/P3 付费采用门控；因缺 `task-closure` 停止 |
| `experiments/rsg_pilot/openhands/deepseek-v4-flash/rsg-pilot-v1-20260723/` | 控制器错误审计目录；已 invalidated，不进入分析 |

当前还没有正式「可选通用 RSG 工具」效果报告。上述 clean1 证据只支持「旧强制采用门 fragile」的历史诊断，不支持效果归因。

## Paper analysis（本地 `reports/paper_analysis/`）

| 本地路径 | 内容 |
| --- | --- |
| `reports/paper_analysis/executive_summary.md` | 一页结果摘要 |
| `reports/paper_analysis/rq1_main_table.md` | RQ1 主表 |
| `reports/paper_analysis/failure_taxonomy*.json/csv` | 失败分布 |
| `reports/paper_analysis/rq4_compactness.json` | Compactness |
| `reports/paper_analysis/rq5_slices.json` | 切片通过率 |
| `reports/paper_analysis/case_studies/` | 案例 |
| `reports/paper_analysis/formal-runs-summary.json` | 正式 run 汇总 |

规范口径与冻结 run：[paper_runs_frozen.md](paper_runs_frozen.md) · 表草稿：[paper_tables.md](paper_tables.md) · 实验清单：[EXPERIMENTS.md](EXPERIMENTS.md)

重建：

```bash
PYTHONPATH=harness .venv/bin/python harness/scripts/generate_paper_analysis.py
```

## Batch-3 sprint 归档（本地 `reports/archive/batch3_202607/`）

| 本地路径 | 角色 |
| --- | --- |
| `reports/archive/batch3_202607/python_hard_batch3_sprint_summary.md` | 100→150 摘要（历史） |
| `reports/archive/batch3_202607/python_hard_batch3_plan.md` | 计划 |
| `reports/archive/batch3_202607/python_hard_batch3_pilot.md` | Pilot |
| `reports/archive/batch3_202607/python_hard_batch3_materialization.md` | 材料化 |
| `reports/archive/batch3_202607/python_hard_batch3_eval_verification.md` | Eval 验证 |
| `reports/archive/batch3_202607/batch3_promotion_readiness.md` | Promote 门禁快照 |
| `reports/archive/batch3_202607/batch3_next_stage_implementation_20260708.md` | 下一阶段笔记 |

## Task audit / lifecycle（本地 `reports/audits/`）

| 本地路径 | 角色 |
| --- | --- |
| `reports/audits/python_task_audit.md` | Task audit |
| `reports/audits/task_lifecycle_report.md` | Lifecycle |
| `reports/audits/missing_high_value_repos.md` | Repo 缺口 |
| `reports/audits/benchmark_integrity_audit/` | Integrity |

## Related tracked docs

| Doc | Role |
| --- | --- |
| [research_analysis/TRAJECTORY_FINDINGS.md](research_analysis/TRAJECTORY_FINDINGS.md) | 轨迹分析（tracked） |
| [research_analysis/BENCHMARK_TAXONOMY_REPORT.md](research_analysis/BENCHMARK_TAXONOMY_REPORT.md) | 题集 taxonomy |
| [research_analysis/expert_review/](research_analysis/expert_review/) | 专家审阅包 |
| [EXPERIMENTS.md](EXPERIMENTS.md) | 实验完成度与缺口 |
