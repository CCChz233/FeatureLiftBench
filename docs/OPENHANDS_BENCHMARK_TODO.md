# OpenHands Benchmark TODO

This is the active execution plan for the current experiment direction:
use **OpenHands as the evaluated agent** on FeatureLiftBench.

Server execution runbook:
[OPENHANDS_SERVER_RUNBOOK.md](OPENHANDS_SERVER_RUNBOOK.md).

`featurelift-agent` remains useful as a protocol reference/control because it
has exact in-repo usage and context audit machinery, but it is no longer the
main experimental agent for the benchmark question.

## Current Status

- [x] `--agent openhands-agent` is registered in the harness.
- [x] The adapter invokes `python -m featureliftbench.openhands_runner`.
- [x] The wrapper writes `agent/openhands_task.md` with the FeatureLiftBench
  workspace/output contract.
- [x] The wrapper supports OpenHands command templates via `--agent-command`
  or `FEATURELIFTBENCH_OPENHANDS_COMMAND`.
- [x] Profile `openhands_deepseek_v4_flash` ships a pinned headless command
  with `--json` event logging.
- [x] The wrapper maps `OPENAI_*` / `FEATURELIFTBENCH_*` to OpenHands `LLM_*`.
- [x] The wrapper writes standard `agent/usage.json` even when OpenHands is not
  configured.
- [x] The wrapper can merge optional OpenHands usage from
  `agent/openhands_usage.json` (including JSONL post-processing).
- [x] Docker agent image supports optional OpenHands install
  (`FEATURELIFTBENCH_INSTALL_OPENHANDS=1`, Python 3.12 base).
- [x] `run_openhands.sh` provides a one-command sanity suite entrypoint.
- [x] Preflight validates openhands-agent command and runtime availability.
- [x] A real OpenHands + `deepseek/deepseek-v4-flash` smoke task has passed (agent
  stage; eval may still fail on extraction quality).
- [x] OpenHands stdout/stderr capture is bounded and JSON events are split into
  `agent/openhands_events.jsonl`.
- [x] Evaluator defaults to direct `PYTHONPATH` import for
  `submission/featurelifted` and avoids bad editable-install metadata by default.
- [x] Agent env forwarding no longer passes unrelated provider secrets from `.env`.
- [x] `run_openhands_pilot5.sh` writes separate `sanity3/` and `batch2/` suites
  and emits `pilot5-summary.json` / `.md`.
- [x] Local OpenAI-compatible usage proxy records provider `usage` into
  `agent/context_audit.jsonl` and `agent/openhands_usage.json`.
- [ ] Verify proxy-recorded per-call prompt tokens on a live OpenHands run. If the
  provider omits usage fields, runs remain `usage_unverified=true` / pilot class.

## P1: Stable Harness Contract

Goal: make OpenHands runnable through the same FeatureLiftBench CLI/evaluator as
mini-swe-agent and featurelift-agent.

- [x] Add `OpenHandsAgentAdapter`.
- [x] Add `featureliftbench.openhands_runner`.
- [x] Generate an OpenHands prompt file instead of relying on append-only chat
  history inside the harness.
- [x] Preserve the normal submission contract:
  `workspace/submission/featurelifted`.
- [x] Preserve the normal evaluator path and suite aggregation.
- [x] Make missing OpenHands configuration a structured agent failure, not a
  missing usage artifact.

Acceptance:

- `PYTHONPATH=harness python -m unittest harness.tests.test_agent_runner
  harness.tests.test_agent_config harness.tests.test_agent_docker` passes.
- `run.json` can include `agent.usage.agent_name == "openhands-agent"`.

## P2: Real OpenHands Runtime

Goal: choose and pin the actual OpenHands headless command.

- [x] Use OpenHands V1 CLI (`openhands` PyPI package, pinned at 1.16.0).
- [x] Add optional install steps to the agent Docker image
  (`FEATURELIFTBENCH_INSTALL_OPENHANDS=1`).
- [x] Map existing OpenAI-compatible env to OpenHands `LLM_*` variables.
- [x] Consume `agent/openhands_task.md` via `-f {prompt_file}`.
- [x] Submission contract documented in prompt; agent writes under
  `workspace/submission/featurelifted`.

