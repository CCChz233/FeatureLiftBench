# Harness-Bench 结构映射与 FeatureLiftBench 写作方案

> **Status: current · Last verified: 2026-09-02**  
> **参考论文：** *Harness-Bench: Measuring Harness Effects across Models in Realistic Agent Workflows* (arXiv:2605.27922v1, 16 pages).  
> **用途：** 只借鉴论证结构和证据排布，不复制其科学主轴、评分公式或实验矩阵。

## 1. 结论

FeatureLiftBench 已经有完整论文框架，也已有足够材料形成一版 **zero draft**。目前不能定稿的主要原因不是没有文字，而是新 Python-200′ 主表、跨模型结果和 Hidden 公平性证据还没有闭环。

Harness-Bench 最值得借鉴的是：

1. 用一个非常清楚的变量定义统一全文；
2. Benchmark 与评测协议在主结果之前讲完；
3. 主结果只回答核心能力问题；
4. 再单独用 Analysis 章命名失败现象；
5. 把配置明细、类别结果和任务卡放到附录。

我们不需要把论文改成“更小的 Harness-Bench”。我们的中心是：

> **FeatureLiftBench 测量的是当前基准没有隔离的仓库级功能抽取能力；其主要诊断现象是 contract-closure failure，而不是 harness dependence。**

## 2. Harness-Bench 的真实结构

Harness-Bench 的正文约 9 页，剩余为参考文献和附录。

| 章节 | 它在完成什么工作 |
| --- | --- |
| Abstract | 问题缺口 → 新 benchmark → 协议和规模 → 主发现 → 命名失败现象 |
| 1 Introduction | 说明 harness 为什么是被忽略的实验变量；用三条列出 benchmark asset / protocol / diagnostic analysis |
| 2 Related Work | 区分静态基准、可执行 Agent 基准和 harness engineering |
| 3 Benchmark | 定义 harness；说明评测 setting、题集设计和验收、运行证据、评分公式 |
| 4 Experiments | 先用控制/变化因子表定义实验，再报主表和 harness dependence |
| 5 Analysis | 从轨迹中归纳互不排他的失败症状，命名 execution alignment / execution drift |
| 6 Discussion | 回到“Agent 能力应报到 model–harness configuration”，说清结论边界 |
| 7 Conclusion | 重述新 benchmark、主发现和用途 |
| Appendix | LLM 使用声明、harness/model 清单、分类结果、代表性任务卡 |

它的论证链非常简洁：

```text
现有基准忽略了一个变量
        ↓
定义该变量与可控评测协议
        ↓
构造可复现题集与证据链
        ↓
主表证明该变量产生明显差异
        ↓
轨迹分析命名一类重复失败现象
        ↓
讨论这对 Agent 评测和系统设计的含义
```

## 3. 对 FeatureLiftBench 的一对一映射

| Harness-Bench | FeatureLiftBench 应对应为 | 说明 |
| --- | --- | --- |
| 被忽略的 harness 变量 | 被忽略的 repository-level feature lifting 能力 | 我们不是研究修 bug 或绿场生成 |
| `Agent = Model + Harness` | `Feature Lift = Locate + Close + Isolate` | 可作为概念图，但不当作数学分解或因果模型 |
| 固定任务/预算/评测，变化 model + harness | 固定仓库/契约/预算/评测/runtime，主表只变化 model | Official Main 应钉死 OpenHands；信息消融单独报告 |
| 106 个多工作流任务 | 200 个仓库级功能抽取任务 | 我们的优势是专一任务深度，不是领域广度 |
| Realism / Solvability / Oracle-checkability / Integrity | 真实仓库 / reference oracle / deterministic evaluator / leak & isolation gates | 这四项验收词法可直接借鉴 |
| Completion × Security × Process | Functional Pass + pass-conditioned RRES | 我们不引入 LLM judge，正确性和紧凑度不加权 |
| Harness dependence | 模型能力差、题型差与信息边界差 | 只做描述性和成对分析，不轻率写因果 |
| Execution drift / alignment | Contract-closure failure | 推理和交付物没有对齐可验证行为契约 |
| 代表性任务卡 | FeatureLift 任务卡 | 列出上游仓库、公开契约、纠缠机制、预期包、评测和失败案例 |

