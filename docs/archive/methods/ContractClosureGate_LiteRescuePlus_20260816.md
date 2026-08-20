# Contract Closure Gate Lite Rescue+（2026-08-16）

> **Status: archived · Last verified: 2026-08-18**
> Rescue+ 开发臂已停止。当前正式 cost arm **V1 = Main + 2M**，见
> [../../METHOD_V1.md](../../METHOD_V1.md)；不要把 Rescue+ 或 Frozen Lite V1 叫做当前 V1。

## 目的

`contract_closure_gate_lite_rescue_plus` 是独立开发实验臂。它不修改或重命名
`contract_closure_gate_lite_rescue`、`contract_closure_gate_v3` 或冻结的 Lite V1。
本臂检验一个单一假设：在保留 Rescue 选择性结构修复的同时，一条低成本、由
Agent 根据公开 Bxxx 条款和可见上游源码编写的行为 smoke case，能否发现
structure-only 门禁遗漏的语义缺陷。

## 固定协议

- Agent 主轮预算：2,000,000 token / 45 OpenHands steps。
- 约 step 12 前运行 structure-only checker；约 step 35 后停止广泛探索。
- 编写 1 条组合式行为 case，仅在必要时增加第 2 条，禁止超过 2 条。
- 行为 case 共享 60 秒执行预算；完整 Bxxx 覆盖不是门槛。
- checker 模式：`lite_plus`；命令：`./flb-contract-check --lite-plus --summary`。
- checker 版本：`contract_closure_checker.v7`；公开契约生成器仍为 v4。
- repair：最多一次，200,000 token / 5 steps。
- repair 信号：小型结构缺口、可执行行为断言失败、或没有有效可执行 smoke case。
- 不 repair：检查环境缺依赖、外部服务不稳定、无法安全检查等 `unknown`。
- 正式 evaluator 始终执行，门禁结果不替代 Functional Pass。

## 上下文与输出控制

专用 profile 使用 65,536 token context、16,384 token safety reserve，因此
OpenHands condenser 在 49,152 token 触发并压缩至约 24,576 token。单条工具消息
上限由 16,000 字符降为 8,000 字符。该设置原本用于消除 2026-08-14 三题 smoke
中观察到的上下文阈值违规；2026-08-16 的付费 pilot 表明代理侧开销仍会让
11/12 个任务越过该阈值，因此后续仍需单独校准主轮 condenser。

## 公平性边界

case 只能引用 `public_spec:Bxxx` 或 Agent 本来可见的上游源码位置；不得读取或引用
public/hidden evaluator、reference solution、既往 evaluator 失败内容。2026-08-14
三题结果只能用于确认“结构门禁遗漏行为语义”这一通用故障类别，不能把具体 hidden
断言编码进 prompt、checker 或 case 模板。

本臂在方法规则冻结后才能进入 External-50。开发 pilot 应使用 8–12 个预声明的
Python-150 任务，并与 Main 和 structure-only Rescue 在相同模型、endpoint、镜像及
primary budget 下比较。

首轮 12 题开发切片已预声明在
`harness/config/experiments/contract_closure_gate_lite_rescue_plus_pilot12.txt`。
该列表不包含 2026-08-14 三题 smoke 的 `alembic`、`cattrs`、`responses`。

## Plan-only 命令

```bash
./harness/scripts/run_python200_paper.sh \
  openhands_deepseek_v4_flash_contract_closure_gate_lite_rescue_plus \
  lite-rescue-plus-plan \
  --workers 2 \
  --agent-image <agent-image-id> \
  --eval-image <eval-image-id>
```

不加 `--execute` 时不会产生模型调用。

## 2026-08-16 付费 pilot 与 repair v2

首轮 12 题真实 DeepSeek API 结果为 8/12。初始 Gate 闭合的 5 题全部通过正式
evaluator，但 5 次有资格的 repair 没有一次把 Gate 修到闭合。轨迹审计发现，
旧 repair 被 OpenHands 再次包装成完整主任务，因此短预算主要消耗在列目录、
重读 TASK/metadata/契约和浏览上游仓库，而不是编辑。

`contract_closure_gate_lite_rescue_plus.v2.1` 保留 v2 主流程，并修复三项信号问题：

- differential 必须严格返回 `{result, exception, state_after}`，任意自定义外层结构不再被归一化为空观察后假通过；
- 纯缺少或无效 smoke case 进入 `evidence_completion`，submission 冻结，任何 submission 修改都会被丢弃；真实结构或行为缺陷进入 `defect_repair`，两类轮次分开记录；
- 公开条款明确顺序、状态、异常、嵌套、重复调用或 reset 语义时使用 direct assertion，只有条款未规定的细节才允许稳定上游 differential。

v2.1 的 defect repair 继续使用独立的定点提示：

- 直接内嵌公开失败报告、PUBLIC_CONTRACT.json 和 behavior-case 协议；
- 不再叠加主阶段的实现、探索和 finish-state prompt；
- 缺少 smoke case 时，第一项工具动作必须创建 case；
- 首次编辑后立即运行 `--lite-plus --summary`，最多再做一次局部修正；
- 禁止用 `ls`、`find`、`tree` 重新盘点工作区，禁止整模块/整测试集浏览和安装依赖；
- evaluator 仍不可见，正式评分路径不变。

v2 只改变 Rescue+ repair 阶段，不改变 primary、Main、冻结 Lite V1 或 evaluator。

## 2026-08-17 v2.2 与 Core-12 决策

v2.2 将 Rescue+ 收缩为一个更严格的实验：Harness 只从公开 Bxxx 中确定性选择一条
高风险 witness，主 Agent 只需编写一条 direct case；缺少证据只记 telemetry，不再
触发付费 repair。repair 仅处理硬结构缺陷或已执行 witness 的真实失败；空提交可做一次
bootstrap，多 API 缺口按最多三个 owner/module 簇处理。

同一 DeepSeek 模型、同一 Core-12 和同一 evaluator 条件下，v2.2 得到 2/12，低于
v2.1 的 3/12。它在主要救援目标上新增救回 `json_logic`，但 `deepdiff`、`transitions`
回退；六次 defect repair 没有救回任何任务。原始 token 比 v2.1 增加 19.2%，有效未
缓存 prompt 加 completion 增加 22.0%。

结论是：公开 witness 在 primary 中有单点价值，但当前第二轮模型 repair 不具备成本收益。
Rescue+ v2.2 不进入 Distill-24 或 Python-200。完整结果见
[../snapshots/RESCUE_PLUS_V22_CORE12_RESULTS_20260817.md](../snapshots/RESCUE_PLUS_V22_CORE12_RESULTS_20260817.md)。
