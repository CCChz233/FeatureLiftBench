# Repository Semantic Graph 设计：Operational Support Subgraph

- 状态：**Design v2 — 研究优先级已降级（2026-07-24）**（实现可保留；非当前提分主线）
- 更新时间：2026-07-24
- **当前权威入口：** [../CURRENT_RESEARCH.md](../CURRENT_RESEARCH.md) · [../BENCHMARK_DESIGN.md](../BENCHMARK_DESIGN.md) · [../TASK_DESIGN_RULES.md](../TASK_DESIGN_RULES.md)
- 实现计划：[REPOSITORY_SEMANTIC_GRAPH_IMPLEMENTATION_PLAN.md](REPOSITORY_SEMANTIC_GRAPH_IMPLEMENTATION_PLAN.md)

> **优先级说明**  
> Hard A/B 显示 **当前 start-here / support retrieval** 未抬 hidden 通过率。仓库 **Benchmark 基础主线** 改为规格宪法与任务迁移；**方法候选** 为 Contract/API closure recovery。  
> **Repository Fact Graph**（导出/异常/资源等事实层）**保留为基础设施**。降级的是 start-here 产品形态，不是否定整图基建。  
> 新实验须服从方法无关评测与 [TASK_DESIGN_RULES.md](../TASK_DESIGN_RULES.md)。

> **相对 v1.1 的变更**  
> ECSM、claim/evidence 状态机、强制 `task-closure` / `submission-check`、stopping gate **全部移出方法核心**。  
> 新核心是：给定 seed，在预算内返回证据可追踪的 **Operational Support Subgraph**，作为 OpenHands 的**可选**工具。

---

## 1. 问题与评测背景

FeatureLiftBench 研究的问题不同于传统修复/定位：

> 给定真实仓库中的目标功能及其 source entrypoint，Agent 能否将其从复杂依赖中解耦为独立、可安装、行为正确且尽量紧凑的模块？

评分（实现口径）：

```text
functional_gate = Build ∧ PublicTests ∧ HiddenTests ∧ OriginalImportPass
final_score     = functional_gate × max(0, 1 − extraction_ratio)
```

- **Pass@1 / functional pass**：功能与隔离门控（二值；**不含**紧凑性）
- **final_score**：在功能通过后连续惩罚大块复制
- 论文主表应**同时**报告 Pass@1 与 mean final_score（及可选 compact@threshold）

当前任务提示提供 `Source entrypoints`（如 `sqlparse.parse`），属于：

> **Entrypoint-conditioned feature extraction**

不是无提示的全仓库检索。定位结论不得外推到无 entrypoint 设定。

---

## 2. 纯 Agent 证据（设计约束）

基于 550 次 OpenHands 运行（主榜当时无 RSG）：

| 观察 | 设计含义 |
| --- | --- |
| 523/550 打开正确入口文件；定位最早失败仅 5 条 | 不做「更好的检索器」当主贡献 |
| 损失主要在入口暴露之后 | 方法目标 = 操作支撑上下文，不是找文件 |
| public→hidden 高损失 | 接口/依赖/资源/配置/行为完整性敏感 |
| 自动归因：依赖发现、实现、动态语义为主 | 自动标签非金标；C/D/E 需后续人工复核 |
| File/Symbol Exposure 当前同为 523 | Symbol 规则偏乐观；论文分开报告并声明限制 |

最可信结论：

> 在提供 entrypoint 时，Agent 通常能较快找到实现，但难以恢复使功能正确工作的跨文件支撑上下文，也难以可靠解耦。

失败类型（人工复核目标）：

| 类 | 含义 | RSG 预期作用 |
| --- | --- | --- |
| C | 关键依赖/接口未被观察到 | **主期望提升** |
| D | 已观察到但取舍/复制错误 | 可辅助，**不保证** |
| E | 取舍合理但实现不保行为 | **不承诺**大涨 |

---

## 3. 方法定位

```text
通用 RSG（Repository Fact Graph + Support 构造器）
        ↓
提供结构、依赖、操作支撑与边界证据
        ↓
OpenHands 自主决定是否调用、如何使用
        ↓
OpenHands 自主阅读、修改、测试、停止
        ↓
FeatureLiftBench evaluator 独立评分
```

