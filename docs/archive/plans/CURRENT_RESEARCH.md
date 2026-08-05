# 当前研究入口

> **Documentation status: archived · Indexed: 2026-08-04**

**更新时间：** 2026-07-31

## 一句话

从仓库来源看，Python-150 已经是相当漂亮的 benchmark 分布；论文成败不取决于
再增加仓库，而取决于这 150 道题是否覆盖足够不同的 **feature-lifting** 能力，
并且每道题的契约都能闭合。

方法侧：**TFL 正式负结果已归档**（Functional **1/6**，相对 Main **−1**）。
关键结论：**“会写测试”≠“会写与 FLB 目标语义对齐的测试”**。

**扩题计划：** [PLAN_EXTERNAL50_EXPANSION.md](../../PLAN_EXTERNAL50_EXPANSION.md)  
（总调度表 + [`external50_design_cards/`](../../../benchmark/selection/external50_design_cards)；当前阶段 = **填 design card**，非批量 materialize）。  
契约审计本波可搁置。

**现在不做：** 修 TFL；Spec-Closure；clean-6；逐题 revision + 重跑 baseline。  
**现在可做：**

1. **题层三张分布**（优先）：Lift 类型 / 行为×coupling / 难度·规模·重叠  
2. **External-50 扩题**（见上计划）  
3. Contract-closure：修订政策冻结 → **批量** revision（可并行搁置）

Lift 定义已冻结：[LIFT_TAXONOMY.md](../../reference/LIFT_TAXONOMY.md)
（**Direct / Adapted / Composite**）。  
全量标注：[`reports/lift_taxonomy/`](../../../reports/lift_taxonomy)（**150/150 labeled**，AI-assisted v1；
约 Direct 56 / Adapted 76 / Composite 18）。  
闭合审计：opened hard closed **1/28**（仅 `glom`）。

TFL 裁决：
[`dev6_tfl_p0_20260731/VERDICT.md`](../../../experiments/methods/test_first_lift_pilot/dev6_tfl_p0_20260731/VERDICT.md) ·
审计：[CONTRACT_CLOSURE_AUDIT.md](CONTRACT_CLOSURE_AUDIT.md) ·
候选方法：[METHOD_SPEC_CLOSURE.md](../methods/METHOD_SPEC_CLOSURE.md)。  
更早路径：`experiments/exec_contract_pilot/`（当前 checkout 未保留） ·
[`cgcc_lite_pilot`](../../../experiments/methods/cgcc_lite_pilot) ·
`experiments/self_contract_pilot/`（当前 checkout 未保留） ·
[METHOD_PAIRED_DIFFERENTIAL_REPAIR.md](../methods/METHOD_PAIRED_DIFFERENTIAL_REPAIR.md)。

## 当前判断

FeatureLiftBench 测量 Agent 能否在完整真实仓库和完整功能契约下，自主定位
实现、恢复 API/行为/依赖闭包，并交付独立且紧凑的功能模块。

Python-150 已满足八条核心原则：

- 150/150 完整公开契约；
- 150/150 No-Hint；
- 150/150 canonical full-repository input；
- 150/150 reference-relative compactness records；
- 450/450 Docker Oracle；
- 12/12 adversarial isolation canaries；
- source/spec/reference/evaluator/environment 已内容寻址冻结。

现有四模型结果使用 `mixed_snapshot_v1`，可以支持早期失败模式分析，但不能
回答 v3 Full-Repository / No-Hint 下的最终性能。

## 下一步

| 优先级 | 工作 | 完成标准 |
| --- | --- | --- |
| **D0** | **Lift 类型全量标注** | **150/150 已 labeled**（AI-assisted）；抽检升 `reviewed`；见 [LIFT_TAXONOMY.md](../../reference/LIFT_TAXONOMY.md) |
| **D1** | 行为语义 × coupling 表 | 从 taxonomy CSV 出正式交叉表，并与 lift_type 交叉 |
| **D2** | 难度 / 规模 / 源码重叠表 | inventory + compactness；经验难度等 v3 baseline |
| **M0** | Contract-closure 修订政策 + 批量 revision | 按问题族批量修；非整题逐个重跑 baseline |
| M1 | Spec-Closure（仅 `closed` 旧题） | ≥2 flips vs Main、0 regressions、成本 ≲ 1.5× Main |
| M2 | 过门后再抽 clean-6 | ≥2 flips、0 regressions |
| P0 | v3 baseline | 每个目标模型完整 150 题、attempt=1、freeze/image/protocol 可审计 |
| P1 | v3 结果分析 | Functional Pass@1、compactness、token、step、latency、failure taxonomy |
| P2 | 难度重校准 | 基于首轮 v3 empirical success，不把旧 hard 标签当实证结论 |

