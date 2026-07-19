# FeatureLiftBench 因果实验计划

## 1. 实验目标

目标不是再测一次“哪个 prompt 更好”，而是区分 `MECHANISM_HYPOTHESES.md` 预注册的六种解释：定位、closure、行为契约、停止、workflow，以及工具/harness 噪声。

当前可运行 pilot 已冻结在：

- manifest：`experiments/ecsm_pilot/pilot_manifest.yaml`
- runner：`experiments/ecsm_pilot/run_pilot.py`
- analyzer：`experiments/ecsm_pilot/analyze_pilot.py`
- 判定规则：`docs/research_analysis/PILOT_DECISION_RULES.md`
- 七臂作用与分阶段规模：`docs/research_analysis/EXPERIMENT_SCOPE_AND_ARM_RATIONALE.md`
- 空跑审计输出：`artifacts/research_analysis/ecsm_pilot/`
- freeze：revision 5，`c94764ed110992a6`
- execution authorization：`artifacts/research_analysis/v1_1/pilot_execution_authorization_status.json`

冻结的完整 pilot 是 10 tasks × 7 arms × 1 seed = 70 cells，但按 14-cell Stage A、20-cell Stage B 和有条件 36-cell Stage C 投入。本文其余 hidden-aware、more-context、reflection 和 executable deletion 实验是后续判别/消融，不混入首轮冻结矩阵。

所有实验固定：

- Agent：OpenHands；模型：`deepseek/deepseek-v4-flash`。
- 同一 131,072 context window、8,192 reserved output、6,000,000 total-token guard、120 最大步骤、temperature 0 和工具集合。
- Docker evaluator、Python 3.11、network off、同一 vendor-wheel snapshot。
- 同一任务首次运行；每个条件至少 3 seeds 时才报告方差。低成本 pilot 可先 1 seed 作方向筛选，但不写因果结论。
- 不向 Agent 暴露 hidden tests、hidden 日志、reference solution 代码。

## 2. 任务分层

### Cohort A：静态/导出 closure（6）

- `requests_cache__cache_key_core__hard3_001`
- `pydantic_v1__validation_error_core__001`
- `alembic__revision_map_core__hard3_001`
- `importlib_resources__traversable_tree_core__hard3_001`
- `isort__settings_resolver_core__hard3_001`
- `keyring__backend_select_core__hard3_001`

选择理由：首错是缺模块、缺导出或缺异常类；`requests_cache` 的所需导出在 TASK 中明确。

### Cohort B：动态状态/registry/resource closure（6）

- `phonenumbers__parse_format_core__001`
- `pytest__marker_registry_core__hard3_001`
- `click__lazy_command_core__hard3_001`
- `jupyter_server__extension_config_core__hard3_001`
- `stevedore__extension_manager_core__hard3_001`
- `sphinx__extension_registry_core__hard3_001`

其中 `click`、`jupyter_server` 的具体 hidden 方法名契约需要先裁决；若不通过公平性复核，用 `flake8__plugin_options_core__hard3_001`、`vibe_app__plugin_registry_core__001` 替换。

### Cohort C：行为义务而非文件 closure（6）

- `pydantic__field_validator_core__hard3_001`
- `pluggy__hook_wrapper_core__hard3_001`
- `aiohttp__url_params_core__hard3_001`
- `license_expression__policy_core__hard3_001`
- `coverage__config_merge_core__001`
- `yamale__schema_validate_core__hard3_001`（使用修复后依赖环境）

### Cohort D：copy-heavy functional pass（6）

- `sqlalchemy__event_dispatch_core__hard3_001`
- `stevedore__extension_manager_core__hard3_001`
- `celery__signal_dispatch_core__hard3_001`
- `multidict__multidict_mutation_core__hard3_001`
- `tox__factor_expression_core__hard3_001`
- `markdown_it__commonmark_render__001`

## 3. 指标

### 3.1 结果指标