**RSG 是可选增强工具，不是 Agent 控制器。**

不做：

- ECSM / 状态机决定 expand·probe·prune·stop
- claim ledger、强制 sync、stopping gate
- 替模型决定抽取内容或任务完成
- 宣称「可执行最小闭包」或行为等价证明

通用问题（论文表述）：

> 给定仓库中一个或多个任务相关实体（seed），如何在有限上下文预算下，恢复使这些实体正常工作的跨文件**操作支撑**上下文？

同一方法可服务抽取、修复、迁移、重构、仓库问答、影响分析。FeatureLiftBench 对支撑完整性尤其敏感，故能暴露「定位之后」的缺口。

---

## 4. 方法核心

### 4.1 形式化

\[
H = \operatorname{Support}(G, S, q, B)
\]

| 符号 | 含义 |
| --- | --- |
| \(G\) | 完整仓库事实图（Repository Fact Graph） |
| \(S\) | 一个或多个 seed |
| \(q\) | 可选任务描述（可用于排序，不写入权威边） |
| \(B\) | 节点/路径/token 预算 |
| \(H\) | Operational Support Subgraph |

\(H\) **不是**可执行最小闭包，也不声称每个节点都必要。它是：

> 在静态分析与预算下，为 seed 提供的高价值**候选**支撑上下文，且路径证据可追踪。

FeatureLift 中 \(S\) 主要来自 `metadata.feature.source_entrypoints`。其他场景可为失败栈、报错函数、修改点、用户 API。

### 4.2 两层结构

```text
Layer 1: Repository Fact Graph     （确定性、只读、无任务决策）
Layer 2: Support Subgraph Constructor （seed → Core / Support / Boundaries）
```

---

## 5. Layer 1：Repository Fact Graph

### 5.1 输入与构建

```text
repo/
  → Tree-sitter / AST
  → Python（完整）/ Go（最小可移植）adapter + resolver
  → 模块、符号、import、调用、类型与引用
  → 配置 / 资源 / 注册等静态规则
  → nodes.jsonl + edges.jsonl + manifest
```

只存仓库事实，不存 FeatureLift 决策。

允许：`returns_type`、`loads_resource`、`exports`、`registers`、`reads_config` …  
禁止：`must_copy`、`required_for_extraction`、`task_complete`、`safe_to_stop` …

### 5.2 边证据

每条边携带 provenance，例如：

```json
{
  "source": "pkg.parser.parse",
  "relation": "loads_resource",
  "target": "pkg/resources/grammar.json",
  "evidence_file": "pkg/parser.py",
  "evidence_span": [42, 42],
  "extractor": "python.importlib_resources",
  "confidence": 1.0,
  "resolution": "resolved"
}
```

动态无法解析时不猜目标：

```json
{
  "source": "pkg.parser.dispatch",
  "relation": "resolves_via",
  "target": null,
  "evidence": "REGISTRY[mode]",
  "resolution": "unresolved_dynamic"
}
```

### 5.3 关系族（愿景全集）

普通图常有：`contains` / `imports` / `calls` / `inherits` / `references`。  
Operational Support 额外需要：

| 族 | 示例关系 | 用途 |
| --- | --- | --- |
| 接口 / API | `exports`, `provides_member`, `accepts_type`, `returns_type`, `raises` | API surface |
| 数据模型 | `constructs`, `accesses_field`, `validates_with`, `serializes_as`, `depends_on_default` | 类型与默认值 |
| 配置 / 环境 | `reads_config`, `reads_env`, `configured_by`, `default_defined_by`, `path_derived_from` | 外部配置 |
| 资源 / 打包 | `loads_resource`, `requires_asset`, `packaged_by`, `declared_in` | 非代码依赖 |
| 注册 / 分派 | `registers`, `registered_as`, `resolves_via`, `dispatches_to`, `discovered_by` | 框架与插件 |
| 状态 / 生命周期 | `reads_state`, `writes_state`, `initializes`, `caches`, `lifecycle_depends_on` | 全局与初始化 |

**MVP 优先实现（预注册，可消融）：**

