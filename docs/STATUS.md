# FeatureLiftBench 当前状态

**最后更新：** 2026-07-24

手写状态摘要。Gate 详表：[research_analysis/V11_IMPLEMENTATION_STATUS.md](research_analysis/V11_IMPLEMENTATION_STATUS.md)。

**整体思路：** [BENCHMARK_DESIGN.md](BENCHMARK_DESIGN.md)  
**规格宪法：** [TASK_DESIGN_RULES.md](TASK_DESIGN_RULES.md)（Python-150：**150/150 compliant**，0 legacy）  
**迁移手册：** [CONSTITUTION_MIGRATION.md](CONSTITUTION_MIGRATION.md)  
**研究入口：** [CURRENT_RESEARCH.md](CURRENT_RESEARCH.md)  
**实验臂：** [EXPERIMENT_ARMS.md](EXPERIMENT_ARMS.md)  
**怎么跑：** [RUN.md](../RUN.md) · **实验账本：** [EXPERIMENTS.md](EXPERIMENTS.md) · **解读：** [FINDINGS.md](FINDINGS.md)

**最新服务器默认：** [SERVER_RUNBOOK_COMPLIANT150.md](SERVER_RUNBOOK_COMPLIANT150.md) —
OpenHands + 指定模型 + test-blind Main + Agent/Eval Docker + 150
engineering-compliant tasks + 每题一次 Pass@1。当前新协议内容审计：
engineering-ready 150/150、完整非模板化契约 150/150、experiment-ready
150/150；含可发现上游测试 48/150 是信息项，不是硬门禁。独立人工审核
0/150，因此 paper-ready 仍为 0/150。

## 当前优先级（摘要）

1. **Benchmark 基础主线：** **150/150 experiment-ready 已完成并冻结**；可以启动 compliant Python-150 模型实验  
2. **实验主线：** OpenHands + 指定模型 + test-blind Main + 双 Docker + 150 题 Pass@1  
3. **方法研究主线（在合规题上）：** Contract/API closure recovery（Checklist / Probe / Reference Support Set）  
4. Repository Fact Graph：基建保留；当前 RSG start-here：**retrieval 基线**  
5. 扩题 / 调 start-here：在独立审核与 compliant 校准完成前低优先级  

排期决定（2026-07-24）：150 题契约/hidden 对齐、Oracle 重验和 spec
freeze 已完成。独立人工 paper-gold 审核按计划延后到 150 题实验之后；
它只阻塞 paper-ready 发布，不阻塞当前模型实验。

150 题工程合规结果：
[reports/audits/new_protocol_readiness.md](../reports/audits/new_protocol_readiness.md)
（逐题验证 **150/150**；当前冻结 Oracle 证据 **450/450**）。

权威叙事：[BENCHMARK_DESIGN.md](BENCHMARK_DESIGN.md)

## Benchmark 规模

| Split | 位置 | 数量 | 说明 |
| --- | --- | ---: | --- |
| Python main | `benchmark/tasks/` | **150 hard** | core-100 + hard50；**150 compliant / 0 legacy** |
| Python smoke | `benchmark/sanity/` | **3** | harness smoke |
| Go calibration | `benchmark/go/` | seed / pilot | 非 paper-ready main |

- 唯一 source 数（Python main）：**121**
- Inventory：[python/02_python_repo_task_inventory.md](python/02_python_repo_task_inventory.md)

## Oracle / Evaluator

| 项 | 状态 |
| --- | --- |
| 当前 Oracle freeze ID | `7c042d5528b7d0fd` |
| 当前 spec freeze ID | `f7c616edb47ea533` |
| Canary | **15/15** runs（5 × 3） |
| Full revalidation | **450/450** runs（150 × 3） |
| Stable pass | **150/150** |
| Active quarantine | **0** |

当前 benchmark 已可在服务器启动正式 compliant Python-150 实验。历史
legacy 模型结果仍不得与新 freeze 下的结果混报。

