# FeatureLiftBench 整体设计思路

- **状态：** 权威叙事 v1.1（2026-07-24，test-blind Main）
- **规格细则：** [TASK_DESIGN_RULES.md](TASK_DESIGN_RULES.md)（宪法）
- **研究入口：** [CURRENT_RESEARCH.md](CURRENT_RESEARCH.md)
- **文档地图：** [README.md](README.md)

本文把近期结论收成一条清晰主线：**测什么、怎么出题、Agent 看见什么、怎么打分、做什么实验、不做什么。**

论文目标仍是 **Benchmark + 方法**：先冻结可辩护的评测基础，再在合规任务上验证针对主瓶颈的方法。不因保住某一历史工具（如 RSG start-here）而扭曲任务定义。

---

## 1. 我们在测什么

### 1.1 一句话

在提供 **完整公开功能契约** 与 pinned 上游仓库上下文的条件下，Agent
能否自行检查源码、上游 tests/docs/examples，解耦目标功能，并构造
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

当前采用的 **OpenHands** 配置已具备仓库搜索、代码编辑、测试执行及上下文管理等通用能力。FeatureLift 仍然有意义，因为主损失在：

1. **从完整契约与上游证据自行构造验证**  
2. **解耦约束**（forbidden import、独立安装）  
3. **紧凑性**（整仓拷贝可过功能门但分数近 0）

**证据边界（须保留）：** 在当前 **entrypoint-conditioned** 的 **OpenHands** 基线中，**自动启发式**归因审计显示入口定位很少成为最早失败点；public 通过后仍约有 **43%** 运行无法通过 hidden。该归因为观察性分析，**待人工复核**，**不能**解释为严格因果分解。另：hard A/B 中当前 RSG start-here/support retrieval 未改善 hidden 通过率。

---

## 2. 任务信息分层（科学边界）

```text
                    ┌─────────────────────────────┐
  Agent 可见        │  public_spec → 生成 TASK     │
                    │  repo/（含上游自带测试/文档） │
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
                    │  ∧ OriginalImportPass        │
                    │  + compactness scoring         │
                    └─────────────────────────────┘
```

### 2.1 公开契约必须清楚

- `required_api` / `optional_api`（强制 vs 可选；禁止模糊「导出超集」）  
- behaviors：前置条件 · 操作 · 可观察结果  
- entrypoints、exclusions、forbidden  

`required_api` **不能只是符号名单**。应覆盖导出路径、实体类型、函数/方法签名、默认参数、必需成员、必要异常类型等 **API surface**。Hidden 不得要求未声明的 surface（例如只声明 `State` 却要求未声明的 `State.parent`）。

`optional_api`：Agent 可以实现，但 **public 与 hidden 均不得依赖**。

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

### 2.3 当前缺陷与迁移状态（2026-07-24）

历史实现存在双轨：包内手写 `TASK.md`、metadata、`build_task_prompt` 不一致（例：isort agent 可见 API 缺 `ProfileDoesNotExist`，hidden 却要求）。

**已落地：** `public_spec` 唯一源 → `render()` 生成 TASK → `spec_hash` 门禁（见 [CONSTITUTION_MIGRATION.md](CONSTITUTION_MIGRATION.md)）。

**进度：** **150/150 experiment-ready**，**0 legacy**。契约与 hidden
已完成自动一致性门禁；Oracle freeze `7c042d5528b7d0fd` 为 450/450，
spec freeze `f7c616edb47ea533` 已生成。独立人工 paper-gold 审核仍为
0/150；历史 legacy run 与 compliant run **不得混报**。

**新协议内容审计：** 完整非模板化契约 **150/150**；
experiment-ready **150/150**。`repo/` 中含可发现上游测试 **48/150**
是信息项，因为 Agent 允许自行发现或构造测试。独立人工审核 **0/150**，
所以可做正式模型实验，但 paper-ready 仍为 **0/150**。逐题队列由
`scripts/audit_new_protocol_readiness.py` 生成。

---

## 3. 打分在量什么

与当前实现（`harness/featureliftbench/scoring.py` + evaluator）一致：

```text
TestPass = PublicTestsPass ∧ HiddenTestsPass

functional_gate =
    BuildPass
    ∧ TestPass
    ∧ OriginalImportPass

final_score =
    functional_gate × max(0, 1 − extraction_ratio)
```