- hidden Pass@1；functional Pass@1。
- public-hidden gap：`public_pass && !hidden_pass`。
- final score 与 extraction ratio。
- copied files、submitted LOC、package bytes。
- build/install pass、forbidden import/path leakage。

### 3.2 Closure 指标

- closure recall：人工标注的 required obligation 中，被 submission artifact 与 executable probe 覆盖的比例。
- closure precision：submission artifact 支持的 obligation 中，必要 obligation 的比例。
- unresolved obligation count；unsupported artifact count。
- static edge recall、dynamic-state edge recall、resource edge recall 分开报告。

文件与 reference oracle 的重合只能作为辅助指标：Agent 可以合法重写更小实现，`oracle_manifest` 也有历史缺口。

### 3.3 过程与成本指标

- total/prompt/completion tokens、API calls、assistant steps、wall time。
- tool calls、tool errors。
- repeated exploration：重复 path view、重复 exact command、语义重复 search。
- time-to-first-correct-locate、首次 public pass 后动作数。
- stop calibration：结束时 unresolved obligations 与 hidden outcome。

## 4. 实验矩阵

### E0 Standard Agent

**假设**：复现现有 public-hidden gap 与重复探索。

**任务**：A/B/C 各 4 个，优先 12 题；已有 frozen run 可作历史对照，但新 harness 版本至少重跑 1 seed。

**实验组/对照**：无额外信息的当前 `_build_openhands_prompt`。

**支持结果**：复现实验与 frozen 的 failure type 方向一致。

**否定结果**：新版环境下大多数历史失败自然消失；此时先检查 benchmark drift。

**代码修改**：只增加 condition id 和统一过程日志，不改 prompt。

**优先级/成本**：P0；已有证据，新增 12 runs。

### E1 FeatureLift-specific stronger prompt

**假设**：失败主要是 prompt 没提醒闭包、隐式依赖和 compactness。

**处理**：在现有 prompt 后加入固定 checklist：列 API/behavior/resource/state 风险，public pass 后逐项复核，最后 prune。只提供文字，不提供新工具或外部信息。

**任务**：A/B/C 各 4 个。

**对照**：E0；模型、token budget、工具完全相同。

**主要指标**：hidden Pass@1、gap、ratio、tokens、repeated exploration。

**支持**：E1 接近 Oracle Closure 的收益，且不同 failure cohort 都提升。

**否定**：只增加 token/动作，不降低 closure failure；这将支持“不是普通 prompt 问题”。

**代码修改**：已实现。`run_pilot.py` 生成登记过的 condition appendix；`openhands_runner.py` 通过 `FEATURELIFTBENCH_OPENHANDS_PROMPT_APPEND_FILE` 注入；不改 CLI 默认行为。

**优先级/成本**：P0；12 runs。

### E2 Hidden-aware checklist

**假设**：行为失败来自可见测试诱导的错误停止。

**处理**：不猜 hidden case；从 TASK 的 Required Behavior 自动生成 obligation checklist，要求每项至少有一个本地 probe 或明确未验证状态。不能读取 hidden tests。

**任务**：Cohort C 6 题 + Cohort A 4 题作为 specificity 对照。

**主要指标**：behavior hidden pass、closure failure、生成 probe 数、false-confidence stop。

**支持**：C 显著提升而 A 收益较小。

**否定**：A/C 都不提升，或仅产生更多普通 reflection。

**代码修改**：新增 `harness/featureliftbench/obligation_extractor.py`；把结构化 obligation JSON 注入 workspace。

**优先级/成本**：P1；10 runs。

### E3 Oracle Locate

**假设**：正确文件定位是主要瓶颈。

**处理**：只给 reference-related 文件/符号的**位置候选**，不告诉哪些是必要闭包，不给代码片段或 oracle submission。

**任务**：A/B/C 各 4 个。

**主要指标**：time-to-first-locate、hidden Pass@1、closure recall、tokens。

**支持**：hidden pass 大幅上升，接近 Oracle Closure。

