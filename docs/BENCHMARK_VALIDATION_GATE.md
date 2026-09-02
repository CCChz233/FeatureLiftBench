# FeatureLiftBench 基准验证与发布门禁

> **Status: current · Gate protocol: v2 · Last verified: 2026-09-02**
> P0 机械门禁已落地；分析子集未发布；筛题与 Agent 评审暂停。
> 本文规定如何验证题目、如何打三态标签。不规定 Agent 方法，也不改已冻结题包。

## 1. 一句话目标

把"每条 Hidden 断言都落在公开契约内"从**由 AI 一次性标注声明的性质**，变成**可复跑、可阻断、可报精确率的检查**，并顺带把现有分散的题目校验收敛成单一发布门禁。

## 2. 为什么现在做

论文的失败归因结论建立在一个前提上：Hidden 测试不引入公开契约之外的要求。这个前提目前的支撑强度是：

| 事实 | 数值 | 来源 |
| --- | ---: | --- |
| `independent_human_review` 为 false 或缺失的任务 | 200/200 | `metadata.evaluation_spec.manual_review` |
| 标为 `ai_assisted` 的 hidden→clause 映射 | 864/1044 | `metadata.evaluation_spec.hidden_test_mappings` |
| 人工映射（`preregistered_author_mapping` + `manual_semantic_mapping`） | 24/1044 | 同上 |

也就是说，契约可追溯性目前**完全由 AI 自动标注支撑**。审稿人问"你怎么保证 Hidden 没超出契约"，现有回答是"我们让模型标了一遍"。

### 2.1 现有校验为什么不够

现有的 `constitution_validate.py` 是**声明式**检查，不是**蕴含式**检查。它验证：映射条目存在、`nodeid` 能解析、每条 behavior clause 都有测试覆盖。它不验证测试的断言是否真的落在该 clause 说的范围内。

具体反例（`aiohttp__url_params_core__hard3_001`，`spec_status: compliant`，通过现有全部校验）：

```json
{"nodeid": "hidden_tests/test_hidden_contract.py::test_invalid_header_name_raises",
 "behavior_ids": ["B002", "B003"], "mapping_method": "ai_assisted"}
```

该测试实际驱动 `CIMultiDict.__setitem__`，而 `required_api` 只声明了 `CIMultiDict.getall`；B003 只说"非法头名抛 `InvalidHeaderName`"，没说在哪个入口校验。把校验放进 `normalize_headers` 满足了每一条已声明条款，却挂在 Hidden 上。

[HIDDEN_CONTRACT_PROVENANCE.md](HIDDEN_CONTRACT_PROVENANCE.md) 已经定义了 Explicit / Recoverable / Ambiguous / Underdetermined 四档，是本设计的直接前身。但它是**一次性快照**：只覆盖 Flash Hidden 失败并集 33 题，产物 `gold: false`、`independent_human_review: false`，且声称当前候选 `unresolved_in_current_candidate: 0`。今天在 `aiohttp` 和 `python_decouple` 上查到的欠定不在那 18 题里，也没有任何机制在任务改动后重新判定。

**缺口的准确表述：已有的是"有人声称这条映射成立"的快照，缺的是"这条映射可被检验"的门禁。**

## 3. 设计原则

1. **可判定与不可判定分离。** 机械层只做有明确判定规则的检查；语义蕴含判定不可完全机械化，走裁决层。任何把两者混在一个布尔值里的设计都会同时失去可信度和可用性。
2. **裁决必须留证据和推翻理由。** 裁决层不是"人说了算"，是"人说了算并且写下为什么，且该判断可被复核"。
3. **报精确率，不报断言。** 机械层的价值取决于它相对裁决集的精确率。没有这个数字，门禁只是一堆主张。
4. **对冻结集只观测，不阻断。** Python-200′ 已冻结，门禁发现的问题进入观测台账和论文测量，不得据此静默修改已冻结题目或已发布结果。
5. **对晋升阻断。** 新题进入主榜必须通过全部 blocking 检查。
6. **只增不改。** 门禁产出新的台账文件，不写回 `metadata.json`，不触碰 `suite.json`、`run.json`、评测日志与提交目录。
7. **契约有意覆盖上游不算缺陷。** 若条款明确写出与上游不同的语义，以契约为准；Agent 照搬上游属于真实失败。这条必须写进判定规则，否则门禁会把正常题判成缺陷。
8. **三态且 fail-closed。** 每项检查只能是 `pass`、`fail` 或
   `undetermined`。缺覆盖、输入哈希不匹配、解析/API 异常、待裁决命中均为
   `undetermined`，不得伪装成通过或已确认违反。
9. **机械发现不等于最终裁决。** C1/C2/C3 的命中先形成 finding；只有证据充分
   的自动规则或裁决确认后才成为 `fail`。对新题，`undetermined` 阻止晋升，但
   仍不得写成 confirmed violation。
10. **模型不拥有发布权限。** API reviewer 只生成带引用的语义证据；最终标签由
    版本化聚合规则生成，默认只写报告。发布分析子集必须显式请求。

## 4. 五层检查

每层标注：**已有**（复用，不重建）/ **新增** / **阻断性**（blocking 用于晋升，advisory 用于冻结集）。

### L1 任务包完整性 — 基本已有

