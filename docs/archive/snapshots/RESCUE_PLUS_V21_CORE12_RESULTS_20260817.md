# Rescue+ v2.1 Core-12 真实 API 结果

> **Status: archived · Last verified: 2026-08-17**

日期：2026-08-17  
模型：`deepseek/deepseek-v4-flash`  
方法臂：`contract_closure_gate_lite_rescue_plus`  
题单：`harness/config/experiments/rescue_plus_core12_v1.txt`  
正式评测：隔离 Docker evaluator，网络关闭，测试对 Agent 不可见

## 结论

Rescue+ v2.1 本轮为 **no-go**，不应直接扩到 Distill-24 或 Python-200。

- 总通过：3/12（25.0%）；失败 8，空提交 1。
- 7 道主要救援目标：0/7。
- 3 道历史 Main/Lite 均失败题：1/3；仅 `deepdiff` 通过。
- 2 道回退保护题：2/2；`transitions`、`cachetools` 均通过。
- 真正执行的 defect repair：1 次，最终仍失败；可归因的功能救回为 0。

v2.1 成功修复了实验口径：畸形 differential 不再假通过，纯证据补全不能改 submission，也不会被记成功能救回。但它没有解决真正的性能瓶颈：语义缺陷召回不足、主轮经常耗尽 step，以及修复资格阈值挡住大缺口提交。

## 分层结果

| 分层 | 任务 | Rescue+ v2.1 |
|---|---|---:|
| Main 对 / Lite V1 错，API | responses, networkx, json_logic, httpx, platformdirs, rich | 0/6 |
| Main 对 / Lite V1 错，External-50 本地证据 | joserfc | 0/1 |
| Main、Lite V1 都错 | alembic, deepdiff, schema | 1/3 |
| Lite V1 优势保护 | transitions | 1/1 |
| 双通过哨兵 | cachetools | 1/1 |

通过任务：

- `cachetools__cache_eviction_core__001`
- `deepdiff__deep_compare_core__001`
- `transitions__state_machine_core__hard3_001`

## Repair 行为

- evidence completion 实际执行 3 次：`alembic`、`deepdiff`、`joserfc`。submission 全程冻结。
- defect repair 实际执行 1 次：`schema`。修改 submission 后仍未通过 evaluator。
- `httpx`、`networkx`、`rich` 被识别为 defect repair，但 actionable API 缺口超过当前上限 3，故 `eligible=false`。
- `json_logic`、`platformdirs`、`responses` 在门禁无 repair 信号的情况下正式失败，是明确的语义假阴性。

`deepdiff` 的通过不能算 repair 救回：其 repair 只是冻结 submission 的证据补全，正式通过来自主轮实现。

## 成本

| 指标 | 数值 |
|---|---:|
| API calls | 522 |
| 原始 total tokens | 18,390,561 |
| 有效未缓存 prompt tokens | 931,560 |
| completion tokens | 509,113 |
| prompt cache hit rate | 94.79% |
| Agent 主轮累计时间 | 3,174.9 秒 |
| Repair 累计时间 | 1,055.5 秒 |
| Agent 总累计时间 | 4,230.5 秒 |

Repair 占原始 token 约 4.7%，但占“有效未缓存 prompt + completion”约 15.6%，占 Agent 累计时间约 25.0%。纯证据补全的成本与功能收益不匹配。

## 失败机制

1. **主轮不收敛**：6 题被归类为 `agent_step_limited`，行为 case 常在主实现耗尽预算后缺失。
2. **语义 witness 太弱**：三个正式失败任务在门禁中无 repair 信号。
3. **修复资格过严**：缺口超过 3 个时完全放弃 defect repair，空提交和多 API 缺失恰好被挡在外面。
4. **证据补全不产生功能价值**：三次 evidence completion 只改善实验记录，其中两题仍失败。
5. **repair 能力不足**：唯一实际 defect repair 没能修好 `schema`。

## 下一步（只做两个改动）

1. **取消模型 evidence-completion repair**：缺 case 只记 telemetry，不再调用付费模型。这样直接消除本轮 3 次低价值 repair。
2. **把唯一 repair 预算留给可执行的语义 defect**：由 harness 从公开条款生成一个最小 direct witness，只有 witness 在 submission 上失败时才允许 repair；结构缺口上限改为“按簇修复”，空提交单独允许一次恢复，不再简单以缺口数大于 3 拒绝。

完成后只跑同一 Core-12；准入条件为：7 道救援目标至少救回 2 道、两个保护题全保住、且 repair 的有效 token 增量不超过 Lite V1 主轮的 10%。未达到则停止 Rescue+ 路线，保留 Frozen Lite V1 作为成本—正确率折中基线。

## 产物

- 原始 suite：`experiments/methods/contract_closure_gate_lite_rescue_plus/rescue_plus_v21_core12_real_api_20260817_1/suite.json`
- 标准分析：`experiments/methods/contract_closure_gate_lite_rescue_plus/rescue_plus_v21_core12_real_api_20260817_1-analysis.md`
- 机器可读分析：`experiments/methods/contract_closure_gate_lite_rescue_plus/rescue_plus_v21_core12_real_api_20260817_1-analysis.json`
