# 测试驱动的 Agent 认知增强（方法故事）

**状态：** 归档 v0.6（2026-07-29）— 干净试点相对 Main **零增益**；**不再扩**；方法主线已切到 [METHOD_EXEC_CONTRACT.md](METHOD_EXEC_CONTRACT.md)  
**定位：** 负对照叙事（「自编探针先行」为何不够）；**不是**当前主候选  
**上位：** [CURRENT_RESEARCH.md](CURRENT_RESEARCH.md) · [FINDINGS.md](FINDINGS.md) · [BENCHMARK_DESIGN_PRINCIPLES.md](BENCHMARK_DESIGN_PRINCIPLES.md)  
**试点：** [`experiments/td_cognition_pilot/`](../experiments/td_cognition_pilot/)（DeepSeek Flash · Phase1→Phase2 · 12 题）  
**有效结果：** Main `compare-20260728-155516/main`（4/12）；干净 TD `td-cognition-clean-20260728-220500`（4/12，零翻盘）。脏跑与锁文件版作废。

---

## 1. 一句话

代码 Agent 的瓶颈往往不是「找不到代码」，而是「不理解代码之间的契约关系」。  
我们主张：在动手改代码之前，把人类式的契约/因果建模重新注入 Agent；具体形态是让 Agent **主动构造或找出关键用例**，以测试为脚手架推演行为边界，再进入实现与解耦。

**命名澄清（防误读）：** 这里的「测试」是 Agent **自建自用的认知工具**（自写探针 / 仓内可发现的用例），**不是** benchmark 提供的验收测试，也不是「让 Agent 看见更多 public/hidden tests」。命名借用 SE 中 TDD 的认知锚点（用例先行约束理解），但干预对象是 Agent 的理解流程，不是评测可见性。

我们把这项工作定位为：

> **测试驱动的 Agent 认知增强**  
> ——测试首先是 Agent **主动构建理解的认知工具**，而不只是交卷后「判对错」的验收工具。

---

## 2. 问题诊断（为何需要这个故事）

### 2.1 任务本质（FeatureLift）

FeatureLiftBench 要求 Agent 在完整真实仓库与完整公开功能契约下，交付独立、行为完整且尽量紧凑的功能模块。评测在交卷后运行 private public/hidden 与 isolation；v3 Main 对 Agent **隐藏** benchmark 测试（test-blind / No-Hint）。

因此成功条件是：**按公开契约完成 API/行为/依赖闭包并解耦**，不是定位到某几个文件即可。

### 2.2 现有证据（历史协议，方向性）

在历史 `mixed_snapshot_v1` / 归因语料上（细节与 caveat 见 [FINDINGS.md](FINDINGS.md)）：

| 观察 | 含义 |
| --- | --- |
| 模型 Functional Pass@1 约 25%–58%，有区分度 | 任务非玩具 |
| ~95% 轨迹能读到正确入口；定位很少是最早关键失败 | 主瓶颈不在「找文件」 |
| public→hidden 出现大幅条件跌落；最早失败中 dependency/API closure 与 implementation/semantics 占比最高 | 主瓶颈在契约/行为闭包 |
| RSG start-here 类导航在 hard 小样本上未抬 hidden | 「告诉先看哪里」不够 |
| Public-feedback 相对 test-blind 可明显改分 | 反馈与理解通道重要，但≠本方法（见 §5） |
| 存在功能测试通过但 extraction 很高的 copy-heavy 例 | 正确性与紧凑性必须分开 |

**可讲的故事：** Agent 常进入「找到 → 改 → 测 → 看报错」的 ReAct 反馈环，用执行反馈代替行动前的契约建模；于是 public 烟雾易过，hidden/边界与 API surface 易漏。

**行为证据落点（历史轨迹，方向性，非精确因果）：** 在 ~550 条轨迹审计中，正确入口文件多能很快被读到（约 523/550 有入口证据；其中约九成在前 5 个 Agent action 内到达，中位约第 3 步），但显式 closure plan 仅约 62/550（~11%）。换言之：多数轨迹先完成仓库探索并很快进入实现，**很少在 first-edit 前留下可审计的契约建模产物**；轨迹中出现的自测/跑测信号更常落在编辑与修补之后，用作验证与报错驱动，而不是在动手前钉住行为边界。这支撑「ReAct 反馈环」叙事，但仍是描述性归因，不是已证明的因果机制。

**尚不能讲：** 任一模型在 v3 Full-Repository / No-Hint 下的最终通过率（须另跑 baseline）。

### 2.3 人类对照（推演，未做 human study）