| 检查 | 状态 | 实现 |
| --- | --- | --- |
| 必需路径（`metadata.json`、`requirements.lock`、`repo/`、`public_tests/`、`hidden_tests/`、`evaluation/`、`forbidden_imports.txt`、`oracle_manifest.json`） | 已有 | `validate.py::validate_task()` |
| metadata 形状与枚举 | 已有 | `metadata.py::validate_metadata_shape()` |
| lock ↔ allowed_dependencies 一致性 | 已有 | `dependency_audit.py::validate_lock_allowed_consistency()` |
| `TASK.md` 存在且与 `public_spec` 一致 | 部分 | 仅 `spec_status: compliant` 走 `validate_constitution()`；**新增**：提为全量必需路径 |
| 参考解可定位 | 新增 | 主 split 按设计不内联 `reference_solution/`，参考解在 `benchmark/submissions/<task_id>/oracle`（当前 150/200）。门禁应检查 oracle 可定位，缺失即 blocking |

**新增工作量：小。** 两条检查加进 `validate_task()`。

### L2 契约蕴含 — 核心缺口

这是唯一需要实质新建的一层，第 5 节展开。

### L3 Oracle 有效性 — 已有但只覆盖 batch-1

`generate_gate_report.py` 已实现 G1–G4，质量很高，问题是只在 batch-1 晋升流水线里跑过：

| Gate | 判定 | 状态 |
| --- | --- | --- |
| G1_oracle | oracle 全通过，extraction ∈ [0.09, 0.60] | 已有 |
| G2_naive | naive：public 过、hidden **挂**、`functional_gate == 0` | 已有 |
| G3_copy_all | copy_all 全过且 extraction 显著高于 oracle | 已有 |
| G4_probes | 移除 probe 文件后指定 hidden 必须失败（反作弊） | 已有 `verify_module_probes.py` |
| **G2′ 原仓库直评** | 未修改的 `repo/` 直接作为提交必须失败 | **新增** |

G2 现在依赖预置的 `benchmark/submissions/<id>/naive`，不是从 `repo/` 机械生成的。补 G2′ 才能真正回答"原始仓库应失败"。

**新增工作量：中。** 主要是把 G1–G4 从 batch-1 脚本推广到全量任务，并补 G2′。

### L4 环境隔离与可复现 — 已有，缺确定性

| 检查 | 状态 | 实现 |
| --- | --- | --- |
| Docker 无网络、`no-new-privileges`、挂载白名单 | 已有 | `docker_eval.py` |
| forbidden imports / 路径访问 / 符号链接攻击 | 已有 | `checks.py`、`isolation_checks.py` |
| 依赖锁定与 vendor wheel | 已有 | `dependency_audit.py` |
| locale / timezone / hash 冻结 | 已有 | `evaluator.py` |
| **重复运行结果一致** | **新增** | 同一 oracle 连跑 N=3 次，`functional_gate` 与失败测试集合必须完全一致 |

**新增工作量：小。** 一个循环加一次集合比较。建议 N=3，只在晋升时跑，全量重跑成本太高。

### L5 难度与泄漏 — 部分已有

| 检查 | 状态 |
| --- | --- |
| `TASK.md` 不得提及 `hidden_tests/`、`evaluation_spec`、`oracle_manifest` | 已有（`_validate_task_leakage()`） |
| agent workspace 不得含测试与参考解 | 已有（v2/v3 readiness audit） |
| **public_tests 与 hidden_tests 不得等同或高度重叠** | **新增** |
| 基础设施失败不计入难度 | 已有，属失败分析层（见 [FAILURE_ANALYSIS_PROTOCOL.md](FAILURE_ANALYSIS_PROTOCOL.md)） |

public≡hidden 检查建议用**归一化 AST 比较**而非文本 diff：剥离注释、docstring、变量名与字面量后比较断言结构，报告重叠率。阈值先设为 advisory，收集分布后再定 blocking 线。

**新增工作量：小。**

## 5. L2 契约蕴含：核心设计

### 5.1 输入与合法信息边界

判定只能使用 Agent 实际可见的两个来源：

- `metadata.public_spec` 及其渲染产物 `TASK.md`；
- source registry 中经 archive/tree SHA 校验的 canonical full source 快照。

历史 task-local `repo/` 仅作 provenance 或旧协议复现，不能替代 v3
Full-Repository 的 canonical source。若 canonical archive 缺失、摘要不匹配或
无法物化，相关 C2/C3/API 语义审查必须标为 `undetermined`。

**不得**把 `hidden_tests/` 内容当作"可恢复"的依据。这条与 [HIDDEN_CONTRACT_PROVENANCE.md](HIDDEN_CONTRACT_PROVENANCE.md) 一致。

### 5.2 机械层：四项可判定检查

已在 `harness/scripts/audit_contract_entailment.py` 实现前三项，第四项待补。

| 检查 | 判定规则 | 阻断性 |
| --- | --- | --- |
| **C1 未声明接口面** | AST 解析 hidden 测试，抽取经 `featurelifted` 导入符号驱动的成员（含 `__setitem__` / `__getitem__` / `__contains__` 等 dunder，通过局部数据流归属到类）；不在 `required_api` 路径或 members 中的即命中。函数返回值按签名返回类型归属，避免把 `f()` 的成员误记到 `f` 上 | blocking |
| **C2 入口锚定** | `public_spec.source_entrypoints` 的每个符号必须能在固定 `repo/` 中找到定义（模块级 def/class/assign、类方法、模块名，均计入）。指空即命中 | blocking |
| **C3 上游蕴含探针** | 把 `repo/` 按 `required_api` 重导出为合成 `featurelifted` 包，跑 hidden 行为用例。**断言级**失败 → `upstream_contradicts`；**形状级**失败（ImportError / TypeError / AttributeError / 任务新造名字的桩） → `api_reshaped`，探针对该题不下结论 | advisory |
| **C4 public≡hidden 重叠** | 归一化 AST 比较，见 L5 | advisory |

C1 的作用域绑定必须满足：类体局部绑定不得泄漏进函数作用域；局部变量被未知
返回类型重新赋值时必须清除旧类型绑定。Graphene 回归用于假阳性保护，
`CIMultiDict.__setitem__` 用于真命中保护。

