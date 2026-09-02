# Python-200′ 现有 Agent 失败的过程级分析

> **Status: trajectory first pass · contract-alignment audit complete · human adjudication pending**

> **Second-pass refinement (2026-09-01):** 本报告中的 19 个“契约对齐”是行为条款层面的一审集合。进一步检查精确 oracle 后，其中 12 个为模型主因、3 个为 mixed、4 个存在 TASK 精确规则不足。模型探索深度与 TASK 清晰度的逐题复核见 `contract_clarity_vs_exploration.md`；论文中不要直接把 19 全部写成纯 Agent 失败。

## 核心结论

原输出侧分析中的 34 个候选不能全部解释为 Agent 失败。逐题对照运行时 TASK 与首败测试后，只有 **21 个**可以进入 Agent 过程归因：其中 19 个形成了提交并发生契约对齐的功能失败，另有 2 个未形成提交。剩余 13 个首先暴露的是 benchmark 契约与 evaluator 的一致性问题。

在 19 个契约对齐的功能失败中，**17/19（89.5%）** 的 Agent 在轨迹末尾明确宣称实现完成或验证通过。这说明主要问题不是完全没有定位或完全没有编码，而是 Agent 在自选测试通过后过早判断契约已经闭合；自测没有区分出 evaluator 所覆盖的关键边界。

## 先做公平性净化

| TASK–evaluator 一致性 | 任务 | 占 34 个候选 | 处理 |
| --- | --- | --- | --- |
| 契约对齐 | 19 | 55.9% | 进入 Agent 分析 |
| 未进入功能评测 | 2 | 5.9% | 进入 Agent 分析 |
| 契约含糊 | 6 | 17.6% | 人工裁决前排除 |
| 评测越界 | 7 | 20.6% | 排除并修订题目 |

明确越界的典型情况包括：测试调用 TASK 未声明的方法、对 TASK 只声明的状态额外检查响应正文、以及要求 TASK 未规定的返回对象相等语义。契约含糊项则是行为目标存在，但入口方法、默认常量或精确异常类型没有公开。

## 可归因失败的过程原因

| 过程原因 | 任务 | 占 21 个可归因失败 |
| --- | --- | --- |
| 错误的契约闭合/自测未区分 | 16 | 76.2% |
| 未形成提交 | 2 | 9.5% |
| 步数与上下文预算耗尽 | 2 | 9.5% |
| 上游语义优先于任务契约 | 1 | 4.8% |

其中“错误的契约闭合”表示 Agent 已形成提交、执行了自选验证并宣布完成，但验证集没有覆盖最终失败的已声明行为；它不是对 Agent 心理状态的推断，而是由轨迹中的测试动作、完成声明和 evaluator 反例共同支持。

## 输出侧表现

| 输出侧结果 | 任务 | 占 21 个可归因失败 |
| --- | --- | --- |
| behavior_drift | 14 | 66.7% |
| contract_api_completion | 5 | 23.8% |
| agent_process_non_delivery | 2 | 9.5% |

输出侧以行为语义漂移为主；过程侧则以验证闭合错误为主。二者共同说明：Agent 往往能够找到相关模块并生成大体可运行的实现，但没有把 TASK 中分散的 API、状态、边界、异常和适配语义转化为一组具有区分力的验收检查。

## 上下文与运行预算

可归因失败中有 **9/21** 个存在 context-window 违规。两道以 step limit 结束的有效题同时存在 context 违规，因此预算耗尽对这两题有直接证据；其他违规题仍形成提交并宣称完成，不能仅凭违规标记把其语义错误归因于上下文。

运行器普遍出现的 `tool_validation_error` 也不能直接当作功能根因：不少任务虽然 Agent 容器返回 86，但提交已生成且 evaluator 正常执行。报告以提交和 evaluator 结果为准，运行器状态只作为过程辅助证据。

## 代表性案例

- **Alembic：自测数量多但区分力不足。** Agent 声称 130 个上游测试和 51 个契约测试通过，最终提交仍在 merge graph 中丢失 base revision。问题不是没有测试，而是自测没有覆盖任务特定的合并后索引不变量。
- **Decorator：上游语义压过任务契约。** Agent 的自写场景已经观察到调用参数形状不一致，随后用上游 `decorator` 的默认行为解释该差异并宣布完成；evaluator 正好在任务要求的调用形状上失败。
- **Pylint / Typer：预算耗尽导致不完整交付。** 两条轨迹都以 `step_limit_exceeded` 结束，且缺失 TASK 明确声明的公开导出或子模块。这类失败与“自测后误判完成”不同。
- **Click / Pluggy：不是 Agent 契约遗漏。** evaluator 分别调用了 TASK 未声明的 `invoke` 和 `call_historic`；这两题必须先修订 TASK 或测试，不能作为 Agent 失败案例。

## 对论文的可用结论

当前证据支持的最稳妥表述是：**现有 Agent 的主要失败不是无法生成代码，而是无法可靠地确认一个跨模块功能的完整可观察契约已经闭合；它们常用大量但非区分性的自测建立错误完成信心。**

同时，这轮分析也给 benchmark 本身提出了硬要求：主表前必须逐题证明 evaluator 的每个可观察断言都能映射到 TASK 的稳定 clause。否则，隐藏契约会把 benchmark 缺陷错误地计入 Agent 缺陷。

## 证据与限制

- 原始 suite：`experiments/python/openhands/deepseek-v4-flash/python200-hard-main-20260829`
- 逐任务过程表：`failure_process_analysis.csv`
- 标注源：`failure_process_annotations.csv`
- 本轮为单 reviewer 的 trajectory first pass；论文定稿前需对 6 个含糊项和全部 Hidden-only 失败进行第二 reviewer 裁决。
- 没有重新运行实验；所有数字来自保留的 TASK、提交、evaluator 日志、run.json 和 OpenHands events。