## 4. 建议模仿的正文结构

### Abstract

六句完成：

1. 仓库级功能抽取是实际软件维护需求；
2. 现有 issue repair、代码生成和定位基准没有隔离这项能力；
3. 我们提出 FeatureLiftBench 和 Full-Repository / No-Hint 协议；
4. 介绍 200 题、176 仓、确定性 Functional Pass 与 RRES；
5. 用最终合格主表填入跨模型能力差和关键失败分布；
6. 命名 contract-closure failure，并说明 benchmark 对未来 Agent 设计的用途。

### 1 Introduction

- 用一个真实场景开场：从一个大型旧系统中抽出 parser、config resolver 或 plugin registry；
- 说明“找到代码”、“修复测试”和“从零重写”都不等于功能抽取；
- 定义缺口：当前基准不同时测量 behavior preservation、independence 和 compactness；
- 简述题集、协议和主发现；
- 用三条贡献收尾：**Benchmark asset / Evaluation protocol / Diagnostic analysis**。

### 2 Related Work

1. Issue-resolution and executable software-engineering benchmarks;
2. Code generation, repository understanding and localization;
3. Program slicing, modularization, library extraction and code reuse;
4. Agent evaluation, information boundaries and execution systems.

### 3 The FeatureLiftBench Benchmark

#### 3.1 Repository-Level Feature-Lifting Setting

- 输入、输出、信息边界和允许操作；
- `featurelifted` 独立包；
- Public/Hidden 是同一公开契约的两层深度。

#### 3.2 Task Suite Design and Validation

- Python-150 + Hard-50；
- 仓库选择、不可变快照、task/spec/evaluator/reference 构建；
- Realism / Solvability / Oracle-checkability / Integrity;
- taxonomy 和题集分布；
- External-50 作为过易、copy-heavy 旁路的原因。

#### 3.3 Run Protocol and Evidence Collection

- 沙箱初始化、Agent 执行、提交物收集、Docker evaluator；
- 轨迹、token、workspace tree、evaluator result 和 provenance；
- 基础设施失败与模型失败分开。

#### 3.4 Metrics

- Functional Pass = build ∧ public ∧ hidden ∧ isolation;
- 互斥首败漏斗；
- pass-conditioned RRES 和 copy/dependency 辅助指标；
- token、steps、latency 与 \(T^*\) 是诊断指标，不与正确性加权。

### 4 Experiments

#### 4.1 Setup

- 用一张“固定什么 / 变化什么”表；
- Official Main 钉死 OpenHands、prompt、budget、Docker images 和 evaluator；
- 主表只变化 model；
- Public-feedback 作为单独信息消融；
- runtime 更换只进附录或 limitations。

#### 4.2 Functional Capability

- Python-200′ 跨模型主表；
- 150 / Hard-50 分解；
- Wilson 置信区间；
- 互斥失败漏斗。

#### 4.3 Compactness and Task Dependence

- 仅在 Functional Pass 上报 RRES;
- 150 / Hard-50 / copy-trap 分解；
- Direct / Adapted / Composite 与 entanglement 切片；
- 小样本只作描述，不写因果。

### 5 Analysis

#### 5.1 Observed Failure Symptoms

- mechanical stage 与 semantic cause 分开；
- missing export、exception semantics、state/resource closure、behavior drift、packaging 等；
- 报告 unknown 率、标注来源和代表案例。

#### 5.2 Contract Closure

- 定义 contract-closure failure;
- 使用 `itsdangerous`、`configobj`、`requests_cache` 案例；
- 说明 localization success / broad copying 不等于 behavior closure;
- 不在无 localization gold 时写排他性因果结论。

#### 5.3 Information and Resource Boundaries

