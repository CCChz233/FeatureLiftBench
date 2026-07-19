# Diagnostic-40 closure expert review

**Reviewer:** `cursor_grok_expert_pass_20260719`  
**Source audit:** `artifacts/research_analysis/v1_1/diagnostic_closure_review_audit.json`  
**Scope reviewed here:** **file-level** necessity only（symbol / runtime / minimality 仍 scope-limited，本 pass 不宣称完成）。

## Aggregate

| Metric | Value |
| --- | ---: |
| Tasks | 40 |
| File requirements | 301 |
| Unresolved task IDs | 0 |
| File-scope marked complete | 40/40 |
| Independent human adjudication | 0/40（不变） |

File-count distribution: min **1**, median **4**, max **44**.

## Expert stance

1. **Engineering usable:** file-scope 列表可作为 Pilot / mechanism analysis 的 gold *候选*。  
2. **Not paper-complete:** 缺双人独立裁决；高 file-count 题尤其需要人工确认「必要 vs 可替换」。  
3. **Selection-source 异质性：** `oracle_manifest.required_source_files` vs `static_entrypoint_import_closure` 混用 — 对分析可接受，但报告必须分层说明，避免把静态闭包膨胀当成人工精修 gold。

## Priority spot-check list（按 file_requirement_count）

| Priority | Task | Files | Selection source | Subset | Expert note |
| --- | --- | ---: | --- | --- | --- |
| P0 | astroid__nodes_core__001 | 44 | static_entrypoint_import_closure | representative20 | 静态闭包极易过宽；优先人工砍/确认 |
| P0 | lark__grammar_loader_core__001 | 34 | oracle_manifest.required_source_files | challenge20 / pilot | grammar+loader 大；核对 resource 文件是否必要 |
| P0 | parso__python_parse_core__001 | 26 | oracle_manifest.required_source_files | representative20 | parser 体量大，确认非 copy-all 伪装 |
| P1 | pydantic_settings__env_source_core__001 | 21 | static_entrypoint_import_closure | representative20 | 静态闭包风险 |
| P1 | sqlparse__format_filters_core__001 | 19 | oracle_manifest.source_files | challenge20 / pilot | source_files 列表 vs required 差异需对齐 |
| P1 | pyyaml__safe_load_dump__001 | 17 | static_entrypoint_import_closure | representative20 | |
| P1 | pydantic_v1__validation_error_core__001 | 15 | oracle_manifest.required_source_files | challenge20 / pilot | Pilot 题；与 behavior 一起看 |
| P1 | phonenumbers__parse_format_core__001 | 12 | static_entrypoint_import_closure | representative20 | |

其余 ≤10 files 的题：工程上 **accept as provisional**；真人可抽样 20%。

## Low-count tasks — accept provisional

例如 boltons / celery / diskcache / click 等 file_requirement_count≈1–2：与「窄提取」叙事一致，**不太可能**是过宽闭包；真人审阅成本低，可快速勾选。

## Closure variants / minimality

本专家 pass **不**裁定：

- symbol-level necessity  
- runtime resource necessity  
- accepted substitutes  
- minimality claims  

这些必须等 `annotation_scope` 对应字段完整且真人裁决后才能进论文。

## Decision

| Layer | Expert decision |
| --- | --- |
| File-scope completeness scaffolding | **accept provisional** |
| High-count (≥15) necessity | **needs_human_spotcheck** |
| Symbol/runtime/minimality | **out of scope** |
| Paper independent adjudication | **still pending** |
