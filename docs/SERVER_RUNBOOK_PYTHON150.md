# Server Runbook: hardened Python-150

Last updated: 2026-07-27

This is the canonical procedure for running the latest FeatureLiftBench Python
main benchmark:

> OpenHands + explicitly selected model + Full-Repository / No-Hint Main +
> agent/eval Docker + 150 frozen tasks + one agent attempt per task
> (Functional Pass@1).

The safe entrypoint is:

```bash
./harness/scripts/run_python150_paper.sh <openhands-profile> [run-id]
```

It is plan-only by default. Add `--execute` only after checking credentials,
external data transmission, API quota, and cost.

## 1. Server prerequisites

- Linux server with Docker and enough disk for images, workspaces, and logs.
- Python 3.11+ on the host; Python 3.12 is recommended for OpenHands tooling.
- No GPU is required when the selected model is accessed through an API.
- The model endpoint and credentials must be reachable from the agent
  container.

Suggested resource baseline:

- one worker initially;
- agent container: 8 GiB memory, 2 CPUs;
- eval container: 4 GiB memory, 2 CPUs;
- per-task agent timeout: 3,600 seconds;
- eval network disabled; agent network uses Docker `bridge` by default and
  switches to `host` for a detected local API endpoint.

The runner does not currently enforce an outbound domain allowlist for the
Agent container. Record the resolved network mode and use infrastructure-level
egress controls if the experiment requires model-endpoint-only networking.

## 2. Checkout and bootstrap

### Option A — runnable bundle（推荐：一包部署）

在开发机（oracle + archives 已齐）打包：

```bash
./scripts/build_runnable_bundle.sh
# experiments/bundles/outgoing/FeatureLiftBench-runnable-<stamp>.tar.gz
```

传到服务器后：

```bash
tar -xzf FeatureLiftBench-runnable-*.tar.gz
cd FeatureLiftBench-runnable-*
# 详见包内 BUNDLE.md
PYTHON=python3.12 SKIP_MINI=1 ./setup.sh
cp -n harness/config/agents.example.toml harness/config/agents.toml
# 配置 .env 与 agents.toml
```

该包已含 `benchmark/submissions/*/oracle` 与 `benchmark/sources/archives`，一般**不必**再拷 oracle，也**不必**联网 materialize（仍建议跑 `--check`）。

### Option B — git pull + 本地缓存

First commit and push (or otherwise transfer) the complete benchmark migration
and runner changes from the development machine. A server-side `git pull`
cannot see uncommitted local files. On the server, check out one exact revision
and record it with the experiment:

```bash
git pull --ff-only
git status --short
git rev-parse HEAD
PYTHON=python3.12 SKIP_MINI=1 ./setup.sh
# Oracle is gitignored: unpack a submissions tarball, or use Option A.
python3 scripts/materialize_full_sources.py --workers 8
python3 scripts/materialize_full_sources.py --check
```

`git status --short` should be empty before the run when using a clean git
checkout (Option B). Bundle unpacks (Option A) are not git checkouts.


The formal run uses OpenHands inside the agent image; no host-level OpenHands
or mini-swe-agent installation is required.

Configure `.env` with the variables required by the selected profile. Never
commit `.env`.

Examples:

```dotenv
FEATURELIFTBENCH_API_KEY=...
FEATURELIFTBENCH_API_BASE=...
```

Qwen paper profiles use their corresponding
`VLLM_*_API_KEY` / `VLLM_*_API_BASE` variables declared in
`harness/config/agents.toml`.

## 3. Build the Docker images

Build the agent image with OpenHands on Python 3.12 and the evaluator on the
benchmark Python 3.11 runtime:

```bash
FEATURELIFTBENCH_AGENT_PYTHON_BASE=python:3.12-slim \
FEATURELIFTBENCH_INSTALL_OPENHANDS=1 \
  docker/build_agent_image.sh featureliftbench-agent:latest

docker/build_eval_image.sh featureliftbench-eval:latest
```

The formal runner defaults to these image names.

## 4. Verify the benchmark before spending API budget

```bash
python3 scripts/report_spec_compliance.py benchmark/tasks
python3 scripts/check_task_lifecycle.py
python3 scripts/build_source_registry.py --check
python3 scripts/build_pruned_source_registry.py --check
python3 scripts/materialize_full_sources.py --check
python3 scripts/build_v3_benchmark_freeze.py --check
python3 scripts/audit_v3_main_readiness.py --strict

./harness/scripts/run_python150_paper.sh \
  openhands_deepseek_v4_flash \
  compliant150-flash-main-001
```

The plan must report:

- `Compliance preflight: 150/150 compliant and valid`
- `Verified 132 canonical source archives`
- `Verified v3 benchmark freeze: <freeze-id>`
- `FeatureLiftBench v3 readiness: PASS; tasks 150/150`
- `Selected: 150 main tasks (Python-150)`
- `Arm: Full-Repository / No-Hint Main`
- `Pass metric: Pass@1 (one agent attempt per task)`
- the intended model, profile, images, output directory, and command

No API request is sent in plan mode.

Source archive bytes are reproducible cache assets and are not committed.
`materialize_full_sources.py` fetches only pinned revisions, reconstructs the
132 archives, and verifies archive/tree digests against the tracked registry.
The tracked compactness registry contains only reference measurements, not
Oracle source code.

The active identifier is printed by
`scripts/build_v3_benchmark_freeze.py --check`. Every task `run.json` records
that freeze ID, task/spec/source hashes, actual Agent/Eval Docker image IDs,
model/profile, arm, visibility settings, and resource limits. Record the
checked-out Git commit as an additional transport identifier. Independent human
review is not an experiment or release gate.

