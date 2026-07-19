# FeatureLiftBench Python 轨迹证据（自动生成）

> 本文件由 `python tools/research_analysis/render_research_docs.py` 从 `artifacts/research_analysis/trajectory_records.csv` 与 `trajectory_statistics.json` 生成。禁止手工修改比例；定性 case 注释在生成脚本中受版本控制。

## 1. 审计范围与完整性

CSV 库存包含所有可发现的 Python OpenHands 轨迹；主分析语料是 `build_trajectory_records.py` 中冻结的 7 个官方 suite：4 个模型配置、450 个首次运行。另有 14 条通过 `analysis_included=false` 保留但不进入主 Pass@1：{"agent_setup_failure_suite": 10, "post_hoc_rerun": 1, "smoke_or_local_calibration": 3}。每行联接可用的 `run.json`、事件轨迹、submission 与 evaluator result；任务契约来自 `benchmark/tasks/<task_id>/TASK.md` 和 `metadata.json`。

- 行数：464；唯一 run_id：464；列数：59。
- 10 个结构字段的 cell 完整率：4640/4640 (100.0%)。
- 事件轨迹可用：464/464 (100.0%)；evaluation result 可用：442/464 (95.3%)。
- 主分析 public/hidden 结果已实际观测：351/450 (78.0%)；库存字段非空为 353/464。未执行为 NA，而不是 false。
- 主分析 extraction ratio 可用：440/450；全库存为 442/464。

重建命令：

```bash
python tools/research_analysis/build_trajectory_records.py
python tools/research_analysis/summarize_trajectory_records.py --check-paths
python tools/research_analysis/render_research_docs.py
```

## 2. 指标定义与分母

| metric | definition | denominator |
|---|---|---|
| strict suite pass | 历史 `run_status == passed` | 所在分组全部 trajectory |
| functional pass | evaluator `scores.functional_gate == 1`；允许 step-limit 前已产生有效 submission 的 run | 所在分组全部 trajectory |
| public/hidden pass | 对应测试阶段实际执行且通过 | `*_executed=true` 的 trajectory；未执行为 NA |
| public→hidden gap | `public_pass=true ∧ hidden_pass=false` | 主文同时报告全体 450 和 public pass 319 两个分母 |
| extraction ratio | evaluator `submission Python LOC / source snapshot Python LOC` | ratio 非空的 440 条；它是 footprint proxy，不证明逐行复制 |
| final score | functional gate 通过时 `clamp(1-extraction_ratio, 0, 1)`，否则 0 | 全部 trajectory |
| copied files / LOC | evaluator submission `file_count` / nonblank noncomment Python LOC | 全部 trajectory；是 submission-footprint proxy |
| repeated file read | 同一规范化路径的 `file_editor view` 在首次之后再次发生 | 全部有 events 的 450 条 |
| repeated line read | 同一路径、完全相同 `view_range` 的重复读取 | 全部有 events 的 450 条 |
| Agent 推理错误 | FinishAction 声称完成/测试成功，但 functional gate=0，且排除 evaluator/environment error | 全部 450；另可在 168 个非环境功能失败上取条件比例 |
| tool 执行错误 | `ObservationEvent.is_error=true`，排除 schema/required-parameter 错误 | 全部 450 |
| harness 格式错误 | Agent/Conversation error 明确是 tool schema/validation/required-parameter failure | 全部 450 |
| evaluator/environment error | 依赖安装、eval tooling 或 Docker sandbox 在有效测试结论前失败 | 全部 450 |
| closure plan/self-tests/hidden risk | 事件文本的保守规则匹配 | 全部 450；仅表示“出现过”，不是质量标注 |

## 3. 总体与分组统计

全体：strict suite pass 218/450 (48.4%)；functional pass 220/450 (48.9%)；public→hidden 为 98/450 (21.8%)，在 public pass 条件下为 98/319 (30.7%)；环境/evaluator error 62/450 (13.8%)。

### 3.1 按模型

| group | n | functional pass | observed public | public→hidden / public pass | environment error | median ratio | median tokens |
|---|---:|---:|---:|---:|---:|---:|---:|
| `deepseek/deepseek-v4-flash` | 150 | 93/150 (62.0%) | 141/150 (94.0%) | 48/141 (34.0%) | 2/150 (1.3%) | 0.363425 | 1,649,321 |
| `openai/Qwen3-Coder-30B-A3B-Instruct` | 100 | 24/100 (24.0%) | 75/100 (75.0%) | 35/60 (58.3%) | 21/100 (21.0%) | 0.167693 | 2,020,808 |
| `openai/Qwen3.6-27B-FP8` | 100 | 54/100 (54.0%) | 69/100 (69.0%) | 9/63 (14.3%) | 21/100 (21.0%) | 0.309449 | 1,553,055 |
| `openai/Qwen3.6-35B-A3B-FP8` | 100 | 49/100 (49.0%) | 66/100 (66.0%) | 6/55 (10.9%) | 18/100 (18.0%) | 0.281882 | 1,746,882 |