```text
exports, provides_member, returns_type, raises,
loads_resource, packaged_by,
reads_config, default_defined_by,
registers, resolves_via
```

其余按失败切片增量加入，禁止一次铺满。

---

## 6. Layer 2：Operational Support Subgraph Constructor

### 6.1 流程

1. **解析 seed** → 实体；歧义则返回候选，不静默选定。  
2. **生成候选支撑类别**（retrieval coverage categories，**不是** Agent 义务）：  
   `implementation | interface | data | configuration | resource | dispatch | state`  
3. **类型感知扩展**：按关系族优先级扩展，而非无差别 BFS。  
   - 高：exports / provides_member / returns_type / raises / loads_resource / reads_config / registers / resolves_via  
   - 中：calls / constructs / references / accesses_field  
   - 低：logging / CLI / docs / distant utility  
   - 框架 hub：标记 boundary，不全量展开  
4. **路径级评分**（对象是 seed→实体的证据路径）：

\[
U(p)=w_r R(p)+w_o O(p)+w_e E(p)-w_d D(p)-w_n N(p)-w_c C(p)
\]

| 项 | 含义 |
| --- | --- |
| \(R\) | 与 seed / 可选任务描述相关性 |
| \(O\) | 覆盖新支撑类别的价值 |
| \(E\) | 证据质量（resolution、provenance） |
| \(D\) | 图距离 |
| \(N\) | 框架噪声 |
| \(C\) | 源码 / token 成本 |

权重在看 Agent 结果前**冻结**；必须消融（去 \(O\)、去 \(N\)、退化为 k-hop）。第一版用确定性规则，不训练。

5. **预算化选择**：按 \(\Delta\)覆盖 / \(\Delta\)成本 贪心加入完整路径，直至预算耗尽；保证连通、路径完整、去重。  
6. **保留 Boundaries**：未解析动态边 + 预算裁剪的高价值候选。

### 6.2 输出格式

`repo_support` / `flb-rsg support` 返回三部分：

| 块 | 含义 |
| --- | --- |
| **Core** | 直接实现 seed 主行为的实体 |
| **Support** | API / 类型 / 配置 / 资源 / 注册 / 状态支撑 |
| **Boundaries** | 动态未解析、框架膨胀或预算裁剪 |

```json
{
  "seeds": ["sqlparse.parse"],
  "core": [
    {
      "entity": "sqlparse.engine.FilterStack.run",
      "role": "direct_implementation",
      "evidence_path": ["sqlparse.parse", "parsestream", "FilterStack.run"]
    }
  ],
  "support": [
    {
      "entity": "sqlparse.sql.Statement",
      "role": "return_data_model",
      "evidence_path": ["sqlparse.parse", "parsestream", "Statement"]
    }
  ],
  "boundaries": [
    {
      "source": "FilterStack.run",
      "kind": "dynamic_dispatch",
      "reason": "target selected through registry",
      "evidence": "src/...:line"
    }
  ],
  "budget": {"limit_tokens": 8000, "used_tokens": 7460}
}
```

`inspect` 同样必须有行数 / 字符预算，防止绕过 support 预算灌入全文。

---

## 7. OpenHands 接入

当前正式路径**只面向 OpenHands**（CLI transport）。不维护 FeatureLiftAgent 强制协议作为方法臂。

对外暴露：

```text
flb-rsg search   …   # 查找实体
flb-rsg inspect  …   # 局部源码与邻居（有界）
flb-rsg support  …   # Operational Support Subgraph
```

`paths` / `closure` / 旧 `risks`：保留为内部调试或离线基线，**默认不写入** OpenHands 工具说明。

TASK 仅简短说明：

```text
You may optionally use `flb-rsg search`, `inspect`, and `support`
to inspect repository structure and operational dependency evidence.
Tool use is optional.
```

禁止：强制调用、必须同步、claim、stopping guard、自动判定完成。

**边界原则：**

> RSG Core 不读取 FeatureLift metadata、不理解 submission、不参与 evaluator。  
> FeatureLift 适配层仅可将 `source_entrypoints` 转为 `support` 的 seeds（可选便利，正式可选工具实验中也可让模型自己传 seed）。

---

## 8. 相对现有代码的迁移

