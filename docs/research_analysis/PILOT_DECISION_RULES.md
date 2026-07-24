# ECSM-Prompt Pilot 预注册判定规则

> **SUPERSEDED（2026-07-23）**  
> ECSM Pilot **已废弃**，本规则不再执行。见 [../CURRENT_RESEARCH.md](../CURRENT_RESEARCH.md)。

## 1. 冻结范围

本规则在运行第一个 pilot cell 之前随 `pilot_freeze_manifest.json` 冻结。实验定义来自 `experiments/ecsm_pilot/pilot_manifest.yaml`，运行器为 `run_pilot.py`，分析器为 `analyze_pilot.py`。任何阈值变更或冻结资产变更必须增加 `pilot_revision`，保留旧结果和 change ledger，不能覆盖历史 cell。

当前冻结为 revision 5（`c94764ed110992a6`），证据状态是 `provisional_ai_assisted_annotations`，0 cells 已执行。工程 freeze 允许管线诊断，但不等于论文标注门禁通过。实际执行还需满足 `pilot_execution_authorization_status.json` 的外部导出授权；hidden tests、hidden nodeids、behavior contract 和任何具体 hidden 输入/断言始终不得外发。

完整矩阵是 10 个任务 × 7 个 arm × 1 seed = 70 cells，但按阶段投入：

- 阶段 A：2 个 control task × 7 arms = 14 cells，只验证管线；
- 阶段 B：4 个机制任务 × 5 arms = 20 cells，只决定是否投入阶段 C；
- 阶段 C：仅在资源门禁触发后补齐剩余 36 cells。

七个完整矩阵 arm 为：

- `standard`
- `strong_prompt`
- `oracle_locate`
- `static_closure_hint`
- `oracle_closure`
- `copy_first_then_prune`
- `ecsm`（论文名称 `ECSM-Prompt`）

所有 arm 固定：DeepSeek-V4-Flash、OpenHands、temperature 0、120 最大步骤、6,000,000 per-instance total-token guard、相同 context/output budget、相同工具、public-only 测试权限、Docker evaluator 和 `submission/featurelifted` 协议。唯一允许差异是已登记的 condition appendix 和非 hidden hint。

## 2. 数据有效性门槛

1. 阶段 A 要求 14/14 完整；阶段 B 资源决策要求其 20/20 完整。未完成 cell 不以失败替代。
2. 若资源门禁未触发，实验合法停止在 34 cells，只能报告“当前资源门禁未触发”；这既不是机制结论，也不否定任何机制。
3. 只有完成阶段 C 后，70-cell pilot 主分析才可使用 `analyze_pilot.py --require-complete`。论文机制结论还必须结合 Diagnostic-40、closure gold 和轨迹证据。
4. dependency install、eval tooling 或 Docker sandbox error 的 cell 标为 infrastructure missing，修复后用相同 submission 重评或重跑同 cell。主表同时保留 raw 与 environment-excluded。
5. 如果任一 arm 有 ≥2 个 infrastructure missing，不能比较该 arm 的 Pass@1。
6. closure P/R/F1 至少覆盖每个 arm 的 8/10 任务，否则 closure 指标只作案例证据，不能触发最终机制结论。
7. `included_source_files` 优先；没有显式 state 时只能使用分析器的 hash/line provenance。无法确认时为 NA，禁止填 0。
8. sanity 两题如果因 prompt/协议错误系统性失败，先判定实验实现失败，不能解释为方法效果。
9. 这是方向选择 pilot，不做显著性宣称。以 paired task wins/losses、绝对任务数和机制一致性为主；完整论文实验再增加 seeds 和区间估计。

## 3. 阶段 B 资源门禁（仅决定是否运行剩余 36 cells）

阶段 B 的四题样本太小，以下条件只用于资源分配，不用于论文机制结论。满足任一项才进入阶段 C：

