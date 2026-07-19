# Expert review summary — 2026-07-19

## Verdict

| Queue | Expert decision | Paper human gate |
| --- | --- | --- |
| Taxonomy AI-assisted 15 | **Accept all 15** (2 with reservation notes) | Still pending |
| Near-duplicate 8 clusters | **Accept all 8 policies** | Still pending |
| Pilot-10 behavior contracts | **Engineering accept 10/10** | Still pending |
| Diagnostic-40 file closure | **File-scope usable**; spot-check high-count tasks | Still pending |

**工程含义：** 当前 AI-assisted 标注质量足够支撑 engineering Pilot 与内部分析；小队列争议可控。  
**论文含义：** 本 pass **不改变** `paper_release_ready`；仍需真人双审。

## Evidence used

Allowed for this expert pass (aligned with taxonomy / contract policy):

- `TASK.md`, `metadata.json`
- `evaluation/behavior_contract.json`（公开条款与映射计数；不反向从 hidden 样例发明公开条款）
- `evaluation/closure_gold.json` / oracle manifest（Diagnostic-40）
- `artifacts/research_analysis/python150_task_taxonomy.csv`
- prior AI ledgers under `artifacts/research_analysis/v1_1/`

Not used as classification evidence: agent trajectories, pass rates, extraction ratios.

## High-priority human spot-checks

1. **Taxonomy reservation**
   - `coverage__glob_matcher_core__001` — `feature_family_primary=config_resolve_discover` vs 更偏 glob/algorithm 的争议
   - `jinja2__filters_tests_core__001` — primary/secondary 与 `has_framework_lifecycle` 边界
2. **Behavior clause thinness**
   - `schema__nested_validate_core__hard3_001` — 条款偏短，依赖 generic API clause
   - `sqlparse__format_filters_core__001` — 同上
   - `celery__signal_dispatch_core__hard3_001` — 条款粗，需确认 weak-ref / dispatch_uid 是否被公开条款覆盖
3. **Closure high-count**
   - `astroid__nodes_core__001` (44 files)
   - `lark__grammar_loader_core__001` (34)
   - `parso__python_parse_core__001` (26)

## What was deliberately not flipped

- No `review_status` changed to `human_reviewed`
- No release gate rebuild claiming human adjudication
- `formal_human_*_pending` remains true in source ledgers

## Next steps for maintainers

1. 真人审阅者用本包作为 worksheet，在 audit 中写入真实 reviewer IDs  
2. 对 reservation / spot-check 题做独立双盲  
3. 通过后重建 `behavior_review_audit.json` / taxonomy / release gate  
4. Workload gate 与 Pilot 授权仍是独立 P0 项