模型间 raw 结果不可直接解释为能力差异：Qwen 三组各有明显环境失败，而 DeepSeek 组只有少量；论文主比较必须同环境重跑或排除环境未观测行。

### 3.2 按 split

| group | n | functional pass | observed public | public→hidden / public pass | environment error | median ratio | median tokens |
|---|---:|---:|---:|---:|---:|---:|---:|
| `core100` | 400 | 212/400 (53.0%) | 306/400 (76.5%) | 61/274 (22.3%) | 60/400 (15.0%) | 0.261016 | 1,698,568 |
| `hard50` | 50 | 8/50 (16.0%) | 45/50 (90.0%) | 37/45 (82.2%) | 2/50 (4.0%) | 0.507656 | 1,771,924 |

### 3.3 按 task type

| group | n | functional pass | observed public | public→hidden / public pass | environment error | median ratio | median tokens |
|---|---:|---:|---:|---:|---:|---:|---:|
| `parser_state_coupling` | 161 | 82/161 (50.9%) | 123/161 (76.4%) | 24/107 (22.4%) | 23/161 (14.3%) | 0.307107 | 1,758,497 |
| `data_model_coupling` | 113 | 52/113 (46.0%) | 81/113 (71.7%) | 21/73 (28.8%) | 18/113 (15.9%) | 0.276073 | 2,206,378 |
| `framework_coupling` | 66 | 26/66 (39.4%) | 46/66 (69.7%) | 18/44 (40.9%) | 14/66 (21.2%) | 0.45565 | 1,699,486 |
| `config_environment_coupling` | 51 | 24/51 (47.1%) | 45/51 (88.2%) | 18/42 (42.9%) | 6/51 (11.8%) | 0.251644 | 1,352,342 |
| `resource_coupling` | 29 | 11/29 (37.9%) | 28/29 (96.6%) | 15/26 (57.7%) | 0/29 (0.0%) | 0.508983 | 1,545,592 |
| `legacy_vibe_clutter` | 24 | 23/24 (95.8%) | 23/24 (95.8%) | 0/23 (0.0%) | 0/24 (0.0%) | 0.111621 | 381,994 |
| `third_party_dependency_coupling` | 6 | 2/6 (33.3%) | 5/6 (83.3%) | 2/4 (50.0%) | 1/6 (16.7%) | 0.127835 | 2,410,213 |

### 3.4 dynamic/global-state metadata 切片

| group | n | functional pass | observed public | public→hidden / public pass | environment error | median ratio | median tokens |
|---|---:|---:|---:|---:|---:|---:|---:|
| `false` | 259 | 122/259 (47.1%) | 185/259 (71.4%) | 42/165 (25.5%) | 46/259 (17.8%) | 0.307107 | 1,924,255 |
| `true` | 191 | 98/191 (51.3%) | 166/191 (86.9%) | 56/154 (36.4%) | 16/191 (8.4%) | 0.24297 | 1,497,118 |

`dynamic_state_task` 只由 metadata entanglement/tags 中的 registry、plugin、dynamic import、entry point、resource、lazy、cache、metaclass/global-state 信号生成。它是宽切片，未控制 split 和难度；只能用于分层抽样，不能做因果结论。

## 4. 失败与噪声分离

### 4.1 Primary outcome 标签

| label | n / 450 |
|---|---:|
| `passed` | 220/450 (48.9%) |
| `evaluator_or_environment_error` | 62/450 (13.8%) |
| `hidden_behavior_contract_failure` | 57/450 (12.7%) |
| `hidden_interface_or_closure_failure` | 39/450 (8.7%) |
| `dependency_closure_omission` | 22/450 (4.9%) |
| `public_api_or_interface_failure` | 17/450 (3.8%) |
| `public_behavior_failure` | 11/450 (2.4%) |
| `missing_submission` | 10/450 (2.2%) |
| `isolation_or_forbidden_import_failure` | 8/450 (1.8%) |
| `build_syntax_or_version_failure` | 3/450 (0.7%) |
| `packaging_or_build_failure` | 1/450 (0.2%) |

这些标签由首个 evaluator 失败与日志模式生成。`hidden_behavior_contract_failure`、`hidden_interface_or_closure_failure` 和 public 行为/接口类别是**启发式标签，需要人工复核**；environment、missing submission、build/import 错误可直接验证。

