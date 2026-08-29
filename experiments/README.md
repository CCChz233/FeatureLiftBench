# experiments/

> **Documentation status: reference · Last verified: 2026-08-29**

原始模型运行和验证证据只进入以下七个目录：

| Directory | Purpose |
| --- | --- |
| `python/` | OpenHands leaderboard（`openhands/`）与可选 runtime ablation（`runtime/`；不是 Main） |
| `GO/` | Go calibration runs |
| `smoke/` | 临时 smoke/debug，不进入论文主表 |
| `methods/` | 方法 pilot、历史 ablation、负结果，以及 AutoSaddler 等 screening |
| `validation/` | reference、oracle、preflight、Hard-50 校准、agentic-evidence 原料 |
| `bundles/` | incoming、outgoing、archive 和 retired 传输包 |
| `registry/` | 可提交的 suite index、路径映射、bundle ledger、维护记录 |

顶层不要再放 run 目录或结果 tar。校验：

```bash
python3.12 scripts/reorganize_experiments.py --check
```

Python-200' 当前状态见 [`docs/STATUS.md`](../docs/STATUS.md)，正式实验条件见
[`docs/EVALUATION.md`](../docs/EVALUATION.md)。正式 OpenHands run 写入：

```text
experiments/python/openhands/<model>/<run-id>/
```

可选 runtime ablation 写入：

```text
experiments/python/runtime/<adapter>/<model>/<run-id>/
```

不得把 runtime 目录并入 OpenHands 主表。规范见
[`docs/METHOD_AGENT_RUNTIME.md`](../docs/METHOD_AGENT_RUNTIME.md)。

正式 ablation 也应使用标准 suite 布局，并在 suite/run metadata 中登记 arm；
`methods/ablation/` 只保留历史方法实验。新的 screening（如 AutoSaddler）写入
`methods/<method-id>/`，不要写入 `evidence/`。

## Path Compatibility

历史报告中的旧路径不重写。解析旧路径：

```bash
PYTHONPATH=harness python3.12 harness/scripts/resolve_experiment_path.py \
  experiments/v1_1_oracle_validation/536c2beec549fdc8
```

映射表是 `registry/path_aliases.json`，采用 longest-prefix resolution。迁移和删除
记录见 `registry/bundle_ledger.json`。2026-08-29 整理见
`registry/repository_maintenance_20260829.md`。

## Maintenance

```bash
python3.12 scripts/reorganize_experiments.py --check
PYTHONPATH=harness python3.12 harness/scripts/build_experiment_registry.py
```

Raw evidence 默认不进 Git；不得覆盖 completed suite。Resume 只能补没有 terminal
`run.json` 的 task。

## Historical result snapshots（不是 Python-200' 主表）

2026-08-18 起，跨模型 **旧** Python-200 Main（冻结 150 + External-50）以逐题
`eval/result.json` 为准，由 `harness/scripts/merge_python200_main_results.py`
按题号合并。快照：
[`python200_cross_model_main_20260818.json`](../artifacts/research_analysis/current_results/python200_cross_model_main_20260818.json)。
这是 superseded 对照，**不是** 150+Hard-50 主表。

2026-08-17 起，DeepSeek 旧 Python-200 Main vs Lite V1 以本机 `suite.json` 与逐题
`eval/result.json` 为准。结论见 [`docs/FINDINGS.md`](../docs/FINDINGS.md) 和
[`deepseek_main_vs_lite_v1_20260817.json`](../artifacts/research_analysis/current_results/deepseek_main_vs_lite_v1_20260817.json)。
那次比较的是已退役 Lite V1 协议，不是当前 [V1 = Main+2M](../docs/METHOD_V1.md)。

当前 V1 分片（旧套件）写入
`experiments/python/openhands/qwen3.6-35b-a3b-fp8/python200-qwen3.6-35b-a3b-fp8-v1-0817-001-shardN-p803N/`，
合并 suite 为同目录下不带 `-shard` 的 run-id。Core-12 诊断路径见
[`docs/METHOD_V1.md`](../docs/METHOD_V1.md)。

Hard-50 Flash 校准原料在 `validation/hard50/`。数字是否进入 STATUS 由
[`docs/STATUS.md`](../docs/STATUS.md) 决定，不因目录位置自动进主表。
