# FeatureLiftBench 当前状态

> **Status: current · Last verified: 2026-08-17**
> 本文件是当前规模、release、可用结果和证据缺口的唯一手写事实源。

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
freeze，不把 External-50 写入旧 freeze。

## Metric Contract

当前主结果只有两项核心指标：

1. **Functional Pass Rate**：`build ∧ public ∧ hidden ∧ isolation`。
2. **Reference-Relative Extraction Size (RRES)**：只在 Functional Pass 题上计算，越低越紧凑。

`final_score` 等于 `functional_gate`，不是额外指标。Tokens、steps、time 和 agent
completion 只是运行诊断。每道 Functional Fail 按 missing submission、build、public、
hidden、isolation 的首败阶段分类。完整定义见 [EVALUATION.md](EVALUATION.md)。

## Current DeepSeek Python-200 Evidence

| 端点 | 方法 | Functional Pass | Pass Rate | RRES 证据 |
| --- | --- | ---: | ---: | --- |
| API | Main | **144/200** | **72.0%** | 99/144 pass 题可用，不完整 |
| API | Frozen Lite V1 | 131/200 | 65.5% | 缺失 |
| 本地 vLLM | Main | **145/200** | **72.5%** | 缺失 |
| 本地 vLLM | Frozen Lite V1 | 127/200 | 63.5% | 127/127 pass 题可用 |

结论：Main 在 API 上领先 6.5 个百分点，在本地 vLLM 上领先 9.0 个百分点。
Frozen Lite V1 目前是 resource-saving trade-off，不是正确性改进。因证据不匹配，
当前不能宣称 Lite 的 RRES 优于 Main。完整解释见 [FINDINGS.md](FINDINGS.md)。

机器可读对账快照：
[`deepseek_main_vs_frozen_lite_v1_20260817.json`](../artifacts/research_analysis/current_results/deepseek_main_vs_frozen_lite_v1_20260817.json)。

## Evidence Completeness

| Result set | Functional | Failure stages | RRES |
| --- | --- | --- | --- |
| API Main-200 | 完整 | Main-150 可分类；External-50 五个失败缺阶段 | 99/144，部分 |
| API Frozen Lite V1-200 | 完整 | 除 missing 外缺失 | 缺失 |
| 本地 Main-200 | 完整 | 除 missing 外缺失 | 缺失 |
| 本地 Frozen Lite V1-200 | 完整 | 完整 | 完整 |

原始结果包的 `summary.passed` 是 workflow/run status，不是 Functional Pass。历史 README
对该字段的标签已过时；当前必须从 evaluator `final_score/functional_gate` 重算。

## Readiness

最近一次本地无模型 preflight：

- release materialization：150 frozen + 50 external；
- External source mapping：50/50 ready；
- dependency closure：50/50 current；
- balance design：PASS；
- Python 3.11 wheel coverage：200/200；
- baseline freeze：150/150 unchanged；
- runnable task compliance：200/200。

服务器正式运行仍必须执行 Docker strict preflight，并记录 agent/evaluator image identity。

## Historical Evidence

旧 Python-150 跨模型分析仍作为历史基线保留，但不再是当前 Main vs Lite
结果入口：

- DeepSeek V4 Flash：99/150；
- Qwen3.5 122B：59/150；
- Qwen3.6 35B：59/150；
- GPT-OSS 120B：27/150。

来源见
[`reports/paper_analysis/python150_with_deepseek150_20260805/`](../reports/paper_analysis/python150_with_deepseek150_20260805/README.md)。
这些数据不与当前 Python-200 方法对比混表。

## Current Evidence Gaps

1. 补齐 API Main External-50 的逐题 `eval/result.json`。
2. 补齐 API Frozen Lite V1 的逐题 evaluator 产物。
3. 补齐本地 Main 的逐题 evaluator 产物。
4. 在同 endpoint、同 task、两方都 Functional Pass 的样本上重算 paired RRES。
5. 论文主表前仍需确认 evaluator image 和 context-window 实验资格。

## Next Actions

1. 先恢复上述缺失的 evaluator 产物，不重跑已有正式结果。
2. 用统一脚本重建 Functional、失败阶段和 paired RRES。
3. 保持 Main 为默认对照；新方法先在高区分度子集上验证，达到正确性不劣后
   再扩展。

运行入口见 [RUN.md](../RUN.md)，实验与结果规范见 [EVALUATION.md](EVALUATION.md)。