C1/C2 的可复跑打标步骤见第 13 节。那套协议只覆盖已经能稳定执行的检查，不是本门禁五层全部落地。

C3 的关键设计点，都来自实测踩过的坑：

- **必须校验加载的是固定快照。** 任务 `repo/` 多为剪枝后的目录且**无 `__init__.py`**，会被系统安装的同名包遮蔽（namespace portion 输给后面的 regular package）。合成包内需在导入后校验 `__file__` 落在 `repo/` 下，并清除预导入的同名顶层模块，否则探针在测系统装的库。
- **任务新造的 API 名要打桩而非直接判缺陷。** 把上游 API 改名、重组、扩参是 benchmark 的题设本身，不是缺陷。
- **形状级失败会遮蔽断言级矛盾。** 例：`python_decouple` 的探针停在 `Config(environ=)` 的 `TypeError`，够不到那条真正矛盾的断言。这类只能靠裁决层，C3 的 `upstream_contradicts` 计数因此是**下界**。
- **上游是测试框架本身时探针失效。** `pytest__marker_registry_core__hard3_001` 在运行中的 pytest 里加载 pytest 快照，fixture scope 解析直接崩。需要 out-of-process runner，或直接标为不可判定。

### 5.3 裁决层

机械层判不了的进裁决队列。裁决可由 API reviewer 先做证据审查，再由独立复核
或 maintainer 确认。裁决使用
[HIDDEN_CONTRACT_PROVENANCE.md](HIDDEN_CONTRACT_PROVENANCE.md) 已有的四档，
不另造语义公平性词表：

| 档 | 门禁含义 |
| --- | --- |
| `Explicit` | 契约写明，题目公平 |
| `Recoverable` | 契约未逐字写，但 `repo/` 有唯一明确实现，题目公平 |
| `Ambiguous` | `repo/` 有 ≥2 套说得通的目标行为，合法信息无法唯一决定 |
| `Underdetermined` | 仅凭 spec + repo 无法确定 Hidden 要的观测，且该观测未写进 `public_spec` |

裁决记录格式（现已落在 `reports/paper_analysis/python200_hard_main_20260829/contract_entailment/adjudications.csv`）：

```text
task_id, verdict, reason
```

`verdict ∈ {underdetermined, fair, undecided}`，`reason` 必须包含可复核的具体证据（条款原文、上游行为、命中的接口面）。`undecided` 表示机械层结果被判为不可用（如 C3 的框架自加载），该题的机械探针结论作废，回落到静态检查。

API surface 合规与 Hidden 语义公平是两个正交字段：

- `surface_compliance`：Hidden 行使的成员是否由 `required_api` 显式声明；
- `hidden_fairness`：Hidden 观测是否为 `Explicit` / `Recoverable`，或属于
  `Ambiguous` / `Underdetermined`。

因此，一道题可以 `hidden_fairness=fair`，同时因缺少显式 dunder/member 而
`surface_compliance=fail`。不得用“语义上自然”逐题豁免已发布的显式 API 规则；
若标准要允许隐式 Python protocol，必须先全局修订 TASK_DESIGN_RULES 并升协议版本。

**裁决必须能推翻机械层，且推翻要记录。** 实测中两次推翻分别是：

- `pygments__lexer_core__001`：机械层报 `upstream_contradicts`。条款 B004 明确写了 `stripall option removes whitespace tokens`，上游只剥输入首尾空白。**契约有意覆盖上游且写明了**，裁决为 `fair`，Agent 照搬上游属真实失败。
- `multidict__multidict_mutation_core__hard3_001`：机械层报 `upstream_contradicts` + C1 命中。B002 明确写了 `popone removes the most recent matching value`；`__getitem__` 是映射类型的固有接口且 B004 写了 `lookup`。裁决为 `fair`。

这两条同时说明：**没有裁决层的纯机械门禁会把正常题判成缺陷**。

### 5.4 API reviewer

`--api-review` 对每道题执行统一的语义审查。输入包括 public contract、Hidden
测试、test↔behavior/API 映射、机械 findings，以及从 canonical source 中提取的
带路径证据。输出必须是结构化 JSON，并至少包含：

- `surface_compliance` 与 `hidden_fairness`；
- behavior ID、hidden nodeid、API path；
- canonical source 文件路径和证据摘要；
- `verdict ∈ {fair, underdetermined, undecided}` 与可复核理由；
- reviewer model、prompt version、请求/响应摘要和 token/cost（若供应方返回）。

模型未返回合法 JSON、引用不存在、输入超限、调用失败或证据不足时，结果为
`undetermined`。模型输出不能直接写 metadata、selection 或 freeze。

API reviewer 默认关闭。启用时必须显式确认 private evaluator 数据策略；只允许
使用明确不训练/不保留该数据的接口或本地模型。门禁记录 endpoint 的非秘密标识、
模型和策略确认，但绝不写入 API key。

仓库本地配置可通过 `--review-env-file .env` 安全读取；模型名必须使用目标
OpenAI-compatible endpoint 接受的原生名称（DeepSeek 官方端点示例为
`deepseek-v4-flash`，而不是 Agent/LiteLLM 的 `deepseek/deepseek-v4-flash`）。
canonical source 只发送围绕声明入口符号的带行号有界摘录，不发送完整上游仓库。

### 5.4.1 Validator Agent v2.3（默认语义路径）

`--agent-review` 是面向规模化审计的默认语义路径。它不是开放式 coding Agent，
而是一个只读、受预算约束的状态机：

1. 初始只接收 public contract、Hidden nodeid↔behavior 索引、声明的
   `source_entrypoints` 和机械 findings；
