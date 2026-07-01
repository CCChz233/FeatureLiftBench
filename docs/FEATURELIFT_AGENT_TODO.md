# FeatureLiftAgent TODO

This checklist now tracks the **reference/control** FeatureLiftBench-native
agent. The active main line for the current benchmark experiments is
[OPENHANDS_BENCHMARK_TODO.md](OPENHANDS_BENCHMARK_TODO.md): use OpenHands as
the evaluated agent and keep FeatureLiftAgent as a protocol/debugging baseline.

## Current Status

- [x] `--agent featurelift-agent` is registered in the harness.
- [x] Local and Docker command paths can invoke
  `python -m featureliftbench.featurelift_agent`.
- [x] The scaffold writes `agent/usage.json`, `agent/context_audit.jsonl`, and
  `agent/state/*`.
- [x] `usage.json` v1 `context_audit` is parsed into `run.json` and compact
  suite entries.
- [x] The agent can run context-audited LLM planning phases.
- [x] The agent can execute a three-phase smoke extraction workflow through the
  normal evaluator.
- [x] The agent can run one bounded repair round for failed extraction/test/final-check actions.
- [x] The repair loop has been validated with a real API-backed sanity task
  using `deepseek/deepseek-v4-flash`.
- [x] One-command sanity suite entrypoint: `./run_featurelift.sh` with profile
  `featurelift_v4_flash`.
- [x] Shared dependency lock install for agent public tests and evaluator
  (`dependency_install.py` + `bootstrap_vendor_wheels.py`).
- [x] FeatureLift-specific suite analysis:
  `harness/scripts/analyze_featurelift_suite.py`.
- [x] OpenHands has a dedicated harness adapter/wrapper:
  `--agent openhands-agent`.
- [ ] FeatureLiftAgent remains available for context-audit comparison, but it
  is not the main evaluated agent for the OpenHands benchmark track.

## P1: Protocol-Complete Scaffold

Goal: make the controller produce useful deterministic state before any model
call. This keeps the harness contract stable while the LLM/runtime layer is
still being built.

- [x] Write durable state directory.
- [x] Write usage/context audit artifacts.
- [x] Write `repo_map.md` from the prepared workspace.
- [x] Write `source_entrypoints.json` from redacted metadata.
- [x] Write a bootstrap dependency manifest seeded from task metadata.
- [x] Add focused tests for scaffold state files.

Acceptance:

- `featurelift-agent` can run one task through `run_agent_on_task`.
- The resulting run may fail evaluation, but it must not be
  `missing_submission`.
- `agent/state/` contains enough input summary for the next LLM phase.

## P2: Minimal LLM Controller

Goal: add a small, auditable LLM loop without depending on OpenHands yet.

- [x] Add OpenAI-compatible chat client.
- [x] Record one `context_audit.jsonl` row per model call.
- [x] Enforce `prompt_tokens + reserved_output_tokens <= context_window_tokens`
  before every call.
- [x] Add deterministic repository map plus LLM prompts for closure plan,
  extraction plan, and final checklist.
- [x] Persist model decisions into `agent/state/*`, not append-only memory.
- [x] Fail with a structured `context_violation` before making an oversized
  call.

Acceptance:

- One smoke task can complete with one or more real model planning calls.
- `usage.json` reports actual or explicitly estimated per-call usage.
- Context violations are deterministic and test-covered.

## P3: Tool Execution Loop

Goal: let the model act on the workspace through a small command interface.

- [x] Define allowed action schema.
- [x] Add bounded shell command execution for fixed public-test/final-check
  commands.
- [x] Add file read/write helpers with workspace path checks.
- [x] Append tool observations to phase-local state summaries.
- [x] Run public tests through a controlled command.
- [x] Write extraction and test logs after each action.
- [x] Iterate action execution across multiple planning/tool rounds.
- [x] Surface failed tool actions in `usage.json`/run status.

Acceptance:

- A simple smoke task can be solved end-to-end without hidden access. **Done
  for the sanity fixture via mocked LLM responses.**
- Command output is bounded and recorded. **Done.**
- The controller never writes outside the prepared workspace or agent output.
  **Path checks are implemented and test-covered for hidden/evaluation paths.**

## P4: FeatureLift Workflow

