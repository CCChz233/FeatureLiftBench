# 顶会投稿就绪路线图

> **Status: active execution plan · Last updated: 2026-08-29**
> 目标：把 FeatureLiftBench 收敛成一篇以 benchmark 和 empirical study 为主的顶会论文。  
> 原则：停止继续发散新 Agent 方法；优先补齐 **Python-200'（150+Hard-50）** 的
> 分析层、干净主表和可复现性。

## 0. 当前判断

项目已经具备任务定义、三轴 taxonomy、150 实证和 Hard-50 校准，但还不适合立即投稿。

当前真正的 blocker 不再是「E50 混进主表却没拆开」——E50 已降为旁路——而是：

1. Python-200' Flash 收到包有 **132/200 audit headline**，但 17 题未启动、16 题离线
   依赖失败、59 题 context violation；严格替换集合为 84 题，不能把它或旧 72%
   直接当最终新主表；
2. 150 工作树相对 freeze 有 drift，脏树上的 200 分不能当冻结分；
3. 150 分析层未与 Hard-50 ledger 合并；
4. Hidden 合同出处审计仍按原路线进行，不阻塞分析层合并。

论文定位固定为：

> **FeatureLiftBench 评测代码 Agent 从完整仓库中抽取行为完整、独立功能包的能力，
> 并揭示行为闭合、不可见 Hidden 合同和无效自测尾部是主要瓶颈。**

不要把论文定位成“提出了一个稳定提升成功率的新 Agent 方法”（包括 Active
Dynamic Exploration）。方法臂以负结果和机制诊断为主，放在 failure analysis /
discussion。

## 1. 已经可以作为论文基础的证据

- 任务定义与 Full-Repository / No-Hint 信息边界。
- Python-150 三轴 taxonomy v2、lift 标注、四模型 Functional 18%–66%。
- Hard-50：50 题 release、Flash 功能 29/50=58%、copy-all RRES ≫ 1。
- 旧 150+E50 跨模型 Main（21.5%–72.5%）可作为 **superseded** 对照，证明 E50 过易。
- 通过轨迹上的 `T*`：完整包通常早于 Agent 停止；合法可见信号不足以推出停机规则。
- Public-feedback Flash-12、Qwen 2M cap、Lite 协议和其他方法 pilot 是信息边界、
  成本和负结果，不能混入新主表。

权威数字和禁止混用的结果边界以 [STATUS.md](../STATUS.md) 为准。

## 2. 硬性原则

### 2.1 不再做的事

- 不再开 V3、Rescue+、TFL、V2 或其他新方法并扩到 200。
- 不把 Core-12、RQ6、Spec-adversarial、runtime smoke 的通过率写进 Python-200 主表。
- 不把 `summary.passed` 或 Agent 正常退出当作 Functional Pass。
- 不把无配对跨模型 RRES 中位数解释成模型紧凑度排名。
- 不把 Hidden 测试源码提供给 coding Agent，也不把 Hidden-aware 审计输出回灌给 coding Agent。

### 2.2 无人工 Hidden 审计规则

人工复核不再作为流程依赖。采用 Agent + 确定性聚合：

1. Auditor A：只看 `TASK.md`、`metadata.public_spec`、`repo/` 和脱敏 `audit_packet.json`。
2. Auditor B：独立运行，只看同一公开输入；可以使用 A 的引用做审查，但不能看到
   Hidden 文件、预期标签或旧报告。
3. 每条记录必须经过 schema、身份、路径、行号和 SHA 引用校验。
4. 两个 Agent 的合法记录给出同一 verdict，才进入 `agent_consensus`。
5. 任一记录无效、`abstain` 或 verdict 冲突，最终标为 `abstain` / `unresolved`，
   不使用当前“按严重度取最大值”的规则强行定 gold。
6. 合成 canary 的正确率只能证明协议能工作，不能替代真实 Flash-33 的公平性证据。

## 3. 执行顺序与通过门槛

按顺序推进；前一阶段没有达到门槛，不扩下一阶段。

### Gate 0：修复后的 Agent 审计闭环 smoke

**目标**：证明 Agent 能在硬步数上限内一次性写出记录，并被独立校验器提前终止。

**动作**：对当前公开的 distlib 单案例先跑一遍 R4；不改变任务输入，不使用旧标签。

**通过条件**：

- `audit_record.json` 存在且独立验证为 valid；
- `source_tree_unchanged=true`；
- 记录稳定后触发 early stop，或 Agent 正常写完后退出；
- 达到 24 步而未写记录时，退出码非零且报告不记为 normal exit；
- stdout/stderr、trajectory、validation 和 run summary 均保留。

**失败处理**：只修协议和 runner，不扩大案例、不调高预算掩盖失败。

