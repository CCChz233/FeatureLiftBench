# FeatureLiftBench 失败分析与人工标注规范

> **Status: current · Protocol version: v1 · Last verified: 2026-09-01**

本文档是 FeatureLiftBench 实验失败分析的操作规范。它规定如何从原始运行证据得到可复现的失败阶段、如何区分基础设施与 Agent 失败、如何进行语义根因标注，以及论文中可以使用哪些分母和结论。

本规范适用于 Python 主榜、Hard-50、候选批次和后续新增模型。历史结果可以按本规范重建，但不得因此覆盖或修改原始 `suite.json`、`run.json`、评测日志与提交目录。

## 1. 核心原则

每条未通过运行必须依次经过四层判断：

```text
证据有效性
  → 互斥首败阶段
  → 输出侧语义根因
  → 轨迹侧过程原因（可选，必须有轨迹证据）
```

必须遵守以下规则：

1. **先判断证据是否有效，再统计 Agent 失败。** 环境、依赖、冻结检查或评测器缺陷不能计入 Agent 根因分布。
2. **每条运行只有一个首败阶段。** 后续失败不重复计数。
3. **每条有效失败只有一个 primary semantic cause。** 可以添加多个 secondary tags，但不能用多标签重复扩大分母。
4. **只描述可观察事实。** 不使用“模型粗心”“没有理解”等心理推断。
5. **证据不足时标记 `unknown`。** 不为了得到完整饼图而强行归因。
6. **功能结果、过程状态和协议合规性彼此独立。** 例如，上下文违规不能覆盖功能通过或失败结论。
7. **隐藏测试只用于裁定外部行为。** 对外报告只能公开稳定契约编号和脱敏行为摘要，不公开隐藏测试名称、输入或断言。

## 2. 输入证据与优先级

每条运行优先使用以下证据：

1. `suite.json`：任务选择、运行汇总、模型和运行条件；
2. `<task_id>/run.json`：是否启动 Agent、过程状态和基础设施错误；
3. `<task_id>/eval/result.json`：Build、Public、Hidden、Isolation 和最终分数；
4. `<task_id>/eval/logs/*.stdout|stderr`：首个失败的直接错误证据；
5. `<task_id>/submission/`：实际交付的 API、模块和实现；
6. `TASK.md`、`metadata.json`、`evaluation/behavior_contract.json`：公开契约与稳定 clause ID；
7. Agent trajectory/events：搜索、读取、编辑、验证和停止过程；
8. 冻结选择、source registry、镜像 digest 和 checksum：实验身份与可复现性。

当不同来源冲突时，保留冲突并按以下原则处理：

- 功能通过以 evaluator gate 和 `final_score` 为准，不使用工作流 `run.status` 替代；
- 是否启动 Agent 以 `run.json` 中的命令、错误和运行证据为准；
- 行为归因以首个失败 gate 的日志和实际提交为准；
- 契约公平性以冻结的公开 clause、可追溯的上游行为和独立审查为准；
- 无法消解的冲突标记 `evidence_conflict`，不得进入最终论文根因比例。

## 3. 第一层：证据有效性

`evidence_eligibility` 必须取以下互斥值之一：

| 值 | 判定标准 | 论文处理 |
| --- | --- | --- |
| `valid_agent_evidence` | Agent 正常进入任务，失败可由提交或过程证据归因 | 可进入 Agent 失败分母 |
| `infrastructure_invalid` | 冻结检查、Docker、依赖安装、资源限制、API/网络或 runner 问题使任务无法被公平评测 | 修复后重跑，不计 Agent 失败 |
| `benchmark_invalid_candidate` | 测试、参考、任务契约或评测器疑似有缺陷，且失败发生在提交行为之外或契约映射存在实质冲突 | 隔离并人工裁决；裁决前不计 Agent 失败 |
| `policy_noncompliant` | 运行违反预注册的上下文、步骤、模型、镜像或其他实验条件 | 结果保留，但不能进入对应主表；按冻结替换策略处理 |
| `evidence_unavailable` | 缺少足够日志、提交或结果文件 | 不作能力结论，补证据或重跑 |

上下文、步骤和预算违规通常还应保留为独立布尔字段。若一条运行既有行为结果又有上下文违规，记录方式为：

```text
functional_pass = false
first_failure_stage = hidden_failure
context_violation = true
paper_eligibility = policy_noncompliant
```

不要把它改写为基础设施失败，也不要删除其行为证据。

## 4. 第二层：互斥首败阶段

按下列固定顺序选择最早失败 gate：

```text
preflight_blocked
  > missing_submission
  > build_failure
  > public_failure
  > hidden_failure
  > isolation_failure
  > functional_pass
```

| 阶段 | 机械判定 |
| --- | --- |
| `preflight_blocked` | Agent 未启动，冻结或运行前检查失败 |
| `missing_submission` | Agent 已启动，但没有可评测提交 |
| `build_failure` | 提交安装、构建、导入或 API collection 失败；依赖环境失败必须在有效性层改判为基础设施 |
| `public_failure` | Build 通过，公开测试失败 |
| `hidden_failure` | Build 和 Public 通过，隐藏测试失败 |
| `isolation_failure` | 行为测试通过，但原仓库依赖、禁止导入、路径访问或复制检查失败 |
| `functional_pass` | Build、Public、Hidden 和 Isolation 全部通过 |
| `stage_evidence_unavailable` | 无法重建首败阶段；这是证据缺失标记，不是 Agent 根因 |