**保留：** Tree-sitter 建图、adapter/resolver、JSONL、cache、CLI、runner opt-in。

**移出 OpenHands 正式路径 / 废弃为方法核心：**

| 旧能力 | 处理 |
| --- | --- |
| `task-closure` | 废弃 → 由通用 `support` 替代 |
| `submission-check` | 移到 FeatureLift evaluator / audit |
| claim / evidence ledger | claim 删除；边级 evidence 保留 |
| 强制 sync / stopping | 删除正式路径 |
| ECSM | 废弃 |

**重构：**

| 能力 | 新角色 |
| --- | --- |
| `search` / `inspect` | 保留并对 OpenHands 暴露 |
| `paths` / `closure` | 底层 / 实验基线 |
| `risks` | 重构进 `boundaries` |

---

## 9. 配置（正交）

旧 `repo_graph_mode = static|closure|evidence` 混合了过多维度。新建议：

```toml
[rsg]
enabled = true
transport = "cli"
bootstrap = "tool_only"          # tool_only | auto_support（仅诊断）
view = "operational_support"
budget_tokens = 8000
inspect_max_chars = 4000
max_depth = 4
relation_families = ["interface", "data", "config", "resource", "dispatch"]
```

- 图始终静态确定性构建；边始终带 provenance。  
- `bootstrap = tool_only`：正式实验默认，只告知工具存在。  
- `bootstrap = auto_support`：**诊断臂**，区分「信息无效」vs「模型不调用」；不得与正式可选工具臂混报。

---

## 10. 实验与成功标准

### 10.1 离线子图质量（先于 Agent）

30–50 题人工标注 seed、API、数据、配置、资源、注册、噪声、boundary。  
同预算比较：keyword / call-import / k-hop / 旧 task-closure / **operational support**。

指标：Obligation-category Recall@Budget、API/Resource/Config/Registry Recall、Noise Ratio、Evidence Path Accuracy、Boundary Recall、输出 token。

### 10.2 OpenHands Pilot

优先：基础设施稳、entrypoint 明确、纯 Agent 已找到入口、偏 dependency/API/resource/framework/config 失败。

主臂：

```text
OpenHands
OpenHands + basic graph（call/import）
OpenHands + optional operational support
```

诊断臂：`auto-injected operational support`。

### 10.3 成功标准

**图层：** 同预算下相对 basic graph / k-hop，提高真实支撑类别覆盖，不显著增噪，路径准，boundary 有用。

**Agent 层（主期望）：** dependency/interface omission ↓，public→hidden retention ↑（在 C 类切片），重复读 ↓，token/step 不恶化。

**Guardrail：** extraction_ratio / copy-heavy **不升高**；mean final_score 不因「多给依赖→多复制」而崩。

**不作为失败判据：** 单纯「调用了工具」。

---

## 11. 明确不做

- Agent / LLM 参与权威建图  
- ECSM、claim 状态机、stopping controller  
- 可执行最小闭包 / 行为等价「证明」  
- 每次修改后自动重建 submission 图  
- 强制调用 RSG  
- 首版全语言 / 全框架 / 训练式图检索 / GNN  

上下文压缩：OpenHands 已有通用 condens；本文不把 summarizer 当主创新。RSG 作为外置可查询记忆，使历史可裁剪后仍能按需取回支撑上下文——属配套叙述，非主方法。

---

## 12. 论文一句话

> 我们先用确定性静态分析构建证据可追踪的仓库事实图；再给定任务相关 seed，在固定预算下沿接口、数据、配置、资源、注册等操作支撑关系选择路径完整的 Operational Support Subgraph，并显式保留无法静态解析或因预算裁剪产生的边界。该子图作为可选工具提供给 OpenHands；代码取舍、实现、测试与停止仍由模型自主完成。

---

## 13. 历史文档

| 文档 | 状态 |
| --- | --- |
| 本文件 v2 | **现行设计** |
| v1.1 设计（已由本文替换） | 仅 git 历史 |
| [ECSM_METHOD_SPEC.md](ECSM_METHOD_SPEC.md) | superseded |
| [ICLR_INNOVATION_ROADMAP.md](ICLR_INNOVATION_ROADMAP.md) | superseded（ECSM 主线） |