### 4.2 四类错误源

| source | affected runs | events | operational definition |
|---|---:|---:|---|
| `agent_reasoning_unsupported_completion_claim` | 68/450 (15.1%) | — | FinishAction asserts completion/test success but final functional gate is 0, excluding evaluator/environment errors. |
| `tool_execution_error` | 187/450 (41.6%) | 465 | OpenHands ObservationEvent has is_error=true, excluding tool-schema validation errors. |
| `harness_format_error` | 193/450 (42.9%) | 589 | Agent/Conversation error explicitly reports tool validation/schema/required-parameter failure. |
| `evaluator_environment_error` | 62/450 (13.8%) | 62 | Dependency installation, evaluator tooling, or Docker sandbox fails before a valid test outcome. |

因此不能把“tool error 很多”与“Agent 机制错误很多”混为同一个统计。harness schema 错误可能被恢复，tool execution error 也可能出现在最终通过的轨迹中；只有 evaluator/environment error 会让本行 public/hidden 结论变成 NA。

## 5. Under-/over-extraction 对照

| ratio bucket | n | functional pass | public→hidden / public pass | environment error | median files | median tokens | closure plan | self tests | unsupported finish |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| `under_proxy_le_0_25` | 197 | 88/197 (44.7%) | 53/141 (37.6%) | 27/197 (13.7%) | 5.0 | 1,705,916 | 19/197 (9.6%) | 23/197 (11.7%) | 37/197 (18.8%) |
| `middle_0_25_to_0_80` | 188 | 101/188 (53.7%) | 31/132 (23.5%) | 31/188 (16.5%) | 9.0 | 1,856,692 | 24/188 (12.8%) | 16/188 (8.5%) | 21/188 (11.2%) |
| `over_proxy_gt_0_80` | 55 | 31/55 (56.4%) | 14/46 (30.4%) | 4/55 (7.3%) | 6.0 | 1,513,048 | 6/55 (10.9%) | 9/55 (16.4%) | 10/55 (18.2%) |

已被数据支持：低比例桶与高比例桶都同时包含通过和 public→hidden 失败；两端的 unsupported finish 比例接近，closure plan 均少见。没有被数据支持：它们必然来自同一个潜变量。当前只能提出“边界不确定性可能分别导致早停或保守复制”的待验证假设，需 Oracle Closure 与 executable deletion 干预。

## 6. 重复探索与停止

| metric | affected runs | duplicate/error events | median among affected |
|---|---:|---:|---:|
| `repeated_file_reads` | 295/450 (65.6%) | 1844 | 4.0 |
| `repeated_line_reads` | 143/450 (31.8%) | 394 | 1.0 |
| `repeated_terminal_commands` | 308/450 (68.4%) | 1446 | 3.0 |
| `tool_error_count` | 187/450 (41.6%) | 465 | 2.0 |
| `harness_format_error_count` | 193/450 (42.9%) | 589 | 2.0 |
| `agent_reasoning_error_count` | 68/450 (15.1%) | 68 | 1.0 |
| `evaluator_environment_error_count` | 62/450 (13.8%) | 62 | 1.0 |

| stop reason | n / 450 |
|---|---:|
| `explicit_finish` | 269/450 (59.8%) |
| `completion_signal` | 88/450 (19.6%) |
| `agent_exit:passed` | 59/450 (13.1%) |
| `step_limit_exceeded` | 23/450 (5.1%) |
| `missing_submission_after_agent_exit` | 9/450 (2.0%) |
| `timeout` | 2/450 (0.4%) |

显式 FinishAction 出现在 269/450 (59.8%)；保守规则检测到 unsupported completion claim 68/450 (15.1%)，占 168 个非环境 functional failure 的 68/168 (40.5%)。这证明当前停止证据经常不充分，但不证明“再多一轮 reflection”能修复；必须要求新的 executable evidence。

## 7. 20 个可审计 case

### 1. `requests_cache__cache_key_core__hard3_001`

- 结果：public=true, hidden=false, functional=false, ratio=0.96319, final=0, files=6, LOC=471, tokens=1,651,172, stop=completion_signal；primary=`hidden_interface_or_closure_failure`。
- 轨迹：`experiments/python/openhands/deepseek-v4-flash/batch3-flash-20260707-113104/requests_cache__cache_key_core__hard3_001/agent/openhands_events.jsonl`
- 评测：`experiments/python/openhands/deepseek-v4-flash/batch3-flash-20260707-113104/requests_cache__cache_key_core__hard3_001/eval/result.json`
- 关键步骤：`ad2fc573-1401-4d53-8856-ab4034c217d6`, `eval:hidden_tests`
- 行为摘要：Located and copied the cache-key/policy region, but the required `normalize_body` export is absent; hidden collection fails.
- 支持结论：High footprint does not guarantee API/closure recall; localization alone is insufficient.

