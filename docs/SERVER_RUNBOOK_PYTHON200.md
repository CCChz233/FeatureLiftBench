# Server Runbook: Python-200 Main

> **Status: current · Last verified: 2026-08-18**  
> Condition: Full-Repository / No-Hint, benchmark tests hidden, one task attempt.
> Launch Main or current V1 only. Rescue+ / Lite checker arms are discontinued.

## 1. Prerequisites

- Linux server with Docker and enough disk for source archives, images and task workspaces.
- Python 3.11 or newer for the harness launcher.
- A configured `.env` and `harness/config/agents.toml` profile.
- Runnable bundle or Git checkout containing `benchmark/python200_tasks/`, sources and wheels.
- Explicitly pinned agent and evaluator images for paper runs.

Do not print `.env`, API keys, or the full private agent configuration into logs.

## 2. Verify the Checkout

```bash
git rev-parse HEAD
python3 benchmark/selection/scripts/materialize_python200_release.py --check
python3 benchmark/selection/scripts/finalize_python200_source_registry.py --check
python3 benchmark/selection/scripts/finalize_python200_dependencies.py --check
python3 benchmark/selection/scripts/audit_python200_balance.py --check
python3 benchmark/selection/scripts/audit_python200_wheels.py --python-version 311
python3 benchmark/selection/scripts/check_python200_baseline_freeze.py
python3 scripts/materialize_full_sources.py --check
```

The official runner executes these checks again. Do not bypass them for a formal run.

## 3. Build and Pin Images

Build the repository's agent and evaluator images using the release instructions, then record
their immutable image identities:

```bash
docker image inspect featureliftbench-agent:latest --format '{{.Id}}'
docker image inspect featureliftbench-eval:latest --format '{{.Id}}'
```

Use those identities explicitly in every model run. If extending an existing baseline, use the
same agent/evaluator identities or re-evaluate the baseline submissions under the new evaluator.

## 4. Plan-Only Preflight

```bash
./harness/scripts/run_python200_paper.sh \
  <openhands-profile> \
  python200-plan \
  --workers <n> \
  --agent-image <agent-image-id> \
  --eval-image <eval-image-id>
```

Expected selection is the exact frozen unified suite. No model calls occur without `--execute`.

## 4b. Current V1 cost arm (Main + 2M cap)

Canonical V1 is Main protocol plus a 2M total-token cap. It is **not** the
retired `contract_closure_gate_lite_v1*` checker/repair protocol. Spec:
[METHOD_V1.md](METHOD_V1.md).

Plan-only:

```bash
./harness/scripts/run_python200_paper.sh \
  openhands_deepseek_v4_flash_v1 \
  python200-v1-plan \
  --workers <n> \
  --agent-image <agent-image-id> \
  --eval-image <eval-image-id>
```

The runner must print `Method arm: v1` and the 120-step / 128k / 2M envelope.

Qwen3.6-35B local four-way shard (50 tasks per replica on `:8030`–`:8033`):

```bash
export FEATURELIFTBENCH_AGENT_DOCKER_NETWORK=host
./logs/start_python200_v1_qwen35b_4shard_tmux.sh
```

Do not share a vLLM port with an in-progress Main run. Merge waits on
`logs/<shard>.done` and writes the unified suite under
`experiments/python/openhands/qwen3.6-35b-a3b-fp8/python200-qwen3.6-35b-a3b-fp8-v1-0817-001/`.

Historical Frozen Lite V1 (45+10) and main-budget Lite V1 profiles remain in
`agents.toml` for replay only. Do not launch them as the current V1 method.

For the frozen Contract Closure Gate Lite V1 **replay**, the runner still
verifies the 2M/45 primary budget, 500k/10 repair budget, and prints
`contract_closure_gate_lite_v1_frozen` as the resolved method arm:

```bash
./harness/scripts/run_python200_paper.sh \
  openhands_deepseek_v4_flash_contract_closure_gate_lite_v1_frozen \
  lite-v1-plan \
  --workers <n> \
  --agent-image <agent-image-id> \
  --eval-image <eval-image-id>
```

