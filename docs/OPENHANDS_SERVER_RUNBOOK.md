# OpenHands Server Runbook

This is the canonical server procedure for evaluating FeatureLiftBench with OpenHands.

Current policy:

- OpenHands is the main evaluated agent.
- Agent runs in `featureliftbench-agent:latest`.
- Eval runs in `featureliftbench-eval:latest`.
- Follow the graduation path: preflight → pilot5 → optional fixed slice → main 100-task suite.
- Results are official only when token/context evidence is either verified or explicitly marked.
- **Do not start a main suite from a laptop without confirming budget, disk (~50GB+), and `tmux`.** Run the main 100-task suite on a server after the gates below pass.

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

**Every machine** (Mac aarch64 or Linux amd64) must rebuild the eval image after pulling dependency changes. The eval image bakes in `benchmark/vendor-wheels/` and `harness/config/benchmark_requirements.lock`.

On a fresh clone or after dependency updates, ensure vendor wheels match the host you will run on:

```bash
PYTHONPATH=harness python harness/scripts/bootstrap_vendor_wheels.py
# If wheels are missing or stale:
PYTHONPATH=harness python harness/scripts/bootstrap_vendor_wheels.py --force
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

## 3.5 Dependency Gate (before main 100-task suite)

Agent eval installs submission dependencies from offline wheels. Run this on the server **after** `git pull` and **before** the main suite:

```bash
PYTHONPATH=harness python harness/scripts/audit_task_dependencies.py
```

Expected: `Audited 100 tasks: 100 ok, 0 with issues`.

If audit fails, sync locks from metadata (maintainers only):

```bash
PYTHONPATH=harness python harness/scripts/sync_task_locks.py --apply
PYTHONPATH=harness python harness/scripts/bootstrap_vendor_wheels.py --force
./docker/build_eval_image.sh featureliftbench-eval:latest
PYTHONPATH=harness python harness/scripts/audit_task_dependencies.py
```

Optional oracle regression (maintainer-facing; does **not** block Agent runs):

```bash
PYTHONPATH=harness python harness/scripts/verify_all_oracles.py --docker \
  --json /tmp/oracle-docker.json
```

Current Docker oracle pass rate may be below 100/100; Agent submissions are scored independently.

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

## 6. Main Suite (100 tasks)

Only run the main suite after preflight, pilot5, and `audit_task_dependencies` are clean.

Run inside `tmux` on the server. Expect **1–3 days** at `NUM_WORKERS=1` and **~200M+ tokens** for a full Flash run.

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

Detach with `Ctrl-B D`. Reattach with `tmux attach -t flb-main100`.

`run_openhands.sh benchmark/tasks ...` performs:

1. preflight with LLM health check (strict for `benchmark/tasks`),
2. smoke-first on `benchmark/sanity/iniconfig__parse_config__001`,
3. main suite if smoke passes,
4. analysis reports plus `infra-summary.json` / `infra-summary.md` at the end.

Skip smoke only when intentionally debugging:

```bash
FEATURELIFTBENCH_SKIP_SMOKE_FIRST=1 ./run_openhands.sh benchmark/tasks "$OUT"
```

Skip LLM health check only when debugging provider connectivity (not recommended for production):

```bash
FEATURELIFTBENCH_SKIP_LLM_HEALTH_CHECK=1 ./run_openhands.sh benchmark/tasks "$OUT"
```

Resume (validates existing artifacts before continuing):

```bash
RESUME_DIR=experiments/openhands-agent/<main-run-id> \
FEATURELIFTBENCH_AGENT_DOCKER=1 \
FEATURELIFTBENCH_EVAL_DOCKER=1 \
AGENT_PROFILE=openhands_deepseek_v4_flash \
NUM_WORKERS=1 \
RETRY_RATE_LIMIT=5 \
FEATURELIFTBENCH_OPENHANDS_MAX_STEPS=180 \
FEATURELIFTBENCH_SUITE_TASK_COOLDOWN_SECONDS=15 \
./run_openhands.sh benchmark/tasks
```

Resume is rejected when task directories are incomplete (missing `submission/`, zero `assistant_steps` with nonzero `api_calls`, etc.). Fix or delete corrupted task dirs before retrying.

### Main suite acceptance (`infra_clean`)

When the suite finishes:

```bash
PYTHONPATH=harness python harness/scripts/summarize_suite_infra.py \
  experiments/openhands-agent/<main-run-id>
```

Treat the run as **infrastructure-valid** when `infra-summary.json` has `"infra_clean": true`. Equivalently, from `suite.json`:

- `summary.agent_failures == 0`
- `summary.docker_sandbox_failures == 0`
- `summary.log_limit_failures == 0`
- no `usage_unverified_runs` in infra summary
- `failure_classes` contains only `passed` and/or `model_failed` (plus zero counts for other classes)
- `rate_limited` share acceptable (target **<5%**; increase `FEATURELIFTBENCH_SUITE_TASK_COOLDOWN_SECONDS` if higher)

`model_failed` is a benchmark outcome, not an infrastructure failure.

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
featurelift-analysis.md
infra-summary.json
infra-summary.md
entanglement-coverage.md
run.log                    # if you tee the main command
```

Important fields:

- `agent.usage.exit_status`
- `agent.usage.api_calls`
- `agent.usage.assistant_steps`
- `agent.usage.context_audit.usage_unverified`
- `agent.usage.context_audit.context_violation`
- `evaluation.docker_sandbox_error`
- `summary.failure_classes`
- `task_cooldown_seconds` (suite-level inter-task throttle setting)
- `infra-summary.json` → `infra_clean`

## 8. Resource Defaults

Recommended starting point:

```bash
export FEATURELIFTBENCH_AGENT_DOCKER_MEMORY=8g
export FEATURELIFTBENCH_AGENT_DOCKER_CPUS=2
export FEATURELIFTBENCH_AGENT_DOCKER_PIDS=512
export FEATURELIFTBENCH_DOCKER_EVAL_TIMEOUT_SECONDS=600
export FEATURELIFTBENCH_COMMAND_OUTPUT_LIMIT_BYTES=8388608
export FEATURELIFTBENCH_OPENHANDS_MAX_STEPS=180
export FEATURELIFTBENCH_SUITE_TASK_COOLDOWN_SECONDS=15
export RETRY_RATE_LIMIT=5
```

For pilot5 and small slices, `FEATURELIFTBENCH_OPENHANDS_MAX_STEPS=120` is fine. Use **180** for the main 100-task suite.

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
| `rate_limited` | Lower workers, increase `FEATURELIFTBENCH_SUITE_TASK_COOLDOWN_SECONDS`, or use provider-side quota |
| `eval dependency_install failed` / missing wheel | Run `audit_task_dependencies.py`; rebuild eval image after `bootstrap_vendor_wheels.py` |
| resume blocked by validate_suite_resume | Delete or rerun corrupted task dirs listed in stderr |
| `docker_sandbox_error=true` | Treat as infra failure; inspect `eval/result.json` and Docker logs |
| `usage_unverified=true` | Provider omitted usage or proxy disabled; do not use as formal context evidence |
| `log_limit_exceeded` | Inspect `agent/openhands_stdout.log`; reduce verbosity or raise output limit |

More historical context is in [OPENHANDS_RUN_PITFALLS.md](OPENHANDS_RUN_PITFALLS.md).