### 2. `pydantic_v1__validation_error_core__001`

- 结果：public=NA, hidden=NA, functional=false, ratio=0.535431, final=0, files=15, LOC=5599, tokens=5,096,343, stop=step_limit_exceeded；primary=`dependency_closure_omission`。
- 轨迹：`experiments/python/openhands/deepseek-v4-flash/main-flash-20260705-232429/pydantic_v1__validation_error_core__001/agent/openhands_events.jsonl`
- 评测：`experiments/python/openhands/deepseek-v4-flash/main-flash-20260705-232429/pydantic_v1__validation_error_core__001/eval/result.json`
- 关键步骤：`16766354-cedc-406d-8563-ff18729b377a`, `997b5fdc-5360-4686-ad4e-9d63812d4c09`, `dd118e51-8dc2-4e9c-b076-c3a91c83247c`, `70c1a821-fd37-47cd-99b6-df6fd517088c`, `9a296cef-cacb-440d-a618-70dfe770fe2b`, `61c42c4f-e27b-4e37-9596-54a1ab44fe6c`, `f7e8dfec-e010-479a-9e27-4f1eaba0547f`, `eval:build`
- 行为摘要：Expanded to 15 submission files and hit the step limit; build still reports missing `featurelifted.datetime_parse`.
- 支持结论：Long exploration and broad expansion can still omit one transitive runtime provider.

### 3. `phonenumbers__parse_format_core__001`

- 结果：public=true, hidden=false, functional=false, ratio=0.426281, final=0, files=10, LOC=2871, tokens=5,142,307, stop=step_limit_exceeded；primary=`hidden_interface_or_closure_failure`。
- 轨迹：`experiments/python/openhands/deepseek-v4-flash/main-flash-20260705-232429/phonenumbers__parse_format_core__001/agent/openhands_events.jsonl`
- 评测：`experiments/python/openhands/deepseek-v4-flash/main-flash-20260705-232429/phonenumbers__parse_format_core__001/eval/result.json`
- 关键步骤：`bf656a8c-c910-4f9b-8f78-05723b8a1682`, `27ac166f-127f-4c68-bf47-80a3d4d89e9b`, `bf595ff8-e45f-4f66-afc6-86533a6183b1`, `0cf51515-3320-4b6e-ae72-8f921be8511c`, `dcbe18c6-a41c-467d-b8bb-fdc994557ae6`, `eval:hidden_tests`
- 行为摘要：Read the same paths repeatedly and included regional data, yet hidden metadata access lacks `same_mobile_and_fixed_line_pattern`.
- 支持结论：Resource closure is field/behavior level, not merely file-level presence.

### 4. `diskcache__eviction_policy_core__hard3_001`

- 结果：public=true, hidden=false, functional=false, ratio=0.041578, final=0, files=2, LOC=117, tokens=1,497,118, stop=completion_signal；primary=`hidden_interface_or_closure_failure`；该任务 hidden contract 标为**需要人工复核**。
- 轨迹：`experiments/python/openhands/deepseek-v4-flash/batch3-flash-20260708-wave5/diskcache__eviction_policy_core__hard3_001/agent/openhands_events.jsonl`
- 评测：`experiments/python/openhands/deepseek-v4-flash/batch3-flash-20260708-wave5/diskcache__eviction_policy_core__hard3_001/eval/result.json`
- 关键步骤：`f5b4b21a-19fd-4434-bc05-d5de5cc5f52e`, `6a5dd66b-3680-4910-aa2c-26de02794acb`, `8983822d-0773-4a70-b596-104bb30fcb8b`, `eval:hidden_tests`
- 行为摘要：Submitted a two-file small implementation after public success; hidden expects an additional state-query interface.
- 支持结论：A low-footprint public pass can stop before interface closure is demonstrated; contract requires review.

### 5. `click__lazy_command_core__hard3_001`

