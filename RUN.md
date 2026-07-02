# FeatureLiftBench Runbook

Current mainline: **OpenHands + agent Docker + eval Docker**.

For detailed server instructions, read [docs/OPENHANDS_SERVER_RUNBOOK.md](docs/OPENHANDS_SERVER_RUNBOOK.md) and [docs/SERVER_DEPLOY.md](docs/SERVER_DEPLOY.md). This file is a command cheat sheet.

## 1. Setup

```bash
cd /path/to/FeatureLiftBench
PYTHON=python3.12 ./setup.sh
cp .env.example .env
nano .env

export PYTHONPATH=$PWD/harness
```

Build Docker images (run on **each machine** after pull):

```bash
PYTHONPATH=harness python harness/scripts/bootstrap_vendor_wheels.py

FEATURELIFTBENCH_AGENT_PYTHON_BASE=python:3.12-slim \
FEATURELIFTBENCH_INSTALL_OPENHANDS=1 \
./docker/build_agent_image.sh featureliftbench-agent:latest

./docker/build_eval_image.sh featureliftbench-eval:latest
```

## 2. Preflight

```bash
PYTHONPATH=harness python harness/scripts/preflight.py \
  --bootstrap \
  --agent openhands-agent \
  --agent-profile openhands_deepseek_v4_flash \
  --docker-suite \
  --llm-health-check \
  --strict \
  --output-dir experiments/openhands-agent/preflight
```

Preflight rejects placeholder keys, bad Docker images, local vLLM URLs without host networking, and conflicting shell-env overrides in strict mode. DeepSeek health check uses `normalize_api_model_name` (`deepseek/deepseek-v4-flash` → `deepseek-v4-flash` for the probe only).

## 2.5 Dependency gate (before main suite)

```bash
PYTHONPATH=harness python harness/scripts/audit_task_dependencies.py
```

## 3. Pilot5

```bash
AGENT_PROFILE=openhands_deepseek_v4_flash \
NUM_WORKERS=1 \
FEATURELIFTBENCH_OPENHANDS_MAX_STEPS=120 \
./run_openhands_pilot5.sh
```

Output:

```text
experiments/openhands-agent/<RUN_ID>/
  sanity3/
  batch2/
  pilot5-summary.json
  pilot5-summary.md
```

Resume the same pilot:

```bash
RUN_ID=<same-run-id> \
RESUME=1 \
AGENT_PROFILE=openhands_deepseek_v4_flash \
NUM_WORKERS=1 \
FEATURELIFTBENCH_OPENHANDS_MAX_STEPS=120 \
./run_openhands_pilot5.sh
```

Pilot5 is clean enough to scale only if:

- `total == 5`
- `agent_failures == 0`
- `docker_sandbox_failures == 0`
- `log_limit_failures == 0`
- no `agent_setup_failed` or `eval_infra_failed`

Model failures are allowed in pilot; they are benchmark outcomes, not infrastructure failures.

## 4. Main Suite (100 tasks)

Run on a server in `tmux`. `run_openhands.sh benchmark/tasks ...` automatically performs preflight and a smoke-first sanity task unless `FEATURELIFTBENCH_SKIP_SMOKE_FIRST=1`.

```bash
tmux new -s flb-main100

OUT=experiments/openhands-agent/main-$(date +%Y%m%d-%H%M%S)

FEATURELIFTBENCH_AGENT_DOCKER=1 \
FEATURELIFTBENCH_EVAL_DOCKER=1 \
AGENT_PROFILE=openhands_deepseek_v4_flash \
NUM_WORKERS=1 \
RETRY_RATE_LIMIT=5 \
FEATURELIFTBENCH_OPENHANDS_MAX_STEPS=180 \
FEATURELIFTBENCH_SUITE_TASK_COOLDOWN_SECONDS=15 \
./run_openhands.sh benchmark/tasks "$OUT" 2>&1 | tee "$OUT/run.log"
```

Resume (validates artifacts first):

```bash
RESUME_DIR=experiments/openhands-agent/<run-id> \
FEATURELIFTBENCH_AGENT_DOCKER=1 \
FEATURELIFTBENCH_EVAL_DOCKER=1 \
AGENT_PROFILE=openhands_deepseek_v4_flash \
NUM_WORKERS=1 \
RETRY_RATE_LIMIT=5 \
FEATURELIFTBENCH_OPENHANDS_MAX_STEPS=180 \
FEATURELIFTBENCH_SUITE_TASK_COOLDOWN_SECONDS=15 \
./run_openhands.sh benchmark/tasks
```

## 5. Inspect Results

Per task:

```text
<OUT>/<task_id>/run.json
<OUT>/<task_id>/agent/usage.json
<OUT>/<task_id>/agent/context_audit.jsonl
<OUT>/<task_id>/agent/openhands_events.jsonl
<OUT>/<task_id>/eval/result.json
```

Suite:

```text
<OUT>/suite.json
<OUT>/benchmark-analysis.md
<OUT>/featurelift-analysis.md
<OUT>/infra-summary.json
<OUT>/infra-summary.md
<OUT>/entanglement-coverage.md
```

Useful checks:

```bash
PYTHONPATH=harness python harness/scripts/summarize_suite_infra.py "$OUT"
PYTHONPATH=harness python harness/scripts/analyze_benchmark_suite.py "$OUT"
PYTHONPATH=harness python harness/scripts/report_entanglement_coverage.py --suite-dir "$OUT"
```

Infrastructure-valid when `infra-summary.json` has `"infra_clean": true`.

Read `suite.json.summary.failure_classes`. Treat these as infrastructure blockers:

- `agent_setup_failed`
- `rate_limited`
- `eval_infra_failed`
- `agent_step_limited`

Treat `model_failed` as a benchmark result.

## 6. Legacy mini-swe-agent

mini-swe-agent append-only runs are legacy baselines. They are not the current long-context mainline because cumulative task histories can exceed model context windows without reliable truncation evidence.

Use old scripts only for controlled ablations or historical comparison.
