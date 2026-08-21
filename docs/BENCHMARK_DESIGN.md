# FeatureLiftBench 整体设计思路

> **Documentation status: current · Last verified: 2026-08-21**

- **状态：** 当前 Full-Repository / No-Hint 设计；release 数字见 [STATUS.md](STATUS.md)
- **简明原则：** [BENCHMARK_DESIGN_PRINCIPLES.md](BENCHMARK_DESIGN_PRINCIPLES.md)
- **规格细则：** [TASK_DESIGN_RULES.md](TASK_DESIGN_RULES.md)（宪法）
- **研究入口：** [STATUS.md](STATUS.md) 与 [paper/](paper/README.md)
- **文档地图：** [README.md](README.md)

本文把近期结论收成一条清晰主线：**测什么、怎么出题、Agent 看见什么、怎么打分、做什么实验、不做什么。**

论文目标仍是 **Benchmark + 方法**：先冻结可辩护的评测基础，再在合规任务上验证针对主瓶颈的方法。不因保住某一历史工具（如 RSG start-here）而扭曲任务定义。

---

## 1. 我们在测什么

### 1.1 一句话

在提供 **完整公开功能契约** 与完整 pinned 上游仓库、但**不提供上游实现
位置提示**的条件下，Agent 能否自行搜索和定位实现、检查上游
tests/docs/examples、恢复依赖并解耦目标功能，最终构造
**独立可安装、行为完整且尽量紧凑** 的功能模块。

目标功能可带有不同类型的仓库级耦合（依赖、配置、状态、注册、资源等）；并不要求整个 upstream 仓库「处处高度纠缠」。

### 1.2 不是什么

| 不是 | 原因 |
| --- | --- |
| SWE-bench 式修 issue | 输出是新包，不是给原仓打补丁 |
| 纯绿场代码生成 | 必须保真上游可观察行为 |
| 拟合 Benchmark 评分测试 | 默认 Main 在提交前不暴露任何 Benchmark 自建测试 |
| 「唯一最小闭包」的数学证明 | `extraction_ratio` 只是紧凑性**代理** |
| 规定 Agent 必须如何推理 | 评测方法无关；不强制工作流 |

### 1.3 与当前实验环境的关系

当前采用的 **OpenHands** 配置是 Official Main 的 coding runtime，具备仓库搜索、
代码编辑、测试执行及上下文管理等通用能力。v3 Main 同时测量自主定位、契约完成、
依赖发现、解耦与验证。DeepSeek Harness / Codex 可作为同信息边界的可选 runtime
消融，不是 Main，见 [METHOD_AGENT_RUNTIME.md](METHOD_AGENT_RUNTIME.md)。

1. **从完整仓库自主定位实现**
2. **从完整契约与上游证据自行构造验证**
3. **解耦约束**（forbidden import、独立安装）
4. **紧凑性**（作为功能正确性之外的独立次要指标）

**证据边界（须保留）：** 当前历史基线属于
`mixed_snapshot_v1`，且 Agent-visible metadata 含 source entrypoints。
其中自动启发式归因显示入口定位很少成为最早失败点、public 通过后仍约有
43% 运行无法通过 hidden；该观察不能外推为 No-Hint Full-Repository Main
中的定位不重要，也不能解释为严格因果分解。另：hard A/B 中当前 RSG
start-here/support retrieval 未改善 hidden 通过率。

---

## 2. 任务信息分层（科学边界）

```text
                    ┌─────────────────────────────┐
  Agent 可见        │  public_spec → 生成 TASK     │
                    │  完整 repo/（源码/测试/文档/  │
                    │  配置/资源）                  │
                    │  redacted metadata（无定位提示）│
                    │  requirements.lock 等         │
                    └─────────────────────────────┘
                    ┌─────────────────────────────┐
  Agent 不可见      │  evaluation_spec             │
                    │  public_tests/ + hidden_tests/│
                    │  entanglement 分析标签       │
                    │  reference / oracle          │
                    └─────────────────────────────┘
                    ┌─────────────────────────────┐
  交卷后评测        │  BuildPass ∧ Public ∧ Hidden │
                    │  ∧ IsolationPass             │
                    │  + 独立 compactness metrics  │
                    └─────────────────────────────┘
```

### 2.1 公开契约必须清楚

- `required_api` / `optional_api`（强制 vs 可选；禁止模糊「导出超集」）
- behaviors：前置条件 · 操作 · 可观察结果
- exclusions、forbidden

`required_api` **不能只是符号名单**。应覆盖导出路径、实体类型、函数/方法签名、默认参数、必需成员、必要异常类型等 **API surface**。Hidden 不得要求未声明的 surface（例如只声明 `State` 却要求未声明的 `State.parent`）。

`optional_api`：Agent 可以实现，但 **public 与 hidden 均不得依赖**。