- 结果：public=true, hidden=false, functional=false, ratio=0.09368, final=0, files=4, LOC=292, tokens=2,601,067, stop=completion_signal；primary=`hidden_interface_or_closure_failure`。
- 轨迹：`experiments/python/openhands/deepseek-v4-flash/batch3-flash-20260708-wave5/click__lazy_command_core__hard3_001/agent/openhands_events.jsonl`
- 评测：`experiments/python/openhands/deepseek-v4-flash/batch3-flash-20260708-wave5/click__lazy_command_core__hard3_001/eval/result.json`
- 关键步骤：`8493e436-818c-4cb1-9f5e-cd46f19ed74e`, `13d8c1ac-7416-4e9a-9d83-9d44babba949`, `3a7f3fcd-bdc9-4a00-85d8-0e32c8016d0e`, `4b66f5b9-0288-48d3-a025-a9b594eb447c`, `be76e535-ea4d-4624-86ce-fd268c30fd6e`, `eval:hidden_tests`
- 行为摘要：Public behavior passes, then the agent signals completion; hidden fails on lazy command/default-map resolution.
- 支持结论：Dynamic resolution paths need executable state-transition probes.

### 6. `pytest__marker_registry_core__hard3_001`

- 结果：public=true, hidden=false, functional=false, ratio=0.102059, final=0, files=4, LOC=233, tokens=1,679,652, stop=completion_signal；primary=`hidden_interface_or_closure_failure`。
- 轨迹：`experiments/python/openhands/deepseek-v4-flash/batch3-flash-20260708-wave5/pytest__marker_registry_core__hard3_001/agent/openhands_events.jsonl`
- 评测：`experiments/python/openhands/deepseek-v4-flash/batch3-flash-20260708-wave5/pytest__marker_registry_core__hard3_001/eval/result.json`
- 关键步骤：`af1d46e2-7746-4cdc-987a-a51865f978f2`, `14dbc6b4-e2ee-435d-b093-d24bb403c0a1`, `e16547b0-aff1-4e70-a9ac-536911810b40`, `03b0dc44-9d97-4a8d-804e-61cdf42d1e29`, `67e343d5-431f-4291-82db-2c27e2b03cf2`, `eval:hidden_tests`
- 行为摘要：Public passes after a compact extraction; hidden marker/plugin registry merge lacks required behavior/interface.
- 支持结论：Registry state is not fully represented by static import reachability.

### 7. `jupyter_server__extension_config_core__hard3_001`

- 结果：public=true, hidden=false, functional=false, ratio=0.597656, final=0, files=2, LOC=153, tokens=1,020,785, stop=completion_signal；primary=`hidden_interface_or_closure_failure`；该任务 hidden contract 标为**需要人工复核**。
- 轨迹：`experiments/python/openhands/deepseek-v4-flash/batch3-flash-20260707-wave2wave4/jupyter_server__extension_config_core__hard3_001/agent/openhands_events.jsonl`
- 评测：`experiments/python/openhands/deepseek-v4-flash/batch3-flash-20260707-wave2wave4/jupyter_server__extension_config_core__hard3_001/eval/result.json`
- 关键步骤：`6682d720-653d-4c41-9e00-24ff374d85f1`, `cf06bb8e-1745-4663-97d0-10393c87192b`, `3e138020-326f-4bc7-9144-4387766f98f7`, `eval:hidden_tests`
- 行为摘要：Configuration storage works publicly, but hidden merged-extension access fails.
- 支持结论：Global/config state closure remains uncertain; the hidden name is contract-review sensitive.

### 8. `parsel__selector_namespace_core__hard3_001`

- 结果：public=true, hidden=false, functional=false, ratio=1.034437, final=0, files=5, LOC=781, tokens=1,248,192, stop=explicit_finish；primary=`hidden_interface_or_closure_failure`；该任务 hidden contract 标为**需要人工复核**。
- 轨迹：`experiments/python/openhands/deepseek-v4-flash/batch3-flash-20260708-wave5/parsel__selector_namespace_core__hard3_001/agent/openhands_events.jsonl`
- 评测：`experiments/python/openhands/deepseek-v4-flash/batch3-flash-20260708-wave5/parsel__selector_namespace_core__hard3_001/eval/result.json`
- 关键步骤：`ba17601f-4bae-49b5-833a-f7ac8bb9ac9e`, `f9de7651-56da-42fa-af18-4f72ece24075`, `ecfdd1ca-b4f5-4a8c-a302-3d947930dadf`, `525c3a9e-dfbb-49f9-9f4d-44e1a37247bb`, `5c22cd8e-a494-4db5-9890-4582da880548`, `eval:hidden_tests`
- 行为摘要：Copies more Python LOC than the source slice and explicitly finishes, but hidden selector namespace API fails.
- 支持结论：Over-extraction can coexist with interface omission; copy volume is not closure evidence.

### 9. `sqlalchemy__event_dispatch_core__hard3_001`