**建议输出目录**：
`experiments/validation/agentic_evidence/runs/flash33-distlib-tool-smoke-r4-<date>/`

### Gate 1：Flash-33 Agent provenance 审计

**目标**：确认 Hidden 失败究竟是 Explicit / Recoverable，还是公开信息不足。

**分波次执行**：

1. 先跑 3 个案例，覆盖不同仓库和不同类型；
2. 再跑 10 个案例，验证成本、valid rate 和冲突处理；
3. 最后跑完整 Flash-33。

每个案例至少需要两个独立审计视角。为了控制 API 成本，可以让第二阶段先做
引用审查；但对于冲突、低置信度和 `underdetermined`，必须回到公开仓库独立检索。

**必须改造**：

- `aggregate_flash33_audit_labels.py` 改为显式读取多个 reviewer/run；
- 不再按 severity 直接覆盖冲突；
- 输出每个 assertion 的 A/B verdict、validity、confidence、citation status、
  consensus 状态和 abstain 原因；
- 将无效记录和缺失记录视为 audit coverage failure，而不是正常标签。

**Gate 1 产出**：

- `flash33_agent_labels_consensus.json`；
- `flash33_agreement.json`：valid rate、agreement、conflict、abstain、citation coverage；
- 每个案例的公开证据包和可重放命令；
- 不把“Agent 共识”称为 human gold，除非另有人工金标实验。

**解释规则**：

- `explicit` / `recoverable`：可用于“公开信息足以推出目标”的主分析；
- `ambiguous`：标记为多目标冲突，不可归因于单纯 Agent 能力；
- `underdetermined` / `abstain` / conflict：进入公平性风险和敏感性分析，不强行归类。

### Gate 2：Hidden 公平性的敏感性分析

**目标**：证明主要模型结论不是由不可观测 Hidden 合同制造的。

重新计算每个 Main 模型至少三种口径：

1. **All tasks**：当前完整 Functional Pass@1；
2. **Observable-only**：剔除被 consensus 标为 `underdetermined`、`ambiguous` 或
   `abstain` 的 Hidden obligation/task；
3. **Conservative bound**：把 unresolved obligation 分别按 fail 和 not-scored 处理。

必须报告：通过率变化、Wilson 区间、模型排序是否变化、失败阶段分布是否变化。

**判定**：

- 如果排序和核心结论稳定：可以保留当前主故事，并把敏感性表放正文或附录；
- 如果排序变化：主表改为 observable-only 或双主表，不能继续用未修正的能力叙事；
- 任一 unresolved obligation 都不能被描述成“模型确定犯错”。

**建议产出**：
`artifacts/research_analysis/current_results/hidden_provenance_sensitivity_<date>.json`

### Gate 3：Python-200' 分析层 + 主表

**目标**：论文主套件是 150 + Hard-50。避免旧 External-50 的 90%–94% 和 RRES≈1.0
掩盖结论；也避免在脏 150 工作树上跑出「冻结」分。

必须先完成：

- ~~合并 150 taxonomy CSV 与 Hard-50 ledger~~（已完成：`python200_hard_v1`）；
- ~~接收并审计 Python-200' Flash 包~~（原始 headline 132/200；评测根
  `benchmark/python200_hard_tasks/`，registry `python200_hard_registry.json`）；
- 修复 16 个离线依赖、解决 17 个 freeze-spec mismatch，并对冻结的 84 题严格替换；
- 列 **150 / Hard-50 / Python-200'**，禁止混入 E50 90%–94%。

然后对主表输出：

- Direct / Adapted / Composite 构成；
- copy fraction、文件数、LOC、依赖和 isolation；
- Functional Pass 条件下的 RRES coverage 和 paired policy。

**论文规则**：

- External-50 只作 easy / copy-heavy 旁路；
- Hard-50 Flash 58% 是校准，不是 200' 主表；
- 若 150 上 RRES 仍贴 1.0 而 Hard-50 通过解明显 <1，按 split 写，不要合成一个中位数；
- 跨模型紧凑度只在成对子集上比较。

### Gate 4：单次运行稳定性

**目标**：估计 Agent stochasticity，而不是只估计任务抽样误差。

**最小方案**：

- 分层选 24 个任务，覆盖 Python-150 / Hard-50、Direct / Adapted / Composite、
  通过/失败和不同首败阶段；
- 对 DeepSeek Flash 固定同一 Main 配置跑 3 次；
- 已有同协议轨迹可计入一次，其余两次新增；
- 若预算允许，再对一个 Qwen 模型复现同一 24 题。

**报告**：task-level pass probability、seed variance、首败阶段稳定性、排名/差异的
bootstrap 区间。不要把这组小样本结果冒充新的 Python-200' leaderboard。