1. `Oracle Closure` 相对 `Oracle Locate` 至少 2/4 hidden wins，且零 loss；
2. 或至少 1/4 hidden win、零 loss，并且有 complete gold 支持的 closure F1 平均提高至少 0.15；
3. 或 `ECSM-Prompt` 相对 `Strong Prompt` 至少 2/4 hidden wins、零 loss，public-hidden gap 至少减少一题，且 token 与 tool-call 中位数均不超过 1.5 倍。

`analyze_pilot.py` 将判定写入 `stage_b_resource_decision.json`，其中必须保持 `purpose: resource_allocation_only` 和 `paper_conclusion_allowed: false`。未触发门禁不能正式否定 localization、closure、behavior validation 或 ECSM-Prompt。

## 4. 指标定义

设 arm (a) 在 10 个任务上的结果：

- (H_a)：hidden Pass@1，hidden 实际通过且 functional gate 未被 isolation/build 硬门否决。
- (G_a)：public pass、hidden fail 的任务数。
- (F_a)：closure F1 的宏平均，只在有可审计 provenance 的任务上算，并报告 coverage。
- (S_a)：final score 中位数。
- (R_a)：extraction ratio 中位数。
- (T_a)：total tokens 中位数。
- (C_a)：tool calls 中位数。
- (E_a)：`repeated_file_reads + repeated_line_reads + repeated_terminal_commands` 中位数。
- (N_a)：copied/submitted file count 中位数；这是 submission footprint 代理，不是逐行复制真值。

paired net win 定义：同 task/seed 上 treatment hidden pass 且 control fail 记 +1，反向记 −1，相同记 0。

## 5. 完整 Pilot 中何时说明 localization 是主要瓶颈

同时满足才支持“本 pilot 中 localization 为主要瓶颈”：

1. `Oracle Locate` 相对 `Standard` 的 paired hidden net win ≥ 2 个任务；
2. (H_{locate}-H_{standard}\ge 0.20)；
3. `Oracle Closure` 相对 `Oracle Locate` 的 hidden 增益 ≤ 1 个任务；
4. `Oracle Locate` 至少消除 Standard 中 50% 的 build/public API 失败；
5. 增益不能只来自两个 sanity/positive-control 任务。

若 Oracle Locate 增益 <1 个任务，或 Oracle Closure 明显继续提升，则否定“localization 是主要瓶颈”的强版本。

## 6. 完整 Pilot 中何时说明 dependency closure 是主要瓶颈

同时满足才支持 closure 瓶颈：

1. `Oracle Closure` 相对 `Oracle Locate` 的 paired hidden net win ≥ 2；
2. (H_{oracle\_closure}-H_{oracle\_locate}\ge 0.20)；
3. (F_{oracle\_closure}-F_{oracle\_locate}\ge 0.15)，closure coverage 均 ≥80%；
4. `dependency_closure_omission` 与 `hidden_interface_or_closure_failure` 总数至少下降 50%；
5. `Static Closure Hint` 的收益位于 Standard 和 Oracle Closure 之间，或仅在静态 import cohort 有收益；
6. Oracle Closure 的增益不以 extraction ratio 增加超过 0.30 为唯一代价。

若 Oracle Closure 对 Oracle Locate 的 hidden 增益 ≤1 个任务且 closure failure 不下降，否定“closure 是主要瓶颈”的强版本。

## 7. 完整 Pilot 中何时说明 behavior validation 是主要瓶颈

同时满足才支持行为验证瓶颈：

1. Oracle Closure 后仍有 ≥2 个 public-pass/hidden-fail，且首错是行为/异常/顺序/状态语义，而非缺 import/export；
2. `ECSM-Prompt` 或 `Copy-first then Prune` 在 `pluggy` 等 behavior-contract strata 上相对 Oracle Closure 净胜 ≥1，并且未增加 closure gold；
3. ECSM-Prompt 相对 Strong Prompt 的 (G) 至少减少 2 个任务；
4. 增益任务的 state 中存在新增的 contract/property/state-transition probe 证据；
5. 仅增加 source files 而不增加 probe evidence 的 arm 没有取得相同增益。

