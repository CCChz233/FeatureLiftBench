# FeatureLiftBench scripts

> **Status: current · Last verified: 2026-09-02**

日常只认这些入口。论文 Main：`--benchmark python200_hard`。不要用
`./harness/scripts/archive/run_python200_paper.sh` 写新主表。

评测与 catalog 用 `python3.12`。

## 现在用这些

| 脚本 | 用途 |
| --- | --- |
| `scripts/run_benchmark.sh` | 稳定入口：benchmark × agent × method |
| `scripts/run_experiment.sh` | 上面那个入口调用的实现 |
| `featureliftbench` CLI | 安装 `harness/` 后的等价入口 |
| `scripts/run_benchmark_gate.py` | 只读套件门禁（三态标签）。P0 不发布分析名单 |
| `scripts/label_benchmark_tiers.py` | 旧打标驱动；筛题暂停，不要 `--write-selection` |
| `scripts/check_docs.py` | 文档链接 / status / 可达性 |
| `scripts/check_task_lifecycle.py` | 题包 split 与生命周期 |
| `scripts/reorganize_experiments.py` | 实验目录整理 |
| `scripts/promote_batch3_task.py` | 仍在用的 promotion 辅助 |
| `scripts/build_runnable_bundle.sh` | 可运行包 |
| `scripts/materialize_full_sources.py` | 物化 pinned source |
| `scripts/build_source_registry.py` | source registry |
| `scripts/build_python200_server_overlay.py` | 服务器 overlay |
| `scripts/build_python200_prime_*freeze.py` | freeze `--check` / 重建（见 runbook） |
| `scripts/audit_python200_contract_closure.py` | constitution 审计（打标输入） |
| `scripts/revalidate_python200_prime_oracles.py` | Oracle N=3 复验 |
| `harness/scripts/verify_all_oracles.py` | CI oracle 冒烟 |
| `harness/scripts/list_tasks.py` | 列题 |
| `harness/scripts/summarize_experiment_runs.py` | 汇总 run |
| `harness/scripts/analyze_python200_hard_main.py` | 论文套件分析 |
| `harness/scripts/audit_contract_entailment.py` | 门禁 C1/C2 |
| `harness/scripts/audit_source_entrypoints.py` | 门禁 C2 入口 |
| `benchmark/selection/scripts/` | Hard-50 / Python-200 物化与 freeze check |

根目录只保留薄转发：`run_benchmark.sh`、`run_experiment.sh`，以及 `setup.sh`。

```bash
./scripts/run_benchmark.sh --benchmark python200_hard --agent openhands --method main
python3.12 scripts/run_benchmark_gate.py --benchmark python200_hard
python3.12 scripts/check_docs.py --warnings-as-errors
```

## 不要当入口的

历史一次性脚本在 [archive/](archive/README.md)：v2/v3 freeze、External-150、
contract-closure dossier、旧 canary。能重建 freeze 所以保留，但不是日常命令。

本地出题草稿（batch3 wave、TFL wait 等）在 `scripts/archive/scratch/`，不进 Git。

`harness/scripts/archive/`：出题脚手架、Kill 方法比较、旧套件
`run_python*_paper.sh`，以及会和正式入口撞名的 mini-swe `run_benchmark.sh`。
详见 [harness/scripts/README.md](../harness/scripts/README.md)。

`tools/research_analysis/` 只服务 taxonomy / 轨迹派生分析。

不要在仓库根目录加新的 `run_*.sh`。新脚本进 `scripts/` 或 `harness/scripts/`，
并写清输入权威、输出目录、覆盖策略和验证命令。
