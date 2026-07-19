# Taxonomy expert review — 15 AI-assisted rows

**Reviewer:** `cursor_grok_expert_pass_20260719`  
**Standard:** [BENCHMARK_TAXONOMY_SPEC.md](../BENCHMARK_TAXONOMY_SPEC.md)  
**Source ledger:** `artifacts/research_analysis/v1_1/taxonomy_ai_review_ledger.json`  
**Decision codes:** `accept` | `accept_with_reservation` | `revise` | `reject`

Overall: **15/15 engineering accept**（其中 2 条 `accept_with_reservation`）。全部仍 `formal_human_review_pending=true`。

---

## Per-task adjudication

### 1. `aiohttp__url_params_core__hard3_001` — **accept**

- **Overrides:** `has_global_state=false`, `has_registry=false`
- **Evidence:** TASK 聚焦 URL query merge / CIMultiDict headers；无网络/client runtime；无 plugin registry。
- **Expert note:** module 常量 ≠ mutable global state。与 `validate_normalize_construct` + `stateless` 一致。

### 2. `alembic__revision_map_core__hard3_001` — **accept**

- **Overrides:** none
- **Evidence:** RevisionMap 图结构、heads/bases、branch labels；排除 SQLAlchemy engine / env loading。
- **Expert note:** `algorithm_data_structure` + `local_state` 正确；保留原 entanglement 多标签。

### 3. `build__pyproject_backend_core__hard3_001` — **accept**

- **Overrides:** `has_framework_lifecycle=false`, `has_registry=false`
- **Evidence:** 解析/校验 `build-system` 表与源目录；排除 isolated env / wheel build 执行。
- **Expert note:** 这是表校验，不是 backend registry 生命周期。

### 4. `coverage__glob_matcher_core__001` — **accept_with_reservation**

- **Overrides:** 清除 dynamic/registry/global；entanglement 归一为 config/implicit/static
- **Evidence:** glob→regex、include/omit 匹配、平台斜杠；明确排除 path alias / source selection / config 文件解析。
- **Reservation:** `feature_family_primary=config_resolve_discover` 可被挑战为更接近路径/匹配算法。**工程上保留**（glob matcher 是 coverage 配置路径选择子系统），但真人审阅应确认是否改为 `algorithm_data_structure` 或增加 secondary。
- **建议:** 若改 family，需同步 Representative constraint audit。

### 5. `coverage__path_remap_core__001` — **accept**

- **Overrides:** 清除 dynamic/framework/registry/global；entanglement 归一
- **Evidence:** PathAliases、通配结尾拒绝、目标不存在则 skip；与 glob matcher 行为边界在 TASK 中已切开。
- **Expert note:** 与 #4 同 source 但不重复；近重复政策见 companion doc。

### 6. `fs__url_opener_core__hard3_001` — **accept**

- **Overrides:** `static_file_closure_depth=1`
- **Evidence:** FS URL 解析 + opener registry；`has_registry=true` / dynamic import 信号合理。
- **Expert note:** depth=1 与「registry entrypoint 依赖 parser 文件」一致。

### 7. `glom__spec_eval_core__hard3_001` — **accept**

- **Overrides:** `feature_family_primary=algorithm_data_structure`, `feature_statefulness=local_state`, `has_registry=false`
- **Evidence:** glom path / Coalesce / T；递归解释器而非 cache/retry 策略。
- **Expert note:** 纠正「像 policy」的误标方向正确。

### 8. `jinja2__filters_tests_core__001` — **accept_with_reservation**

- **Overrides:** primary=`serialize_format_render`, secondary=`registry_plugin_dispatch`, state=`local_state`
- **Evidence:** Environment 上 filter/test 注册与调用；排除 custom extension / async / 深层 inheritance。
- **Reservation:** `has_framework_lifecycle=true`（来自 framework_coupling）与「instance-local registry」并存。对 taxonomy 轴合理，但真人应确认 lifecycle 布尔是否过强（Environment 构造是否算 framework lifecycle）。
- **建议:** 保持现状；若收紧，只改 boolean，不改 primary/secondary。

### 9. `lark__visitor_transform_core__001` — **accept**

- **Overrides:** none
- **Evidence:** visitor/transformer 局部树遍历；parser closure 深。
- **Expert note:** `algorithm_data_structure` + `local_state` + depth=4 可信。

### 10. `parsel__selector_namespace_core__hard3_001` — **accept**

- **Overrides:** `has_framework_lifecycle=false`
- **Evidence:** selector namespace 注册是实例态；非 app startup lifecycle。
- **Expert note:** `has_registry=true` 保留正确。

### 11. `pyramid__configurator_action_core__hard3_001` — **accept**

- **Overrides:** none
- **Evidence:** action commit / conflict；workflow + registry secondary。
- **Expert note:** `lifecycle_state` + `has_framework_lifecycle=true` 一致。

### 12. `referencing__json_schema_refs_core__001` — **accept**

- **Overrides:** `feature_statefulness=local_state`
- **Evidence:** Registry/Resolver 链式查找状态在对象上，非进程全局。
- **Expert note:** 与 `config_resolve_discover` 匹配。

### 13. `starlette__route_matching_core__hard3_001` — **accept**

- **Overrides:** `feature_statefulness=local_state`
- **Evidence:** Router 实例匹配；非应用启动阶段正确性依赖。
- **Expert note:** framework_lifecycle entanglement 可与 local_state 共存（仓库轴 vs 特征态）。

### 14. `werkzeug__routing_core__001` — **accept**

- **Overrides:** `local_state`, `has_dynamic_import=false`, `has_global_state=false`
- **Evidence:** Map/MapAdapter；converter 表非动态 import。
- **Expert note:** 深 closure（depth=7）与 routing 子系统规模一致。

### 15. `wheel__metadata_normalize_core__hard3_001` — **accept**

- **Overrides:** `has_registry=false`
- **Evidence:** metadata/filename 规范化；非 registry。
- **Expert note:** `resource_metadata_loading` + `stateless` 正确。

---

## Aggregate

| Decision | Count |
| --- | ---: |
| accept | 13 |
| accept_with_reservation | 2 |
| revise / reject | 0 |

**Expert recommendation:** 将本 15 行视为 **provisional engineering gold**；论文发布前对 2 条 reservation 做真人 spot-check 即可优先解锁 taxonomy adjudication 队列。