Pinned command (profile default):

```bash
openhands --headless --override-with-envs --exit-without-confirmation \
  -f {prompt_file} --json
```

Build OpenHands agent Docker image:

```bash
FEATURELIFTBENCH_AGENT_PYTHON_BASE=python:3.12-slim \
FEATURELIFTBENCH_INSTALL_OPENHANDS=1 \
./docker/build_agent_image.sh featureliftbench-agent:latest
```

Harness-supported placeholders:

```text
{workspace} {task_file} {submission_dir} {agent_output_dir} {prompt_file} {model} {python}
```

## P3: Usage and Context Audit

Goal: avoid repeating the mini-swe-agent invalidity problem.

- [x] Parse OpenHands `--json` JSONL into `agent/openhands_usage.json`.
- [x] Aggregate prompt/completion tokens when present in event payloads.
- [x] Write 128k-fair context metadata and detect per-call prompt overflow.
- [x] Add local proxy mode for OpenAI-compatible providers so provider usage can
  be audited even when OpenHands JSON events omit token fields.
- [ ] Verify proxy token fields on a live OpenHands run.

If JSONL lacks usage fields, runs remain `usage_unverified=true` (pilot class).

## P3.5: Large-Run Safety Fixes

Goal: make the OpenHands integration safe enough for a 5-10 task server slice
before any 50/100 task run.

- [x] Bound OpenHands stdout/stderr capture with
  `FEATURELIFTBENCH_COMMAND_OUTPUT_LIMIT_BYTES`; terminate the OpenHands process
  group when exceeded.
- [x] Write `agent/usage.json.exit_status = "log_limit_exceeded"` on wrapper log
  limit and count it in suite `log_limit_failures`.
- [x] Stream OpenHands JSONL parsing line by line; skip non-JSON banner/UI text.
- [x] Keep JSON OpenHands events in `agent/openhands_events.jsonl`; keep only
  non-JSON stdout in `agent/openhands_stdout.log`.
- [x] Add prompt constraints discouraging `pyproject.toml` and forbidding
  `setuptools.backends._legacy:_Backend`.
- [x] Avoid forwarding unrelated `.env` secrets into agent Docker.
- [x] Fix pilot5 script so 3 sanity tasks and 2 batch tasks do not overwrite the
  same suite output.
- [ ] Re-run one real API Docker smoke after these fixes and confirm
  `docker_sandbox_error=false`.

## P4: Smoke and Suite Runs

Goal: produce the first defensible OpenHands results.

- [x] Run one sanity task with real OpenHands and `deepseek/deepseek-v4-flash`
  (`experiments/openhands-agent/smoke-iniconfig-20260701-150955`: agent passed,
  submission created, eval failed).
- [x] Run the 3-task sanity suite under agent Docker + eval Docker
  (`experiments/openhands-agent/sanity-pilot-20260701-151923`: 0 agent failures,
  0/3 eval passed, all `usage_unverified=true`).
- [x] Inspect `agent/openhands_stdout.log`, `agent/usage.json`, and `run.json`.
- [ ] Promote to a small fixed slice, then the full Python main suite.

Recommended entrypoint:

```bash
FEATURELIFTBENCH_AGENT_DOCKER=1 FEATURELIFTBENCH_EVAL_DOCKER=1 ./run_openhands.sh
```

Single-task smoke:

```bash
FEATURELIFTBENCH_AGENT_DOCKER=1 FEATURELIFTBENCH_EVAL_DOCKER=1 \
./run_openhands.sh benchmark/sanity/iniconfig__parse_config__001 \
  experiments/openhands-agent/smoke-iniconfig-$(date +%Y%m%d-%H%M%S)
```

## Reporting Policy

- `openhands-agent` is the main evaluated agent once real OpenHands execution
  and usage evidence are available.
- `featurelift-agent` is a reference/control for protocol debugging and
  context-audit comparisons.
- Runs with missing or unverifiable OpenHands token evidence must be labeled
  `usage_unverified=true`.
- Results with unverified context behavior should not be used as main claims
  about long-context software feature extraction.