- Public-feedback 将 Public 失败 6/6 救回，但 4/5 已有 Hidden 失败不动；
- \(T^*/T\) 与 post-sufficiency self-testing tail;
- 脚手架负结果；
- 这些是机制证据，不是新方法 leaderboard。

### 6 Discussion

- Feature lifting 作为独立能力的意义；
- 正确性和紧凑度的张力；
- 为什么合法自测信号不能直接作为 Hidden oracle 或停机规则；
- 对契约推理、边界例生成和可验证交付物的启示；
- 限制：Python library/tooling 偏置、Hidden 有限性、AI-assisted 标注、runtime 绑定、单次运行。

### 7 Conclusion

只重述三件事：新能力、可复现基准、contract-closure 实证发现。

## 5. 控制与变化因子表（建议进正文）

| Factor | Official Main treatment |
| --- | --- |
| Task contract and repository snapshot | Fixed per task |
| Initial workspace and source registry | Fixed per task |
| Agent runtime | Fixed to OpenHands Official Main |
| Prompt, action budget and context envelope | Fixed |
| Evaluator and Docker images | Fixed and digest-attested |
| Model backend | Varied in the main matrix |
| Public-test visibility | Withheld in Main; varied only in RQ6 |
| Source-location hint | Withheld in Main; future paired ablation only |
| Reference solution and Hidden tests | Never exposed to the Agent |

这张表是 Harness-Bench 最值得借鉴的表达方式之一。它可以在审稿人读主表之前，先回答“分数差异究竟归属于什么实验配置”。

## 6. 可以模仿与不能模仿的边界

### 可以模仿

- 三段式贡献：Benchmark asset / protocol / analysis;
- 在 Experiments 前完整定义任务和指标；
- 控制与变化因子表；
- 主结果后单列 Analysis；
- 给失败现象一个可反复使用、但有证据边界的名字；
- 任务卡和完整配置进附录；
- 将结果限定为“在本协议下的描述性测量”。

### 不能模仿

- 不把论文变成 harness 比较；
- 不引入 LLM-as-judge 过程分与 Functional Pass 相乘；
- 不为了看起来“大”而把专一任务稀释成多领域日常工作流；
- 不在没有同等证据时仿写 6 harness × 8 model 的 factorial 叙事；
- 不把 OpenHands / Codex / DeepSeek Harness 的非对齐结果混入主表；
- 不把契约闭合写成已经被排他性证明的唯一原因。

## 7. 对当前初稿完成度的判断

| 部分 | 现在能否写 | 主要材料 | 未闭环项 |
| --- | --- | --- | --- |
| Abstract | 可写结构稿 | 任务、规模、指标、机制证据 | 最终主表数字不能填 |
| Introduction | 可写 90% | 任务定义、相邻基准差异、贡献 | 最终主表数字仍空；related-work 主引用已进 LaTeX 稿 |
| Benchmark | 可写 90% | 冻结套件、taxonomy、设计和评测文档 | 入题 attrition 和红队细节待浓缩 |
| Evaluation / Setup | 可写 90% | `EVALUATION.md`、freeze、images、profiles | 最终 paper bundle 尚未冻结 |
| Main Results | 只能写表结构与证据边界 | 收到包审计、旧套件历史对照 | 合格 Python-200′ 主表与新套件跨模型 |
| Failure Analysis | 可写 60%–70% | 漏斗、案例、taxonomy、轨迹证据 | Hidden 审计、独立语义编码和 unknown 率 |
| Information / Cost | 可写 80% | RQ6、\(T^*\)、负结果方法 | 要明确这些主要来自旧套件或子集 |
| Discussion | 可写 80% | 信息边界、正确性/紧凑度、Agent 启示 | 结论强度需随最终主表调整 |
| Limitations | 可写 90% | `limitations.md` | seed / runtime 做不做需最终拍板 |

因此现在适合的产物是 **有完整论证链的 zero draft**，不是伪装数字齐全的 submission draft。