2. `inspect_hidden` 每轮只能读取索引中明确列出的少量 nodeid，工具只返回该测试
   函数的带行号摘录；
3. `inspect_source` 返回的就是本题 **canonical pinned upstream**，这就是要审的实现，
   不存在另一份 featurelifted 源码树。`featurelifted.*` 只是抽取包别名，上游包名不是缺陷。
   禁止 import 上游的 Hidden 约束针对 Agent 提交，不针对 canonical source。
   C1 机械 clear 且已检查 hidden 时，不得把 `surface_compliance` 标成 `undetermined`，
   也不得仅因包名重命名而 `fail`；C1 机械命中则必须 `fail` 并引用那些成员；
4. `submit` 必须返回固定 JSON。确定性校验器拒绝未检查 nodeid、未知 behavior/API、
   未提供的 source path、空 finding 和无理由结论。符号名会尽量归一成已检文件路径；
   机械层命中的未声明成员（含 `featurelifted.` 前缀）可以引用。提交若只是引用格式
   失败，给一轮定向修补，不立刻结案；
5. 默认 `reasoning_effort=low`、最多 6 轮、40k 总 token、60k 上下文字符。重复动作、超预算、超时、非法
   JSON 或越权查询一律 fail-closed 为 `undetermined`；
6. Agent **只标不合格、不改题**。`surface_compliance` 与 `hidden_fairness` 正交：
   Hidden 可以语义公平，同时因缺少显式 dunder 而 surface fail。声称 fair+pass 才必须
   看完所有 mapped nodeid；仅报 surface 不合格时只需引用已检查的 nodeid；
7. 默认只升级 C1/C2 为 `undetermined` 的题；`--agent-review-all-selected` 仅用于
   校准时加入机械层清楚的负对照。通过校验的 `confirmed_violation` 写入
   `agent_unqualified.csv`，供人改题，不写 metadata / selection / freeze。

报告只保存动作、请求对象、证据摘要 hash、token usage 和最终结构化 review，
不保存 API key，也不把 Agent 输出直接写入 selection、metadata 或 freeze。Agent
结论仍是待裁决证据，最终发布必须经过独立裁决层。

OpenAI-compatible 请求启用原生 JSON Output（`response_format=json_object`），并在
输出截断或空 JSON 时最多执行一次更高输出预算的协议恢复；恢复仍受任务总 token
上限约束，禁止用启发式字符串修补伪造结构化结果。

三题校准命令：

```bash
PYTHONPATH=harness python3.12 -m featureliftbench.cli validate-benchmark \
  --benchmark python200_hard \
  --task-id graphene__schema_execute_core__001 \
  --task-id aiohttp__url_params_core__hard3_001 \
  --task-id multidict__multidict_mutation_core__hard3_001 \
  --agent-review --agent-review-all-selected \
  --review-model deepseek-v4-flash --review-env-file .env \
  --review-api-key-env FEATURELIFTBENCH_API_KEY \
  --acknowledge-private-evaluator-policy
```

### 5.5 为什么这一层值得单独建

C1 与 C2 都是**静态、不依赖运行环境**的，可以对全部 200 题稳定给出判定，并且能抓到现有 `constitution_validate.py` 结构性漏掉的问题（C1 抓到的 aiohttp `__setitem__` 通过了现有全部校验）。C3 依赖环境，覆盖率有限，但它提供的是另外两项给不出的证据类型。

## 6. 门禁判定与阻断策略

每项 check 聚合后均为三态。任务标签按固定优先级生成：

```text
存在 confirmed fail                 → violates
否则存在 undetermined / pending      → undetermined
否则全部 required checks pass        → meets_standard
```

晋升新题时，`fail` 和 `undetermined` 都阻止发布，但两者必须分报。冻结集上全部
检查只写台账，不改题、不改已发布结果。机械命中尚未裁决时只能进入
`adjudication_queue.csv`，不能进入 confirmed violations。

冻结集用 advisory 是硬约束：Python-200′ 已冻结，任何据门禁静默改题都会让已有实验结果失去可比性。发现问题的正确处理是**记录 + 下一次 freeze 时修复**，与 [FAILURE_ANALYSIS_PROTOCOL.md](FAILURE_ANALYSIS_PROTOCOL.md) 第 11 节的 `benchmark_invalid_candidate` 流程对接。

## 7. 产物格式

单一入口产出一份带版本的台账，可 diff、可引用：

```text
reports/benchmark_gate/<suite>_<date>/
  manifest.json             # gate/prompt 版本、suite/source/evidence 输入 SHA
  gate_report.json          # 逐题逐检查结果 + 门禁版本 + 输入 SHA
  gate_report.md            # 人读汇总
  tasks/<task_id>.json      # 单题可复查记录
  findings.jsonl            # 机械/API findings
  adjudication_queue.csv    # 待裁决项
  adjudications.csv         # 已完成裁决（可选输入）
  meets_standard.txt
  violates.txt
  undetermined.txt
  precision.md              # 机械层相对裁决集的精确率
```

`gate_report.json` 每题一条：

```text
task_id
gate_version
input_identity: {task_revision, spec_hash, task_tree_sha256, source_tree_sha256}
checks: {C1: {status, mechanical_result, adjudication, evidence}, ...}
blocking_failures: []
advisory_findings: []
manual_verdict, manual_reason
```

同一题在两次运行间的状态变化必须可 diff——门禁的价值在于回答"上次改动之后基准还成不成立"，而不只是给一次快照。

## 8. 精确率报告（论文所需）

裁决集是机械层的参照真值。至少报告：

