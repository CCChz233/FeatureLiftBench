# FeatureLiftBench Task Design Rules（规格宪法）

- **状态：** Adopted v1.1（2026-07-24，test-blind Main）
- **效力：** 主榜入库与新题/晋升的权威规则；与旧文档冲突时以本文为准
- **迁移：** Python-150 **150/150 engineering-compliant**、0 legacy（2026-07-24）；全量任务已完成工程迁移、逐题校验与 Oracle 复验，独立人工 paper-gold 审核仍待完成。手册：[CONSTITUTION_MIGRATION.md](CONSTITUTION_MIGRATION.md)
- **相关：** [BENCHMARK_DESIGN.md](BENCHMARK_DESIGN.md)（整体思路）· [EXPERIMENT_ARMS.md](EXPERIMENT_ARMS.md)（臂）· [06_task_schema.md](06_task_schema.md)（包布局）· [07_incremental_task_rules.md](07_incremental_task_rules.md)（生命周期）· [03_evaluator_and_scoring.md](03_evaluator_and_scoring.md)（计分）

---

## 0. Benchmark 定义（方法无关）

FeatureLiftBench 评估：在提供完整公开功能契约与 pinned 上游仓库上下文
的条件下，Agent 能否自行检查实现与上游测试证据、解耦目标功能，构造
独立可安装、行为完整且尽量紧凑的功能模块。

Benchmark **不规定** Agent 的探索、推理、测试或停止流程；任何方法只要遵守相同的可见信息、工具环境与输出约束，均可参与评测。

论文路线是 **Benchmark 基础 + 方法研究**：先冻结规格与评测口径，再在合规任务上验证 Contract/API closure recovery；不提前承诺某一工具有效。

`extraction_ratio` / `final_score` 中的紧凑项是 **紧凑性代理指标**，不是“唯一最小闭包”或“每一行都必要”的证明。不得将评测目标表述为“行为完备的最小闭包提取”之严格意义。方法上界实验宜称 **Reference Support Set / Contract Checklist**，避免 “Oracle Closure” 歧义。

推荐的失败分析框架（规格账本 → 闭包 → 改写 → 验证 → prune）可用于归因与方法讨论，**不得**写入入库规范或强制 Agent 工作流。

---

## 1. 单一事实源与两层 metadata

### 1.1 原则

> `metadata.public_spec` 是唯一人工维护的 **Agent 可见契约**。  
> 所有 Agent-facing `TASK.md`、OpenHands prompt 功能规格片段与文档视图均由它 **生成**；禁止人工修改生成物。

`metadata.evaluation_spec`（及等价私有评测配置）**不对 Agent 可见**。

### 1.2 逻辑结构

```text
metadata
├── public_spec       # 可生成 Agent TASK；唯一人工维护的可见契约
└── evaluation_spec   # Agent 不可见：测试映射、isolation、reference 指针等
```

### 1.3 生成与哈希

1. `TASK.md`（workspace / 包内若保留）= `render(public_spec)` 的生成物。  
2. 记录 `spec_hash = hash(canonical_json(public_spec))` 与 `generated_task_hash = hash(render(public_spec))`。  
3. CI / `validate`：手写偏离、hash 不一致、第二规格源 → **任务无效**。  
4. 每次评测 run 日志保存 `task_revision + spec_hash`（及可选 `generated_task_hash`）。

### 1.4 禁止

- 包内手写一份更全的 `TASK.md`、agent 另读更窄的 metadata 提示（历史 isort 类分叉）。  
- 将 `evaluation_spec`、hidden 内容、entanglement 分析字段注入默认 Agent TASK。

---

## 2. `public_spec` 必填契约

### 2.1 `required_api` / `optional_api`

不得使用模糊的“Target API = 允许依赖的导出超集”。`required_api` **不能只是符号名单**。

| 字段 | 含义 |
| --- | --- |
| `required_api` | **必须全部存在**；应覆盖 **API surface**：导出路径、实体类型、函数/方法签名、默认参数、必需成员、必要异常类型等；hidden **必须**覆盖每一个 required 条目（见 §4） |
| `optional_api` | Agent **可以实现**，但 **public 与 hidden 均不得依赖** |

规则：

1. public / hidden 只能使用已声明的 API（`required_api ∪ optional_api`）；hidden 不得要求未声明的 surface（例如只声明 `State` 却要求未声明的 `State.parent`）。  
2. 类成员等必须用完整路径，例如 `featurelifted.State.parent`、`featurelifted.CryptContext.identify`。  
3. 每个 API 条目应尽量包含：`path`、`kind`、`signature`、默认参数、必需成员、主要异常。  
4. Agent 必须能从 `required_api` 判断强制契约；不得依赖“超集里哪些随便做”。

示例：

