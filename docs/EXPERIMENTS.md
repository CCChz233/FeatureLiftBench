# FeatureLiftBench 实验清单

**最后更新：** 2026-07-27

## 当前实验版本

正式主结果只接受：

```text
benchmark policy: featureliftbench.full_repository_no_hint_main.v3
freeze:
  artifacts/research_analysis/v3/current_benchmark_freeze.json
agent: OpenHands
arm: Main
workspace: Full-Repository / No-Hint / evaluator-test-blind
sandbox: agent Docker + evaluator Docker
tasks: Python External-150
attempts: 1 per task
primary metric: evaluator Functional Pass@1
```

运行入口：
[SERVER_RUNBOOK_PYTHON150.md](SERVER_RUNBOOK_PYTHON150.md)。

## v3 完成度

| 实验 | 状态 | 还缺什么 |
| --- | --- | --- |
| Reference/Oracle validation | 完成，450/450 | 无 |
| Isolation/compactness canaries | 完成，12/12 | 无 |
| End-to-end model smoke | 待在服务器做 | 1 题、正式镜像和 profile |
| DeepSeek/Flash v3 Python-150 | 未运行 | 150 次独立 task attempts |
| Qwen 系列 v3 Python-150 | 未运行 | 每个模型各 150 次 |
| 其他 baseline v3 Python-150 | 未运行 | 先冻结模型名单和 profile |
| v3 cross-model leaderboard | 未生成 | 至少两个同协议完整 suites |
| v3 failure/token/compactness analysis | 未生成 | 等 baseline 完成 |

因此当前可以开始实验，但还不能在论文中报告 v3 模型性能。

## 历史 `mixed_snapshot_v1` 结果

### 2026-07-26 四模型 candidate

四组均为 OpenHands、test-blind、agent/eval Docker、150 tasks、attempt=1，
但 Agent 输入是 mixed/pruned source snapshots，且 server bundle 缺完整
per-run v3 freeze provenance。

| Model | Evaluator Functional Pass@1 | Agent-completion pass |
| --- | ---: | ---: |
| DeepSeek-V4-Flash-DSpark | **87/150（58.0%）** | 84/150 |
| Qwen3.5-122B-A10B-FP8 | **56/150（37.3%）** | 56/150 |
| Qwen3.6-35B-A3B-FP8 | **49/150（32.7%）** | 47/150 |
| gpt-oss-120b | **37/150（24.7%）** | 37/150 |

两种 pass 口径差异来自五条 agent step-limit 后 evaluator 通过的记录。
论文 benchmark 主指标使用 evaluator functional gate；Agent completion、
step limit 和 token 作为过程指标单列。

完整文件：
[`reports/python150_compliant_20260726/`](../reports/python150_compliant_20260726/)。
已知 caveat：

- DeepSeek 1 条、Qwen3.6-35B 4 条 context violation；
- Qwen3.5-122B 有一条 fail→fail post-hoc rerun 说明；
- Qwen3.6-27B 尚未包含；
- compact bundle 不能独立证明服务器 task/spec 与当前 v3 freeze 一致；
- 最重要的是源码条件不是 v3 full-repository。

### 更早的 frozen/candidate runs

2026-07-12 的 core-100、hard-extension-50 和拼接 Python-150 结果保存在
[v1 mixed-snapshot run archive](../reports/archive/v1_mixed_snapshot_runs_20260712.md)。
这些数字只用于历史复现，不再作为当前 paper table。

### Public-feedback 配对

同一历史 hard-50、DeepSeek V4 Flash：

| 当前语义 | 历史标签 | Pass |
| --- | --- | ---: |
| Public-feedback | Main | 11/50 |
| Test-blind | No-public | 4/50 |

这表明 evaluator feedback 会显著改变结果，因此实验臂必须显式命名。
它不证明 v3 Main 的绝对性能。

## 报告指标

每个完整 suite 至少报告：

### Headline

- assigned / completed tasks；
- evaluator Functional Pass@1；
- Core-100 / Hard-50（仅分析切片）；
- bootstrap confidence interval 或 task-level paired comparison。

### Correctness layers

- build/import；
- public regression layer；
- hidden behavior layer；
- isolation/forbidden checks；
- agent/evaluator status mismatch。

### Compactness

- submission/reference LOC ratio；
- file-count ratio；
- copied LOC/fraction；
- dependency footprint；
- excess copied LOC。

### Cost and process

- API calls；
- prompt/completion/total tokens；
- interaction steps；
- agent/evaluator/wall-clock time；
- step-limit、context-limit、rate-limit 和 infra failures。

### Slices

- repository archetype/domain；
- entanglement primary/types；
- source size；
- task footprint；
- popular vs long-tail source；
- model and agent configuration。

## 冻结要求

一个 suite 进入 v3 paper table 前必须保存：

- benchmark freeze ID；
- task ID set；
- source/spec/reference/evaluator hashes；
- agent/eval image digests；
- model identifier、provider、profile 和 prompt arm；
- attempt policy、timeouts、worker count；
- 每题 `run.json`、`eval/result.json`、submission 和 usage；
- context/rerun/infra exception ledger；
- suite checksum 和数据质量报告。

原始结果默认留在 `experiments/`，不进入 benchmark 代码提交；小型索引、
校验和和审计摘要可进入 `reports/`。

## 相关文档

- 实验臂：[EXPERIMENT_ARMS.md](EXPERIMENT_ARMS.md)
- 评测口径：[03_evaluator_and_scoring.md](03_evaluator_and_scoring.md)
- 实验协议：[04_experiment_protocol.md](04_experiment_protocol.md)
- 结论边界：[FINDINGS.md](FINDINGS.md)
- 报告索引：[REPORTS_INDEX.md](REPORTS_INDEX.md)
