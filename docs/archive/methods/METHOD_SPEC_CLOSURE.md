# Main + Monotone Spec-Closure Pass

> **Documentation status: archived · Indexed: 2026-08-04**

**方法简称：** Spec-Closure（暂定）  
**状态：** 设计草案 · 从未实现 · **不是**当前主线  
**前置：** 完成 [CONTRACT_CLOSURE_AUDIT.md](../plans/CONTRACT_CLOSURE_AUDIT.md)；只用
contract-closed 题开发。  
**更新时间：** 2026-07-31

## 1. 一句话

在 Main 之后增加一轮**单调、可回退**的规格闭合修补：只根据合法证据修 API/
签名/TASK 明文行为/同构上游执行结果；禁止把 Agent 自创 adapter 或上游
observation 自动当作目标 oracle。

## 2. 为什么换这条路

TFL 正式负结果（1/6，相对 Main −1，~2.71× tokens）表明：

> “会写测试”≠“会写与 FLB 目标语义对齐的测试”。

对 cross-API / Adapted / Composite 任务，写正确 paired test 本身就要求先解决
目标语义映射，难度不低于模块剥离。动态分析应帮助理解源码与发现闭包缺口，
**不能替目标 TASK 定义答案。**

（Lift 类型定义见 [LIFT_TAXONOMY.md](../../reference/LIFT_TAXONOMY.md)。）

## 3. 协议（最小）

```text
正常 Main 实现 candidate A
  → 冻结 A
  → 检查全部 Required API 与 signatures
  → 针对 TASK 条款做少量定向运行 / Debugger 查询
  → 只对有合法证据的缺口作局部补丁，得到 B
  → B 未通过全部保持检查则回退 A
  → formal（test-blind，无条件）
```

### 仅允许三类修复证据

1. **机械可判定**：Required API / 签名缺失或明显不匹配；
2. **TASK 明文**：条款直接写出的行为、异常类型、返回形状；
3. **同构执行**：上游与目标场景直接同构时的执行结果（`direct-oracle`）。

### 明确禁止

- 把上游 observation 当目标 oracle（当需要 Agent 发明 adapter/投影/期望值时）；
- paired case 框架、`oracle.json`、大批量自编 tests、freeze/verify 两阶段；
- 自动 full-repo trace 当契约；
- 第二个 Agent；
- formal/hidden 反馈修复。

## 4. 与已失败路径的对比

| | TFL | PDR / Self-Contract | Spec-Closure |
| --- | --- | --- | --- |
| 答案来源 | 上游执行（经 Agent 写的 adapter） | Agent 探针 / 差分 | TASK + 机械 API + 仅同构上游 |
| 风险 | 错误语义写进 oracle | 自圆其说 | 证据过窄则少修、回退 A |
| 成本目标 | 实测 ~2.71× Main | PDR ~2.16× | ≤ ~1.5× matched Main |

## 5. 怎么验证（暂不消耗新 untouched）

1. TFL 已归档为正式负结果（见
   `experiments/methods/test_first_lift_pilot/dev6_tfl_p0_20260731/VERDICT.md`）。
2. 完成 hard-task contract-closure audit。
3. 从**已经打开且 contract-closed** 的旧开发任务中选 6–8 题开发本方法。
4. 开发门槛：
   - 相对 Main ≥2 Functional flips；
   - 0 regressions；
   - 成本 ≤ matched-compute Main 的约 **1.5×**。
5. 过门后再抽新 clean-6；clean-6 仍要求 ≥2 flips、0 regressions。

## 6. 实现状态

未实现。不创建 CLI arm，直到 audit 完成并选定开发题集。
