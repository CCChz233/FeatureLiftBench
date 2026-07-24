# 当前研究入口

更新时间：2026-07-24

这是论文创新、当前实验结果和下一轮实验的**唯一入口**。

## 一句话结论

FeatureLiftBench 上，在 **entrypoint-conditioned OpenHands** 基线下，Agent 通常能找到实现，但卡在入口之后的 **API/行为契约完成与紧凑解耦**。规格、测试与 Agent 可见信息现已在 150/150 任务上完成工程统一；下一步优先运行冻结后的 compliant Python-150 模型实验，而不是扩题或调 start-here 检索。独立人工审核按计划在完整模型实验之后进行。

论文目标仍是 **Benchmark + 方法**：

- **Benchmark 基础主线：** 冻结规格、任务质量与评测口径。  
- **方法研究主线：** 在合规任务上验证 Contract/API closure recovery；具体方案由失败分析与先导实验决定。

**先读：** [BENCHMARK_DESIGN.md](BENCHMARK_DESIGN.md) → [TASK_DESIGN_RULES.md](TASK_DESIGN_RULES.md) → [CONSTITUTION_MIGRATION.md](CONSTITUTION_MIGRATION.md) → [EXPERIMENT_ARMS.md](EXPERIMENT_ARMS.md)

**服务器跑最新 engineering-compliant Python-150：**
[SERVER_RUNBOOK_COMPLIANT150.md](SERVER_RUNBOOK_COMPLIANT150.md)。正式默认已改为
test-blind Main；当前 spec freeze 已通过实验门禁，独立人工审核留到
150 题实验之后。

## 当前最高优先级

> 主榜已达到 **150/150 experiment-ready、0 legacy**。契约与 hidden 已对齐，
> Oracle freeze `7c042d5528b7d0fd` 完成 450/450 Docker 复验，spec freeze
> `f7c616edb47ea533` 已生成。现在可运行 compliant Python-150 模型实验；
> 独立人工审核按计划在实验后进行，只影响 paper-ready 发布。

| # | 项 | 状态 |
| --- | --- | --- |
| 1 | Validate + 生成器 + CLI | ✅ |
| 2 | 试点 isort / transitions / scrapy + hidden 重判 | ✅ |
| 3 | Hard-50 宪法迁移 + API surface + Oracle 复验 | ✅ 50/50 |
| 4 | Python-150 分批规格迁移 | ✅ **150/150 已验收** |
| 5 | Hard-50 compliant 可见性配对重跑 | ✅ 历史 Public-feedback **11/50**；test-blind Main **4/50** |
| 6 | Compliant Python-150 test-blind Main 模型实验 | ⏳ **现在可启动** |
| 7 | Python-150 独立人工 paper-gold 审核 | ⏸ **实验后；0/150** |
| 8 | Contract Checklist / Probe / Reference Support Set | ⏳ |

150 题工程合规结果：
[new_protocol_readiness.md](../reports/audits/new_protocol_readiness.md)
（逐题协议就绪度）与
[spec_compliance_frozen_20260724.csv](../reports/audits/spec_compliance_frozen_20260724.csv)
（冻结合规清单）。

## 方法线怎么放

| 路线 | 状态 |
| --- | --- |
| Benchmark 规格宪法与任务迁移 | ✅ **150/150 engineering-compliant** |
| Contract/API closure recovery | **当前方法候选**（在 compliant 子集上验证） |
| Repository Fact Graph | **基础设施保留** |
| 当前 RSG start-here / support retrieval | **降级为实验基线** |
| ECSM / 强制 task-closure | **废弃** |

- **不做** ECSM / 强制状态机 / claim·stopping / 强制 `task-closure`。  
- **评测** Pass@1 = evaluator `functional_gate`；与 Agent `run_status` 分离。  
- **legacy 与 compliant 实验分报**（见 [CONSTITUTION_MIGRATION.md](CONSTITUTION_MIGRATION.md)）。

## 当前证据（带边界）

- Python-150：工程合规 **150/150**；完整非模板化契约
  **150/150**；experiment-ready **150/150**；逐题 validation **150/150**。  
- Oracle freeze `7c042d5528b7d0fd`：canary **15/15**、full
  **450/450**、150 stable、0 quarantine；spec freeze
  `f7c616edb47ea533`。  
- `repo/` 含可发现上游测试 **48/150**，这是 Agent 可用证据统计而非
  硬门禁，因为任务允许 Agent 自行构造测试。独立人工审核 **0/150**，
  所以 benchmark 可做正式实验，但仍不是 paper-ready release。  
- 历史 550 OpenHands runs 仍按 legacy 规格口径；不得与 compliant rerun 混报。  
- Compliant hard-50 的旧命名结果：可见 evaluator tests 的历史 `Main`
  （现称 Public-feedback）**11/50（22%）**；不可见 evaluator tests 的历史
  `No-public`（现称 test-blind Main）**4/50（8%）**。配对净差 +7 题，
  0 个 test-blind-Main-only pass。  
- 定位很少成最早失败；public→hidden 条件失败约 43%（非严格因果）。  
- RSG hard A/B：start-here 无 hidden 通过率收益。  
- 规格缺陷例：isort 双轨 API（试点已 compliant 修复）。  
- 报告：`experiments/ablation/hard50-compliant-deepseek-v4-flash-20260724/paired-analysis.md` · `reports/failure_attribution_20260720/` · `reports/repo_graph_phase2/rsg_hard_ab_20260724.md`

## 今天只读

| 目的 | 文件 |
| --- | --- |
| **整体思路** | [BENCHMARK_DESIGN.md](BENCHMARK_DESIGN.md) |
| **规格宪法** | [TASK_DESIGN_RULES.md](TASK_DESIGN_RULES.md) |
| **迁移怎么操作** | [CONSTITUTION_MIGRATION.md](CONSTITUTION_MIGRATION.md) |
| **实验臂** | [EXPERIMENT_ARMS.md](EXPERIMENT_ARMS.md) |
| 状态 / 实验 | [STATUS.md](STATUS.md) · [EXPERIMENTS.md](EXPERIMENTS.md) |
| 怎么跑 | [../RUN.md](../RUN.md) |

## 已废弃 / 降级

| 项 | 说明 |
| --- | --- |
| ECSM | superseded |
| 当前 RSG start-here 提分主线 | retrieval baseline |
| 「最小闭包 / Oracle Closure」严格宣称 | 紧凑代理 + Reference Support Set |
| 理想 Agent 工作流入库规范 | 禁止 |

## 目录职责

| 目录 | 放什么 |
| --- | --- |
| `docs/` | 规范与入口；宪法 + 迁移手册优先 |
| `harness/featureliftbench/` | 评测、校验、迁移 |
| `experiments/` | 原始运行（标注 legacy/compliant） |
| `reports/audits/` | 已跟踪的冻结合规与协议就绪度摘要 |