若 Oracle Closure 已消除全部 gap，或者 ECSM-Prompt 增益完全由多复制文件解释，则不支持“行为验证是剩余主要瓶颈”。

## 8. 完整 Pilot 中何时说明 stopping strategy 是主要瓶颈

支持停止策略错误需要：

1. Standard/Strong Prompt 的失败任务在最终 submission revision 前已有 public success；
2. `ECSM-Prompt` 相对 Strong Prompt 至少减少 2 个 public-hidden gap；
3. 获救任务在 public success 后执行了至少一个产生新 state evidence 的 expand/probe/prune，而不是普通重复读取；
4. ECSM-Prompt 的 repeated exploration 中位数不高于 Strong Prompt，或至少下降 20%；
5. `Native ECSM - stopping guard` 消融在后续实验中丢失主要收益。Pilot 没有该消融，因此本轮最多给“支持”，不能给最终因果结论。

## 9. 完整 Pilot 中何时说明 ECSM-Prompt 只是增加计算量

满足以下计算增加条件之一：

- (T_{ecsm}/T_{strong}\ge 1.25)，或
- (C_{ecsm}/C_{strong}\ge 1.25)，或
- (E_{ecsm}/E_{strong}\ge 1.25)。

并且同时满足所有“无实质收益”条件时，判定为 compute-only：

1. ECSM-Prompt 相对 Strong Prompt 的 hidden paired net win ≤ 0；
2. hidden Pass@1 增益 <1 个任务；
3. public-hidden gap 没有减少；
4. closure F1 增益 <0.05 或 coverage 不足；
5. final score 中位数增益 <0.03。

该判定不允许用“state 更可解释”翻案；它意味着暂不继续扩大实验。

## 10. ECSM-Prompt 值得继续的最低标准

以下是**合取条件**：

1. 相对 Strong Prompt，hidden paired net win ≥2，且 (H_{ecsm}-H_{strong}\ge0.20)；
2. public-hidden gap 至少减少 2/10；
3. 以下三项至少满足一项：
   - closure F1 宏平均提高 ≥0.10，coverage 均 ≥80%；
   - final score 中位数提高 ≥0.05；
   - 在 hidden 不回退的前提下，copied files 或 extraction ratio 中位数下降 ≥15%；
4. total tokens 和 tool calls 的中位数都不超过 Strong Prompt 的 1.5 倍；
5. 两个 sanity task hidden 都不回退；
6. 至少一个 closure strata 和一个 behavior/global-state strata 获益，不能只由单一任务族驱动；
7. ECSM-Prompt state 完整率 ≥8/10，且 finalize 任务都满足停止 guard 字段。

若只达到 +1 hidden task，可进入“再跑 2 个 seeds”的灰区，但不能宣称方法方向已成立。若 hidden 提升为 0，即使 compactness 改善，也只支持 pruning 子模块，不支持 Native ECSM 论文主张。

## 11. 竞争假设到实验结果的映射

| 观察 | 优先支持 | 主要削弱 |
|---|---|---|
| Oracle Locate 大增，Oracle Closure 追加很小 | H1 定位失败 | H2 闭包主因 |
| Oracle Closure 显著超过 Oracle Locate | H2 闭包恢复 | H1 定位主因 |
| Oracle Closure 后 behavior gap 仍多，ECSM-Prompt probe 获救 | H3 行为契约 / H4 停止 | 纯 closure 解释 |
| Strong Prompt 接近 ECSM-Prompt | prompt/workflow mismatch 的简单解释 | Native ECSM 状态机必要性 |
| Static Hint 只救静态 import，动态 cohort 不改善 | 动态状态闭包 | 普通依赖图充分性 |
| Copy-first 提升 hidden 但 ratio/score 恶化；ECSM-Prompt 保持 hidden 并变紧凑 | expand–prune 机制 | 纯多复制策略 |
| 所有结构 arm 受 tool/harness error 同方向影响 | H6 工具/harness 噪声 | 对 Agent 机制的强结论 |

所有结论先按 task-level paired table复核，再看 arm 汇总。禁止只挑成功案例。
