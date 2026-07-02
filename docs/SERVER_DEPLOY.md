# Server Deploy

Current server mainline is **OpenHands**, not mini-swe-agent.

Use [OPENHANDS_SERVER_RUNBOOK.md](OPENHANDS_SERVER_RUNBOOK.md) for the full procedure. This file is a **server checklist** for the 100-task main suite.

## Quick Checklist (Linux server)

```bash
git clone git@github.com:CCChz233/FeatureLiftBench.git
cd FeatureLiftBench
git pull   # if updating

PYTHON=python3.12 ./setup.sh
source .venv/bin/activate
export PYTHONPATH=$PWD/harness

cp .env.example .env
nano .env   # FEATURELIFTBENCH_API_KEY, FEATURELIFTBENCH_API_BASE
```

### 1. Vendor wheels + Docker images

```bash
PYTHONPATH=harness python harness/scripts/bootstrap_vendor_wheels.py
# After dependency changes or on a new architecture:
# PYTHONPATH=harness python harness/scripts/bootstrap_vendor_wheels.py --force

FEATURELIFTBENCH_AGENT_PYTHON_BASE=python:3.12-slim \
FEATURELIFTBENCH_INSTALL_OPENHANDS=1 \
./docker/build_agent_image.sh featureliftbench-agent:latest

./docker/build_eval_image.sh featureliftbench-eval:latest
```

### 2. Preflight (must pass)

```bash
PYTHONPATH=harness python harness/scripts/preflight.py \
  --bootstrap \
  --agent openhands-agent \
  --agent-profile openhands_deepseek_v4_flash \
  --docker-suite \
  --llm-health-check \
  --strict \
  --output-dir experiments/openhands-agent/preflight-$(date +%Y%m%d)
```

### 3. Dependency gate (must pass before main suite)

```bash
PYTHONPATH=harness python harness/scripts/audit_task_dependencies.py
# Expected: Audited 100 tasks: 100 ok, 0 with issues
```

### 4. Optional: pilot5

```bash
tmux new -s flb-pilot5

AGENT_PROFILE=openhands_deepseek_v4_flash \
NUM_WORKERS=1 \
FEATURELIFTBENCH_OPENHANDS_MAX_STEPS=120 \
./run_openhands_pilot5.sh
```

### 5. Main 100-task suite (tmux)

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

Detach: `Ctrl-B D`. Reattach: `tmux attach -t flb-main100`.

### 6. Resume (if interrupted)

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

Resume runs `validate_suite_resume.py` first; fix any reported task dirs before retrying.

### 7. Acceptance

```bash
PYTHONPATH=harness python harness/scripts/summarize_suite_infra.py \
  experiments/openhands-agent/<main-run-id>
```

Infrastructure-valid when `infra_clean=true`. See [OPENHANDS_SERVER_RUNBOOK.md](OPENHANDS_SERVER_RUNBOOK.md) §6 for full criteria.

## Planning

| Item | Estimate |
| --- | --- |
| Time | 1–3 days at `NUM_WORKERS=1` |
| Tokens | ~200M+ (DeepSeek Flash, varies by model/steps) |
| Disk | Reserve **50GB+** under `experiments/` |
| Session | Always use `tmux`; do not rely on SSH without detach |

## Stability Rules

- Run in `tmux` or an equivalent session manager.
- Keep `NUM_WORKERS=1` until rate limits and memory are measured.
- Do not run two suites into the same output directory.
- Treat `run-agent` exit code `1` as benchmark failure, not infrastructure crash.
- Treat exit code `>=2` as harness/config failure.
- Report `agent_setup_failed`, `rate_limited`, `eval_infra_failed`, and `agent_step_limited` separately from `model_failed`.

## Legacy mini-swe-agent

The old server flow used `run.sh` or `run-batch1-docker-flash.sh` with mini-swe-agent. Keep it only for historical comparison or controlled ablations.

Reason: append-only mini-swe-agent trajectories can consume millions of cumulative tokens, while model context windows are 128k-1M. Old runs did not reliably record whether prompts exceeded context or were truncated, so they are not the current main evidence for long-context feature extraction.

## Related Docs

- [OPENHANDS_SERVER_RUNBOOK.md](OPENHANDS_SERVER_RUNBOOK.md) — canonical runbook
- [../RUN.md](../RUN.md) — command cheat sheet
- [SETUP.md](SETUP.md) — harness setup and eval details
- [limitations.md](limitations.md) — known limitations
- [OPENHANDS_RUN_PITFALLS.md](OPENHANDS_RUN_PITFALLS.md) — historical pitfalls
