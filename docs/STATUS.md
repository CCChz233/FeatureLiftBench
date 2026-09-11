# FeatureLiftBench 当前状态

> **Status: current · Last verified: 2026-09-11**

当前工作是基于已完成实验撰写 FSE 论文。最终范围为 **200 个任务；六配置在相同 150 题上进行主比较；五配置额外覆盖其余 50 题**。

正式输入登记在 [paper_sources.json](paper/paper_sources.json)，日常操作见 [论文工作流](paper/WORKFLOW.md)。该清单指向现有数据，不新建 benchmark 版本，也不改写运行记录。

## 最终范围与结果

| 项目 | 当前范围 |
| --- | --- |
| Benchmark | FeatureLiftBench，200 个 Python 任务 |
| Source repositories / snapshots | 176 / 182 |
| 主比较 | 同一 150 题 × 6 配置 = 900 条保留结果 |
| 扩展评测 | 其余 50 题 × 5 配置；Pro 不在此范围 |
| 人工复核 | 作者确认全部 200 个保留任务已完成复核，AI 辅助 |
| Reference replay | 已保存的 200 × 3 次执行，600/600 通过 |

| 配置 | 主比较 / 150 | 额外 / 50 | 完整覆盖 / 200 |
| --- | ---: | ---: | ---: |
| DeepSeek V4 Pro | 115 | — | — |
| DeepSeek V4 Flash | 108 | 49 | 157 |
| GPT-5.6 Luna | 102 | 42 | 144 |
| GLM-5.3-Flash | 68 | 30 | 98 |
| Qwen3.6-35B-A3B-FP8 | 63 | 23 | 86 |
| GPT-OSS 120B | 36 | 25 | 61 |

表中为 evaluator functional pass 数，不使用 agent 完成状态代替正确性。此表是现有逐题结果的摘要；统计脚本以清单指定的 CSV 和 evaluator 输出为输入。

## 指标与术语

- Functional pass：Build、Public、Hidden、Isolation 全部通过。Public / Hidden 两组 benchmark tests 均不向智能体开放。
- RRES、Copy：通过产物的大小与直接源码重合诊断；不改变 functional pass，也不构成单一质量排名。
- Steps、Tokens：运行效率统计，按论文声明的计数方式和缺失情况报告。
- FeatureLiftBench 是唯一论文名称。路径中的 `python150`、`hard50`、`prime`、`v2` 是内部标识，不定义 Core / Hard 等难度层级。

## 数据与稿件入口

| 需要 | 入口 |
| --- | --- |
| 正文、引用与图片 | [论文 README](paper/README.md) |
| 输入路径、模型顺序与打包清单 | [paper_sources.json](paper/paper_sources.json) |
| 输入读取与范围检查 | [paper_inputs.py](paper/paper_inputs.py) |
| 核对、更新表格、绘图、打包 | [scripts/paper.py](../scripts/paper.py) |
| 主比较逐题结果 | [task_results.csv](../reports/paper_analysis/python150_prime_v2_analysis_20260905/task_results.csv) |
| 200 题身份记录 | [current_benchmark_freeze.json](../artifacts/research_analysis/python200_prime/current_benchmark_freeze.json) |

题包保留在 `benchmark/tasks/` 与 `benchmark/hard50/`，组合入口仍为 `benchmark/python200_hard_tasks/`。保留原路径以维护已有引用；物理目录不等于论文分类。

整理前的状态说明见 [历史快照](archive/snapshots/paper_workflow_20260911/README.md)。旧开发批次、临时分数和核对日志不作为当前论文数据入口；原始记录保留。

当前只读检查命令：`python -B scripts/paper.py check`。不启动模型、不执行任务、不编译 LaTeX。
