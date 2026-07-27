# experiments/

本目录保存原始模型运行、传输包和机器索引。大体积 runs 默认不进 Git；
benchmark 定义不依赖本目录。

当前研究入口：
[`docs/CURRENT_RESEARCH.md`](../docs/CURRENT_RESEARCH.md)。正式结果口径：
[`docs/EXPERIMENTS.md`](../docs/EXPERIMENTS.md)。

## 目录

| 路径 | 内容 |
| --- | --- |
| `python/openhands/<model>/<run_id>/` | Python OpenHands runs |
| `GO/openhands/<model>/<run_id>/` | Go calibration |
| `smoke/` | smoke/debug |
| `ablation/` | 显式实验臂 |
| `rsg_pilot/` | 历史 RSG 证据 |
| `ecsm_pilot/` | 已废弃 ECSM 原始证据 |
| `v1_1_*` | 历史 contract/oracle validation |
| `batch3-*` | 历史 100→150 materialization |
| `bundles/incoming/` | 外部传输包与 SHA-256 |
| `registry/` | 跨 run 机器索引 |

历史目录可能被报告和 ledger 引用，不为视觉整齐而移动。当前入口统一由
`registry/` 和 `reports/` 提供。

## v3 当前状态

Full-Repository / No-Hint Python-150 模型 baseline 尚未导入。本目录中的
现有正式规模结果都必须保留其 `mixed_snapshot_v1` 或其他历史 arm 标签。

新 v3 suite 必须记录并匹配 active freeze pointer：

```text
artifacts/research_analysis/v3/current_benchmark_freeze.json
```

并保存 agent/eval image digests、exact task set、attempt policy、逐题 run/eval、
submission、usage 和 exception ledger。

## 2026-07-26 历史四模型视图

这些 suites 各有 150 tasks，但使用 mixed snapshots。

| 模型 | Evaluator Functional Pass@1 | Agent-completion pass |
| --- | ---: | ---: |
| DeepSeek-V4-Flash-DSpark | 87/150 | 84/150 |
| Qwen3.5-122B-A10B-FP8 | 56/150 | 56/150 |
| Qwen3.6-35B-A3B-FP8 | 49/150 | 47/150 |
| gpt-oss-120b | 37/150 | 37/150 |

统一审计：
[`reports/python150_compliant_20260726/`](../reports/python150_compliant_20260726/)。

更早的 core-100/hard50/patched Python-150 run set 见
[`reports/archive/v1_mixed_snapshot_runs_20260712.md`](../reports/archive/v1_mixed_snapshot_runs_20260712.md)。

## 结果口径

- Benchmark correctness：逐题 evaluator `functional_gate`；
- Agent process：completion status、step/context/rate/infra failures；
- Compactness：reference-relative vector；
- Cost：tokens、API calls、steps、agent/eval/wall time；
- `suite.summary` 是可重建缓存，不是唯一事实源；
- continuation 只能补没有终态 `run.json` 的题，不能重试已完成失败并仍称
  Pass@1。

## 常用命令

```bash
# 重建 suite 索引
PYTHONPATH=harness python harness/scripts/refresh_suite_from_task_runs.py <suite_dir>

# 重建全实验 registry
PYTHONPATH=harness python harness/scripts/build_experiment_registry.py

# 分析单个 suite
PYTHONPATH=harness python harness/scripts/analyze_benchmark_suite.py <suite_dir>
```

正式 Python-150 运行见
[`docs/SERVER_RUNBOOK_PYTHON150.md`](../docs/SERVER_RUNBOOK_PYTHON150.md)。
