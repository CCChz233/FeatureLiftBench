# Expert review package（专家审阅包）

**审阅角色：** FeatureLiftBench taxonomy / behavior / closure 专家（AI-assisted expert pass）  
**日期：** 2026-07-19  
**审阅者 ID：** `cursor_grok_expert_pass_20260719`

## 边界（必读）

本包是**专家质检与裁决意见文档**，用于：

- 固化 AI-assisted 标注是否站得住
- 给后续真人双盲审阅提供优先清单与争议点
- 工程 Pilot / 内部决策

**不是**论文门禁要求的「两位独立人类标注 + 第三方裁决」。  
因此：

- `formal_human_review_pending` / `formal_human_double_review_pending` **保持 true**
- **不得**把本包写成 human gold 或宣称 paper release gate 已过
- release gate 仍以 `artifacts/research_analysis/v1_1/release_gate_report.json` 为准（当前 8/13）

## 文档索引

| 文档 | 范围 | 结论摘要 |
| --- | --- | --- |
| [00_EXPERT_REVIEW_SUMMARY.md](00_EXPERT_REVIEW_SUMMARY.md) | 总裁决 | 小队列可工程采用；论文门禁仍缺真人 |
| [01_TAXONOMY_EXPERT_REVIEW.md](01_TAXONOMY_EXPERT_REVIEW.md) | 15 taxonomy AI rows | **15/15 accept**（2 条带保留意见） |
| [02_NEAR_DUPLICATE_EXPERT_REVIEW.md](02_NEAR_DUPLICATE_EXPERT_REVIEW.md) | 8 near-duplicate 簇 | **8/8 accept policy** |
| [03_PILOT10_BEHAVIOR_EXPERT_REVIEW.md](03_PILOT10_BEHAVIOR_EXPERT_REVIEW.md) | Pilot-10 behavior contracts | **10/10 engineering accept**；3 条建议加固 |
| [04_DIAGNOSTIC40_CLOSURE_EXPERT_REVIEW.md](04_DIAGNOSTIC40_CLOSURE_EXPERT_REVIEW.md) | Diagnostic-40 file closure | file scope 可用；高 file-count 题优先真人核 |

机器可读 ledger：`artifacts/research_analysis/v1_1/expert_review/expert_adjudication_ledger.json`

## 建议的真人审阅顺序（若要过 P0-1）

1. 本包标 `accept_with_reservation` / `needs_human_spotcheck` 的条目  
2. Pilot-10 behavior（本包已写逐题意见）  
3. Diagnostic-40 中 file_requirement_count ≥ 15 的题  
4. 其余 140 behavior contracts（可抽样）
