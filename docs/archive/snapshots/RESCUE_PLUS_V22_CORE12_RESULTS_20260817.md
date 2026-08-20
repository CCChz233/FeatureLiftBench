# Rescue+ v2.2 Core-12 真实 API 结果

> **Status: archived · Last verified: 2026-08-17**

日期：2026-08-17  
模型：`deepseek/deepseek-v4-flash`  
方法臂：`contract_closure_gate_lite_rescue_plus`  
题单：`harness/config/experiments/rescue_plus_core12_v1.txt`  
正式评测：隔离 Docker evaluator，网络关闭，测试对 Agent 不可见

## 结论

Rescue+ v2.2 本轮为 **no-go**。它修正了 v2.1 的方法逻辑，但没有改善总体效果，
不应扩到 Distill-24 或 Python-200。

- 总通过：2/12（16.7%），低于 v2.1 的 3/12（25.0%）。
- 7 道主要救援目标：1/7；新增救回 `json_logic`，但未达到预先设定的至少 2/7。
- 2 道回退保护题：1/2；`cachetools` 保持通过，`transitions` 从通过退化为失败。
- 6 次 defect repair 全部未能改变正式失败结果，可归因的 repair 救回为 0。
- 原始 token 比 v2.1 增加 19.2%，有效未缓存 prompt 加 completion 增加 22.0%。

因此，v2.2 证明了“让 Agent 在提交前写一个公开条款 witness”有可能救回真实语义题，
但也证明当前一次短 repair 不能可靠修复由 witness 或结构门禁发现的缺陷。整体上，新增
复杂度和成本大于收益。

## v2.2 改动

v2.2 只使用公开任务信息，不修改 evaluator，也不向 Agent 暴露任何测试：

- Harness 从公开 Bxxx 条款确定性选择一个高风险条款，写入 `PUBLIC_WITNESS.json`。
- 主 Agent 被要求在同一轮中实现一条对应的 direct witness；缺失 witness 只记 telemetry。
- 删除付费 evidence-completion repair，只有硬结构缺陷或选中 witness 的真实执行失败可触发 repair。
- 空提交允许一次 bootstrap repair；大量 API 缺口按 owner/module 聚类，最多修三个缺陷簇。
- paid repair 在 runner 层硬限制为 `defect_repair`，避免证据问题误触发模型调用。

## 分层结果

| 分层 | 任务 | v2.1 | v2.2 |
|---|---|---:|---:|
| Main 对 / Lite V1 错，API | responses, networkx, json_logic, httpx, platformdirs, rich | 0/6 | 1/6 |
| Main 对 / Lite V1 错，External-50 本地证据 | joserfc | 0/1 | 0/1 |
| Main、Lite V1 都错 | alembic, deepdiff, schema | 1/3 | 0/3 |
| Lite V1 优势保护 | transitions | 1/1 | 0/1 |
| 双通过哨兵 | cachetools | 1/1 | 1/1 |

v2.2 通过任务：

- `cachetools__cache_eviction_core__001`
- `json_logic__evaluator_core__hard3_001`

逐题净变化：

- 新增通过：`json_logic`。Agent 编写的 B002 dotted-variable/default direct witness 通过，
  正式 evaluator 也通过。这一收益发生在 primary 阶段，不是 repair 救回。
- 退化：`deepdiff`。v2.1 主实现本来已通过，v2.2 没有生成有效 witness，也未触发 repair。
- 退化：`transitions`。B001 witness 正确暴露 `NotImplementedError` 并触发 defect repair，
  但五步 repair 未能修好；v2.1 和 Lite V1 在该题通过。

## Public witness 与 repair

12 题中有 7 题产出了行为 case：

- pass：4 题（`cachetools`、`json_logic`、`platformdirs`、`schema`）。
- fail：2 题（`rich`、`transitions`）。
- unknown：1 题（`responses`，checker 环境依赖不可用）。
- 未生成有效 case：5 题（`alembic`、`deepdiff`、`httpx`、`joserfc`、`networkx`）。

