# Plan: External-50 扩题（+50 → Python-200）

**状态：** 已冻结 External-50 release · **50/50 design cards 已填** · **Python-200 release checks 通过**  
**日期：** 2026-08-01  

| 产物 | 路径 |
| --- | --- |
| 仓×题总表（机读） | [`benchmark/selection/external50_expansion_20260731.json`](../benchmark/selection/external50_expansion_20260731.json) |
| **Design cards（50 已填）** | [`benchmark/selection/external50_design_cards/`](../benchmark/selection/external50_design_cards/) |
| Cards 索引 | [`external50_design_cards/README.md`](../benchmark/selection/external50_design_cards/README.md) |
| 填卡脚本 | [`benchmark/selection/scripts/fill_external50_design_cards.py`](../benchmark/selection/scripts/fill_external50_design_cards.py) |
| Pilot materialize 脚本 | [`harness/scripts/materialize_external50_pilot.py`](../harness/scripts/materialize_external50_pilot.py) |
| W1 materialize 脚本 | [`harness/scripts/materialize_external50_w1.py`](../harness/scripts/materialize_external50_w1.py) |
| W2 materialize 脚本 | [`harness/scripts/materialize_external50_w2.py`](../harness/scripts/materialize_external50_w2.py) |
| W3 materialize 脚本 | [`harness/scripts/materialize_external50_w3.py`](../harness/scripts/materialize_external50_w3.py) |
| W4 materialize 脚本 | [`harness/scripts/materialize_external50_w4.py`](../harness/scripts/materialize_external50_w4.py) |
| W5 materialize 脚本 | [`harness/scripts/materialize_external50_w5.py`](../harness/scripts/materialize_external50_w5.py) |
| Staging（50 题） | [`benchmark/staging/`](../benchmark/staging/) |

**目标：** 新增 50 道题（50 个新 upstream 仓，不复用 External-150）。  
**本波不做：** 旧 150 全量 contract audit、方法实验、旧题 baseline。

**当前阶段结论：**  
Design card 六段已全部写入；W1-W5 全部 pin + materialize，并从候选池冻结 40 个 retained task 与 10 个平衡 replacement。最终 External-50 已发布到 `benchmark/external50/`，通过 50/50 contract validation、static isolation、reference regression（357 tests）和 source/dependency closure。  
W2 中 `libcst` 因 native 扩展硬编码模块名无法 rename → **blocked**，未进入最终 50。最终集合与冻结 Python-150 通过 `benchmark/python200_tasks/` 组成 Python-200；旧 `benchmark/tasks/` 未修改。  
分类分布与约束见 `benchmark/selection/python200_balance_policy.json` 和 `benchmark/selection/external50_expansion_20260731.json`。本地尚未执行的唯一运行门禁是 Docker reference；由服务器严格 preflight 在全量模型调用前完成。

---

## 0. Agent 开工方式（锁定）

```text
第一步：为 50 题全部填完 design card  ✅ 已完成（design_card_ready）
第二步：人工快速审核 planned/final lift 与 target_api  ✅ pilot skim pass
第三步：先 materialize 5 题试运行（pilot） ✅ staging validated（未 promote）
第四步：流程稳定后，再按 5×10 波次执行  ✅ W1–W5 全部 staging validated
```

### 单题领取规则（design_card 阶段已结束）

1. 当前 50 题均为 `design_ready` / `design_card_ready`；下一阶段只领经人工 skim 通过的题做 materialize。  
2. 必读：`docs/TASK_DESIGN_RULES.md`、`.agents/skills/featureliftbench-create-task/SKILL.md`、本题 design card。  
3. Materialize 前必须先 pin `feasibility.commit`；仍禁止跳过 card 直接写 tests/reference。  
4. **禁止**在 card 未 ready 时写 `public_tests` / `hidden_tests` / `reference_solution`。  
5. 禁止直接写入 `benchmark/tasks/`；staging only。  
6. 换题：只用 ledger `backup`，尽量同 `planned_lift_type`，并改 JSON + 新建 card。

### Pilot 五题（试跑）

见 ledger `pilot_candidates`：

1. `cssselect__selector_xpath_core__001`（lift 易被高估，必复核）  
2. `semver__version_core__001`（Direct）  
3. `uritools__uri_join_normalize_core__001`（Adapted）  
4. `dateparser__parse_settings_pipeline_core__001`（Composite）  
5. `tinydb__query_storage_core__001`（较小 Composite）

Pilot 通过后再开 W1–W5 批量 materialize。

---

## 1. 配额：计划值，不是强制终标

| planned_lift_type | 计划 n |
| --- | ---: |
| Direct | 8 |
| Adapted | 14 |
| Composite | 28 |
| **Total** | **50** |