首败阶段只回答“最先在哪一关失败”，不能单独回答“为什么失败”。

## 5. 第三层：输出侧语义根因

只有 `valid_agent_evidence` 才进入本层主分布。`root_cause_primary` 使用以下标签：

| 标签 | 定义 | 最低证据要求 |
| --- | --- | --- |
| `agent_process_non_delivery` | Agent 正常执行但没有形成可评测提交 | `run.json` 和提交目录共同证明 |
| `localization` | 提交集中在错误功能或错误模块，未触及相关实现边界 | 搜索/读取轨迹加提交证据；仅凭测试失败不能使用 |
| `contract_api_completion` | 已接近目标功能，但遗漏公开导出、成员、默认值、异常或必要行为分支 | 缺失 API、collection 错误或明确缺失行为证据 |
| `dependency_closure` | 必要 helper、类型、常量、资源、配置、注册表或传递依赖未纳入独立实现 | 提交依赖图、ImportError、资源缺失或直接调用证据 |
| `behavior_drift` | 提交实现了相似功能，但外部可观察语义不同 | 返回值、顺序、状态、解析、异常、平台或格式差异 |
| `packaging_modularization` | 逻辑基本存在，但无法作为要求的独立 `featurelifted` 包暴露 | 包布局、导出、安装或隔离证据；与环境依赖失败分开 |
| `test_gaming_narrow` | 对样例硬编码、依赖测试 fixture 或只实现明显已知用例 | 必须有代码或轨迹直接证据；Hidden 失败本身不足以证明 |
| `task_or_evaluator_defect` | 失败来自测试、任务、参考或评测器缺陷 | 失败发生在提交调用前、参考也失败、契约冲突或确定性缺陷 |
| `unknown` | 证据不足，或多个原因无法区分 | 明确记录缺少的证据和下一步检查 |

`over_copy`、`unapproved_dependency` 和 `path_source_leakage` 是质量或隔离标签，不应冒充首败语义根因。

### 5.1 Primary cause 决策顺序

1. 未产生提交：`agent_process_non_delivery`；
2. 失败发生在提交行为之外：`task_or_evaluator_defect` 或基础设施；
3. 必需模块、导出、类或方法不存在：`contract_api_completion`；
4. 缺少内部 helper、资源或传递依赖：`dependency_closure`；
5. 模块/API 存在，但签名、返回、异常、顺序或状态不兼容：`behavior_drift`；
6. 逻辑存在但独立包无法暴露：`packaging_modularization`；
7. 只有轨迹和提交直接证明定位错误时才使用 `localization`；
8. 无法稳定区分时使用 `unknown`。

### 5.2 Secondary tags

辅助标签用于描述失败触及的契约维度。推荐词表：

```text
api_surface
call_signature
argument_binding
default_values
return_value
exception_semantics
validation_boundary
ordering_precedence
state_lifecycle
registry_dispatch
parsing_normalization
tokenization
serialization_rendering
resource_loading
platform_path
data_structure_semantics
equality_protocol
packaging_export
missing_submission
```

可以新增标签，但必须在报告中给出定义，不能只为单个案例制造不可复用的同义词。

## 6. 第四层：轨迹侧过程原因

以下标签只能在阅读 trajectory/events 后使用，不能从最后一行报错反推：

- `scope_not_inspected`：没有检查必要模块或调用方；
- `contract_not_recorded`：发现相关行为但未形成契约清单；
- `dependency_not_followed`：读取入口后未追踪关键依赖；
- `probe_not_selected`：存在可执行验证条件但未运行针对性 probe；
- `stale_verification`：最后修改后未重新验证；
- `budget_exhaustion`：明确因步骤、时间或 token 结束；
- `evidence_lost_after_condensation`：必须证明信息在压缩前出现、摘要未保留且之后未再出现；
- `process_unknown`：轨迹不足或无法区分。

输出侧 `behavior_drift` 不等价于过程侧“没有理解契约”。它也可能来自实现错误、验证遗漏或预算终止。论文若要宣称过程机制，必须单独完成本层审查。

## 7. 标注记录格式

每个模型—任务运行一行，至少包含：

```text
task_id
model
split
lift_type
feature_family
evidence_eligibility
functional_pass
first_failure_stage
root_cause_primary
secondary_tags
contract_clause_ids
context_violation
evidence_summary
evidence_path
review_status
annotator
adjudicated
```

约束：

- `task_id + model + suite_id` 必须唯一；
- `secondary_tags` 和 `contract_clause_ids` 使用分号分隔；
- `evidence_summary` 只写脱敏行为事实；
- `review_status` 区分 `automatic`、`assistant_first_pass`、`human_single_review`、`human_double_reviewed` 和 `adjudicated`；
- 不使用主观概率式 confidence；证据不足直接使用 `unknown`；
- 任何有效性 override 必须写明原因并保留原始 audit class。