| 指标 | 定义 |
| --- | --- |
| C1 精确率 | C1 命中中，经裁决确认 owner 归属正确且缺少显式声明的比例 |
| C2 精确率 | 命中 C2 的题中，经人工确认符号确实缺失的比例 |
| C3 精确率 | 报 `upstream_contradicts` 的题中，裁决未推翻的比例 |
| 覆盖率 | 机械层能下判定的题数 / 总题数 |
| 推翻数 | 裁决推翻机械层的条数（分方向：漏报 / 误报） |

召回率需要独立人工抽样才能估计：从机械层判为"无问题"的题中随机抽 20–30%，人工按四档标注，统计漏报。**没有这一步不能声称召回率。**

当前基线（25 题失败集，见 `reports/paper_analysis/python200_hard_main_20260829/contract_entailment/`）：契约欠定 2 题、入口溯源缺陷 5 题、机械层误报 2 题（被裁决推翻）。样本太小，不能作为论文数字，但结构可用。

## 9. 实施阶段

### P0 — 把已有的审计升格为门禁（1–2 天）

1. `harness/scripts/audit_contract_entailment.py` 已实现 C1/C2/C3 与裁决通道；补 C4，加 `gate_version` 与输入 SHA。
2. 新增统一只读入口，接入三态聚合、canonical source identity、API reviewer
   与裁决队列；API reviewer 保持 opt-in。
3. 跑满 200 题，产出第一份 `gate_report`，不得自动覆盖 analysis selection。
4. 对机械/API 命中完成裁决，并对机械无命中题分层抽样，产出 `precision.md`。

**产出即论文素材**：这一步结束就能回答"契约欠定占多少、机械层多准"。

### P1 — 合并为单一发布门禁（3–5 天）

1. 新增 `scripts/run_benchmark_gate.py`，串联 L1–L5，复用现有 `validate_task()`、`generate_gate_report()`、`verify_module_probes.py`，不重写。
2. 补 L1 的 `TASK.md` 必需性与 oracle 可定位、L3 的 G2′、L4 的 N=3 确定性、L5 的 public≡hidden。
3. 把 G1–G4 从 batch-1 推广到全量。
4. 接 CI：晋升 PR 上 blocking，`benchmark/**` 变更上跑 advisory。当前 CI 只有 `eval-oracles.yml` 的 oracle 冒烟。

### 发布派生分析子集

发布不是普通 gate run 的副作用。仅当父套件被精确覆盖、三类标签互斥完备、
`undetermined=0`、所有输入 SHA 匹配且裁决文件可复核时，显式
`--publish-selection` 才可写 analysis selection。产物必须记录父 freeze/suite
identity、gate protocol、prompt、evidence、adjudication 和 task-set SHA；原始
Python-200' 资产保持不变。

### P2 — 外部验证（可选，但决定论文分量）

把 C1/C2 跑到外部 benchmark（SWE-bench 等）。这两项是静态的，移植成本主要在适配它们的契约表述。**这一步是把门禁从"自证清白"抬成"领域测量工具"的唯一途径。**

## 10. 与现有机制的关系（不要重建）

| 现有 | 关系 |
| --- | --- |
| `validate.py::validate_task()` | L1 主体，直接复用 |
| `constitution_validate.py` | 保留声明式检查；L2 是它的语义补充，不是替代 |
| `generate_gate_report.py` G0–G5 | L3 主体，推广覆盖范围 |
| `verify_module_probes.py` / `verify_all_oracles.py` | L3 反作弊与 oracle 复验，直接复用 |
| `scripts/check_task_lifecycle.py` | split 规则与跨 split 重复，纳入 L1 |
| `audit_v2/v3_main_readiness.py` | no-hint workspace 与 capsule，纳入 L5 |
| `docs/HIDDEN_CONTRACT_PROVENANCE.md` | L2 裁决词表的来源；本门禁把它从快照变为可复跑检查 |
| `.agents/skills/featureliftbench-validate-task` | 人工/Agent 入口，改为调用统一门禁 |

## 11. 论文中怎么写

**不要写成"我们做了一个五层验证工具"。** 每篇 benchmark 论文都声称验证过，审稿人视为 hygiene，最多进 artifact appendix。且当前 contribution 1（Benchmark asset）已隐含此项。

**写成测量结果：**

> 智能体编程基准的失败归因，只有在 Hidden 测试可由公开契约蕴含时才成立。我们把该性质形式化为可检验属性，实现检查器，并报告它重新归类了多少此前归于 Agent 的失败。

可信度取决于三件事，前两件已有证据：

1. **能在自己的基准上抓出真问题**——已抓到，且是现有全部校验漏掉的（C1 命中 aiohttp `__setitem__`）；
2. **能展示假阳方向**——`pygments`、`multidict` 机械层报缺陷、裁决推翻为真实 Agent 失败。这一条比抓到缺陷更有说服力，它证明这是有判别力的仪器而非一份牢骚；
3. **能跑到别人的基准上**——P2，未做。

必须同时披露：L2 不可完全机械化、机械层精确率、召回率是否经独立抽样、裁决是否为独立人工（当前全部为 AI 辅助，`gold: false`）。

## 12. 已知限制

1. **语义蕴含判定不可完全机械化。** C3 的形状级失败会遮蔽断言级矛盾，`upstream_contradicts` 是下界。
2. **C3 覆盖率受环境限制。** 剪枝快照缺 `__init__.py`、缺第三方依赖，实测 25 题中 13 题无法判定。要提高覆盖需按题 `requirements.lock` 建环境或在评测镜像内跑。
3. **裁决目前是 AI 辅助，不是 human gold。** 与现有 `manual_review.independent_human_review: false` 同样的限制，论文中不得表述为独立人工复核。
4. **门禁本身需要被验证。** 精确率与召回率数字若由同一套 AI 流程产生，说服力有限；至少召回率抽样应由独立标注者完成。
5. **对冻结集不可阻断。** 门禁发现的冻结集问题只能进观测与修复队列，不能改变已发布结果。