（本节为对照推演，用于说明干预动机；**不是**已测 human baseline，也未做访谈/过程研究。）

人类拆模块时，我们推演其典型顺序会是：

1. 读清要交付的契约；  
2. 想清楚「解耦后最基本的用例是什么」；  
3. 用少量用例/探针钉住行为边界；  
4. 再定点抽取与改写；  
5. 最后才 prune 求紧凑。

在此推演下，关键差别往往不是「更会搜」，而是 **更早开始用用例约束因果理解**。若后续做 human study，可把本小节升格为经验对照；在此之前不得写成已观察事实。

---

## 3. 核心假说

### 3.1 假说 H1

在 FeatureLift 类任务上，于 **首次实质性编辑 `submission/` 之前**，强制 Agent 完成一轮 **用例驱动的契约推演**（自建或仓内用例 + 行为边界陈述），相对同配置的纯 ReAct baseline，能提高交卷后的 Functional Pass@1（或至少降低 public✓ / hidden✗ 比例）。

### 3.2 机制陈述

| 现状 | 主张 |
| --- | --- |
| 用评测/报错反馈事后补洞 | 用自建用例事前建模 |
| 上下文以原始文件/检索片段为主 | 以「用例 → 义务 → 支持集」组织理解 |
| 测试只当验收 | 测试当认知脚手架 |

### 3.3 非假说（明确不做主 claim）

- 不是「更强的仓库检索 / start-here」主线（RSG 导航已降级）。  
- 不是恢复 ECSM / 强制状态机工作流入库。  
- 不是让 Agent 看见更多 / 更早看见 benchmark 验收测试（≠「喂更多官方测试」）。  
- 不是压缩上下文 / token efficiency / context management 主线（与长上下文压缩、记忆剪枝、预算调度类工作可有交叉现象，但本文主 claim 是认知阶段注入，不是省 token）。  
- 不是证明人类一定按此流程（需独立 human study 才可声称）。  
- 第一阶段不绑定 SFT/RL；先验证认知注入是否有效。

---

## 4. 方法草图：测试驱动的认知阶段

### 4.1 阶段划分（概念）

```text
[认知阶段]  读 TASK + 完整 repo
            → 提出/找出最小关键用例
            → （可选）在隔离沙箱跑自建探针
            → 写出行为边界与必达表面（API/异常/资源/exclusions）
            → 得到「用例脚手架 + 契约理解」

[实现阶段]  才允许大规模编辑 submission/
            → 用脚手架自检
            → prune
            → 提交

[评测阶段]  harness 跑 private public+hidden+isolation（Agent 不可见）
```

### 4.2 用例允许的来源（兼容 v3）

| 允许 | 禁止 |
| --- | --- |
| 任务公开契约（生成 TASK / `public_spec`） | benchmark `public_tests/`、`hidden_tests/`（v3 test-blind） |
| 完整仓内 upstream tests / docs / examples | 评测器、oracle、evaluation_spec |
| Agent **自己编写** 的探针测试 | 把 hidden 行为当成「猜题目标」写入自测 |

### 4.3 认知阶段期望产出（草案 schema）

可落盘为 workspace 内文件（名称待定，如 `COGNITION.md` / `probes/`）：

1. **关键用例列表**（3–N 条）：前置条件 · 操作 · 可观察结果；每条对齐公开契约中的 API 或 behavior。  
2. **必达表面**：exports / 异常 / 关键成员与资源。  
3. **支持集假设**：拟纳入的文件/模块/数据（可修正）。  
4. **Exclusions**：明确不搬的子系统（抑制 copy-heavy）。  
5. **探针**：可执行的自建测试（若协议允许在 Agent 环境运行）。

认知阶段结束的门闩（验证实验用）：未产出合格脚手架前，禁止或强烈抑制对 `submission/` 的实现性编辑。

---

## 5. 与相邻设定的边界

| 设定 | 关系 |
| --- | --- |
| **v3 Full-Repo / No-Hint Main** | 方法实验的默认底板；不改变评测器与信息边界 |
| **Public-feedback 臂** | 官方 public 可自测 = 额外反馈通道；本方法强调 **自建用例认知**，即使 test-blind 也可做 |
| **No-public / Short-prompt** | 消融臂；本故事不依赖缩短契约 |
| **Contract-Map 文档** | 可视为认知产出的一种序列化；本故事以 **用例/测试** 为第一公民 |
| **RSG / Fact Graph** | 可作可选事实底座；不作为本假说的主干预 |
| **紧凑性** | 认知阶段含 exclusions；主指标仍先看 Functional Pass，紧凑性分报 |