## 8. 实际执行流程

### A. 自动阶段

1. 校验 suite、任务选择、冻结和 source identity；
2. 提取所有 assigned tasks；
3. 识别 Agent 是否启动、是否提交；
4. 按固定顺序生成首败阶段；
5. 识别 freeze、Docker、dependency install、timeout 等基础设施结果；
6. 记录 context、step、token、API call 和过程状态，但不用于覆盖功能结果；
7. 生成待人工标注表。

### B. 单条语义审查

1. 只打开首败 gate 的日志；
2. 检查实际提交是否存在对应模块/API；
3. 将失败映射到公开 clause ID；
4. 选择一个 primary semantic cause；
5. 添加描述契约维度的 secondary tags；
6. 写一条不包含隐藏测试细节的 evidence summary；
7. 若失败发生在提交调用前或契约映射冲突，转入 task-defect 审查；
8. 若无法判断，标记 `unknown`，并写明缺少的证据。

### C. 轨迹审查（论文机制分析需要）

1. 检查 Agent 是否读取正确入口、依赖和调用方；
2. 检查是否形成完整功能/契约清单；
3. 检查是否运行 public、自建 probe、安装和 isolation；
4. 检查最后一次修改之后验证是否仍有效；
5. 将过程原因与输出侧根因分开记录；
6. 选择代表性案例，保存脱敏证据步骤 ID。

## 9. 双人复核与一致性

论文使用语义根因比例前，应进行独立人工复核：

1. 先对全部有效失败做第一轮标注；
2. 至少抽取 20%–30%，并对全部 `unknown`、task-defect candidate 和 Hidden-only 失败进行双人独立复核；
3. 第二位 reviewer 在看不到第一位标签的情况下标注；
4. 报告 Cohen's κ 或 Krippendorff's α；
5. 若一致性不足，先修改 codebook 和边界案例，再重新标注；
6. 分歧经书面规则裁决，保留原标签、复核标签和最终标签；
7. 只有实际完成独立复核后才能写 `human_double_reviewed` 或报告一致性数字。

AI 辅助的两次检查不等于两位独立人工 reviewer。

## 10. 汇总分母与论文报告

至少同时报告四个分母：

| 分母 | 用途 |
| --- | --- |
| 所有 assigned tasks | 描述整个运行包的完成情况 |
| 有 evaluator 证据的任务 | 报告机械 gate 漏斗 |
| `valid_agent_evidence` 的未通过任务 | 报告 Agent 根因比例 |
| 符合预注册实验协议的任务 | 进入最终主表 |

推荐输出：

1. Assigned → Agent launched → Submission → Build → Public → Hidden → Isolation 漏斗；
2. 互斥首败阶段分布；
3. 基础设施、题目缺陷和协议违规分布；
4. 有效 Agent 失败的 primary semantic cause；
5. 按模型、split、lift type 和 feature family 的交叉表；
6. Hidden-only 失败对应的公开 clause 覆盖与人工公平性审查；
7. 代表性案例：完整功能边界、Agent 检查范围、遗漏契约、失败证据和最小修复；
8. `unknown` 和待复核比例。

比例必须同时给出计数和分母。小样本比较应给出 Wilson 区间或 task-level bootstrap；多组探索性比较需要多重检验校正。Token、步骤、读取次数和 API calls 只能作为诊断关联，不能自动解释为因果原因。

## 11. 隐藏契约公平性

Hidden-only 失败进入论文前，至少确认：

1. 隐藏断言映射到冻结的公开 clause ID；
2. 该行为可从 TASK、上游代码、调用方、文档或已有测试中合理恢复；
3. 断言测试外部可观察行为，不锁定参考实现细节；
4. 参考实现通过；
5. 测试在隔离环境中确定性通过；
6. 没有依赖隐藏网络、时间、平台或缺失资源；
7. 映射冲突和 AI-assisted review 状态被公开记录。

未满足时使用 `benchmark_invalid_candidate`，修复并重新冻结，不能将其包装为 Agent 的契约发现失败。

## 12. 当前仓库中的实现

- 机械 gate 与候选审计：`harness/scripts/analyze_python200_hard_main.py`、`harness/scripts/audit_python200_hard_candidate.py`；
- 通用语义分类汇总：`harness/scripts/analyze_failure_taxonomy.py`；
- 当前 Python-200′ 标注：`reports/paper_analysis/python200_hard_main_20260829/failure_root_cause_annotations.csv`；
- 当前逐任务输出：`reports/paper_analysis/python200_hard_main_20260829/failure_analysis.csv`；
- 当前分析报告：`reports/paper_analysis/python200_hard_main_20260829/failure_analysis.md`；
- 历史 550-run 审计：`reports/failure_attribution_20260720/`。

对未来 suite 的建议流程：先运行 suite 分析和 evidence audit，复制当前 annotation CSV 的列结构完成第一轮标注，再用 `analyze_failure_taxonomy.py` 校验唯一性、标签合法性、覆盖率和汇总算术。
