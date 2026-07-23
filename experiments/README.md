# experiments/

这里保存实验的原始证据、可复查索引和传输包。体积较大的 run 默认不进 Git；目录结构、注册表和校验和进 Git。

论文与当前实验讨论统一从 [docs/CURRENT_RESEARCH.md](../docs/CURRENT_RESEARCH.md) 开始；不要把本目录当作文档入口。

## 目录分区

| 路径 | 类别 | 说明 |
| --- | --- | --- |
| `python/openhands/<model>/<run_id>/` | leaderboard | Python core-100、hard50 与完整榜实验 |
| `GO/openhands/<model>/<run_id>/` | calibration | Go pilot / calibration，非 Python 主榜 |
| `smoke/` | smoke | 烟囱、调试和并发验证 |
| `ecsm_pilot/` | mechanism | ECSM 机制实验；运行输出仍默认忽略 |
| `rsg_pilot/openhands/deepseek-v4-flash/<experiment_id>/` | mechanism | 冻结的 P0/P3、2 tasks × 3 repeats OpenHands RSG Pilot |
| `v1_1_*` | validation | v1.1 修复、隔离与 infra re-evaluation 的历史证据 |
| `batch3-*` | materialization | batch3 reference / task materialization 历史证据 |
| `bundles/incoming/` | transport | 收到的原始压缩包和可追溯 SHA-256；压缩包本身不进 Git |
| `registry/` | index | 全目录机器可读清单、数据质量报告和跨 run study |

历史目录的路径已被 quarantine ledger、报告和脚本引用，因此不为“看起来整齐”而批量移动。统一入口是 `registry/`，原始目录保持可追溯。

## 当前 RSG Pilot 状态

- `rsg-pilot-v1-20260723`：控制器重试分类错误暴露后的审计目录，已标记
  `invalidated`，不得进入分析。
- `rsg-pilot-v1-20260723-clean1`：修复后的干净付费门控；完成 P0/P3
  2/12 cells 后以 `paid_pair_rsg_adoption_gate_failed` 停止。
- clean1 的 P3 采用了 fresh `submission-check`，但没有调用
  `task-closure`；剩余 10 cells 未运行。
- 恢复 Pilot 前必须完成 OpenHands 原生 RSG tools 和新的 mechanism smoke。

这两批均不是完整 Pilot，也不能用于 RSG 效果或因果结论。

## 当前 Python-150 视图

| 模型 | 状态 | 覆盖 | Pass | Avg final |
| --- | --- | ---: | ---: | ---: |
| DeepSeek-V4-Flash | frozen | 150/150 | **91/150** | 0.358817 |
| Qwen3.6-27B-FP8 | candidate | 150/150 | **58/150** | 0.224684 |
| Qwen3.6-35B-A3B-FP8 | candidate | 150/150 | **52/150** | 0.210023 |
| Qwen3-Coder-30B | incomplete | 100/150 | **24/100** | 0.172782 |

`candidate` 表示结果已导入并通过结构检查，但尚未写入论文冻结集。论文表继续以 [docs/paper_runs_frozen.md](../docs/paper_runs_frozen.md) 为准。

## 结果口径

同一任务中，评测分数、build/test 门禁以 `<task_id>/eval/result.json` 为准；任务最终状态以 `<task_id>/run.json` 的 agent + evaluator 组合结论为准。只有 task-local 文件缺失时，才回退到 `suite.json` 的紧凑 run 记录。

`suite.summary` 是可重建缓存，不作为注册表的原始指标来源。平均 final score 的分母是全部 assigned tasks；缺 submission、构建失败和测试失败均计 0。agent 本身失败时，即使残留 submission 通过 evaluator，也不计为任务 pass。

生命周期统一使用 `incoming → candidate → validated → frozen`；被新实验取代但仍需保留的结果标记为 `superseded`，不删除原始证据。

## 常用命令

```bash
# 从 task-local 结果重建一个 suite 的可移植索引
PYTHONPATH=harness python harness/scripts/refresh_suite_from_task_runs.py <suite_dir>

# 扫描整个 experiments 并重建 registry
PYTHONPATH=harness python harness/scripts/build_experiment_registry.py

# 分析单个 suite
PYTHONPATH=harness python harness/scripts/analyze_benchmark_suite.py <suite_dir>

# 只冻结、预热并查看 12-run RSG Pilot 顺序（不调用付费 API）
PYTHONPATH=harness python harness/scripts/run_repo_graph_pilot.py \
  --experiment-id <experiment_id>

# 通过镜像、profile 和 graph prewarm 门后执行 Pilot
PYTHONPATH=harness python harness/scripts/run_repo_graph_pilot.py \
  --experiment-id <experiment_id> --execute
```

详细清单见 [registry/INVENTORY.md](registry/INVENTORY.md)，正式实验状态见 [docs/EXPERIMENTS.md](../docs/EXPERIMENTS.md)，运行方法见 [RUN.md](../RUN.md) §6.1。