看源码后允许改类，必须记录：

```text
planned_lift_type
final_lift_type
reclassification_reason
```

**禁止为保配额制造假 Composite。**  
Composite 仅当目标表面需要**组合多个上游能力**且无法用单一上游 API 直接对应。

### 优先复核 lift 的题（可能降为 Direct/Adapted）

| task_id | 原因 |
| --- | --- |
| `cssselect__selector_xpath_core__001` | selector→XPath 可能已是单一上游表面 |
| `toolz__compose_pipe_core__001` | compose/pipe/curry 可能是薄抽取 |
| `pyparsing__grammar_compose_core__001` | 组合 ParserElement 可能是常态上游 API |
| `tinycss2__stylesheet_roundtrip_core__001` | parse+serialize 可能是成对入口而非新表面 |
| `parsimonious__grammar_visitor_core__001` | Grammar+Visitor 是否已是文档化工作流 |
| `more_itertools__recipes_core__001` | 确认 Direct |

---

## 2. 每题 Design Card（六段，强制）

路径：`benchmark/selection/external50_design_cards/<task_id>.md`  
**50 张骨架已生成**；Agent 任务是把 YAML 填实，不是空着 materialize。

```yaml
target_api:
  module:
  signatures:
  returns:
  exceptions:
  defaults:
  state_effects:

upstream_mapping:
  primary_symbols:
  supporting_components:
  semantic_delta:

oracle_basis:
  # upstream | task_specified | mixed
  basis:

scope:
  included:
  excluded:

feasibility:
  commit:
  license:
  python_versions:
  native_or_heavy_dependencies:
  offline_resources:

acceptance:
  closure_review:
  reference_pass:
  isolation_pass:
  no_original_import:
  overlap_check:
```

另在 card 头字段维护：`planned_lift_type` / `final_lift_type` / `reclassification_reason`。

---

## 3. 新题轻量 closure review（promotion 前）

不对旧 150 做本波审计；**新 50 晋升前**至少：

1. 每个 hidden assertion 都能对应 TASK 条款或明确上游行为；  
2. Required API 覆盖所有测试调用路径；  
3. 无未声明默认值、异常、成员、状态语义。  

对应 card `acceptance.closure_review`（及后续 validate 门禁）。

---

## 4. 波次（仅在 pilot 成功后）

| Wave | 题数 | 内容 |
| --- | ---: | --- |
| W1 | 10 | Composite 前段 |
| W2 | 10 | Composite validate / AST 等 |
| W3 | 10 | Composite 收尾 + Adapted 开头 |
| W4 | 10 | Adapted |
| W5 | 10 | Direct + 换题缓冲 |

落地：`benchmark/staging/<task_id>/` → validate →（批准后）promote。

规模风险（优先 backup）：`frictionless`、`libcst`、`sqlglot`、`textX`。

---

## 5. 仓 × 题总表

完整 50 行见 JSON；可读表见下方。字段含义：

- `planned_lift_type`：计划配额标签  
- 最终以 card 的 `final_lift_type` 为准  

### 5.1 Composite（计划 28）

| # | Wave | Package | task_id | family |
| ---: | --- | --- | --- | --- |
| 1 | W1 | dateparser | `dateparser__parse_settings_pipeline_core__001` | parse_tokenize_decode |
| 2 | W1 | omegaconf | `omegaconf__merge_interpolate_core__001` | config_resolve_discover |
| 3 | W1 | watchdog | `watchdog__observer_dispatch_core__001` | protocol_state_transition |
| 4 | W1 | cachecontrol | `cachecontrol__heuristic_store_core__001` | cache_retry_policy |
| 5 | W1 | structlog | `structlog__processor_chain_core__001` | serialize_format_render |
| 6 | W1 | flask-login | `flask_login__session_guard_core__001` | registry_plugin_dispatch |
| 7 | W1 | sqlglot | `sqlglot__parse_transpile_core__001` | parse_tokenize_decode |
| 8 | W1 | pyparsing | `pyparsing__grammar_compose_core__001` | parse_tokenize_decode |
| 9 | W1 | tinycss2 | `tinycss2__stylesheet_roundtrip_core__001` | parse_tokenize_decode |
| 10 | W1 | cssselect | `cssselect__selector_xpath_core__001` | parse_tokenize_decode |
| 11 | W2 | typeguard | `typeguard__check_type_pipeline_core__001` | validate_normalize_construct |
| 12 | W2 | frictionless | `frictionless__schema_resource_validate_core__001` | validate_normalize_construct |
| 13 | W2 | strictyaml | `strictyaml__schema_load_core__001` | validate_normalize_construct |
| 14 | W2 | pykwalify | `pykwalify__map_seq_validate_core__001` | validate_normalize_construct |
| 15 | W2 | premailer | `premailer__inline_css_core__001` | serialize_format_render |
| 16 | W2 | libcst | `libcst__parse_transform_core__001` | parse_tokenize_decode |
| 17 | W2 | textX | `textx__metamodel_model_core__001` | parse_tokenize_decode |
| 18 | W2 | parsimonious | `parsimonious__grammar_visitor_core__001` | parse_tokenize_decode |
| 19 | W2 | anytree | `anytree__tree_resolve_render_core__001` | algorithm_data_structure |
| 20 | W2 | toolz | `toolz__compose_pipe_core__001` | algorithm_data_structure |
| 21 | W3 | boolean.py | `boolean_py__expr_simplify_core__001` | algorithm_data_structure |
| 22 | W3 | tinydb | `tinydb__query_storage_core__001` | algorithm_data_structure |
| 23 | W3 | huey | `huey__task_schedule_core__001` | workflow_session_orchestration |
| 24 | W3 | invoke | `invoke__collection_context_core__001` | workflow_session_orchestration |
| 25 | W3 | icalendar | `icalendar__component_roundtrip_core__001` | serialize_format_render |
| 26 | W3 | tldextract | `tldextract__suffix_resolve_core__001` | resource_metadata_loading |
| 27 | W3 | vcrpy | `vcrpy__cassette_match_core__001` | protocol_state_transition |
| 28 | W3 | joserfc | `joserfc__jwt_claims_core__001` | validate_normalize_construct |