## 5. Run one end-to-end smoke task

Before the 150-task run, test the same profile and Docker images on one
compliant task:

```bash
export FEATURELIFTBENCH_MOUNT_PUBLIC_TESTS=0
export FEATURELIFTBENCH_PROMPT_STYLE=standard
export FEATURELIFTBENCH_OPENHANDS_MAX_STEPS=120

PYTHONPATH=harness .venv/bin/python -B -m featureliftbench.cli run-agent \
  benchmark/tasks \
  --agent openhands-agent \
  --agent-config harness/config/agents.toml \
  --agent-profile openhands_deepseek_v4_flash \
  --agent-command "openhands --headless --override-with-envs --exit-without-confirmation -f {prompt_file} --json" \
  --no-agent-public-tests \
  --no-agent-source-hints \
  --prompt-style standard \
  --source-context full_repository \
  --env-file .env \
  --num-workers 1 \
  --timeout-seconds 3600 \
  --extra-agent-passes 0 \
  --max-task-attempts 1 \
  --retry-rate-limit 5 \
  --agent-docker \
  --agent-docker-image featureliftbench-agent:latest \
  --eval-docker \
  --eval-docker-image featureliftbench-eval:latest \
  --task-id arrow__parse_format_core__001 \
  --output experiments/smoke/compliant150-openhands-main
```

Check its `run.json`:

- `agent_backend == "docker"`
- `eval_backend == "docker"`
- `ablation.ablation_arm == "main"`
- `ablation.mount_public_tests == false`
- `ablation.expose_source_hints == false`
- `source.snapshot_scope == "full_tracked_tree"`
- `benchmark_freeze.freeze_id` equals the active v3 freeze
- workspace has no top-level `public_tests/` or `hidden_tests/`
- evaluator result exists under `eval/result.json`

A benchmark failure is acceptable for smoke; infrastructure, missing
submission, context-policy, or Docker failures are not.

## 6. Launch the full 150-task run

Plan first:

```bash
./harness/scripts/run_python150_paper.sh \
  openhands_deepseek_v4_flash \
  compliant150-deepseek-v4-flash-main-001
```

Then enter `tmux` and execute the same explicit profile and run ID:

```bash
tmux new -s flb150

./harness/scripts/run_python150_paper.sh \
  openhands_deepseek_v4_flash \
  compliant150-deepseek-v4-flash-main-001 \
  --workers 1 \
  --execute
```

This performs 150 external model tasks over canonical complete source
workspaces. Rate-limit retries only recover API
infrastructure failures; `--extra-agent-passes 0 --max-task-attempts 1` keeps
the benchmark metric at one agent attempt per task, including after resume.

The runner deliberately overrides any workstation-specific executable path in
the profile and invokes `openhands` from the agent container's `PATH`.

Outputs are written to:

```text
experiments/python/openhands/<model-slug>/<run-id>/
```

Do not reuse an output directory for a different model, arm, task revision, or
prompt configuration.

## 7. Monitor the run

In another shell:

```bash
bash harness/scripts/check_run_health.sh \
  experiments/python/openhands/<model-slug>/<run-id>
```

Useful artifacts:

- `suite.json`: incremental checkpoint and final suite summary
- `<task_id>/run.json`: resolved model, arm, spec hash, agent/eval status
- `<task_id>/agent/`: OpenHands trajectory and logs
- `<task_id>/eval/result.json`: functional gate and compactness result

Do not start a second runner against the same output directory.

## 8. Resume after interruption

Use the exact same profile, images, and output directory:

```bash
./harness/scripts/run_python150_paper.sh \
  openhands_deepseek_v4_flash \
  --resume experiments/python/openhands/<model-slug>/<run-id> \
  --workers 1 \
  --execute
```

Resume retains every task that already has a completed `run.json`—including a
failed result—and runs only tasks with no completed attempt. Do not create a
new run ID for an interrupted suite.

## 9. Completion and acceptance checks

The runner automatically invokes:

```bash
PYTHONPATH=harness .venv/bin/python \
  harness/scripts/analyze_benchmark_suite.py <suite-dir>

PYTHONPATH=harness .venv/bin/python \
  harness/scripts/report_entanglement_coverage.py --suite-dir <suite-dir>
```

Before freezing a result, confirm:

1. 150 selected tasks and 150 final run records.
2. Every missing submission is recorded as a model outcome; there are zero
   missing run records or unexplained transport losses.
3. Zero agent/eval Docker infrastructure failures.
4. Every run records test-blind Main, evaluator tests not mounted, standard prompt, model,
   task revision, and spec hash.
5. Pass@1 comes from evaluator `functional_gate`, not OpenHands `run_status`.
6. Failed task IDs and root failure classes are preserved.
7. The result records the active v3 policy/freeze; it is not mixed with
   `mixed_snapshot_v1` or other historical scores.

Independent human review is not a benchmark release gate. A model run also
does not turn AI-assisted annotations into human gold.

## 10. Other model profiles

Use the same runner and change only the explicit profile:

```bash
./harness/scripts/run_python150_paper.sh \
  openhands_qwen3_6_27b_fp8_paper \
  compliant150-qwen27b-main-001
```

Common configured profiles:

- `openhands_deepseek_v4_flash`
- `openhands_qwen3_6_27b_fp8_paper`
- `openhands_qwen3_6_35b_a3b_fp8_paper`
- `openhands_qwen3_coder_30b_paper`

For a new model, add an OpenHands profile to
`harness/config/agents.toml` with its model name, credential variable names,
context window, output reserve, and `openhands_command`; plan mode will reject
unknown or non-OpenHands profiles before any API call.