## 5. Smoke Before Full Cost

Run one representative task with the same profile and images using the standard CLI. Confirm:

- agent container starts and receives no benchmark tests or source hints;
- source archive materializes;
- submission is saved outside the agent workspace;
- isolated evaluator completes with network disabled;
- `run.json`, `eval/result.json`, usage and image IDs are present.

Do not promote the smoke attempt into Pass@1 of the formal suite.

## 6. Launch Full Python-200

```bash
./harness/scripts/run_python200_paper.sh \
  <openhands-profile> \
  <run-id> \
  --workers <n> \
  --timeout 3600 \
  --agent-image <agent-image-id> \
  --eval-image <eval-image-id> \
  --execute
```

The runner performs strict Docker preflight before model calls and writes under
`experiments/python/openhands/<model>/<run-id>/`.

Lite V1 **main-budget replay** (historical fair-vs-Main, 120 steps; not current V1):

```bash
./harness/scripts/run_python200_paper.sh \
  openhands_deepseek_v4_flash_contract_closure_gate_lite_v1_main_budget \
  python200-deepseek-v4-flash-lite-v1-main-budget-001 \
  --workers <n> \
  --timeout 3600 \
  --agent-image <agent-image-id> \
  --eval-image <eval-image-id> \
  --execute
```

Do not edit the method profile after the plan-only preflight. If any setting
changes, use a new release ID and rerun the smoke before the formal suite.

Lite Rescue、Rescue+ 和 Adaptive Budget V2 已停。不要再跑
`contract_closure_gate_lite_rescue*` profile，也不要把它们标成当前 V1。历史协议见
[archive/methods/](archive/methods/README.md)。当前 cost arm 规范见
[METHOD_V1.md](METHOD_V1.md)。

## 7. Launch External-50 Only

Use this only when a complete baseline exists under identical experiment conditions:

```bash
./harness/scripts/run_python200_paper.sh \
  <openhands-profile> \
  <run-id> \
  --external-only \
  --workers <n> \
  --agent-image <agent-image-id> \
  --eval-image <eval-image-id> \
  --execute
```

The runner enforces exactly 50 selected extension tasks. Preserve baseline and extension as
separate immutable suites; combine them by task ID during analysis.

## 8. Monitor and Resume

Monitor task-level terminal `run.json` files and suite progress without editing results. Resume
an interrupted suite in place:

```bash
./harness/scripts/run_python200_paper.sh \
  <openhands-profile> \
  --resume experiments/python/openhands/<model>/<run-id> \
  --workers <n> \
  --agent-image <agent-image-id> \
  --eval-image <eval-image-id> \
  --execute
```

Add `--external-only` when resuming an External-only suite. Resume may fill tasks without a
terminal attempt; it must not retry completed failures under Pass@1.

## 9. Acceptance and Export

```bash
PYTHONPATH=harness python3 harness/scripts/analyze_benchmark_suite.py <suite-dir>
PYTHONPATH=harness python3 harness/scripts/report_entanglement_coverage.py --suite-dir <suite-dir>
```

Before export, verify exact task coverage, attempt counts, image IDs, context violations, missing
submissions and Functional/completion mismatches. Create a tarball and SHA256 without deleting
the server copy. Paper metrics must be recomputable from per-task `run.json` and
`eval/result.json`.

## 10. Failure Policy

- Infra failure before a valid agent attempt: record and rerun only under the declared exception policy.
- Missing submission after a valid attempt: Functional failure.
- Agent timeout/step limit with a valid submission: evaluate it; process status and Functional status remain separate.
- Context-window violation: retain the result, flag it, and run the predeclared sensitivity procedure.
- Evaluator image mismatch: do not silently merge; attest or re-evaluate saved submissions.

Current blockers and available evidence are listed in [STATUS.md](STATUS.md).