Main 的公开契约**不得**包含 source entrypoints、上游源文件/符号/行号、
调用链或依赖文件清单。目标提交 API 用于统一交付接口，不等同于上游实现定位。
source entrypoints 若作为维护 provenance 保留，必须位于 evaluator 私有层；
若向 Agent 暴露，只能作为单独的 `Entrypoint-Hint` ablation。

**不能**把 TASK 糊成一句「把这功能抽出来」——那会把 hidden 变成唯一规格，变成猜题。

### 2.2 两级私有 evaluator 测试（同契约，不同覆盖深度）

- `public_tests/` 是历史目录名，表示基础契约测试层，**不表示 Agent 可见**。
- Public 与 hidden **必须来自同一组公开行为契约**。
- Hidden **不得**增加新 API、新行为类别或新环境假设；可增加输入组合、状态序列、边界与异常路径。
- Public 可只覆盖部分 behavior，或对全部行为做浅层 smoke。
- **双向覆盖（防漏测）：**
  - 每个 public/hidden test ≥1 个公开 behavior ID；
  - 每个 `required_api` 至少被一个 **hidden** test 覆盖；
  - 每个 required behavior 至少被一个 **hidden** test 覆盖。
- 默认 Main：workspace 不可访问两级 evaluator 测试；提交后运行同一组测试。

### 2.3 已解决的历史双轨问题

历史实现存在双轨：包内手写 `TASK.md`、metadata、`build_task_prompt` 不一致（例：isort agent 可见 API 缺 `ProfileDoesNotExist`，hidden 却要求）。

**已落地：** `public_spec` 唯一源 → `render()` 生成 TASK → `spec_hash`
门禁。操作与准入规则见 [TASK_DESIGN_RULES.md](TASK_DESIGN_RULES.md) 和
[07_incremental_task_rules.md](reference/07_incremental_task_rules.md)。

当前 release 规模、source registry、Oracle 和 canary 状态不在本文重复维护，
统一见 [STATUS.md](STATUS.md)。Compactness 使用 frozen-reference-relative
独立指标，release 由 readiness、Oracle 与对抗性 canary 门禁共同约束。

历史任务目录中的 pruned/mixed `repo/` 保留作 provenance 和旧协议复现，
但 v3 Agent workspace 只从经 digest 校验的 canonical source archive
生成。独立人工审核不是正式准入门槛；历史 `mixed_snapshot_v1` 模型结果
仍不得冒充 v3 Main 结果。详见
[v3_main_readiness.md](../reports/audits/v3_main_readiness.md)。

---

## 3. 打分在量什么

v3 headline 定义：

```text
FunctionalPass =
    BuildPass
    ∧ PublicTestsPass
    ∧ HiddenTestsPass
    ∧ IsolationPass
```

其中：

- **BuildPass：** 干净环境中安装/导入（或语言对应的 build）成功。
- **PublicTestsPass / HiddenTestsPass：** 对应 pytest（或 Go 等价）通过。
- **IsolationPass：** forbidden import/dependency、运行时 import origin、source
  filesystem absence、禁用网络和 submission location 等隔离子门全部通过。

网络隔离、allowlist 安装等若失败，通常表现为 BuildPass/环境失败，计入 gate 失败路径；不另设省略号项。

**口径分离：** `functional_gate` 与 Agent suite 的 `run_status`（Agent 是否正常结束工作流）**分开计算**。主榜 **Pass@1** 采用 evaluator 功能门，不采用 Agent 工作流是否正常结束。这避免「hidden 通过数」与「formal pass」因工作流状态被混淆。

- Gate：行为是否在干净环境成立（含 Agent 交卷前可能从未跑过的 hidden）
- 紧凑项：功能结果之外独立报告，使用 reference/reference-support-set
  相对指标；**不是**最小性证明

**实现口径：** `final_score` 仅作为兼容字段，恒等于 `functional_gate`。
紧凑性单独报告 `reference_relative_loc_ratio`、`compactness_score`、文件数、
复制比例和依赖指标；完整 upstream LOC 不参与紧凑性分母。

Functional 阶段只挂载 submission、测试、锁定依赖、允许 wheels、harness 和
输出目录；source/reference 只进入不执行 submission 的只读 metrics 阶段。
详情：[EVALUATION.md](EVALUATION.md)

---

## 4. 实验臂（语义契约相同）

完整规定见 [EVALUATION.md](EVALUATION.md)。

| 臂 | 仓库上下文 | 定位提示 | Benchmark tests |
| --- | --- | --- | --- |
| **Main** | 完整仓库 | 无 | 两级全盲 |
| **Entrypoint-Hint** | 完整仓库 | 有 | 两级全盲 |
| **Public-feedback** | 完整仓库 | 无 | public 可见 |
| **Pruned-Context** | 裁剪快照 | 按臂定义 | 两级全盲 |
| **Short-prompt** | 完整仓库 | 无 | 两级全盲；仅压缩文案 |

