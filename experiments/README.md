# experiments/

> **Documentation status: reference · Last verified: 2026-08-18**

原始模型运行和验证证据只进入以下七个目录：

| Directory | Purpose |
| --- | --- |
| `python/` | Python OpenHands leaderboard 和历史正式 runs |
| `GO/` | Go calibration runs |
| `smoke/` | 临时 smoke/debug，不进入论文主表 |
| `methods/` | 方法 pilot、历史 ablation 和负结果 |
| `validation/` | reference、oracle、preflight 和 release validation |
| `bundles/` | incoming、outgoing、archive 和 retired 传输包 |
| `registry/` | 可提交的 suite index、路径映射和 bundle ledger |

Python-200 当前状态见 [`docs/STATUS.md`](../docs/STATUS.md)，正式实验条件见
[`docs/EVALUATION.md`](../docs/EVALUATION.md)。正式模型 run 继续写入：

```text
experiments/python/openhands/<model>/<run-id>/
```

正式 ablation 也应使用标准 suite 布局，并在 suite/run metadata 中登记 arm；
`methods/ablation/` 只保留历史方法实验。

## Path Compatibility

历史报告中的旧路径不重写。解析旧路径：

```bash
PYTHONPATH=harness python3 harness/scripts/resolve_experiment_path.py \
  experiments/v1_1_oracle_validation/536c2beec549fdc8
```

映射表是 `registry/path_aliases.json`，采用 longest-prefix resolution。迁移和删除
记录见 `registry/bundle_ledger.json`。

## Maintenance

```bash
# 验证目录布局和迁移状态
python3 scripts/reorganize_experiments.py --check

# 重建 suite registry
PYTHONPATH=harness python3 harness/scripts/build_experiment_registry.py
```

Raw evidence 默认不进 Git；不得覆盖 completed suite。Resume 只能补没有 terminal
`run.json` 的 task。

## Current Result Correction

2026-08-18 起，跨模型 Python-200 Main 以冻结 Python-150 与 External-50 的逐题
`eval/result.json` 为准，由 `harness/scripts/merge_python200_main_results.py`
按题号合并。当前主表见 [`docs/STATUS.md`](../docs/STATUS.md) 和
[`python200_cross_model_main_20260818.json`](../artifacts/research_analysis/current_results/python200_cross_model_main_20260818.json)。

2026-08-17 起，DeepSeek Python-200 Main vs Lite V1 以本机实验目录中的
`suite.json` 与逐题 `eval/result.json` 为准，由
`harness/scripts/reconcile_current_deepseek_results.py` 重建。当前结论见
[`docs/FINDINGS.md`](../docs/FINDINGS.md) 和
[`deepseek_main_vs_lite_v1_20260817.json`](../artifacts/research_analysis/current_results/deepseek_main_vs_lite_v1_20260817.json)。

旧 results-pack README 把 `summary.passed` 误标为 Functional pass；旧 pack 对账
JSON `deepseek_main_vs_frozen_lite_v1_20260817.json` 因缺少逐题 eval 已过时。
那次比较的是已退役 Lite V1 协议（Main 预算 120 步），不是 Frozen 45 步信封，
也不是当前 [V1 = Main+2M](../docs/METHOD_V1.md)。

当前 V1 分片写入
`experiments/python/openhands/qwen3.6-35b-a3b-fp8/python200-qwen3.6-35b-a3b-fp8-v1-0817-001-shardN-p803N/`，
合并 suite 为同目录下不带 `-shard` 的 run-id。Core-12 诊断在
`experiments/methods/main_2m_cap/`。
