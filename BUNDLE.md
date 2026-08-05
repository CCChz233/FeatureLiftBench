# FeatureLiftBench v3 frozen release

> **Documentation status: reference · Last verified: 2026-08-04**

Built: 20260801-ready
Base ref: 8438e3a3c05e9c8ed65a835f42321c7cf07d5977
Freeze ref: 8fc6c11
Freeze id: 846b814726217623fa205cb7688bee61e6c21c43efda1ebd05e79b5ed8cb4fbd
Oracle dirs: 150
Source archives: 132

This is the mechanically reproducible Python External-150 Full-Repository /
No-Hint release. It intentionally excludes machine-local `.env` and
`harness/config/agents.toml`.

The GitHub branch contains the versioned benchmark code. The companion full
bundle contains the 132 source archives and 150 Python oracle directories and
is transferred separately for server runs so that large immutable assets do
not become permanent Git history.

## Server quick start

```bash
cd /data1/FeatureLiftBench/experiments/FeatureLiftBench-v3-846-20260801-ready
PYTHON=python3 SKIP_MINI=1 ./setup.sh
```

Add the server API credentials to `.env`, then review
`harness/config/agents.toml`. Neither machine-local file is committed.

Build the two runtime images:

```bash
FEATURELIFTBENCH_AGENT_PYTHON_BASE=python:3.12-slim \
FEATURELIFTBENCH_INSTALL_OPENHANDS=1 \
  docker/build_agent_image.sh featureliftbench-agent:latest
docker/build_eval_image.sh featureliftbench-eval:latest
```

Run the no-API plan gate first, then start the experiment:

```bash
./harness/scripts/run_python150_paper.sh \
  openhands_deepseek_v4_flash server-python150-plan

./harness/scripts/run_python150_paper.sh \
  openhands_deepseek_v4_flash server-python150-run \
  --workers 4 --timeout 3600 --execute
```

Use a worker count appropriate for server CPU, memory, Docker capacity, and
provider rate limits. See `docs/SERVER_RUNBOOK_V2_PYTHON150.md` for resuming,
monitoring, and collecting results.
