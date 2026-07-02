# OpenHands Server Runbook

> **内容已合并到 [RUN.md](../RUN.md) 与 [ARCHITECTURE.md](ARCHITECTURE.md)。** 本文仅保留服务器约束摘要。

## 何时用服务器

- 全量 `main`（~100 题）应在服务器 `tmux` 中跑，预留 **50GB+** `experiments/` 磁盘。
- 笔记本适合：smoke、pilot5、单题调试。

## 毕业路径

```text
featureliftbench setup → smoke → pilot5 → main
```

无强制门禁；建议 pilot5 `docker_sandbox_failures==0` 后再 main。

## 服务器检查清单

1. `PYTHON=python3.12 ./setup.sh` + `pip install -e .`
2. `flb.local.toml` + `.env`
3. 重建 agent/eval Docker 镜像
4. `featureliftbench setup` 通过
5. （main 前）`audit_task_dependencies.py` → 100 ok
6. `tmux` 内 `featureliftbench run --suite main`

## 稳定性

- `NUM_WORKERS=1`；main 建议 `max_steps=180`，`task_cooldown_seconds=15`（写在 `flb.local.toml`）
- 勿对同一 output 目录并行两次 run
- `run-agent` exit `1` = 基准失败；`>=2` = 基础设施/配置失败

完整命令见 [RUN.md](../RUN.md)。