**Main 严谨表述：** 任务包中的 `public_tests/` 与 `hidden_tests/` 均为
evaluator 资产；Agent workspace 不复制、不挂载、不可访问。`repo/` 内
原本属于上游项目的 tests/docs/examples 仍是仓库上下文，允许 Agent
检查、改写和运行。TASK、redacted metadata 和辅助状态均不暴露上游实现
位置。交卷后 evaluator 再运行两级 Benchmark 测试。

实验框架已实现 test visibility / prompt-style profiles：
`…_main` / `…_public_feedback` / `…_short_prompt`，以及显式 opt-in
`--agent-public-tests`。可验证的 No-Hint Main 与 Entrypoint-Hint 切换已
落地；当前 release 的 Full-Repository materialization 状态见
[STATUS.md](STATUS.md)。RQ6 Public-feedback 的 Flash-12 成对规范见
[METHOD_RQ6_PUBLIC_FEEDBACK.md](METHOD_RQ6_PUBLIC_FEEDBACK.md)。历史 `no_public`
名称保留为 test-blind 的兼容别名，但不自动等同于 v3 Main。换 coding runtime
（DeepSeek Harness / Codex）不是上表信息消融，见
[METHOD_AGENT_RUNTIME.md](METHOD_AGENT_RUNTIME.md)。

---

## 5. 主线关系：Benchmark 基础 vs 方法研究

| 路线 | 状态 | 说明 |
| --- | --- | --- |
| **Benchmark 规格宪法与任务迁移** | **当前基础主线** | 冻结公开契约、测试映射、评分与门禁；先有可辩护评测 |
| **Contract/API closure recovery** | **当前方法候选** | 面向 required API、成员、异常、状态与行为证据；方案由失败分析与先导实验决定 |
| **Repository Fact Graph** | **基础设施保留** | 导出/类型/异常/资源/配置等可追踪事实；可为契约恢复与分析提供底座 |
| **当前 RSG start-here / support retrieval** | **降级为实验基线** | 主要提供文件与结构导航；hard pilot 未改善 hidden；通过率与 token 均无优势 |
| **ECSM / 强制 task-closure** | **废弃** | 不再作为正式方法 |

说明：

- **Benchmark 基础主线**：先冻结规格、任务质量与评测口径。
- **方法研究主线**：在 **合规任务** 上验证契约/闭包恢复方法；不提前承诺某一工具有效。
- 「降级」的是 **当前 start-here retrieval 产品形态**，不是否定整个 Fact Graph / 关系抽取基建。
- 闭包类干预宜称 **Contract Checklist / Probe / Reference Support Set（上界）**，避免「Oracle Closure / 唯一最小闭包」用语。

RSG 的当前可执行说明见
[`harness/featureliftbench/repo_graph/README.md`](../harness/featureliftbench/repo_graph/README.md)；
实验报告保存在 `reports/repo_graph_phase*/`。

---

## 6. 理想分析框架 ≠ 评测规定

失败分析可用：

```text
读公开契约 → 构实现闭包 → 解耦改写 →（可选）自测/自建探针 → prune → 提交
```

这用于理解「哪里断了」。
**Benchmark 入库与评测不得强制** Agent 采用该流程或任何中间状态机。

---

## 7. 推进顺序

设计、task contract、source policy 和 evaluator 必须先冻结，再运行模型与方法
实验。当前执行顺序和阻塞项只在 [STATUS.md](STATUS.md) 维护；历史迁移和方法
路线保存在 [archive/](archive/plans/README.md)。

当前操作手册：[SERVER_RUNBOOK_PYTHON200.md](SERVER_RUNBOOK_PYTHON200.md)

---

## 8. 相关文档

| 文档 | 角色 |
| --- | --- |
| [BENCHMARK_DESIGN_PRINCIPLES.md](BENCHMARK_DESIGN_PRINCIPLES.md) | v3 简明权威原则 |
| [TASK_DESIGN_RULES.md](TASK_DESIGN_RULES.md) | 出题与门禁宪法 |
| [FULL_REPOSITORY_SOURCE_POLICY.md](FULL_REPOSITORY_SOURCE_POLICY.md) | canonical source policy |
| [EVALUATION.md](EVALUATION.md) | Main、消融、评测与报告 |
| [06_task_schema.md](reference/06_task_schema.md) | 包布局 |
| [07_incremental_task_rules.md](reference/07_incremental_task_rules.md) | 生命周期 |
| [SERVER_RUNBOOK_PYTHON200.md](SERVER_RUNBOOK_PYTHON200.md) | 当前正式运行手册 |
| [STATUS.md](STATUS.md) | 当前状态与结果边界 |