- 结果：public=true, hidden=true, functional=true, ratio=1.139605, final=0, files=8, LOC=1502, tokens=4,307,124, stop=explicit_finish；primary=`passed`。
- 轨迹：`experiments/python/openhands/deepseek-v4-flash/batch3-flash-20260707-wave2wave4/sqlalchemy__event_dispatch_core__hard3_001/agent/openhands_events.jsonl`
- 评测：`experiments/python/openhands/deepseek-v4-flash/batch3-flash-20260707-wave2wave4/sqlalchemy__event_dispatch_core__hard3_001/eval/result.json`
- 关键步骤：`c46dddd1-b647-45aa-9784-4c584e29461c`, `ebb5381a-141c-4303-847b-b0132febea20`, `06778ac4-d540-49f4-98c1-574539ec120c`, `73e62f4b-7fe3-49a7-b393-473575b9ea84`, `6cf04002-1109-41c2-a810-0f839a2ee1fb`, `3aecc8c6-df21-4897-854e-7575cadbb4e4`
- 行为摘要：A broad eight-file extraction passes both test suites, but extraction ratio above one drives final score to zero.
- 支持结论：Conservative expansion can recover behavior while failing compactness; it is a prune positive control.

### 10. `stevedore__extension_manager_core__hard3_001`

- 结果：public=true, hidden=true, functional=true, ratio=0.878917, final=0.121083, files=4, LOC=617, tokens=1,113,070, stop=completion_signal；primary=`passed`。
- 轨迹：`experiments/python/openhands/deepseek-v4-flash/batch3-flash-20260707-113104/stevedore__extension_manager_core__hard3_001/agent/openhands_events.jsonl`
- 评测：`experiments/python/openhands/deepseek-v4-flash/batch3-flash-20260707-113104/stevedore__extension_manager_core__hard3_001/eval/result.json`
- 关键步骤：`c98c6e5a-d4b1-45f8-8a7d-cde36690b202`
- 行为摘要：A copy-heavy plugin/entry-point extraction passes hidden tests.
- 支持结论：Dynamic-state tasks are not intrinsically impossible; this is an expand-then-prune positive control.

### 11. `pluggy__hook_wrapper_core__hard3_001`

- 结果：public=true, hidden=false, functional=false, ratio=0.387231, final=0, files=5, LOC=467, tokens=1,719,320, stop=completion_signal；primary=`hidden_behavior_contract_failure`。
- 轨迹：`experiments/python/openhands/deepseek-v4-flash/batch3-flash-20260708-wave5/pluggy__hook_wrapper_core__hard3_001/agent/openhands_events.jsonl`
- 评测：`experiments/python/openhands/deepseek-v4-flash/batch3-flash-20260708-wave5/pluggy__hook_wrapper_core__hard3_001/eval/result.json`
- 关键步骤：`532fa682-0eea-4a3f-9258-390009b27fd0`, `2f60e1d2-0955-4484-941d-14ad65fe6ce5`, `2af74bd3-8b88-491b-9177-229e620a9c10`, `de336333-b4de-4cb8-ac54-52a4f932bd01`, `a23ff659-f27c-4467-9a7a-e786e3f1820a`, `7500865e-a69f-44a9-b666-4e7b64695a45`, `eval:hidden_tests`
- 行为摘要：Public wrapper/replay cases pass; hidden historic direct-call behavior raises the wrong exception.
- 支持结论：Closure recovery alone cannot replace behavior-contract validation.

### 12. `pydantic__field_validator_core__hard3_001`

- 结果：public=NA, hidden=NA, functional=false, ratio=NA, final=0, files=0, LOC=0, tokens=35,316, stop=missing_submission_after_agent_exit；primary=`missing_submission`。
- 轨迹：`experiments/python/openhands/deepseek-v4-flash/batch3-flash-20260708-wave5/pydantic__field_validator_core__hard3_001/agent/openhands_events.jsonl`
- 评测：`experiments/python/openhands/deepseek-v4-flash/batch3-flash-20260708-wave5/pydantic__field_validator_core__hard3_001/eval/result.json`
- 关键步骤：`31f49cae-d932-478e-b085-9ea747031afb`, `e7db6b9b-d9f9-42fe-9c7d-bef038fa8a75`, `7ad35608-7fc0-4456-8a66-9b09f605ec5c`
- 行为摘要：The frozen first run exits without a submission after tool/schema errors.
- 支持结论：A harness/workflow failure must not be counted as a hidden behavior observation.

### 13. `coverage__config_merge_core__001`