Repo URL / entanglement / 一句话：见 JSON 或各 design card 头字段。

### 5.2 Adapted（计划 14）

| # | Wave | Package | task_id |
| ---: | --- | --- | --- |
| 29–30 | W3 | dill, python-json-logger | `dill__serialize_settings_core__001`, `python_json_logger__json_formatter_core__001` |
| 31–42 | W4 | flask-cors … ConfigUpdater | 见 JSON / cards 索引 |

### 5.3 Direct（计划 8）

| # | Wave | Package | task_id |
| ---: | --- | --- | --- |
| 43–50 | W5 | more-itertools … pyrsistent | 见 JSON / cards 索引 |

### 5.4 Backup（16）

见 JSON `disposition=backup` 与下文历史表；换题时补 `task_id` + 新 card。

---

## 6. Materialize 门禁（card ready 之后）

Skill：`featureliftbench-create-task` → `validate-task` →（批准）`promote-task`  
规则：`TASK_DESIGN_RULES` / `07_incremental_task_rules` / `FULL_REPOSITORY_SOURCE_POLICY`

单题 Done：

1. design card 六段填实 + lift 已审  
2. `feasibility.commit/license` 已解析并进 registry  
3. staging package + reference 过 public/hidden  
4. isolation / no upstream import  
5. `acceptance.closure_review=pass`  
6. 更新 ledger：`final_lift_type`、`pin_status`、`status=validated`（或 blocked）

---

## 7. 成功标准

1. 50/50 design cards = `design_card_ready`（或 documented drop/replace）  
2. Pilot 5 materialize + validate 通过  
3. 其后 45 按波次完成；仓不与 External-150 重复  
4. `final_lift_type` 分布可偏离计划配额，但有 reclassification 记录  
5. 新题 promotion 前轻量 closure review 全过  

---

## 8. 发布结果

1. ~~人工 skim（优先 pilot + 已 reclass 的 5 题）~~ ✅  
2. ~~Materialize pilot 5（先 pin commit）~~ ✅ staging validated  
3. ~~W1–W5 批量 materialize（pin → staging → validate）~~ ✅ **50/50**  
4. ~~轻量 closure review + balance replacement~~ ✅ **40 retained + 10 replacement**  
5. ~~冻结 External-50 独立 split，并生成 Python-200 unified root~~ ✅  
6. **下一步：** 服务器 Docker preflight 后执行 `run_python200_paper.sh --execute`

### 仅运行 External-50

已有完整、同条件 Python-150 结果时，可以只运行扩展的 50 题：

```bash
./harness/scripts/run_python200_paper.sh \
  <openhands-profile> \
  <run-id> \
  --external-only \
  --workers <n> \
  --agent-image <pinned-agent-image-id> \
  --eval-image <pinned-eval-image-id> \
  --execute
```

该模式仍执行全部 Python-200 release checks，但模型调用只选择冻结
`python200_suite.json` 中属于 `benchmark/external50/` 的 50 题，并强制选择数为
50。合并时必须保持 model revision、agent profile、Main arm、attempt policy、agent
image 和 evaluator image 一致；原 150 与新 50 分别保留，分析阶段按 task ID 合并，
不得覆盖或重试旧 150 的失败样本。
