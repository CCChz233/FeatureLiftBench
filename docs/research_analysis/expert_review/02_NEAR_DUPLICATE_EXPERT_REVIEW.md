# Near-duplicate expert review — 8 clusters

**Reviewer:** `cursor_grok_expert_pass_20260719`  
**Source:** `artifacts/research_analysis/v1_1/near_duplicate_review_queue.csv`  
**Rule:** Jaccard / same-source 仅是 warning；语义关系与 main-stat 政策才是裁决对象。

Overall: **8/8 accept** 既有 `semantic_relation` 与 `main_stat_policy`。

---

## Cluster adjudications

### 1. `coveragepy / config_resolve_discover` — **accept**

- **Tasks:** config_merge · glob_matcher · path_remap · source_selection
- **Relation:** 共享路径/配置词汇，但入口与行为契约不同（merge vs glob vs alias remap vs source 选择）。
- **Policy:** retain + source-group macro + cluster-collapsed sensitivity — **同意**。
- **Note:** 与 taxonomy 中 glob/path 两条 override 一致；不要物理删题。

### 2. `jinja2 / serialize_format_render` — **accept**

- **Tasks:** compile_render · filters_tests
- **Relation:** 部分嵌套（filter/test 依赖 Environment 子集）。
- **Policy:** retain diagnostic；independence sensitivity 可 collapse — **同意**。
- **Note:** filters_tests 的 secondary=`registry_plugin_dispatch` 解释了重叠来源。

### 3. `pluggy / registry_plugin_dispatch` — **accept**

- **Tasks:** hook_call_order · hook_specs · hook_wrapper(hard3)
- **Relation:** 同 hook 引擎上的分层变体；specs/wrapper 与 call-order 有包含关系。
- **Policy:** retain + source-group cluster + sensitivity collapse — **同意**。
- **Note:** Pilot-10 含 `hook_specs`；报告时应声明同源簇。

### 4. `pydantic / validate_normalize_construct` — **accept**

- **Tasks:** pydantic field_validator(hard3) · pydantic_v1 validation_error
- **Relation:** 概念相关，**主版本 API 与契约不等价**。
- **Policy:** retain；按 source-group 并报告 version/API 区分 — **同意**。
- **Note:** 这是「相关」不是「近重复」。

### 5. `pytest / registry_plugin_dispatch` — **accept**

- **Tasks:** fixture_resolve · marker_registry(hard3)
- **Relation:** 同仓不同子系统（fixture 闭包 vs marker 注册）。
- **Policy:** retain + source-group uncertainty — **同意**。

### 6. `sqlparse / parse_tokenize_decode` — **accept**

- **Tasks:** parse_format · parse_split · token_tree
- **Relation:** 层级重叠；split/token_tree 更接近 parse_format 的子集表面。
- **Policy:** retain task-level；independence sensitivity 选一代表 — **同意**。
- **Note:** Pilot-10 用的是 `format_filters`（不在此簇），报告时勿混用簇名。

### 7. `vibe_app / workflow_session_orchestration` — **accept**

- **Tasks:** csv_transform · session_registry
- **Relation:** **粗粒度 family 假阳性**；入口与行为无共享。
- **Policy:** retain；source-group macro 防 curated 过权 — **同意**。
- **Expert emphasis:** 应在论文方法节写明「same family ≠ duplicate」。

### 8. `vibe_app / cache_retry_policy` — **accept**

- **Tasks:** pricing_rules · rules_engine
- **Relation:** 假阳性；定价计算 vs 通用规则引擎。
- **Policy:** retain + source-group macro — **同意**。

---

## Reporting guidance (for paper / tables)

1. Primary tables：保留全部 task-level 结果。  
2. Uncertainty：对簇 1–3、6 报告 source-group / collapsed sensitivity。  
3. 明确标注簇 7–8 为 warning-only 假阳性，避免被审稿人误读为「未处理重复」。  
4. 不要因近重复 warning 删除主榜题目。

## Decision table

| Cluster | Expert | Formal human pending |
| --- | --- | --- |
| coveragepy / config_resolve_discover | accept | yes |
| jinja2 / serialize_format_render | accept | yes |
| pluggy / registry_plugin_dispatch | accept | yes |
| pydantic / validate_normalize_construct | accept | yes |
| pytest / registry_plugin_dispatch | accept | yes |
| sqlparse / parse_tokenize_decode | accept | yes |
| vibe_app / workflow_session_orchestration | accept | yes |
| vibe_app / cache_retry_policy | accept | yes |