**否定**：定位时间下降但 gap 基本不变。

**代码修改**：pilot 内已实现：从 metadata source entrypoint 在公开 source snapshot 中定位，只输出路径，不读 hidden/evaluator log。

**优先级/成本**：P0；12 runs。

### E4 Oracle Closure

**假设**：瓶颈是 closure selection，而不是 locate。

**处理**：给 artifact/obligation 清单：必要源文件类别、输出符号、资源/状态类型；不提供 reference solution 内容和 hidden assertions。

**任务**：与 E3 完全相同。

**主要指标**：hidden Pass@1、closure recall/precision、ratio、copied files。

**支持**：E4 明显优于 E3，尤其 A/B；若 ratio 上升，说明 recall 获益但仍需 prune。

**否定**：E4 与 E3 无差异，或只改善 public/build 不改善 hidden。

**代码修改**：pilot 内已实现：只读取 `evaluation/oracle_manifest.json` 的 `required_source_files` 和 `target_api`；运行前仍需对 10 题 hint 做人工泄漏审计。

**优先级/成本**：P0，最关键；12 runs。

### E5 Static dependency hint

**假设**：静态 import/call edge 已能解决大多数 closure failure。

**处理**：给基于 AST 的 imports、re-exports、相对 import、被调用本地 symbol 候选；不含运行时 trace。

**任务**：A 6 + B 6。

**主要指标**：static/dynamic closure recall、hidden pass、ratio。

**支持**：A 明显提升，B 提升有限；这支持动态闭包分层。

**否定**：A/B 同幅提升，说明简单静态图已足够；或 A 也不提升，说明问题在行为/改写。

**代码修改**：pilot 内已实现 bounded AST-import depth≤2 候选生成器；它输出候选而非强制复制列表。正式方法若继续，再抽成 harness 模块。

**优先级/成本**：P0；12 runs，分析代码成本约 1–2 天。

### E6 More-context baseline

**假设**：失败只是上下文不足。

**处理**：一次性附加 target entrypoint 周边文件和 repo map，token budget 不变；减少可用生成/交互预算，真实反映上下文机会成本。

**任务**：A/B 各 4 个。

**主要指标**：hidden pass、max prompt tokens、total tokens、tool calls。

**支持**：显著接近 Oracle Closure。

**否定**：tokens 增加而 closure/gap 不改善。

**代码修改**：prompt context packer；记录注入文件和 token。

**优先级/成本**：P1；8 runs。

### E7 Reflection baseline

**假设**：普通多一轮反思足以修复。

**处理**：public pass 后固定一轮“检查遗漏和 hidden risk”，无新工具/提示。

**任务**：A/B/C 各 3 个。

**主要指标**：hidden pass、额外 tokens/actions、submission diff。

**支持**：以较小成本接近结构化 closure。

**否定**：重复已有检查，主要增加 token，且没有产生新的 state-changing probe evidence。

**代码修改**：OpenHands 完成信号拦截器或 prompt protocol。

**优先级/成本**：P1；9 runs。

### E8 Copy-first then prune

**假设**：先提高 closure recall 再优化 footprint，比一次性猜最小边界稳定。

**处理**：先复制 Oracle-Locate 候选的自包含运行子树直到 probes 饱和，再进入 prune 阶段；不允许直接 copy whole repo。

**任务**：D 6 + A/B 各 3。

**主要指标**：expand 后 hidden/pass proxy、prune 后 ratio、删除数、回归次数、tokens。

**支持**：A/B hidden pass 提升；D 的 ratio 显著下降且 hidden 保持。

**否定**：prune 无法识别 necessity，或成本爆炸。

**代码修改**：pilot 当前只有可运行 prompt-protocol arm；正式 controller 的类、接口和修改点已在 `ECSM_METHOD_SPEC.md` 定义，尚未实现，不能把 prompt arm 的收益直接称为 ECSM 算法收益。

**优先级/成本**：P0 原型；12 runs。

### E9 Executable deletion / dependency necessity test

