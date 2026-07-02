# OpenHands Server Runbook

This is the canonical server procedure for evaluating FeatureLiftBench with OpenHands.

Current policy:

- OpenHands is the main evaluated agent.
- Agent runs in `featureliftbench-agent:latest`.
- Eval runs in `featureliftbench-eval:latest`.
- Start with pilot slices; do not jump directly to 50/100 tasks.
- Results are official only when token/context evidence is either verified or explicitly marked.

## 1. Setup

```bash
git clone git@github.com:CCChz233/FeatureLiftBench.git
cd FeatureLiftBench

PYTHON=python3.12 ./setup.sh
source .venv/bin/activate
export PYTHONPATH=$PWD/harness

cp .env.example .env
nano .env
```

Minimum `.env` for DeepSeek Flash:

```bash
FEATURELIFTBENCH_API_KEY=<real-key>
FEATURELIFTBENCH_API_BASE=https://api.deepseek.com/v1
```

Do not commit `.env`.

## 2. Docker Images

OpenHands needs Python 3.12+ in the agent image:

```bash
FEATURELIFTBENCH_AGENT_PYTHON_BASE=python:3.12-slim \
FEATURELIFTBENCH_INSTALL_OPENHANDS=1 \
./docker/build_agent_image.sh featureliftbench-agent:latest

./docker/build_eval_image.sh featureliftbench-eval:latest
```

Check:

```bash
docker info
docker image inspect featureliftbench-agent:latest >/dev/null
docker image inspect featureliftbench-eval:latest >/dev/null
```

## 3. Preflight

```bash
PYTHONPATH=harness python harness/scripts/preflight.py \
  --bootstrap \
  --agent openhands-agent \
  --agent-profile openhands_deepseek_v4_flash \
  --docker-suite \
  --llm-health-check \
  --strict \
  --output-dir experiments/openhands-agent/preflight-$(date +%Y%m%d-%H%M%S)
```

Preflight checks:

- Python version.
- Docker daemon and images.
- OpenHands CLI inside the agent image.
- Placeholder API keys.
- Shell env overriding `.env`.
- Local vLLM URL with non-host Docker network.
- One minimal OpenAI-compatible chat request when health check is enabled.
  Preflight normalizes provider model names via `normalize_api_model_name` (for example
  `deepseek/deepseek-v4-flash` in `agents.toml` becomes `deepseek-v4-flash` for the
  health-check request). OpenHands/LiteLLM still use the profile model string as configured.

For local vLLM with `127.0.0.1`/`localhost` API base:

```bash
export FEATURELIFTBENCH_AGENT_DOCKER_NETWORK=host
```

## 4. Pilot5

Run inside `tmux` or another session manager.

```bash
tmux new -s flb-openhands-pilot5

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

Resume:

```bash
RUN_ID=<same-run-id> \
RESUME=1 \
AGENT_PROFILE=openhands_deepseek_v4_flash \
NUM_WORKERS=1 \
FEATURELIFTBENCH_OPENHANDS_MAX_STEPS=120 \
./run_openhands_pilot5.sh
```

Pilot5 acceptance:

- `pilot5-summary.json` exists.
- `summary.total == 5`.
- `summary.agent_failures == 0`.
- `summary.docker_sandbox_failures == 0`.
- `summary.log_limit_failures == 0`.
- no `agent_setup_failed`, `rate_limited`, or `eval_infra_failed`.

`model_failed` is a benchmark outcome, not an infrastructure failure.

## 5. Small Fixed Slice

After pilot5 is infrastructure-clean, run a fixed 5-10 task slice:

```bash
OUT=experiments/openhands-agent/slice10-$(date +%Y%m%d-%H%M%S)

PYTHONPATH=harness python -B -m featureliftbench.cli run-agent benchmark/tasks \
  --agent openhands-agent \
  --agent-config harness/config/agents.toml \
  --agent-profile openhands_deepseek_v4_flash \
  --env-file .env \
  --agent-docker \
  --eval-docker \
  --num-workers 1 \
  --retry-rate-limit 1 \
  --output "$OUT" \
  --task-id arrow__parse_format_core__001 \
  --task-id bleach__sanitize_core__001
```

Use fixed task IDs, not random samples, so runs are reproducible.

## 6. Main Suite

Only run the main suite after preflight, pilot5, and a small slice are clean.

```bash
OUT=experiments/openhands-agent/main-$(date +%Y%m%d-%H%M%S)

