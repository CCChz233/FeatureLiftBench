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

## 主要缺陷

1. **Public 过、Hidden 挂** — 行为保真不足（hard50 上 public→hidden 失败极高）。
2. **依赖闭包不完整** — 找得到入口，收不齐 helper / 资源 / 注册。
3. **Over-copy** — 功能门过了但 extraction 接近整仓，final score 接近 0。
4. **框架 / 资源缠绕更难**；vibe clutter 反而相对容易。
5. **过程质量差** — 重复读文件、过早宣称完成；弱模型还有更高环境噪声。

## 分析边界

- 同一 agent（OpenHands）+ 特定模型；不可外推所有框架。
- 四模型完整 150 公平对比需先补三模型 hard50。
- 机制臂（ECSM）无数据前，不做因果干预结论。

## 延伸阅读

- 数字表：[paper_tables.md](paper_tables.md)
- 一页摘要：`reports/paper_analysis/executive_summary.md`（本地）
- 轨迹证据：[TRAJECTORY_FINDINGS.md](research_analysis/TRAJECTORY_FINDINGS.md)
- 失败标签定义：[05_failure_taxonomy.md](05_failure_taxonomy.md)
- 报告索引：[REPORTS_INDEX.md](REPORTS_INDEX.md)