---

## 13. 标准符合性标注协议（v2）

原独立文档 `BENCHMARK_STANDARD_LABELING.md` 已并入本节。日常机械检查用 `scripts/run_benchmark_gate.py`；`scripts/label_benchmark_tiers.py` 是旧打标驱动，筛题暂停。

>
> v1 的二分类（`meets_standard` / `violates`）及据此写出的 163/37 名单是
> **provisional / superseded pending v2 adjudication**，不能当作最终论文数字。

本文规定如何判定一道 FeatureLiftBench 题目是否符合已发布的出题标准，以及如何把判定落成可复跑标签。

标准本身在 [TASK_DESIGN_RULES.md](TASK_DESIGN_RULES.md)。五层门禁见上文。本节规定**怎么检、怎么标、怎么发布**，不改标准，也不改已冻结的 200 道题包。

当前套件上的候选标签只写在 [STATUS.md](STATUS.md) 和
`reports/paper_analysis/benchmark_tiers_v2_candidate/`。本文不维护题数。v1 产物留在
`reports/paper_analysis/benchmark_tiers/`，供对照，不得再覆盖。

## 13.1 何时使用

在下列任一情况下按本协议重跑：

- 新题要进入主榜或论文子集；
- 已有题目改了 `public_spec`、测试、`repo/` 或参考解；
- 需要从一套题里筛出符合标准的子集做分析或实验；
- 换了一套 `task_root`，不能沿用另一套题的旧评审或旧标签。

失败归因仍走 [FAILURE_ANALYSIS_PROTOCOL.md](FAILURE_ANALYSIS_PROTOCOL.md)。本协议只给题目本身打标签，不给某次 Agent 运行打标签。

## 13.2 权威与原则

1. **以写出的条款为准。** 不得用「AI 标的 / 人标的」代替条款判定。独立人工审核不是硬门禁（[07_incremental_task_rules.md](reference/07_incremental_task_rules.md) 原则 7）。
2. **三态、fail-closed。** 证据不足、审计缺失、解析失败、机械命中尚未裁决，一律 `undetermined`，不得记成 `violates`，也不得记成 `meets_standard`。
3. **机械命中不是违反。** C1 检测命中和 `source_entrypoints` 的 `dangling` 先进入裁决队列。只有裁决写成 `confirmed_violation` 才变成 `violates`。
4. **对当前题包重检。** 另一套 `task_root`、已过期的 `spec_hash` / `task_revision`、输入哈希不匹配的审计，都不能当作本套件的标签依据；应标 `undetermined` 或先刷新审计。
5. **检查器漏检不等于条款通过。** 现有 `validate_constitution` 抽不到下标/包含运算对应的 dunder。`R-SURFACE` 按门禁 C1 的数据流抽取执行。
6. **行为句子里出现名字不等于声明了路径。** §2.1 规则 2 要求成员用完整路径写入 `required_api`。
7. **不改 R-SURFACE 的规范含义。** Hidden 在语义上公平，与 `required_api` 是否按现行标准显式声明了 `__getitem__` 等协议方法，是两件独立的事。不得为了留题把「缓存天然支持下标」解释成已声明。若要允许隐式 Python Protocol，必须先全局修改 `TASK_DESIGN_RULES`，定义可推导的 protocol，再统一重标 200 道，禁止逐题豁免。
8. **对冻结集只观测。** 默认只写 `reports/`。不写回 `metadata.json`，不改冻结题包，不静默覆盖 v1 标签或正式分析名单。

## 13.3 标签

每道题恰好一个标签。逐条规则先得到 `pass` / `fail` / `undetermined`，再按下面的优先级聚合：

```text
存在 confirmed fail → violates
否则存在 undetermined → undetermined
否则 → meets_standard
```

| 标签 | 条件 |
| --- | --- |
| `meets_standard` | 所有强制条款都有证据且通过 |
| `violates` | 至少一个条款被确认违反 |
| `undetermined` | 审计缺失、解析失败、命中等待裁决、输入哈希不匹配，或证据不足 |

不得另造 A/B/C/D、完美/可修/需人工 等第二套分级。修复代价可以从违反条款推出来，但不是标签。

下列情况必须是 `undetermined`，不能冒充违反：

- 本题不在 constitution / oracle / 入口审计覆盖内；
- `strict_validation.valid` 或 `runnable_validation.valid` 字段缺失；
- 审计文件缺失或与当前题包输入哈希无法证明一致；
- C1 访问器抛错或 hidden 测试无法解析；
- C1 机械命中尚未裁决；
- `R-ENTRY` 的 `dangling` 或 `undecidable` 尚未裁决（动态定义 / 元类可能造成假阳性）。

## 13.4 检查条款

每条规则保存：

```json
{
  "rule": "R-SURFACE",
  "status": "pass | fail | undetermined",
  "mechanical_result": "clear | hit | error",
  "adjudication": "not_needed | pending | confirmed_violation | false_positive | insufficient_evidence",
  "evidence": [],
  "input_sha256": "..."
}
```