FEATURELIFTBENCH_AGENT_DOCKER=1 \
FEATURELIFTBENCH_EVAL_DOCKER=1 \
AGENT_PROFILE=openhands_deepseek_v4_flash \
NUM_WORKERS=1 \
RETRY_RATE_LIMIT=1 \
FEATURELIFTBENCH_OPENHANDS_MAX_STEPS=120 \
./run_openhands.sh benchmark/tasks "$OUT"
```

`run_openhands.sh benchmark/tasks ...` performs:

1. preflight with LLM health check,
2. smoke-first on `benchmark/sanity/iniconfig__parse_config__001`,
3. main suite if smoke passes.

Skip smoke only when intentionally debugging:

```bash
FEATURELIFTBENCH_SKIP_SMOKE_FIRST=1 ./run_openhands.sh benchmark/tasks "$OUT"
```

Resume:

```bash
RESUME_DIR=experiments/openhands-agent/<main-run-id> \
FEATURELIFTBENCH_AGENT_DOCKER=1 \
FEATURELIFTBENCH_EVAL_DOCKER=1 \
AGENT_PROFILE=openhands_deepseek_v4_flash \
./run_openhands.sh benchmark/tasks
```

## 7. Outputs

Per task:

```text
run.json
agent/usage.json
agent/context_audit.jsonl
agent/openhands_events.jsonl
agent/openhands_stdout.log
agent/openhands_stderr.log
eval/result.json
```

Suite:

```text
suite.json
benchmark-analysis.md
entanglement-coverage.md
```

Important fields:

- `agent.usage.exit_status`
- `agent.usage.api_calls`
- `agent.usage.assistant_steps`
- `agent.usage.context_audit.usage_unverified`
- `agent.usage.context_audit.context_violation`
- `evaluation.docker_sandbox_error`
- `summary.failure_classes`

## 8. Resource Defaults

Recommended starting point:

```bash
export FEATURELIFTBENCH_AGENT_DOCKER_MEMORY=8g
export FEATURELIFTBENCH_AGENT_DOCKER_CPUS=2
export FEATURELIFTBENCH_AGENT_DOCKER_PIDS=512
export FEATURELIFTBENCH_DOCKER_EVAL_TIMEOUT_SECONDS=600
export FEATURELIFTBENCH_COMMAND_OUTPUT_LIMIT_BYTES=8388608
export FEATURELIFTBENCH_OPENHANDS_MAX_STEPS=120
```

Start with `NUM_WORKERS=1`. Increase only after rate limits and infrastructure failures are understood.

## 9. Failure Classes

Use `suite.json.summary.failure_classes`:

| Class | Meaning |
| --- | --- |
| `passed` | Task passed eval |
| `model_failed` | Agent produced a submission, eval failed normally |
| `missing_submission` | Agent ended without valid submission |
| `agent_setup_failed` | Agent did not actually reach the model/tool loop |
| `rate_limited` | Provider/API throttling |
| `eval_infra_failed` | Docker/evaluator infrastructure failure |
| `agent_step_limited` | OpenHands exceeded configured step cap |
| `invalid_task` | Task directory/spec invalid |

Do not mix infrastructure failures into model capability conclusions.

## 10. Troubleshooting

| Symptom | Action |
| --- | --- |
| `openhands CLI not found` | Rebuild agent image with Python 3.12 and `FEATURELIFTBENCH_INSTALL_OPENHANDS=1` |
| preflight rejects key | Replace placeholder key; do not use `sk-...`, `your-key`, `changeme`, etc. |
| local vLLM unreachable from Docker | Set `FEATURELIFTBENCH_AGENT_DOCKER_NETWORK=host` |
| `api_calls == 0` | Check `.env`, profile, model name, and preflight health check |
| `rate_limited` | Lower workers, increase retry spacing, or use provider-side quota |
| `docker_sandbox_error=true` | Treat as infra failure; inspect `eval/result.json` and Docker logs |
| `usage_unverified=true` | Provider omitted usage or proxy disabled; do not use as formal context evidence |
| `log_limit_exceeded` | Inspect `agent/openhands_stdout.log`; reduce verbosity or raise output limit |

More historical context is in [OPENHANDS_RUN_PITFALLS.md](OPENHANDS_RUN_PITFALLS.md).
