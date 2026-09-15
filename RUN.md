# FeatureLiftBench 运行与写作入口

> **Status: current · Last verified: 2026-09-14**

当前论文基于已完成实验写作，日常工作不需要调用模型或执行 benchmark。

## 写作

```bash
python -B scripts/paper.py check
python -B scripts/paper.py tables
python -B scripts/paper.py package
```

完整原始运行审计：`python -B scripts/paper.py audit`。
当前主实验 profile 仅恢复 307/900，因此该严格审计会失败；数值检查可独立执行。
单图与临时预览见 [绘图源码索引](docs/paper/figures/scripts/README.md)。

## 新实验与历史复现

正式运行入口仍为 `./scripts/run_benchmark.sh`。完整准备过程见
[服务器手册](docs/SERVER_RUNBOOK_PYTHON200.md) 与 [评测协议](docs/EVALUATION.md)。
当前目录经过历史 payload 归档，不能仅凭 catalog 检查通过就假定 Docker、源码、wheels 和原始 freeze 已就绪。

```bash
PYTHONPATH=harness python -B -m featureliftbench.cli catalog check
PYTHONPATH=harness python -B -m featureliftbench.cli catalog list
```

实验配置仍由 benchmark × agent × method 决定。
历史 `python200_hard` suite 包含 200 题；当前论文只选其中固定 150 题。
运行前明确任务选择、源与镜像身份、OpenHands 配置、信息臂和单次 attempt 政策。
不将历史方法或其他 runtime 分数并入当前 Main 表，也不通过重跑已完成失败改变保留结果。

源码与原始结果恢复状态见 [项目地图](docs/PROJECT_MAP.md) 和
[实验恢复说明](experiments/paper_results_20260913/README.md)。