---

## 6. 拟议验证（已确认干预形态；待开跑）

### 6.1 最小实验：两臂

| 臂 | 干预 |
| --- | --- |
| **Baseline** | 现行 OpenHands + 标准 TASK；无强制认知阶段（`--arm main`） |
| **TD-Cognition** | **两阶段**：Phase1 只产 `COGNITION.md`+`probes/`；Phase2 注入脚手架后再实现（`--arm td_cognition`） |

**已拍板：** 模型 `deepseek/deepseek-v4-flash`（API）；两阶段协议（已从锁文件硬门闩改为分阶段）；探针在 Phase1 写+跑。  
**Phase1 gate：** 在 **agent Docker** 内执行 `python -m pytest probes/`（与 Agent 同镜像），不再用宿主机解释器；脚手架标题/用例格式已放宽；`gate.ok=false` 仍进入 Phase2（软门闩），报告按 gate 分桶。  
暂不设 Token-matched 臂。Oracle-Scaffold 留作第二波。

题集与跑法：[`experiments/td_cognition_pilot/`](../experiments/td_cognition_pilot/)。

### 6.2 规模与成功标准（草案）

- 规模：**12** 题（历史 flash public✓/hidden✗ / closure 取向），attempt=1，同一 Docker 配置。  
- 主指标：evaluator **Functional Pass@1**；次要：public/hidden 分项、token/steps、是否先 unlock。  
- 预先判定：  
  - TD-Cognition 相对 Baseline **无稳定增益** → 修订脚手架协议或放弃该注入形态；  
  - 有稳定增益 → 再扩题集，并考虑是否进入 SFT 内化（后置，非本草案范围）。

### 6.3 明确不做（验证前）

- 不上全量 150 做方法扫盲；  
- 不上 Layer-2 SFT / Layer-3 RL，直到两臂结果阳性；  
- 不靠改题抬方法臂。

---

## 7. 论文叙事骨架（若验证阳性）

1. **Claim：** ReAct 式 Agent 系统性跳过行动前的契约建模；对契约完备的仓库级提取任务，这构成可诊断瓶颈。  
2. **Intervention：** 测试驱动的认知阶段——自建/仓内用例作为脚手架。  
3. **Evidence：** FeatureLift 上 Baseline vs TD-Cognition；辅以历史归因（定位非主因、闭包为主因、导航消融阴性）。  
4. **Limitation：** 历史与 v3 协议分报；**Agent 自建认知用例的能力上限**（见 §8.6）；紧凑性与正确性分离；非跨语言外推；≠ token-efficiency 主线。

若验证阴性，本文档降级为「已尝试的假说记录」，不写入主结果宣称。

---

## 8. 开放讨论点（确认前）

1. ~~认知阶段门闩强度~~ → **已定：硬阻断**。  
2. ~~探针是否必须可执行~~ → **已定：写+跑通 `pytest probes/`**。  
3. ~~首批题与模型~~ → **已定：DeepSeek Flash + [`experiments/td_cognition_pilot/task_ids.txt`](../experiments/td_cognition_pilot/task_ids.txt)**。  
4. 是否需要 Oracle-Scaffold 臂测上限（第二波）。  
5. 方法实验与 **v3 正式 baseline** 的优先级：并行小样本方法试跑 vs 先出 v3 主表。  
6. **Agent 自建测试的能力上限（limitation，先承认、不急于回答）：** 若某题的契约复杂度已超出 Agent 的理解力，它生成的认知用例可能是错的或漏的，认知阶段就会变成 garbage-in-garbage-out。本方法隐含假设：**Agent 生成认知用例的能力下限，高于其直接实现解耦代码的能力下限**；该阈值的精确刻画与失效边界留作后续研究（可用 Oracle-Scaffold 臂部分探测「完美脚手架」上限，但无法单独回答「自建质量何时崩塌」）。

---

## 9. 相关文档

| 文档 | 角色 |
| --- | --- |
| [FINDINGS.md](FINDINGS.md) | 历史结果能/不能支持什么 |
| [EXPERIMENT_ARMS.md](EXPERIMENT_ARMS.md) | Main / No-public / Short-prompt |
| [TASK_DESIGN_RULES.md](TASK_DESIGN_RULES.md) | 公开契约与可见性宪法 |
| [SERVER_RUNBOOK_PYTHON150.md](SERVER_RUNBOOK_PYTHON150.md) | v3 正式跑法 |
| [06_paper_outline.md](06_paper_outline.md) | 论文大纲（方法节可挂本故事） |