```yaml
required_api:
  - path: featurelifted.ProfileDoesNotExist
    kind: exception
  - path: featurelifted.resolve_settings
    kind: function
    signature: "(config_files=(), profile=None, overrides=None) -> Settings"
  - path: featurelifted.Machine
    kind: class
    members:
      - path: featurelifted.Machine.__init__
        signature: "(model, states=None, initial='initial', transitions=None, ignore_invalid_triggers=False)"
optional_api: []
```

### 2.2 Behaviors（可观察断言级）

每条 behavior 至少包含：**前置条件 · 操作 · 可观察结果**（可合并成一句，但三者语义必须齐全）。

不合格：

> Supports nested states.

合格：

> When a machine is created with a dotted nested state name such as `parent.child`, the model exposes the nested hierarchy such that `model.parent.state == "child"`.

不合格：

> Handles missing fields correctly.

合格：

> Accessing an undefined field through the item-loader API raises `KeyError`.

每条必须有稳定 `id`（如 `B001`）。描述可不暴露具体 hidden 输入样本，但须使合理实现者知道义务。

### 2.3 其它公开字段

- `source_entrypoints`：≥1，且在 pinned `repo/` commit 可解析。  
- `exclusions`：明确不做的能力；hidden 不得要求 exclusions 内行为。  
- `forbidden`：原包 import / 外部依赖等，与 evaluator 门一致。

### 2.4 默认不对 Agent 可见的分析字段

以下属 benchmark **私有**（分层统计、采样、失败分析、实验切片），默认不进 TASK；若研究提示增强，须作为 **单独 ablation**：

- `entanglement.*`（含 types / signals）  
- `failure_mode` / `difficulty` 叙事细节  
- `hidden_behavior_category`  
- 其它直接暗示 hidden 重点或解法类型的标签  

Agent 默认只见正常功能规格（entrypoint、API、behaviors、exclusions、forbidden、输出布局与评分一句说明）。

---

## 3. `evaluation_spec`（私有）

至少包含：

- public / hidden 测试清单与映射：`test_id → behavior_ids`、`test_id → api_ids`（或等价 manifest）  
- isolation / forbidden 检查配置  
- reference / oracle 指针  

测试对 API 的引用须维护 **显式 manifest**；AST 扫描仅作交叉校验（无法可靠覆盖 `import featurelifted as fl` / 反射）。

---

## 4. Public / Hidden 关系

### 4.1 核心原则

> Public 与 hidden **必须来自同一组公开行为契约**。  
> Hidden 可以增加案例、组合、边界、异常路径、状态序列、配置与类型变体，但 **不得** 增加新的 API、新的行为类别或新的环境假设。

### 4.2 覆盖（双向强制）

1. 每个 public / hidden 测试至少映射一个 **公开** behavior id。  
2. 每个 **required behavior** 至少被一个 **hidden** 测试覆盖。  
3. 每个 **required_api** 条目（含必需成员/异常等 surface）至少被 hidden 覆盖（导入或可观察使用）。  
4. 测试使用的 API ⊆ `required_api ∪ optional_api`；**optional_api 不得被 public/hidden 依赖**。  
5. Hidden 不引用 `exclusions` 中明确排除的能力。  
6. Public 可只覆盖部分 behavior，或对全部行为做浅层 smoke；hidden 可加深案例/组合/边界，但不得新增契约。

“Public 是行为条款的严格子集”**不是**准确表述：允许 public 对全部行为做浅层 smoke，hidden 做更深覆盖。

### 4.3 可见性

- 默认 Main 中，`public_tests/`、`hidden_tests/`、evaluation 与 reference
  均不进入 Agent workspace；两级测试只在提交后运行。
- `public_tests/` 是基础 evaluator 层的历史目录名，不代表 Agent 可见。
- `repo/` 内随 pinned 上游快照保留的 tests/docs/examples 属于源码上下文，
  Agent 可以检查、改写并用于自测。
- Public-feedback 臂可显式挂载 `public_tests/`；它与 Main 必须共用相同
  `public_spec`、任务版本和 evaluator，结果须分报。

---

## 5. Agent 可见输入与输出（只规定边界）

Benchmark 只规定：

| 维度 | 内容 |
| --- | --- |
| 输入 | `repo/`（含保留下来的上游 tests/docs/examples）、由 `public_spec` 生成的 TASK、redacted 运行元数据、依赖锁等 |
| 允许工具/环境 | 与 harness 配置一致；方法专用工具须标明为可选且不改变可见契约 |
| 输出 | `submission/` 下独立可安装包（Python：`submission/featurelifted/`） |
| 指标 | `functional_gate = BuildPass ∧ TestPass ∧ OriginalImportPass`（`TestPass = Public ∧ Hidden`）；`final_score = gate × max(0, 1−extraction_ratio)`。Pass@1 用 evaluator 功能门，不用 Agent `run_status` |

不规定 Agent 必须维护何种中间状态或采用何种推理顺序。

---

## 6. 实验臂（语义契约不变）