witness 信号有一定精度，但召回和充分性都不足：4 个 witness pass 中只有 2 个正式通过；
`platformdirs` 和 `schema` 说明单个公开行为样例远不能代表全部契约闭合。

实际执行 6 次 defect repair：

- `alembic`：结构缺陷簇 repair，最终失败。
- `httpx`：空/不完整提交 bootstrap 与结构 repair，最终失败。
- `joserfc`：空提交 bootstrap repair，最终失败。
- `networkx`：多 API 缺口按簇 repair，最终失败。
- `rich`：结构缺陷和 witness failure repair，最终失败。
- `transitions`：纯语义 witness failure repair，最终失败。

v2.2 成功消除了 v2.1 的三次 evidence-completion 付费调用，但放宽 defect repair 资格后，
触发了更多真正的代码修复调用。这些调用没有带来一题正式救回。

## 成本对比

| 指标 | v2.1 | v2.2 | 变化 |
|---|---:|---:|---:|
| API calls | 522 | 619 | +18.6% |
| Assistant steps | 514 | 615 | +19.6% |
| 原始 total tokens | 18,390,561 | 21,921,513 | +19.2% |
| 有效未缓存 prompt tokens | 931,560 | 1,160,850 | +24.6% |
| Completion tokens | 509,113 | 596,311 | +17.1% |
| 有效未缓存 prompt + completion | 1,440,673 | 1,757,161 | +22.0% |
| Agent 累计时间 | 4,230.5 秒 | 4,896.8 秒 | +15.8% |

v2.2 repair 阶段单独消耗：

- 44 次 API call、53 个 assistant steps；
- 1,084,123 原始 token；
- 73,272 有效未缓存 prompt token、188,067 completion token；
- 1,266.1 秒，占 Agent 累计时间 25.9%。

虽然 repair 原始 token 只占全轮约 4.9%，但它占有效 token 约 14.9%，占累计时间四分之一，
且本轮功能收益为零。主轮本身也因更强的 witness 指令和随机轨迹比 v2.1 更贵。

## 方法判断

1. **公开 witness 方向不是完全无效**：`json_logic` 是一个真实新救回，说明提交前执行
   针对高风险公开条款的最小自测，能够改变 Agent 的实现结果。
2. **当前 repair 机制无效**：六次触发覆盖空提交、结构簇和纯语义失败三类情况，均未救回。
   问题已经不是触发资格不足，而是五步短修复无法完成大范围实现，也不能稳定做局部语义修正。
3. **单 witness 不是 closure**：`platformdirs`、`schema` 的 witness 通过但正式失败，说明它只能
   是局部证据，不能作为闭合判据。
4. **主轮方差大于小样本收益**：`deepdiff` 和 `transitions` 的回退抵消了 `json_logic` 的收益，
   Core-12 上没有形成稳定净提升。
5. **不值得继续直接堆 V3/V4**：在同一模型上继续增加 prompt、checker 或 repair 分支，最可能
   继续提高 token，而不是改善 Functional Pass。

## 决策

- 停止把 Rescue+ v2.2 扩到 Distill-24 或 Python-200。
- 保留 v2.2 代码和结果，作为“公开 witness 有单点收益、模型 repair 无净收益”的消融证据。
- 当前主方法仍应以 Frozen Lite V1 作为成本—正确率基线。
- 若继续研究，只保留 public witness 作为 primary 内的轻量提示，不再调用第二轮模型 repair；
  下一次验证仍使用预声明的高区分度切片，并要求同时满足净通过提升和 token 不回归。

## 产物

- 原始 suite：`experiments/methods/contract_closure_gate_lite_rescue_plus/rescue_plus_v22_core12_real_api_20260817_1/suite.json`
- 标准分析：`experiments/methods/contract_closure_gate_lite_rescue_plus/rescue_plus_v22_core12_real_api_20260817_1-analysis.md`
- 机器可读分析：`experiments/methods/contract_closure_gate_lite_rescue_plus/rescue_plus_v22_core12_real_api_20260817_1-analysis.json`
- v2.1/v2.2 配对比较：`experiments/methods/contract_closure_gate_lite_rescue_plus/rescue_plus_v22_core12_real_api_20260817_1-comparison.json`
