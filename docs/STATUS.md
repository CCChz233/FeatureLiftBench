# FeatureLiftBench 当前状态

**最后更新：** 2026-07-19

本文是手写状态摘要。详细 gate 表格由脚本生成，见 [research_analysis/V11_IMPLEMENTATION_STATUS.md](research_analysis/V11_IMPLEMENTATION_STATUS.md)（`python tools/research_analysis/build_v11_audit_status.py`）。

## Benchmark 规模

| Split | 位置 | 数量 | 说明 |
| --- | --- | ---: | --- |
| Python main | `benchmark/tasks/` | **150 hard** | core-100 + hard50（batch3） |
| Python smoke | `benchmark/sanity/` | **3** | harness smoke |
| Go calibration | `benchmark/go/` | seed / pilot | 非 paper-ready main |

- 唯一 source 数（Python main）：**121**
- 难度 metadata：全部 `hard`

完整 task ID 列表：[python/02_python_repo_task_inventory.md](python/02_python_repo_task_inventory.md)

## Oracle / Evaluator

| 项 | 状态 |
| --- | --- |
| 当前 freeze ID | `5f9012f6dc748c90` |
| Full revalidation | **450/450** runs（150 tasks × 3） |
| Stable pass | **150/150** |
| Active quarantine | **0** |
| Quarantine ledger | `benchmark/quarantine/python_v1_1_revision_3.json` |
| Freeze 指针 | `artifacts/research_analysis/v1_1/current_oracle_freeze.json` |
| Oracle 报告 | [research_analysis/ORACLE_REVALIDATION_REPORT.md](research_analysis/ORACLE_REVALIDATION_REPORT.md) |

Engineering 实验（reference / Docker eval）可在 Oracle 稳定后运行；aggregate 计分应使用当前 main split 与 freeze 口径。

## v1.1 论文门禁（摘要）

| 区域 | 状态 |
| --- | --- |
| Behavior contracts（映射完整） | 150/150 mapped；**独立人工 gold：0/150** |
| Diagnostic-40 closure | file scope 40/40（AI-assisted）；**独立裁决：0/40** |
| Taxonomy | 15 rows 仍待人工 adjudication |
| Paper release gates | **8/13** — `paper_release_ready: false` |
| Engineering Pilot freeze | revision 5 / `c94764ed110992a6` |
| Pilot Stage A 执行 | 0/14 cells（待外部导出授权） |

下一步执行清单：[research_analysis/NEXT_WEEK_ACTIONS.md](research_analysis/NEXT_WEEK_ACTIONS.md)

### 专家审阅包（2026-07-19）

工程质检文档已写入 [research_analysis/expert_review/](research_analysis/expert_review/)：taxonomy 15、近重复 8、Pilot-10 behavior、Diagnostic-40 均已给出专家裁决意见。  
**这不替代**独立人工双审；`paper_release_ready` 仍为 false。

## 实验与复现

- 运行命令：根目录 [RUN.md](../RUN.md)
- 协议：[04_experiment_protocol.md](04_experiment_protocol.md)
- 冻结 formal runs / leaderboard：[paper_runs_frozen.md](paper_runs_frozen.md)

## 历史里程碑

| 阶段 | 内容 | 文档 |
| --- | --- | --- |
| batch-0 | 50 hard grandfather | [07_incremental_task_rules.md](07_incremental_task_rules.md) |
| batch-1 | +50 → 100 hard | [../BATCH1_PLAYBOOK.md](../BATCH1_PLAYBOOK.md)（归档） |
| batch-3 | +50 → 150 hard | [../reports/python_hard_batch3_sprint_summary.md](../reports/python_hard_batch3_sprint_summary.md) |
| v1.1 repair | 13 quarantine → 0 | [research_analysis/ORACLE_REVALIDATION_REPORT.md](research_analysis/ORACLE_REVALIDATION_REPORT.md) |