## Agent 实验（摘要）

| 范围 | 状态 |
| --- | --- |
| 四模型 core-100 | ✅ 已冻结 |
| Flash Python-150 | ✅ 91/150 |
| Flash compliant hard-50 | ✅ 历史 Public-feedback **11/50**；test-blind Main **4/50** |
| Qwen 27B / 35B Python-150 | ⚠️ candidate；待冻结 |
| Qwen-Coder hard50 | ❌ 待跑 |
| ECSM Pilot | ⛔ 已废弃 |
| RSG v2 OpenHands | ✅ 基建可跑；easy token 不稳；**hard A/B 无通过率收益** → 降级 |
| 规格宪法门禁 / test-blind Main | ✅ 校验器 + 生成器已落地；Python-150 全量 compliant |

RSG hard 报告：`reports/repo_graph_phase2/rsg_hard_ab_20260724.md`  
失败归因：`reports/failure_attribution_20260720/`

## 规格宪法与迁移（2026-07-24）

| 项 | 状态 |
| --- | --- |
| 工程：schema / render / validate / CLI | ✅ |
| Compliant 批次 | **150**（完整 Python main；AI 辅助工程审核） |
| Legacy 主榜 | **0** |
| Hard-50 Oracle 复验 | **50/50** functional gate；48 local + 2 Docker |
| 第一批 Core-50 Oracle 复验 | **50/50** Docker functional gate |
| 最终 Core-50 Oracle 复验 | **50/50** Docker functional gate |
| 全量 compliant main validation / Oracle | **150/150** / **450/450（150 × 3）** |
| 契约内容门禁 | **150/150 experiment-ready**；0 generic；0 unresolved callable |
| Harness / 生命周期回归 | **318 tests pass**（7 skipped）；167 packages，0 task/global issue |
| Hard-50 compliant rebaseline | ✅ 旧标签 Main=现 Public-feedback **11/50**；旧标签 No-public=现 test-blind Main **4/50**；两臂各 50/50 完整 |
| Python-150 独立人工审核 | **0/150；延后，仅阻塞 paper-ready** |
| Spec freeze | `f7c616edb47ea533`（Oracle freeze `7c042d5528b7d0fd`） |
| Hard-50 paired report | 本地历史结果（不进 Git）：`experiments/ablation/hard50-compliant-deepseek-v4-flash-20260724/paired-analysis.md` |
| 冻结合规报表 | [reports/audits/spec_compliance_frozen_20260724.csv](../reports/audits/spec_compliance_frozen_20260724.csv) |
| 新协议内容审计 | [reports/audits/new_protocol_readiness.md](../reports/audits/new_protocol_readiness.md) |
| 操作手册 | [CONSTITUTION_MIGRATION.md](CONSTITUTION_MIGRATION.md) |

## v1.1 论文门禁（摘要）

| 区域 | 状态 |
| --- | --- |
| Behavior contracts 映射 | 150/150 mapped；**独立人工 gold：0/150** |
| Diagnostic-40 closure | file scope 40/40；**独立裁决：0/40** |
| Paper release gates | **8/13** — `paper_release_ready: false` |

宪法要求主榜逐题审核与双向 behavior/API 覆盖。Python-150 已完成 AI 辅助工程审核与可执行门禁；独立人工 paper-gold 审核仍为 0/150。

## 历史里程碑

| 阶段 | 内容 | 文档 |
| --- | --- | --- |
| 2026-07 | 规格宪法 Adopted；RSG 提分主线降级 | TASK_DESIGN_RULES · BENCHMARK_DESIGN |
| 2026-07 | RSG v2 可选工具实现 + 真 API 烟测/ hard A/B | research_analysis/REPOSITORY_SEMANTIC_GRAPH_* |
| 更早 | ECSM 废弃；Oracle freeze；550-run 归因 | FINDINGS · failure_attribution |