- 结果：public=true, hidden=false, functional=false, ratio=1, final=0, files=2, LOC=264, tokens=1,354,848, stop=explicit_finish；primary=`hidden_behavior_contract_failure`。
- 轨迹：`experiments/python/openhands/deepseek-v4-flash/main-flash-20260705-232429/coverage__config_merge_core__001/agent/openhands_events.jsonl`
- 评测：`experiments/python/openhands/deepseek-v4-flash/main-flash-20260705-232429/coverage__config_merge_core__001/eval/result.json`
- 关键步骤：`89c4db31-c9c8-483e-8b1d-cf9d53395808`, `3b5cf3a1-ab42-4e7d-a4bb-13cf9ac4058c`, `eval:hidden_tests`
- 行为摘要：The trajectory says the repository is empty, implements from prior knowledge, self-tests, and finishes; hidden setup.cfg merging fails.
- 支持结论：This is direct evidence for an input/localization failure followed by an unsupported behavioral completion claim.

### 14. `dynaconf__settings_merge_core__001`

- 结果：public=true, hidden=true, functional=true, ratio=0.178331, final=0.821669, files=14, LOC=3835, tokens=11,474,158, stop=explicit_finish；primary=`passed`。
- 轨迹：`experiments/python/openhands/deepseek-v4-flash/main-flash-20260705-232429/dynaconf__settings_merge_core__001/agent/openhands_events.jsonl`
- 评测：`experiments/python/openhands/deepseek-v4-flash/main-flash-20260705-232429/dynaconf__settings_merge_core__001/eval/result.json`
- 关键步骤：`e30b970e-e5ee-41f7-8db9-ae18dd2e177d`, `a2186545-7309-498a-a0e5-7f98a6b4331f`, `998202f5-1c38-4b58-9ac6-0a6dce5afcf0`, `7b53e3b4-9c8a-404b-a7f2-4b6e1ffdcfe5`, `8d686c00-9481-42be-a622-e3ceb7ff9769`
- 行为摘要：A very long, repeat-heavy run ultimately passes with a compact ratio.
- 支持结论：High token use and repeated reads do not imply failure; cost must be tied to state-changing evidence.

### 15. `sphinx__extension_registry_core__hard3_001`

- 结果：public=NA, hidden=NA, functional=false, ratio=0.115282, final=0, files=5, LOC=129, tokens=1,860,449, stop=completion_signal；primary=`build_syntax_or_version_failure`。
- 轨迹：`experiments/python/openhands/deepseek-v4-flash/batch3-flash-20260707-wave2wave4/sphinx__extension_registry_core__hard3_001/agent/openhands_events.jsonl`
- 评测：`experiments/python/openhands/deepseek-v4-flash/batch3-flash-20260707-wave2wave4/sphinx__extension_registry_core__hard3_001/eval/result.json`
- 关键步骤：`64906364-b28d-43f3-95c9-3f58f081d8b8`, `03da34c1-c7d4-497f-a431-d664ba3baa2b`, `eval:build`
- 行为摘要：The agent signals completion, but the build fails on Python-version syntax before public/hidden tests execute.
- 支持结论：Syntax/build compatibility is distinct from hidden behavior and closure recovery.

### 16. `readme_renderer__content_type_core__hard3_001`

- 结果：public=NA, hidden=NA, functional=false, ratio=3.044248, final=0, files=5, LOC=344, tokens=3,778,387, stop=completion_signal；primary=`dependency_closure_omission`。
- 轨迹：`experiments/python/openhands/deepseek-v4-flash/batch3-flash-20260708-wave5/readme_renderer__content_type_core__hard3_001/agent/openhands_events.jsonl`
- 评测：`experiments/python/openhands/deepseek-v4-flash/batch3-flash-20260708-wave5/readme_renderer__content_type_core__hard3_001/eval/result.json`
- 关键步骤：`c5208f5e-528b-4d64-ba6d-ef42395f252b`, `3040bfc9-df69-4263-acf0-2e4454ec221d`, `f274ab53-2a2a-4bc0-9f08-0d1a68cc0b8a`, `c27b24cb-6d6d-4f13-a746-f5ddf3eeac11`, `eval:build`
- 行为摘要：Submission LOC is over three times the source slice, yet build fails because `nh3` is absent.
- 支持结论：More copied code does not recover an allowed external dependency automatically.

### 17. `bleach__sanitize_core__001`