| 条款 | 出处 | 机械通过 | 机械命中后 | 实现 |
| --- | --- | --- | --- | --- |
| `R-PACKAGE` | TASK_DESIGN_RULES §1–§4 | `validate_constitution` 的 strict 与 runnable 均显式 `valid: true`，且本题在审计覆盖内 | 显式失败 → `fail`；缺覆盖或缺 `valid` → `undetermined` | `scripts/audit_python200_contract_closure.py` |
| `R-ORACLE` | 参考解必须是稳定 oracle | 本题在三轮 Docker 复验覆盖内，且未进入 failed / unstable | 复验失败/不稳定 → `fail`；未覆盖或输入哈希无法证明一致 → `undetermined` | `scripts/revalidate_python200_prime_oracles.py` |
| `R-SURFACE` | TASK_DESIGN_RULES §2.1 规则 1、§4.2.4；门禁 C1 | hidden 测试行使的 `featurelifted` 成员 ⊆ `required_api` 声明路径（含 `members`，含 `__getitem__` / `__setitem__` / `__contains__`） | `hit` / `error` → 先裁决，不得直接 `violates` | `harness/scripts/audit_contract_entailment.py` 的 C1 访问器 |
| `R-ENTRY` | 门禁 C2 | 本题在入口审计覆盖内，且最差判定不是 `dangling` / `undecidable` | `dangling` 先裁决；`undecidable` 为 `undetermined` | `harness/scripts/audit_source_entrypoints.py` |

`misplaced` 与 `resolved`、以及未声明 `source_entrypoints` 的 `undeclared`，本条款机械通过。`dangling` 因为动态定义可能假阳性，必须人工看过再确认违反。

未纳入 v2 标签、但标准里存在的项：

| 项 | 为什么不进 v2 |
| --- | --- |
| 门禁 C3 上游蕴含探针 | 依赖按题环境，覆盖不稳定；`upstream_contradicts` 是下界 |
| 门禁 C4 public≡hidden 重叠 | 尚未实现 |
| `evaluation_spec` 与 `evaluation/behavior_contract.json` 双份映射漂移 | constitution 映射已通过时，这不是 Agent 可见契约条款 |
| `review_status` / 独立人工审核 | 原则 7：不是硬门禁 |
| 契约承诺多于 hidden 检查 | §4.2.6 允许 public 做浅层 smoke |
| 另一套件上的历史评审 | 不是当前 `task_root` |

后两条若要升级进标签，必须先写成可判定规则并改本协议版本号，不得靠一次性名单。

Oracle 不必每次重跑 Docker：若题包、reference、evaluator 与已有复验输入哈希完全一致，可复用 `summary.json`。无法证明一致时标 `undetermined` 或重跑，不得把缺证据写成违反。

## 13.5 操作步骤

对论文主套件，在仓库根目录执行。先刷新证据（若输入已变），再打标，再裁决，最后才发布名单。

### 13.5.1 刷新 constitution 审计

```bash
python3.12 scripts/audit_python200_contract_closure.py \
  --suite benchmark/selection/python200_hard_suite.json \
  --output reports/contract_closure_hard200_refresh
```

`--suite` 必须指向**本题集**的 suite JSON，不能指向 `benchmark/selection/python200_suite.json`。后者的 `task_root` 是 `benchmark/python200_tasks/`。

### 13.5.2 刷新入口审计

```bash
python3.12 harness/scripts/audit_source_entrypoints.py \
  --tasks benchmark/python200_hard_tasks \
  --output reports/paper_analysis/source_entrypoints_audit
```

### 13.5.3 确认 oracle 复验覆盖本题集

已有产物：`reports/audits/python200_prime_oracle_revalidation/summary.json`。

套件或参考解变了必须重跑：

```bash
python3.12 scripts/revalidate_python200_prime_oracles.py
```

该步骤需要评测镜像，耗时长。题包未变则复用现有 summary，但必须确认 `runs[].task_id` 覆盖当前 `task_root` 的每一道题。

### 13.5.4 生成 v2 候选标签

对完整 200 道运行。不要只跑旧的 26 道 C1 命中，也不要重跑 v1 打标命令。

```bash
python3.12 scripts/label_benchmark_tiers.py \
  --tasks-root benchmark/python200_hard_tasks \
  --constitution-audit reports/contract_closure_hard200_refresh/machine_audit.json \
  --entrypoints-audit reports/paper_analysis/source_entrypoints_audit/source_entrypoints_audit.json \
  --oracle-summary reports/audits/python200_prime_oracle_revalidation/summary.json \
  --output reports/paper_analysis/benchmark_tiers_v2_candidate
```

参数可省略；上面就是默认值。默认**只写** `reports/paper_analysis/benchmark_tiers_v2_candidate/`。

禁止：

- `--output reports/paper_analysis/benchmark_tiers`（拒绝覆盖 v1 报告）；
- 不加 `--write-selection` 却期望改正式名单（默认不写）；
- 在 `undetermined` 仍非空时加 `--write-selection`（拒绝发布）。

不要加 `--write-metadata`。冻结题包禁止写回 `metadata.json`。

### 13.5.5 裁决机械命中

打开 `adjudication_queue.csv`。每个 C1 命中至少记录：

- hidden 测试文件和 nodeid；
- 被推断的对象类型；
- 使用的成员，例如 `Cache.__getitem__`；
- `required_api` 中是否显式存在；
- 对应 behavior；
- 上游测试、文档或源码证据；
- `confirmed_violation` / `false_positive` / `insufficient_evidence`；
- 裁决理由和裁决 provenance。

`dangling` 入口同样裁决。同一题若同时命中 C1 与 dangling，只裁决一次，但分别记录规则结论。

C1 未命中的题中分层抽查约 20 道，用于估计漏报。否则论文只能报告检测器精确率，无法说明召回风险。

把裁决写入 `adjudications.csv`（与队列分开，避免被脚本覆盖）：

```text
task_id,rule,verdict,hidden_file,nodeid,inferred_type,member,in_required_api,behavior,upstream_evidence,rationale,provenance
```

`verdict` 只能是 `confirmed_violation` / `false_positive` / `insufficient_evidence`。然后带着该文件重跑 §5.4。

### 13.5.6 核对候选

打开 `reports/paper_analysis/benchmark_tiers_v2_candidate/labels.md`。确认：