### Gate 5：Runtime replication（强烈建议）

**目标**：检查主要现象是否完全由 OpenHands runtime 造成。

使用已经固定的 Core-12，比较同一模型下：

- Official OpenHands；
- DeepSeek Harness 或 Codex 其中一个。

这是成对 runtime ablation，不是新的主模型排行榜。若不做，论文范围必须明确写成
“OpenHands 下的模型和轨迹研究”，不能泛化为所有 coding Agent。

### Gate 6：论文和 artifact freeze

提交前生成一个不可变 paper bundle，包含：

- task selection / source registry / baseline freeze ID；
- model revision、agent profile、agent/evaluator image digest；
- 每题 `run.json`、`eval/result.json` 和缺失/infra/rerun ledger；
- 主表、失败 funnel、敏感性表、RRES 分解、`T*` 分析和 RQ6；
- 所有派生表的重建命令和 SHA256；
- licensing、training contamination、有限测试完备性等 limitations。

论文中的所有数字只能来自这个 bundle，不再从历史 README 或 mixed-snapshot 结果手抄。

## 4. 论文结构锁定

### 主贡献

1. repository-level feature extraction 的任务定义；
2. 200-task、176-repository 的 Full-Repository / No-Hint benchmark（150 + Hard-50）；
3. 跨模型能力差异和互斥失败 funnel（主表以 200' 为准，出分前不写旧 72%）；
4. Hidden 不可见性、无效自测尾部和成本/行为闭合机制发现。

### 主表

1. Python-200' Functional Pass@1，并拆 Python-150 / Hard-50；
   旧 150+E50 只作 superseded 对照；
2. build / public / hidden / isolation 首败 funnel；
3. observable-only / conservative Hidden sensitivity；
4. 通过题的 compactness diagnostics；
5. 同模型方法/成本对比；
6. `T*` 与 lift type 分层；
7. RQ6 Public-feedback 成对结果（单独小节，不替换主表）。

### 不放进主表

Rescue+、V2、TFL、Core-12、Spec-adversarial、runtime smoke、未完成的 Hidden
provenance 初标，以及任何 `summary.passed` 计数。

## 5. 完成定义（Definition of Done）

只有以下条件全部满足，才认为“可以投稿”：

- [ ] Gate 0 smoke 通过，审计 runner fail-closed；
- [ ] Flash-33 公开审计 33/33 有明确的 valid/invalid/abstain 状态；
- [ ] 冲突不会被 severity 规则覆盖；
- [ ] 所有非 abstain 标签都有可重放公开引用；
- [ ] Hidden sensitivity 已完成，且主结论对 unresolved 的处理方式透明；
- [x] Python-150 / Hard-50 的通过率和 copy/compactness 已拆分；
- [x] Python-200' 分析层（taxonomy × lift × copy-trap）已合并；
- [ ] 关键比较有正确的 paired policy 和区间；
- [ ] 至少完成 DeepSeek 24-task 三次运行稳定性检查，或在 limitations 中明确延期；
- [ ] 至少完成一个 Core-12 runtime replication，或严格收窄论文泛化范围；
- [ ] Docker strict preflight、镜像 digest、task/source checksum 全部归档；
- [ ] 论文主表数字可由 paper bundle 一键重建。

## 6. 实际执行顺序

当前下一步只做（与组会口径一致）：

1. Python-200' 分析层已合并（`python200_hard_task_taxonomy.csv`）；
2. 收到包 audit headline 为 132/200；按冻结清单修复依赖与 freeze mismatch，并对
   84 题做严格替换、按 task ID 合并，闭环前不要写冻结主表；
3. Hidden provenance 仍按 Gate 0→1→2 推进，不阻塞第 1 步；
4. 生成 150 / Hard-50 RRES 分解；E50 只作旁路；
5. 跑 24-task stability（在 200' 主表之后分层抽样）；
6. 跑 Core-12 runtime replication，或收窄论文泛化范围；
7. 冻结 paper bundle，开始写正文。

在 Gate 1 和 Gate 2 完成前，不把当前 Hidden 初标写成论文金标结论。
在 Python-200' 严格替换结果通过全部资格门前，不把 132/200 或旧 72% 写进
摘要。不再扩展新的 Agent 方法。

相关入口：

- [Paper Outline](06_paper_outline.md)
- [Current Status](../STATUS.md)
- [Hidden Contract Provenance](../HIDDEN_CONTRACT_PROVENANCE.md)
- [Known Limitations](limitations.md)
- [Reports index](../../reports/README.md)
- [External-50 → Python-150 工程规格](../archive/plans/PLAN_EXTERNAL50_TO_PYTHON150_QUALITY.md)
  （Gate 3 的建设路径；独立 freeze，不并进 150）