- 结果：public=NA, hidden=NA, functional=false, ratio=0.506234, final=0, files=36, LOC=12709, tokens=2,005,228, stop=completion_signal；primary=`dependency_closure_omission`。
- 轨迹：`experiments/python/openhands/deepseek-v4-flash/main-flash-20260705-232429/bleach__sanitize_core__001/agent/openhands_events.jsonl`
- 评测：`experiments/python/openhands/deepseek-v4-flash/main-flash-20260705-232429/bleach__sanitize_core__001/eval/result.json`
- 关键步骤：`14a279c3-172d-486b-aad4-efec65f14628`, `b38c1249-27ba-425c-b459-ff3839259165`, `e1f713d4-1f5c-4e6d-b95d-ba08ebdb971a`, `a798783a-9e8e-43f8-b42f-df9167da7a13`, `eval:build`
- 行为摘要：A 36-file submission cannot build because `webencodings` is missing.
- 支持结论：File-level copying and dependency replacement/packaging are different actions.

### 18. `responses__request_matcher_core__hard3_001`

- 结果：public=NA, hidden=NA, functional=false, ratio=0.311381, final=0, files=3, LOC=487, tokens=1,277,571, stop=completion_signal；primary=`evaluator_or_environment_error`。
- 轨迹：`experiments/python/openhands/deepseek-v4-flash/batch3-flash-20260707-wave2wave4/responses__request_matcher_core__hard3_001/agent/openhands_events.jsonl`
- 评测：`experiments/python/openhands/deepseek-v4-flash/batch3-flash-20260707-wave2wave4/responses__request_matcher_core__hard3_001/eval/result.json`
- 关键步骤：`b135beca-fec3-49a3-85f1-f81db6c13e44`, `c0dbe9f4-bcb7-46d2-b997-1b23d35f78da`, `d45122ae-c345-4c36-af03-1200ca011f68`, `9664ab72-299d-4ba7-a400-7ccc5fff384f`, `eval:build`, `eval:dependency_install_failed`
- 行为摘要：The frozen evaluator cannot install the required dependency, so no public/hidden result is observed.
- 支持结论：This row is evaluator/environment noise, not an Agent failure; saved-submission re-evaluation is supplementary.

### 19. `yamale__schema_validate_core__hard3_001`

- 结果：public=NA, hidden=NA, functional=false, ratio=1.298456, final=0, files=16, LOC=757, tokens=2,679,835, stop=completion_signal；primary=`evaluator_or_environment_error`。
- 轨迹：`experiments/python/openhands/deepseek-v4-flash/batch3-flash-20260707-wave2wave4/yamale__schema_validate_core__hard3_001/agent/openhands_events.jsonl`
- 评测：`experiments/python/openhands/deepseek-v4-flash/batch3-flash-20260707-wave2wave4/yamale__schema_validate_core__hard3_001/eval/result.json`
- 关键步骤：`ee3433b3-5447-4827-85bf-80d78e697ee8`, `cba1c648-5bf8-492f-824b-a9a173f14558`, `eval:build`, `eval:dependency_install_failed`
- 行为摘要：The frozen evaluator dependency set fails before testing.
- 支持结论：Raw Pass@1 must be reported, but mechanism analysis must exclude this as an unobserved test outcome.

### 20. `pyyaml__safe_load_dump__001`

- 结果：public=true, hidden=true, functional=false, ratio=1.002022, final=0, files=17, LOC=4459, tokens=2,217,561, stop=explicit_finish；primary=`isolation_or_forbidden_import_failure`。
- 轨迹：`experiments/python/openhands/qwen3-coder-30b-a3b-instruct/main-20260702-212731/pyyaml__safe_load_dump__001/agent/openhands_events.jsonl`
- 评测：`experiments/python/openhands/qwen3-coder-30b-a3b-instruct/main-20260702-212731/pyyaml__safe_load_dump__001/eval/result.json`
- 关键步骤：`e355fb56-3a68-4c5d-88d7-f33498675e8e`, `043fd0df-7da6-4c20-82da-0af4d49ca216`, `61e3efb5-ff31-4183-9ede-f91e33e1deb5`, `2d95128b-1926-44f3-a5d0-cc5502f4f82a`, `3efca204-2383-4e72-b969-c1d80169967b`
- 行为摘要：Public and hidden tests pass, but the forbidden-original-import gate fails.
- 支持结论：Functional completion includes isolation; test pass alone is not the final gate.

## 8. 可以与不可以下的结论

**已被数据支持：** public pass 后仍有大量 hidden failure；依赖/接口、行为契约、隔离、build 和环境错误是不同 failure source；低/高 footprint 都不能单独保证成功；轨迹有显著重复读取/命令；62 条环境/evaluator 失败污染 raw 模型比较。

**合理推测：** 缺少显式 executable closure state 可能把定位、扩张、行为验证、裁剪和停止割裂。

**待验证假设：** Oracle Closure 会显著强于 Oracle Locate；counterfactual deletion 能在不损伤 hidden pass 的情况下提升 compactness；ECSM 的收益超过等预算 strong prompt。