其中：

- **BuildPass：** 干净环境中安装/导入（或语言对应的 build）成功。  
- **PublicTestsPass / HiddenTestsPass：** 对应 pytest（或 Go 等价）通过。  
- **OriginalImportPass：** 无 forbidden import/dependency，且 submission 不依赖原仓路径（含「不在 source repo 内」等 harness 检查）。  

网络隔离、allowlist 安装等若失败，通常表现为 BuildPass/环境失败，计入 gate 失败路径；不另设省略号项。

**口径分离：** `functional_gate` 与 OpenHands suite 的 `run_status`（Agent 是否正常结束工作流）**分开计算**。主榜 **Pass@1** 采用 evaluator 功能门，不采用 Agent 工作流是否正常结束。这避免「hidden 通过数」与「formal pass」因工作流状态被混淆。

- Gate：行为是否在干净环境成立（含 Agent 交卷前可能从未跑过的 hidden）  
- 紧凑项：惩罚整仓拷贝；**不是**最小性证明  

详情：[03_evaluator_and_scoring.md](03_evaluator_and_scoring.md)

---

## 4. 实验臂（语义契约相同）

完整规定见 [EXPERIMENT_ARMS.md](EXPERIMENT_ARMS.md)。

| 臂 | Agent 侧 | 不变 |
| --- | --- | --- |
| **Main** | 两级 evaluator 测试全盲；标准生成 TASK | API/behaviors/evaluator |
| **Public-feedback** | 显式挂载基础 `public_tests/` 供反馈 | 同上 |
| **Short-prompt** | Main 可见性不变；砍方法建议/冗余 | 同上 |

**Main 严谨表述：** 任务包中的 `public_tests/` 与 `hidden_tests/` 均为
evaluator 资产；Agent workspace 不复制、不挂载、不可访问。`repo/` 内
原本属于上游项目的 tests/docs/examples 仍是仓库上下文，允许 Agent
检查、改写和运行。交卷后 evaluator 再运行两级 Benchmark 测试。

臂实现已落地：profiles `…_main` / `…_public_feedback` /
`…_short_prompt`，以及显式 opt-in `--agent-public-tests`。
历史 `no_public` 名称保留为 test-blind Main 的兼容别名。

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

RSG 设计文档仍见 `research_analysis/REPOSITORY_SEMANTIC_GRAPH_*`（已标优先级降级）。

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

| # | 项 | 状态 |
| --- | --- | --- |
| 1 | 冻结 `TASK_DESIGN_RULES.md` 与本文叙事 | ✅ |
| 2 | 实现 validate：API / behavior / TASK hash / isolation | ✅ |
| 3 | 试点 isort、transitions、scrapy + hidden 重判 | ✅ |
| 4 | 主榜 `spec_status: legacy` 标注 + 分批迁移 | ✅ 150/150 compliant；0 legacy |
| 5 | Test-blind Main / Public-feedback / Short-prompt 工程 | ✅ |
| 6 | Compliant Python-150 重跑 OpenHands 基线 | 🚧 全榜 test-blind Main 正式实验待运行 |
| 7 | Contract Checklist / Probe / Reference Support Set | ⏳ |
| 8 | RSG start-here 仅 retrieval baseline | ✅ 政策 |

手册：[CONSTITUTION_MIGRATION.md](CONSTITUTION_MIGRATION.md)

---

## 8. 相关文档

| 文档 | 角色 |
| --- | --- |
| [TASK_DESIGN_RULES.md](TASK_DESIGN_RULES.md) | 出题与门禁宪法 |
| [EXPERIMENT_ARMS.md](EXPERIMENT_ARMS.md) | Test-blind Main / Public-feedback / Short-prompt |
| [01_task_definition.md](01_task_definition.md) | 任务语义摘要 |
| [03_evaluator_and_scoring.md](03_evaluator_and_scoring.md) | 评测与打分（实现口径） |
| [06_task_schema.md](06_task_schema.md) | 包布局 |
| [07_incremental_task_rules.md](07_incremental_task_rules.md) | 生命周期 |
| [CONSTITUTION_MIGRATION.md](CONSTITUTION_MIGRATION.md) | 规格迁移操作手册 |
| [FINDINGS.md](FINDINGS.md) | 已有实验结果解读 |
