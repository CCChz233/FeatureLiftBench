# Reports

本目录保存小型、可复查的审计和分析结果。当前数字以
[`docs/STATUS.md`](../docs/STATUS.md) 为准，完整索引见
[`docs/REPORTS_INDEX.md`](../docs/REPORTS_INDEX.md)。

## 当前 v3

| Path | Role |
| --- | --- |
| [`audits/v3_main_readiness.md`](audits/v3_main_readiness.md) | External Python-150 严格准入 |
| [`audits/v3_oracle_revalidation/`](audits/v3_oracle_revalidation/) | 450/450 Docker Oracle 稳定性 |
| [`audits/v3_adversarial_canaries.json`](audits/v3_adversarial_canaries.json) | 12/12 对抗性隔离与 compactness canaries |
| [`audits/task_lifecycle_report.md`](audits/task_lifecycle_report.md) | task lifecycle |

v3 模型 baseline 尚未产生。v2 审计与 freeze 保留为不可变历史 provenance。

## 历史结果

| Path | Boundary |
| --- | --- |
| [`python150_compliant_20260726/`](python150_compliant_20260726/) | mixed-snapshot v1 四模型 candidate |
| [`paper_analysis/`](paper_analysis/) | 2026-07-12 v1 run set 的生成分析 |
| [`failure_attribution_20260720/`](failure_attribution_20260720/) | v1/mixed trajectory failure analysis |
| [`token_efficiency_20260720/`](token_efficiency_20260720/) | v1/mixed token/process analysis |
| [`repo_graph_phase1/`](repo_graph_phase1/) | RSG infrastructure evidence |
| [`repo_graph_phase2/`](repo_graph_phase2/) | RSG smoke/A-B evidence |
| [`repo_graph_phase3/`](repo_graph_phase3/) | RSG prototype evidence |
| [`archive/`](archive/) | batch construction and old freeze provenance |

历史报告不得重新命名或拼接成 Full-Repository / No-Hint v3 结果。