- 分母等于当前 `task_root` 下的题目数，且等于父套件 200；
- `meets_standard_candidate.txt` ∪ `violates_confirmed.txt` ∪ `undetermined.txt` = 全套；
- 三者两两不相交。

数字写入 [STATUS.md](STATUS.md) 时必须标明是 v2 **候选**还是已发布。本协议和 `labels.md` 冲突时，以本次命令产出的 `labels.json` 为准。

## 13.6 产物

默认输出目录：`reports/paper_analysis/benchmark_tiers_v2_candidate/`。

| 文件 | 用途 |
| --- | --- |
| `labels.json` | 逐题标签、逐条规则对象、输入哈希；机器可读权威 |
| `labels.md` | 人读报告 |
| `meets_standard_candidate.txt` | 当前机械+已裁决后符合标准的 task_id |
| `violates_confirmed.txt` | 已确认违反的 task_id |
| `undetermined.txt` | 待定的 task_id |
| `adjudication_queue.csv` | 待人工裁决的规则命中 |

`labels.json` 必须记录 `protocol_version`、`gate_version`、父套件哈希、任务输入哈希、审计证据哈希、裁决文件哈希。

不要在这一步生成正式 `python200_hard_standard_suite.json`。

## 13.7 换套件或换批次

1. 准备该套件自己的 suite JSON（含 `task_root` 与 `task_ids`）。
2. 对**那个** `task_root` 重跑 §5.1–§5.3，输出到单独目录，不要覆盖论文套件的 refresh。
3. 用对应路径调用 `label_benchmark_tiers.py`，`--output` 也换目录，不要指向 v1 的 `benchmark_tiers/`。
4. 禁止把 `python200_tasks` 的评审、`spec_hash` 已变的旧审计、或只含 Hidden 失败子集的 C1 快照，当作新套件的标签。

例：给 staging 打标：

```bash
python3.12 scripts/audit_python200_contract_closure.py \
  --suite benchmark/selection/<staging_suite>.json \
  --output reports/contract_closure_staging
python3.12 harness/scripts/audit_source_entrypoints.py \
  --tasks benchmark/staging \
  --output reports/paper_analysis/source_entrypoints_staging
python3.12 scripts/label_benchmark_tiers.py \
  --tasks-root benchmark/staging \
  --constitution-audit reports/contract_closure_staging \
  --entrypoints-audit reports/paper_analysis/source_entrypoints_staging/source_entrypoints_audit.json \
  --oracle-summary <该套件的 oracle summary.json> \
  --output reports/paper_analysis/benchmark_tiers_staging_v2
```

没有覆盖该 `task_root` 的 oracle summary 时，不要用论文套件的 summary 凑数：未覆盖的题必须标 `R-ORACLE` 的 `undetermined`。

## 13.8 发布分析名单

只有同时满足下列条件，才允许显式 `--write-selection`：

```text
meets ∪ violates ∪ undetermined = 200
三者两两不相交
undetermined = 0
所有证据哈希匹配
```

发布冻结的是**选择关系**，不是重新冻结或修改 200 道题：

```text
父 Python-200′ freeze hash
+ protocol v2 hash
+ 审计证据 hash
+ adjudication hash
+ 最终 task-id set hash
```

写出：

- [`benchmark/selection/python200_hard_standard_suite.json`](../benchmark/selection/python200_hard_standard_suite.json)
- [`benchmark/selection/python200_hard_excluded.json`](../benchmark/selection/python200_hard_excluded.json)
- `harness/config/experiments/python200_hard_standard.txt`
- `benchmark/suites.toml` 中的分析 suite（如需改别名，与发布同一提交）
- [STATUS.md](STATUS.md) 与论文中的标准子集数量

在此之前，`--benchmark python200_hard_standard` 指向的仍是 **v1 provisional** 163 名单，不得当作 v2 最终分析集，也不得据此开新实验。

- **修题：** 按已确认的 `failed_rules` 修对应条款。`R-SURFACE` 是把 hidden 用到的成员写入 `required_api.members`，或从 hidden 删除该用法。`R-ENTRY` 是把 `source_entrypoints` 改成 pinned `repo/` 里存在的符号，或删掉编造的指针。
- **不修冻结主表上的题来制造方法增益。** TASK_DESIGN_RULES §9.4。
- **修完必须从 §5.1 重跑。** 标签不是一次性清单。

## 13.9 与上文五层门禁的关系

上文 仍是五层发布门禁的设计。本协议是其中已经可以复跑的子集：

- L1 的 constitution 部分 → `R-PACKAGE`
- L2 的 C1 → `R-SURFACE`
- L2 的 C2 → `R-ENTRY`
- L3 的 oracle 复验 → `R-ORACLE`

C3、C4、G2′ 原仓库直评等未进 v2。把它们加进标签时，增加条款 ID、升协议版本，并保持三态，不要恢复按修复代价或标注者分档。

## 13.10 已知限制

1. C1 访问器只跟踪「绑定到已声明类之构造的局部变量」。经工厂函数、多层返回值或反射到达的成员可能漏检。因此必须对未命中题做分层抽查。
2. `R-ENTRY` 只检查符号存在，不检查是否为该题真正该引用的实现。`dangling` 对动态构造可能假阳性。
3. `R-SURFACE` 不检查行为条款是否被 hidden 真正验证；它只检查接口面声明。§2.2 的「前置条件 · 操作 · 可观察结果」目前没有机械检查。
4. Hidden 语义公平与 API surface 显式声明是两件事。C1 命中可以是「hidden 合理、题包未声明」，这仍是当前标准下的 surface 问题，不是把协议方法改成隐式通过的理由。
5. 主实验交叉表来自可选的 `task_portability.json`，缺席不影响标签。
