# FeatureLiftBench 当前状态

> **Status: current · Last verified: 2026-08-04**
> 本文件是当前规模、release、freeze、实验完成度和下一步的唯一手写事实源。

## Release

当前可运行 release 为 **Python-200 Full-Repository / No-Hint Main**：冻结的
Python-150 baseline 与独立冻结的 balanced External-50 组成统一 task root。

| Item | Current value |
| --- | --- |
| Unified suite | `python200-full-repository-no-hint-20260801-v1` |
| Task set SHA256 | `cee22c263a3c190e8b13b0c3c70d9fabac5c6c767010e5c21220f2c8c61bfa74` |
| Baseline freeze | `846b814726217623fa205cb7688bee61e6c21c43efda1ebd05e79b5ed8cb4fbd` |
| External selection | `external50-expansion-20260801-v2` |
| Unified task root | `benchmark/python200_tasks/` |
| Unified source registry | `benchmark/sources/python200_registry.json` |

权威组合清单是
[`benchmark/selection/python200_suite.json`](../benchmark/selection/python200_suite.json)。
`artifacts/research_analysis/v3/current_benchmark_freeze.json` 仍是不可变的 baseline
freeze，不把 External-50 偷写进旧 freeze。

## Readiness

最近一次本地无模型 preflight：

- release materialization：150 frozen + 50 external；
- External source mapping：50/50 ready；
- dependency closure：50/50 current；
- balance design：PASS；
- Python 3.11 wheel coverage：200/200；
- baseline freeze：150/150 unchanged；
- runnable task compliance：200/200。

服务器正式运行仍必须执行 Docker strict preflight，并记录 agent/evaluator image
identity。Runner 会在模型调用前执行该门禁。

## Available Model Evidence

冻结 Python-150 结果（Functional Pass@1；DeepSeek 已于 2026-08-05 补齐 150）：

| Model | Coverage | Evaluator Functional Pass@1 | Use |
| --- | ---: | ---: | --- |
| DeepSeek V4 Flash | 150/150 | 99/150 | paper candidate；需 image/context 收尾 |
| Qwen3.5 122B | 150/150 | 59/150 | candidate；需 context sensitivity |
| Qwen3.6 35B | 150/150 | 59/150 | candidate；需 context sensitivity |
| GPT-OSS 120B | 150/150 | 27/150 | Python-200 extension candidate |

最新合并主表见
[`reports/paper_analysis/python150_with_deepseek150_20260805/`](../reports/paper_analysis/python150_with_deepseek150_20260805/README.md)。
GPT-OSS/Qwen 逐题来源仍是
[`reports/paper_analysis/python150_frozen_20260803/`](../reports/paper_analysis/python150_frozen_20260803/README.md)。
归档自带 MANIFEST 的 pass 数不是主指标，不能引用。

## Result Eligibility

冻结 baseline 与 External-50 只能在以下条件完全一致时按 task ID 合并：exact model
revision/endpoint、agent profile、prompt/arm、attempt policy、agent image、evaluator
image/scoring code 和 Main information boundary。缺失 submission 计入分母并视为
Functional failure；不相交 task shards 是分区，不是重复样本。

当前结果资格：

| Result set | Classification |
| --- | --- |
| DeepSeek、GPT-OSS、Qwen3.5、Qwen3.6 frozen baseline（均 150/150） | 解决 evaluator/context 条件后可接 External-50 |
| Balanced External-50 | benchmark ready；model results 尚未完成 |
| Older mixed-snapshot suites | historical；不得并入 current Main |

主结果必须从逐题 evaluator `functional_gate` 重算，并与 `eval/result.json` 交叉核验；
agent completion、bundle MANIFEST 和 stale suite summary 都不是 headline metric。实验条件、
留存和统计要求见 [EVALUATION.md](EVALUATION.md)。

## Evidence Boundary

现有证据支持：

- frozen baseline 能区分被测 coding agents；
- Agent completion 不能替代 evaluator Functional Pass；
- 完整 baseline 模型在环境问题解决后可做 task-paired comparison；
- External-50 已 package-complete，可在兼容条件下扩展完整 baseline。

现有证据尚不支持：

- final Python-200 leaderboard；
- 在 evaluator image mismatch 未解决时声称精确 frozen-environment 结果；
- 未做 sensitivity analysis 时声称 Qwen/DeepSeek 排名与 context window 无关；
- 仅由 `copied_fraction` 推导 plagiarism，或泛化到未覆盖的语言与仓库总体。

## Blocking Issues Before Paper Tables

1. 旧结果实际 evaluator image 与 baseline freeze 登记的 evaluator image 不同；需
   attestation 或 evaluator-only re-evaluation。
2. Qwen3.5、Qwen3.6 与 DeepSeek 存在 context-window violations；需重跑违规
   model-task 或预注册 sensitivity analysis。
3. Python-200 的模型 extension（External-50）结果尚未完成，不应提前发布完整
   leaderboard。

## Next Actions

1. 固定 model revision、agent profile、Main arm、attempt policy 和 image identities。
2. 对四组完整 baseline 模型运行 External-50。
3. 对旧 submission 统一 evaluator 环境并生成 200 题逐题合并表。
4. 冻结论文统计口径后再生成 leaderboard、置信区间和 paired comparison。

运行入口见 [RUN.md](../RUN.md)，实验与结果规范见 [EVALUATION.md](EVALUATION.md)。
