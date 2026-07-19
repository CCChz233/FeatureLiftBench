# Reports index（可提交版）

`reports/` 目录在 `.gitignore` 中（本地生成物）。本文件是**可进 git 的索引**，指向本地 `reports/` 路径与 docs 内权威文档。

数字型当前状态以 [STATUS.md](STATUS.md) 为准，不以 sprint 报告为准。

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

## Batch-3 sprint（本地 `reports/`）

| 本地路径 | 角色 |
| --- | --- |
| `reports/python_hard_batch3_sprint_summary.md` | 100→150 摘要（历史） |
| `reports/python_hard_batch3_plan.md` | 计划 |
| `reports/python_hard_batch3_pilot.md` | Pilot |
| `reports/python_hard_batch3_materialization.md` | 材料化 |
| `reports/python_hard_batch3_eval_verification.md` | Eval 验证 |
| `reports/batch3_promotion_readiness.md` | Promote 门禁快照 |
| `reports/batch3_next_stage_implementation_20260708.md` | 下一阶段笔记 |

## Task audit / lifecycle（本地）

| 本地路径 | 角色 |
| --- | --- |
| `reports/python_task_audit.md` | Task audit |
| `reports/task_lifecycle_report.md` | Lifecycle |
| `reports/missing_high_value_repos.md` | Repo 缺口 |
| `reports/benchmark_integrity_audit/` | Integrity |

## Related tracked docs

| Doc | Role |
| --- | --- |
| [research_analysis/TRAJECTORY_FINDINGS.md](research_analysis/TRAJECTORY_FINDINGS.md) | 轨迹分析（tracked） |
| [research_analysis/BENCHMARK_TAXONOMY_REPORT.md](research_analysis/BENCHMARK_TAXONOMY_REPORT.md) | 题集 taxonomy |
| [research_analysis/expert_review/](research_analysis/expert_review/) | 专家审阅包 |
| [EXPERIMENTS.md](EXPERIMENTS.md) | 实验完成度与缺口 |