已归档负结果：TFL；PDR held-out clean-6；FCEC admission 0/6。  
**暂停方法实验；不加仓。** 合规表述：历史 150/150 仅表示通过旧自动门禁，**不**表示 contract-closed。  
审计主表：[`reports/contract_closure_audit/OPENED_HARD_SUMMARY.md`](../../../reports/contract_closure_audit/OPENED_HARD_SUMMARY.md)。

## PDR held-out clean-6（2026-07-30—31）

| Arm | Public | Hidden | Functional |
| --- | ---: | ---: | ---: |
| Main | 4/6 | 2/6 | **2/6** |
| clean3 | 4/6 | 2/6 | **2/6** |
| PDR + abstention | 4/6 | 2/6 | **2/6** |

硬结论：

- 预注册门槛要求至少 2 个 PDR Functional flips；实际 **0**。
- PDR gate 接受 2 个修复、4 个 abstention；一个修在原本已通过的
  Pyramid，另一个 setuptools-scm 仍 p✗h✗。
- PDR 额外 341 API calls / 16.99M tokens / 3,071 秒 agent time；
  clean3+PDR 总 token 是 Main 的约 2.16×。
- clean3 六题上游 collector 全失败，合约不 substantive；这是当前最先
  要修的实现问题。
- clean 后审计发现 Pytest、Parsel、setuptools-scm 存在 TASK/evaluator
  精确要求不闭合，不能反向塞进方法 prompt。

结果、哈希与尸检：
[PDR clean-6 RESULTS](../../../experiments/methods/pdr_clean6_20260730/RESULTS_20260731.md) ·
[selection audit](../../../experiments/methods/pdr_clean6_20260730/SELECTION_AUDIT.md) ·
[submission freeze](../../../experiments/methods/pdr_clean6_20260730/SUBMISSION_FREEZE.json)。

## Focus 方法快照（alembic + click，2026-07-30）

| Arm | alembic | click | 备注 |
| --- | --- | --- | --- |
| Main `compare-20260728-155516/main` | p✗ h✗ | p✗ h✗ | 基线 |
| **exec clean3** | **p✓ h✗** | **p✓ h✗** | 当前最佳干净模板 |
| exec clean4 | p✗ h✗ | p✓ h✗ | B006 → `"base"` 过度泛化 |
| self_contract `…-140322` | p✗ h✗ | p✗ h✗ | 闸门绿；base 泛化 + 漏 invoke |
| CGCC-lite one-shot `…cgcc-lite…` | p✓ h✗ | p✓ h✗ | 修复 symbol/invoke 闭包，Functional 仍 0/2 |
| CGCC-ROC one-shot `…cgcc-roc…` | p✗ h✓ | p✓ h✗ | 表示闭包命中，但从零重写引入 traversal 回退 |
| CGCC-RMC one-shot `…cgcc-rmc…` | p✓ h✗ | — | required-method 修复；从零重写又丢双 branch 过滤 |
| **CGCC monotone delta repair** | **p✓ h✓ (3/3)** | p✓ h✗（沿用 ROC） | 开发集 1/2 Functional；保留旧 candidate，只修新增冻结合约 |
| free DPR | p✗ h✗ | — | upstream 差异有效，但自由探针与弱保持门导致 public 回归 |
| **paired DPR / PDR** | **p✓ h✓ (1 seed)** | p✓ h✗ | 开发集 1/2 Functional；双 oracle + 整域 control；Click 暴露 TASK admission 边界 |

详表历史路径：`experiments/exec_contract_pilot/CLEAN_FOCUS.md`（当前 checkout 未保留） ·
[CGCC RESULTS](../../../experiments/methods/cgcc_lite_pilot/RESULTS_20260730.md) ·
[PDR RESULTS](../../../experiments/methods/dpr_pilot/RESULTS_20260730.md) ·
`experiments/self_contract_pilot/FOCUS_RESULTS.md`（当前 checkout 未保留）
导出：`exports/flb-useful-focus-expts-20260730-144258.tar.gz`

## Exec-Contract 试点快照

| 项 | 状态 |
| --- | --- |
| 模型 | `deepseek/deepseek-v4-flash` |
| 12 题对照 Main | `compare-20260728-155516/main` → **4/12** |
| Focus 最佳 | `exec-contract-clean3-20260729-214504` |
| 故事 | [METHOD_EXEC_CONTRACT.md](../methods/METHOD_EXEC_CONTRACT.md) |
| 操作 | `experiments/exec_contract_pilot/README.md`（当前 checkout 未保留） |

## Self-Authored Contract 快照

