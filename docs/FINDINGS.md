# 实验结果能说明什么（Findings）

基于已冻结 OpenHands 实验（详见 [EXPERIMENTS.md](EXPERIMENTS.md) 与 [TRAJECTORY_FINDINGS.md](research_analysis/TRAJECTORY_FINDINGS.md)）。

**设计前提（2026-07-24）：** 见 [BENCHMARK_DESIGN.md](BENCHMARK_DESIGN.md)。决策权在大模型；Benchmark 不规定工作流。ECSM 已废弃。RSG 文件导航臂**降级**（非当前提分主线）。规格统一优先于扩方法。

## 完成度如何

| 口径 | 结果 |
| --- | --- |
| 最强 Flash · core-100 | **83/100（83%）**，avg score **0.52** |
| 最强 Flash · 全 150 | **91/150（60.7%）**，avg **0.36** |
| Flash · hard50（legacy 冻结口径） | **8/50（16%）** |
| Flash · compliant hard50 Public-feedback（旧标签 Main） | **11/50（22%）** |
| Flash · compliant hard50 test-blind Main（旧标签 No-public） | **4/50（8%）** |
| 开源最好 Qwen3.6-27B · core-100 | **54/100** |
| Qwen3-Coder-30B · core-100 | **24/100** |

强模型在常规 hard 题上可用；一到 hard3 / 强缠绕切片就断崖下跌。

2026-07-24 的 compliant hard-50 配对重跑中，Public-feedback 比
test-blind Main 多通过 7 题（+14 percentage points；11/50 vs 4/50），
4 个 test-blind Main pass 全部也是 Public-feedback pass，0 个
test-blind-Main-only pass。精确配对 McNemar
`p=0.015625`，支持「可运行 public feedback 对本设置有帮助」。两臂均
无缺提交、限流或 Docker/evaluator 基建失败。

与 legacy hard-50 的 8/50 相比，compliant Public-feedback 为
11/50（+6 points）；逐题为 4 个 compliant-only、1 个 legacy-only，配对
`p=0.375`。由于规格、测试与单次随机轨迹均有变化，这只能视为方向性改善，
不能宣称迁移必然提分。
配对报告：
`experiments/ablation/hard50-compliant-deepseek-v4-flash-20260724/paired-analysis.md`。

该批运行发生在实验臂改名前：旧 `Main` 挂载 evaluator public tests，旧
`No-public` 不挂载。当前默认 `Main` 是后一种 test-blind 条件。

2026-07-20 新导入但尚未冻结的同任务集 candidate 结果为：Qwen3.6-27B **58/150（38.7%）**、Qwen3.6-35B **52/150（34.7%）**。两者 hard50 分别只有 4/50 和 3/50，与上述难度断崖一致；论文正式表在 re-freeze 前仍不使用这两个结果。

## RSG 说明什么（含 2026-07-24）

- 旧强制 `task-closure` / `submission-check` Pilot：只能说明强制采用门脆，**不能**因果断言图工具增益。  
- RSG v2 可选工具 + hard3×P0/tuned A/B（transitions / isort / scrapy）：**6/6 hidden fail**，tuned 无通过率提升且 token 更高。失败模式为契约/行为（缺导出、嵌套态、KeyError），非「找不到文件」。  
- 结论：把 RSG 当 **start-here 导航** 对主损失不对齐 → **降级**；若再做须服务 `required_api`/behavior 清单，而非扩搜文件。报告：`reports/repo_graph_phase2/rsg_hard_ab_20260724.md`。

## 主要缺陷

1. **Public 过、Hidden 挂** — 行为保真不足（hard50 上 public→hidden 失败极高）。
2. **依赖闭包不完整** — 找得到入口，收不齐 helper / 资源 / 注册。
3. **Over-copy** — 功能门过了但 extraction 接近整仓，final score 接近 0。
4. **框架 / 资源缠绕更难**；vibe clutter 反而相对容易。
5. **过程质量差** — 重复读文件、过早宣称完成；弱模型还有更高环境噪声。

这些缺陷支持「公开契约下的 API/行为完成与紧凑解耦」是主问题，**不支持**「用状态机替模型决定步骤」，也**不支持**「仅加强文件定位/RSG start-here 即可抬 hard 通过率」。下一步见 [CURRENT_RESEARCH.md](CURRENT_RESEARCH.md)。

## 分析边界

- 同一 agent（OpenHands）+ 特定模型；不可外推所有框架。
- 三模型已有完整 150 覆盖（Flash frozen，两个 Qwen candidate）；Qwen-Coder 仍缺 hard50。
- 不做 ECSM 因果结论（该线已废弃）。
- 现有 RSG 轨迹不足以评价通用工具增强效果。

## 延伸阅读

- 当前研究入口：[CURRENT_RESEARCH.md](CURRENT_RESEARCH.md)
- 数字表：[paper_tables.md](paper_tables.md)
- 一页摘要：`reports/paper_analysis/executive_summary.md`（本地）
- 轨迹证据：[TRAJECTORY_FINDINGS.md](research_analysis/TRAJECTORY_FINDINGS.md)
- 失败标签定义：[05_failure_taxonomy.md](05_failure_taxonomy.md)
- 报告索引：[REPORTS_INDEX.md](REPORTS_INDEX.md)