Goal: make the agent behavior match the benchmark task shape.

- [x] Closure plan phase can identify runtime files, resources, dependencies,
  and excluded subsystems through structured actions/state.
- [x] Extraction phase can create `submission/featurelifted`.
- [x] Hidden-boundary checks run before final submission even if public tests
  pass.
- [x] Footprint-pruning phase attempts safe deletion of transient submission
  files.
- [x] Final audit checks output import, forbidden imports, and public tests.
- [x] Add a repair loop when public tests or final checks fail.
- [x] Run at least one real API-backed sanity task, not only mocked LLM calls.

Acceptance:

- The workflow can pass at least one sanity task. **Done with mocked LLM
  responses and with real `deepseek/deepseek-v4-flash`.**
- State files explain why each copied file is present. **Partially done through
  action reasons and tool observations.**
- Public-test pass does not immediately submit. **Done: final-check phase runs
  after public tests.**

## P5: OpenHands Comparison Support

Goal: keep FeatureLiftAgent useful as a comparison point while OpenHands is the
main evaluated agent.

- [x] Add a separate `openhands-agent` adapter instead of folding OpenHands into
  `featurelift-agent`.
- [x] Keep the existing `usage.json` and `context_audit.jsonl` contract.
- [ ] Compare OpenHands runs against FeatureLiftAgent runs on the same sanity
  and fixed-slice tasks.
- [ ] Use FeatureLiftAgent exact context audit as a sanity check for reporting
  expectations.

Acceptance:

- FeatureLiftAgent can still run the existing sanity workflow.
- OpenHands is reported separately as `openhands-agent`, not as a
  FeatureLiftAgent implementation detail.

## P6: External Agent Baselines

Goal: run real open-source agent baselines under the same harness where
possible.

- [ ] Add Cline headless recipe or adapter.
- [ ] Add Aider recipe or adapter.
- [ ] Mark runs `usage_unverified=true` if exact per-call usage cannot be
  captured.
- [ ] Document limitations separately from FeatureLiftAgent main results.

Acceptance:

- At least one external baseline can run one task through `--agent command` or a
  dedicated adapter.
- Its output can still be evaluated by the normal FeatureLiftBench evaluator.

## Real API Smoke

Completed on 2026-07-01 with `deepseek/deepseek-v4-flash` through the real
DeepSeek API:

- Run: `experiments/featurelift-agent/deepseek-v4-flash-sanity-real-004/run.json`
- Usage: `experiments/featurelift-agent/deepseek-v4-flash-sanity-real-004/agent/usage.json`
- Context audit: `experiments/featurelift-agent/deepseek-v4-flash-sanity-real-004/agent/context_audit.jsonl`
- Result: `status=passed`, `functional_gate=1.0`, `final_score=0.49925`
- Context: 5 real API calls, max prompt tokens per call `24096`, provider
  usage verified, no context violation.
- Tooling: `exit_status=actions_complete_with_repairs`; historical tool
  failures were repaired before final check.

## Immediate Next Step

Run the 3-task sanity suite under Docker with the standard experiment entrypoint:

```bash
PYTHONPATH=harness python harness/scripts/bootstrap_vendor_wheels.py
docker/build_agent_image.sh featureliftbench-agent:latest
docker/build_eval_image.sh featureliftbench-eval:latest

FEATURELIFTBENCH_AGENT_DOCKER=1 \
FEATURELIFTBENCH_EVAL_DOCKER=1 \
AGENT_PROFILE=featurelift_v4_flash \
RUN_ID=featurelift-sanity-$(date +%Y%m%d) \
./run_featurelift.sh
```

Then inspect `featurelift-analysis.md`, failed tasks (especially
`python_pathspec__gitignore_match__001`), and per-task `agent/context_audit.jsonl`.

## Sanity Pilot (2026-07-01)

Docker suite run: `experiments/featurelift-agent/sanity-pilot-20260701/`

- Harness: `./run_featurelift.sh` completed end-to-end with analysis artifacts.
- Single-task Docker smoke passed separately:
  `experiments/featurelift-agent/smoke-docker-iniconfig-20260701-095440/`.
- Suite agent quality still varies by task; see `featurelift-analysis.md` for
  per-task `exit_status`, tool summary, and context audit.