| 项 | 状态 |
| --- | --- |
| 臂 | `--arm self_contract` |
| Focus | **0/2** Functional；历史路径 `experiments/self_contract_pilot/FOCUS_RESULTS.md`（当前 checkout 未保留） |
| 故事 | [METHOD_SELF_CONTRACT.md](../methods/METHOD_SELF_CONTRACT.md) |

## TD-Cognition 归档快照（2026-07-28，负对照）

| 项 | 状态 |
| --- | --- |
| 干净 TD | `td-cognition-clean-20260728-220500` → **4/12**，相对 Main **零翻盘** |
| 结论 | 自编探针易锁死错误认知；不扩。尸检动机写入 Exec-Contract 文档 §2 |
| 故事 | [METHOD_TEST_DRIVEN_COGNITION.md](../methods/METHOD_TEST_DRIVEN_COGNITION.md) |

正式默认：

```text
OpenHands
+ specified model
+ Full-Repository / No-Hint Main
+ agent Docker
+ evaluator Docker
+ Python-150
+ one attempt per task
+ evaluator Functional Pass@1
```

操作见
[SERVER_RUNBOOK_PYTHON150.md](../runbooks/SERVER_RUNBOOK_PYTHON150.md)。

## 论文主线

1. **Benchmark contribution**：把 feature extraction 定义为完整仓库、
   完整公开契约、No-Hint、submission 后私有评测的独立任务。
2. **Dataset contribution**：150 External Main tasks、126 external
   repositories、132 immutable snapshots，以及独立 Curated-7 split。
3. **Evaluation contribution**：Functional Pass@1 与 reference-relative
   compactness 分离，并记录 isolation、copy/dependency footprint。
4. **Empirical contribution**：比较模型在正确性、紧凑性、成本和失败机制上
   的差异。
5. **Method contribution（后置）**：验证面向 API/behavior completion 的
   closure recovery 是否改善 Main，而不是只提升文件定位。

## 现有证据的边界

历史 `mixed_snapshot_v1` 四模型 evaluator Functional Pass@1 为
87/150、56/150、49/150、37/150。它们提示：

- 强模型和弱模型存在明显区分；
- 常见失败发生在 API/行为完成、依赖/资源遗漏和 copy-heavy；
- 单纯提供定位或 RSG start-here 尚未显示稳定 hard-task 增益；
- public-feedback 与 test-blind 条件不能混报。

这些是方向性证据。完整仓库会增加 localization 和上下文负担，No-Hint 会
去掉旧 entrypoints，因此 v3 通过率、token 和失败分布必须重新测量。

## 方法状态

| 路线 | 状态 |
| --- | --- |
| Benchmark v3 工程 | 完成 |
| Contract/API closure recovery | PDR 停止扩；FCEC 修通 dependency doctor 但 dev-6 admission 0/6，暂不跑模型。瓶颈从“能否执行”推进到“能否重建 stateful transition / adapter mapping” |
| Repository Fact Graph 基础设施 | 保留 |
| RSG start-here/support retrieval | 降级为历史基线 |
| ECSM / 强制 task-closure 状态机 | 废弃 |
| 独立人工审核门禁 | 取消 |

废弃路线的规划文档和取消的审核包已经从当前文档树移除；原始实验结果仍保留
在 `experiments/` / `reports/`，用于复查而非指导当前路线。

## 今天只读

- [设计原则](../../BENCHMARK_DESIGN_PRINCIPLES.md)
- [当前状态](../../STATUS.md)
- [方法故事：Exec-Contract](../methods/METHOD_EXEC_CONTRACT.md)
- [方法故事：CGCC-lite / ROC / RMC](../methods/METHOD_CGCC_LITE.md)
- [方法故事：Paired Differential Repair](../methods/METHOD_PAIRED_DIFFERENTIAL_REPAIR.md)
- [方法故事：Fail-Closed Execution Contract](../methods/METHOD_FAIL_CLOSED_EXEC_CONTRACT.md)
- [方法故事：Self-Authored Contract](../methods/METHOD_SELF_CONTRACT.md)
- Exec-Contract focus 结果历史路径：`experiments/exec_contract_pilot/CLEAN_FOCUS.md`（当前 checkout 未保留）
- [CGCC focus 开发结果](../../../experiments/methods/cgcc_lite_pilot/RESULTS_20260730.md)
- [PDR focus 开发结果](../../../experiments/methods/dpr_pilot/RESULTS_20260730.md)
- Self-Contract focus 结果历史路径：`experiments/self_contract_pilot/FOCUS_RESULTS.md`（当前 checkout 未保留）
- [TD 负对照故事](../methods/METHOD_TEST_DRIVEN_COGNITION.md)
- [实验规范](../../EVALUATION.md)
- [当前结果](../../STATUS.md)
- [服务器运行手册](../runbooks/SERVER_RUNBOOK_PYTHON150.md)
- [报告索引](../../../reports/README.md)
