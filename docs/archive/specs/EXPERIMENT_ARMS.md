# FeatureLiftBench 实验臂

> **Status: archived · Last verified: 2026-08-04**
> 已由 [EVALUATION.md](../../EVALUATION.md) 替代，仅供历史复查。

所有实验臂共享相同 task contract、hidden evaluation、Functional metric 和 attempt
policy。实验臂只能改变明确登记的信息或工具条件，不能通过改题、改 hidden tests 或
重试失败样本制造增益。

## Main

| Dimension | Required value |
| --- | --- |
| Source context | full upstream repository |
| Source hints | hidden |
| Benchmark tests | hidden |
| Prompt style | standard |
| Extra agent passes | 0 |
| Max task attempts | 1 |
| Functional stage | isolated Docker evaluation |

Main 是 leaderboard 和论文主结果的唯一默认条件。

## Formal Ablations

| Arm | Single intended change | Interpretation |
| --- | --- | --- |
| Entrypoint-Hint | expose source entry hints | localization information value |
| Public-Feedback | expose/mount public tests | benchmark-feedback value |
| Pruned-Context | replace full repo with declared pruned context | source-context value |
| Short-Prompt | alter prompt style only | prompt sensitivity |

每个 ablation 必须记录 `ablation_arm`、changed dimension 和其余 Main 不变量；不能与
不同模型、不同 image 或不同 task revision 的结果直接归因比较。

## Archived Method Arms

Test-First Lift、TD-Cognition、Exec-Contract、Self-Contract、CGCC-lite、FCEC 和 PDR
属于历史方法开发或负结果，不是当前正式 arm。原始设计与结果边界保存在
[archive/methods/](../methods/README.md)。

## Minimum Reporting Matrix

1. Main Functional Pass@1。
2. 至少一个信息边界 ablation，使用相同模型与镜像。
3. task-paired difference，而不是只比较两个总通过率。
4. context、infra、rate-limit 和 rerun exception 单独列账。

运行约束见 [Experiment Protocol](04_experiment_protocol.md)。