**假设**：可执行反事实删除能提供普通依赖图没有的 necessity 信号。

**处理**：对候选文件/符号做隔离副本删除或替换，运行 output API probes + generated behavior probes；记录删后失败对应的 obligation。绝不在最终 submission 上做不可逆操作。

**任务**：D 6，随后扩到 B 4。

**主要指标**：ratio 降幅、hidden retention、necessity precision/recall、probe runtime。

**支持**：显著降低 ratio，hidden 不降；动态状态 artifact 也能被 probe 捕获。

**否定**：public-derived probes 无法保护 hidden behavior，prune 后 gap 上升。

**代码修改**：新增 `harness/featureliftbench/necessity_verifier.py`；使用临时 submission clone、缓存 evaluator build/probe；输出 `necessity_evidence.jsonl`。

**优先级/成本**：P0，论文方法关键；6 runs + 每题若干本地 probe，不新增大量模型调用。

## 5. 已冻结的主 pilot 矩阵

10 个任务（以 revision-5 freeze 和 manifest 为唯一真值）：

1. `pluggy__hook_specs_core__001`
2. `pydantic_v1__validation_error_core__001`
3. `coverage__config_merge_core__001`
4. `lark__grammar_loader_core__001`
5. `websockets__handshake_parse_core__001`
6. `boltons__iterutils_core__001`
7. `schema__nested_validate_core__hard3_001`
8. `requests_cache__cache_key_core__hard3_001`
9. `sqlparse__format_filters_core__001`
10. `celery__signal_dispatch_core__hard3_001`

七个完整矩阵 arm：Standard、Strong Prompt、Oracle Locate、Static Closure Hint、Oracle Closure、Copy-first then Prune、ECSM-Prompt。共 70 cells，按 task block 内确定性打乱 arm 顺序，并按 A/B/C 阶段投入：A 为 2 题 × 7 arms = 14 cells；B 为 4 题 × 5 arms = 20 cells；只有资源门禁触发后才补 C 的 36 cells。Stage B 只决定资源投入，不作为论文机制结论。

运行方式：

```bash
python experiments/ecsm_pilot/pilot_freeze.py verify
python experiments/ecsm_pilot/run_pilot.py --stage A
python experiments/ecsm_pilot/run_pilot.py --stage A --execute
python experiments/ecsm_pilot/analyze_pilot.py
python experiments/ecsm_pilot/run_pilot.py --stage B --execute
python experiments/ecsm_pilot/analyze_pilot.py
# 仅在 stage_b_resource_decision.json 通过后：
python experiments/ecsm_pilot/run_pilot.py --stage C --execute
python experiments/ecsm_pilot/analyze_pilot.py --require-complete
```

当前 0 个 cell 已执行。实际执行前还必须取得 Pilot-10 外部导出的明确授权；不得向 Agent 或外部服务发送 hidden tests、hidden nodeids、`behavior_contract.json` 或任何具体 hidden 输入与断言。

精确 go/no-go 阈值只以 `PILOT_DECISION_RULES.md` 为准：`Oracle Locate≈Oracle Closure` 支持 localization；`Oracle Closure≫Oracle Locate` 支持 closure；ECSM-Prompt 只有相对 Strong Prompt 至少 +2 paired hidden wins、gap 至少 -2、并满足 closure/compactness 与 ≤1.5× compute guard 才值得继续投入 Native ECSM。

## 6. 统计与报告

- 预注册 primary metrics：hidden Pass@1、public-hidden gap、closure F1；extraction ratio/final score 是 compactness 双目标。任何 hidden correctness 恶化都不能用 compactness 掩盖。
- 以 task 为配对单位，用 exact paired differences；小样本报告 bootstrap CI 和逐题结果，不只报均值。
- raw frozen、environment-adjusted、contract-clean subset 三套表并列。
- 公开所有 prompt、hint、state transition、tool trace 和失败 submission。
- 不把单 seed pilot 写成显著性结论。