| 臂 | 允许改变 |
| --- | --- |
| Main | 两级 Benchmark evaluator 测试全盲；标准生成 TASK |
| Public-feedback | 显式挂载基础 `public_tests/` |
| Short-prompt | Main 可见性不变；删除方法建议与冗余说明，保留完整契约 |

**不得**在臂之间改变：`required_api`、behaviors、exclusions、entrypoints、forbidden、hidden tests、evaluator。否则不是 ablation，而是不同任务。

---

## 7. 自动入库门禁

未通过则不得进入 / 留在宣称合规的主榜集合。

### 7.1 契约一致性

1. `required_api` / `optional_api` 路径格式合法。  
2. public/hidden 使用的 API 均已声明。  
3. 每个 required API 被 hidden 覆盖。  
4. 每个测试映射 ≥1 behavior。  
5. 每个 required behavior 被 hidden 覆盖。  
6. hidden 不触及 exclusions。  
7. 显式 test↔API/behavior manifest 存在；AST 交叉校验可选但推荐。

### 7.2 来源一致性

8. Agent-facing TASK 仅由 `public_spec` 生成。  
9. 禁止人工维护第二份可见规格。  
10. `spec_hash` / `generated_task_hash` 一致。  
11. run 日志记录 `task_revision + spec_hash`。

### 7.3 可执行性

12. entrypoint 在 pinned commit 可解析。  
13. reference 在干净、无网络环境通过。  
14. public、hidden、isolation、forbidden 全过。  
15. evaluator 连续运行确定。  
16. reference 不依赖原仓运行时路径。

### 7.4 泄漏检查

17. `public_tests/`、hidden 与 evaluation 均不在默认 Main workspace。  
18. private metadata 不进 TASK。  
19. TASK 不含 hidden 的具体 I/O 样本。  
20. public fixture 不间接加载 hidden。  
21. 日志/缓存不暴露 hidden 内容。
22. `repo/` 快照记录上游 tests/docs/examples 的保留情况；若缺失，须说明
    Agent 依靠何种公开证据自建测试。

### 7.5 任务有效性

23. 空实现 / 简单 stub 必须失败。  
24. 仅拟合浅层基础测试的方案应被 hidden 区分。  
25. 直接 import 原仓必须失败。  
26. 整仓复制可以 functional pass，但须受明确 compactness 惩罚。  
27. 不依赖随机网络、墙钟时间或机器特定环境（除非规格显式声明且可复现）。

---

## 8. 人工审核（主榜逐题，非仅抽检）

每道主榜题至少一次明确审核，回答：

- 题面是否足以唯一确定预期行为？  
- hidden 是否完全属于公开契约？  
- 是否遗漏异常、默认值、状态或资源要求？  
- exclusions 是否明确？  
- `required_api` 是否完整？  
- reference 是否利用了未公开知识？  
- public 是否过强或过弱？  
- 是否主要测解耦/契约实现，而非环境偶然性？  

高风险题（framework lifecycle、nested state、resource/package、dynamic registry、config/environment）建议 **双人复核**。

---

## 9. 实现优先级（相对扩题 / 旧 retrieval）

| # | 项 | 状态 |
| --- | --- | --- |
| 1 | 落地本文 + [BENCHMARK_DESIGN.md](BENCHMARK_DESIGN.md) | ✅ |
| 2 | 校验器：API surface / behavior–test mapping / TASK hash / isolation | ✅ `constitution_validate` + `validate-task` |
| 3 | 试点 isort / transitions / scrapy + hidden 重判 | ✅ |
| 4 | 生成器 `public_spec → TASK.md` | ✅ `render-task`；compliant agent workspace 已接入 |
| 5 | 主榜分批迁移；`spec_status: legacy` 标注 | ✅ 150/150 compliant；0 legacy |
| 6 | Compliant Python-150 重跑 OpenHands 基线 → 方法实验 | 🚧 全榜 test-blind Main 正式实验待运行 |
| 7 | RSG start-here 仅 retrieval baseline；扩题低优先级 | ✅ 政策已冻结 |

操作细节：[CONSTITUTION_MIGRATION.md](CONSTITUTION_MIGRATION.md)

---

## 10. 与旧文档的关系

| 旧说法 | 本文 |
| --- | --- |
| `TASK.md` 推荐手写、与 metadata 并行 | 禁止双轨；生成自 `public_spec` |
| Target API 模糊超集 | `required_api` + `optional_api` |
| “最小闭包”作为评测宣称 | 行为完整 + 独立 + 尽量紧凑 |
| 理想 Agent 工作流入库规范 | 禁止；仅可作分析框架 |
| Entanglement signals 默认进 prompt | 默认私有；ablation 可选 |
| Public 必须是行为子集 | 改为同契约下的覆盖深度差异 |

生命周期仍见 [07_incremental_task_rules.md](07_incremental_task_rules.md)；包路径仍见 [06_task_schema.md](06_task_schema.md)。二者与本文冲突时，**契约与可见性以本文为准**，并应回修那两份文档。
