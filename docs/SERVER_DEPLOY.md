# Server Deploy

> **已合并到 [RUN.md](../RUN.md)。** 以下为服务器速查。

```bash
cd FeatureLiftBench
PYTHON=python3.12 ./setup.sh && source .venv/bin/activate && pip install -e .
cp flb.local.toml.example flb.local.toml && cp .env.example .env
export PYTHONPATH=$PWD/harness

# Docker — 见 RUN.md §1
featureliftbench setup

# 可选：main 前
PYTHONPATH=harness python harness/scripts/audit_task_dependencies.py

tmux new -s flb-main100
featureliftbench smoke --output experiments/openhands-agent/smoke-$(date +%Y%m%d-%H%M%S)
MAIN_OUT=experiments/openhands-agent/main-$(date +%Y%m%d-%H%M%S)
mkdir -p "$MAIN_OUT"
featureliftbench run --suite main --max-steps 180 --output "$MAIN_OUT" | tee "$MAIN_OUT/run.log"
```

| 项 | 建议 |
|----|------|
| 时间 | 1–3 天（`NUM_WORKERS=1`） |
| 磁盘 | 50GB+ |
| 会话 | 必须 `tmux` |

验收：`summarize_suite_infra.py` → `infra_clean=true`。

详见 [RUN.md](../RUN.md)、[ARCHITECTURE.md](ARCHITECTURE.md)。
