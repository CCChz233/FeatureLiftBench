# FeatureLiftBench 当前状态

> **Status: current · Last verified: 2026-09-14**

当前工作是基于用户提供的新版 `FSE.zip` 撰写 FSE 论文。
论文范围为 **150 个 Python 任务，126 个仓库、132 个快照**；
六配置在同一集合上形成 **900 条保留结果**。历史 200 题资产仍保留，额外 50 题不进入本文。

## 已保存结果

| 配置 | Functional pass / 150 | 百分比 |
| --- | ---: | ---: |
| DeepSeek V4 Pro | 115 | 76.7% |
| DeepSeek V4 Flash | 108 | 72.0% |
| GPT-5.6 Luna | 102 | 68.0% |
| GLM-5.3-Flash | 68 | 45.3% |
| Qwen3.6-35B-A3B-FP8 | 63 | 42.0% |
| GPT-OSS 120B | 36 | 24.0% |

- 源码消融：同一 40 题，Luna Full/Contract Only 为 23/9，Pro 为 25/6，Qwen 为 12/1；共 240 条结果。
- Pro 消融中 18 次 Contract-only 空提交伴随 LLM timeout，解释时保留该限制。
- 源码暴露：900 条轨迹派生记录中，241/303 次行为首败有入口关联文件内容返回证据；不等于完整定位或理解。
- 参考执行：选定 150 题的历史记录为 450/450 通过；本轮没有重新执行。

## 证据完整性

逐题主结果矩阵、消融结果及源码暴露派生数据可用于离线写作核对。
当前本地原始主实验 profile 为 **307/900**：Pro 150、Flash 150、GLM 7；其余 593 未恢复。
GLM 原目录共恢复 12 题，其余 5 题不在本文集合。
Luna、Qwen、OSS 的完整原始运行仍需完整结果包，见 [恢复记录](../experiments/paper_results_20260913/README.md)。

Luna/GLM Token 用量仍不可核验，不能用日志默认零值代替缺失数据。
`paper.py check` 的数值检查与 `paper.py audit` 的完整原始证据检查分开报告。

## 当前入口

- [项目地图](PROJECT_MAP.md)：论文、代码、数据、实验的对应关系。
- [论文工作流](paper/WORKFLOW.md)：编辑、检查、图表及打包。
- [数据来源清单](paper/paper_sources.json)：唯一正式输入路径与模型顺序。
- [本轮同步记录](paper/FSE_SYNC_20260914.md)：新版导入、修复与验证。

功能正确性仍由 Build ∧ Primary ∧ Extended ∧ Isolation 决定，agent 完成状态不替代功能分数。
RRES/Copy 只描述成功产物；Steps/Token 只作执行诊断。方法与历史批次不得并入当前主比较。
