# Historical v1 paper analysis

> Historical `mixed_snapshot_v1` output generated from the 2026-07-12 run set.
> It is not the v2 paper analysis directory and must not be refreshed as though
> it represented Full-Repository / No-Hint results.

Frozen run provenance:
[`reports/archive/v1_mixed_snapshot_runs_20260712.md`](../archive/v1_mixed_snapshot_runs_20260712.md).

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

- **Core-100** leaderboard：四模型共享历史子集。
- **Python-150** full split：Flash 完整 150 题结果需合并 core-100 与 hard50 extension waves。
- 当前 benchmark 规模与 Oracle 状态：[docs/STATUS.md](../../docs/STATUS.md)
