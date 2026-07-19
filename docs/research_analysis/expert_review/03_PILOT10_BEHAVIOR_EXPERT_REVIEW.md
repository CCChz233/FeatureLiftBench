# Pilot-10 behavior contract expert review

**Reviewer:** `cursor_grok_expert_pass_20260719`  
**Subset:** `diagnostic_subset_manifest.json` → `challenge_groups.pilot_10`  
**Method:** 对照 `TASK.md` included/excluded behaviors 与 `behavior_contract.json` 的 **public_clauses**；检查映射完整性（unmapped=0）。**不**从 hidden 样例发明新的公开条款。

Overall: **10/10 engineering accept**。3 题建议加固公开条款措辞（仍可工程使用）。

---

## Aggregate mapping health

| Task | Public clauses | Pub maps | Hid maps | Unmapped | Audit conflicts | Expert |
| --- | ---: | ---: | ---: | ---: | ---: | --- |
| pluggy__hook_specs_core__001 | 9 | 2 | 3 | 0 | 0 | accept |
| pydantic_v1__validation_error_core__001 | 7 | 4 | 6 | 0 | 0 | accept |
| coverage__config_merge_core__001 | 6 | 2 | 4 | 0 | 0 | accept |
| lark__grammar_loader_core__001 | 6 | 1 | 2 | 0 | 0 | accept |
| websockets__handshake_parse_core__001 | 9 | 4 | 18 | 0 | 0 | accept |
| boltons__iterutils_core__001 | 8 | 3 | 11 | 0 | 0 | accept |
| schema__nested_validate_core__hard3_001 | 5 | 1 | 3 | 0 | 0 | accept_with_reservation |
| requests_cache__cache_key_core__hard3_001 | 13 | 3 | 5 | 0 | 0 | accept |
| sqlparse__format_filters_core__001 | 5 | 1 | 2 | 0 | 0 | accept_with_reservation |
| celery__signal_dispatch_core__hard3_001 | 6 | 1 | 4 | 0 | 0 | accept_with_reservation |

---

## Per-task notes

### `pluggy__hook_specs_core__001` — accept

公开条款覆盖 HookspecMarker、unknown args 拒绝、hookwrapper generator 约束、historic 组合错误。与 TASK 插件规范表面一致。priority overrides 存在但不构成冲突。

### `pydantic_v1__validation_error_core__001` — accept

BaseModel / pre-each_item validators / root_validator / Config.extra forbid 等条款对齐 v1 API。注意与 hard3 field_validator 题的版本边界（见近重复簇 #4）。

### `coverage__config_merge_core__001` — accept

coveragerc / setup.cfg / tox.ini / env override / path expansion 条款与 included behaviors 匹配；excluded 的 measurement/CLI 未泄漏进公开条款。

### `lark__grammar_loader_core__001` — accept

`Lark.open`、相对 `%import`、`open_from_package`、lalr 编译后解析 — 与 TASK 一致。resource packaging 风险应由 hidden 覆盖；公开条款未过度承诺。

### `websockets__handshake_parse_core__001` — accept

握手 header/ABNF/Request.parse/校验条款完整；excluded 的 socket/frame/protocol SM 未进入公开条款。hid_maps 较多（18）属正常（细粒度 header 用例）。

### `boltons__iterutils_core__001` — accept

chunked/windowed/pairwise/unique/bucketize/remap 条款覆盖主 API。remap 栈语义是难点；公开条款已提及 visit/enter/exit 方向，足够 engineering。

### `schema__nested_validate_core__hard3_001` — accept_with_reservation

- 条款偏短（nested dict / Optional / Or-And + generic API clause）。
- **风险：** 错误聚合、callable validator、forbidden extra keys 等 TASK signals 可能主要落在 hidden，公开面偏薄。
- **建议（真人/后续修订）：** 在不泄漏 hidden 的前提下，把 metadata `included_behaviors` / signals 中已公开的错误与 Optional default 语义写成独立 public clauses。

### `requests_cache__cache_key_core__hard3_001` — accept

create_key / normalize_* 条款细；与「无 session/backend」排除一致。clause 数 13 合理。

### `sqlparse__format_filters_core__001` — accept_with_reservation

- 公开条款偏综合（格式化选项一把抓 + generic API）。
- **风险：** keyword/identifier case、reindent、operator spacing 等是否各自可审计不够清晰。
- **建议：** 拆成 2–3 条可映射的公开条款，便于 nodeid 对齐。

### `celery__signal_dispatch_core__hard3_001` — accept_with_reservation

- 条款粒度粗（registration / sender filter / dispatch / weak cleanup）。
- TASK signals 含 dispatch_uid、exception capture；公开条款未显式点名。
- **建议：** 在公开面补充「duplicate dispatch_uid」与「dispatch 返回异常结构」——若这些已在 public tests 中出现。

---

## Contract review hygiene checklist（给真人）

对每题确认：

1. 每条 public clause 都能在 TASK `included_behaviors` 或公开 API 描述中找到来源  
2. 无 hidden 输入/断言文本进入 public clause  
3. excluded behaviors 未变成正向要求  
4. 每个 public/hidden nodeid 有映射且不 orphan  
5. 两名真人独立勾选后，分歧交裁决者

## Status statement

本文件将 Pilot-10 标为 **expert engineering accept**。  
`behavior_contract.json` 内 `review_status` 仍为 `ai_assisted_reviewed`；**未**改为 human-reviewed。
