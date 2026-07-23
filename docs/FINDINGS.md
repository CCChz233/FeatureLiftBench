# 实验结果能说明什么（Findings）

基于已冻结 OpenHands 实验（详见 [EXPERIMENTS.md](EXPERIMENTS.md) 与 [TRAJECTORY_FINDINGS.md](research_analysis/TRAJECTORY_FINDINGS.md)）。  
**不是** ECSM Pilot 结论（Pilot 尚未跑）。

## 完成度如何

| 口径 | 结果 |
| --- | --- |
| 最强 Flash · core-100 | **83/100（83%）**，avg score **0.52** |
| 最强 Flash · 全 150 | **91/150（60.7%）**，avg **0.36** |
| Flash · hard50 | **8/50（16%）** |
| 开源最好 Qwen3.6-27B · core-100 | **54/100** |
| Qwen3-Coder-30B · core-100 | **24/100** |

强模型在常规 hard 题上可用；一到 hard3 / 强缠绕切片就断崖下跌。

2026-07-20 新导入但尚未冻结的同任务集 candidate 结果为：Qwen3.6-27B **58/150（38.7%）**、Qwen3.6-35B **52/150（34.7%）**。两者 hard50 分别只有 4/50 和 3/50，与上述难度断崖一致；论文正式表在 re-freeze 前仍不使用这两个结果。

## RSG 机制门目前说明什么

2026-07-23 的 `rsg-pilot-v1-20260723-clean1` 只完成了第一对 P0/P3，
随后按预注册采用门停止。P3 成功执行了 fresh `submission-check`，但没有
执行初始 `task-closure`。因此当前最直接的工程结论是：**CLI 可用和 prompt
中明确要求，并不能保证 OpenHands 稳定采用 RSG 工具。**

两条 run 都没有 context violation，最大 prompt 也没有达到压缩触发值；
这次停止不是上下文压缩故障。由于只有一对且 RSG treatment 未完整采用，
不能用它判断 RSG 是否改善 correctness、hidden pass 或 token 效率。

## 主要缺陷

1. **Public 过、Hidden 挂** — 行为保真不足（hard50 上 public→hidden 失败极高）。
2. **依赖闭包不完整** — 找得到入口，收不齐 helper / 资源 / 注册。
3. **Over-copy** — 功能门过了但 extraction 接近整仓，final score 接近 0。
4. **框架 / 资源缠绕更难**；vibe clutter 反而相对容易。
5. **过程质量差** — 重复读文件、过早宣称完成；弱模型还有更高环境噪声。

## 分析边界

- 同一 agent（OpenHands）+ 特定模型；不可外推所有框架。
- 三模型已有完整 150 覆盖（Flash frozen，两个 Qwen candidate）；Qwen-Coder 仍缺 hard50。
- 机制臂（ECSM）无数据前，不做因果干预结论。
- RSG clean1 是采用门诊断，不是完整 Pilot；P3 treatment 未完整执行，不能做 P0/P3 效果归因。

## 延伸阅读

- 数字表：[paper_tables.md](paper_tables.md)
- 一页摘要：`reports/paper_analysis/executive_summary.md`（本地）
- 轨迹证据：[TRAJECTORY_FINDINGS.md](research_analysis/TRAJECTORY_FINDINGS.md)
- 失败标签定义：[05_failure_taxonomy.md](05_failure_taxonomy.md)
- 报告索引：[REPORTS_INDEX.md](REPORTS_INDEX.md)
