# Paper analysis artifacts

Formal run 分析与论文表格工件。冻结 run ID 的规范来源：[docs/paper_runs_frozen.md](../../docs/paper_runs_frozen.md)。表格草稿：[docs/paper_tables.md](../../docs/paper_tables.md)。

## Key files

| File | Role |
| --- | --- |
| [executive_summary.md](executive_summary.md) | High-level summary |
| [rq1_main_table.md](rq1_main_table.md) | RQ1 main results |
| [rq1_main_table.json](rq1_main_table.json) | Machine-readable RQ1 |
| [failure_taxonomy.csv](failure_taxonomy.csv) | Failure taxonomy export |
| [case_studies/](case_studies/) | Representative case studies |
| [case_studies_index.json](case_studies_index.json) | Case study index |

## Scope notes

- **Core-100** leaderboard：四模型共享子集（见 `paper_runs_frozen.md`）。
- **Python-150** full split：Flash 完整 150 题结果需合并 core-100 与 hard50 extension waves。
- 当前 benchmark 规模与 Oracle 状态：[docs/STATUS.md](../../docs/STATUS.md)
