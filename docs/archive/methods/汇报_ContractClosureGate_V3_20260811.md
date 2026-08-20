# Contract Closure Gate V3 阶段结论（2026-08-11）

> **Status: archived · Last verified: 2026-08-17**
> 负结果切片，不是当前协议。

## 结论先行

V3 已实现并完成真实 API 三题小切片，但当前版本失败，不能扩大实验：

- V2.1：1/3 Functional Pass，5,919,461 raw tokens；
- V3：0/3 Functional Pass，5,422,221 raw tokens；
- token 降低 8.40%，但丢掉了原本通过的 Rich，因此不是有效改进。

本轮没有 evaluator 泄漏。Agent 只看到公开契约、公开上游仓库和本地
micro checker；私有 evaluator 始终在 agent 完成后独立运行。

## V3 做了什么

V3 保留 V2.1 的 2M/45 主预算和 200k/5 修复预算，在结构检查之外要求
Agent 写两条、最多三条公开行为冒烟 case。`--micro` 模式只执行少量 case，
不要求覆盖全部 Bxxx；只有具体行为不一致或小型结构缺口可以触发修复。

工程回归为 462 passed、7 skipped。

## 三题结果

| 任务 | V2.1 | V3 | V3 token | V3 gate | V3 case |
|---|---:|---:|---:|---:|---:|
| Bleach | fail | fail | 1,650,153 | open | 0 |
| Importlib Resources | fail | fail | 1,989,487 | closed | 2 |
| Rich | pass | fail | 1,782,581 | open | 0 |

三个 Agent 都耗尽 45-step 上限。只有 Importlib Resources 真正写出了两条
case；另外两题直到结束仍未进入行为验证阶段。

## 暴露出的核心问题

1. **阶段调度不可靠。** 仅靠 prompt 要求模型“最后写两条 case”无法保证它
   预留步骤。Bleach 和 Rich 都在源码阅读/复制中耗尽预算。
2. **micro 闭合条件太松。** Importlib 一条 case 通过，另一条因为
   `SimpleReader` 未定义而 `NameError`。检查器把它记为 unknown，并因已有一条
   pass 而整体闭合；正式 evaluator 随后发现公开契约要求的父路径逃逸没有抛
   `TraversalError`。
3. **repair 粒度计算太粗。** Rich 缺少 `markup` 和 `text` 两个根模块，检查器
   展开成六条嵌套 API 缺口，超过“三条 finding”阈值，导致没有修复。语义上
   这是两个根缺口，不应被判断为大范围不可修。
4. **token 下降不等于效率提升。** 本轮没有任何任务通过，也没有运行 repair；
   少用的 token 主要来自更早耗尽/停止，而不是更高效地完成任务。

## 下一步建议：V3.1，而不是直接扩大样本

- 主实现先结束并通过结构 gate，再进入独立的少步行为 case 阶段；
- `NameError`、语法错误、case 协议错误记为 fail，只有环境不可用、超时或不稳定
  才记 unknown；
- 两条选中的 case 必须都有效执行，不能用“一条 pass + 一条 unknown”闭合；
- repair 决策按缺失根 API 聚类，嵌套成员不重复计数；
- 根据公开 Bxxx 文本优先选择 `raise`、`prevent`、`strip`、嵌套路径、状态变化、
  delegation/recursion 等高风险条款。

V3.1 仍先跑相同三题。最低门槛是恢复到 V2.1 的 1/3，通过率不下降，且总 token
不超过 5,919,461；达不到就停止 Contract Closure Gate 路线，不进入 12 题。

完整实验报告见
`experiments/methods/contract_closure_gate_v3/v3_smoke3_real_api_20260811_1-summary.md`。
