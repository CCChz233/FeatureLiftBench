# FeatureLiftAgent Design

FeatureLiftBench should not rely on a generic SWE-style append-only agent as its
main experimental protocol. The benchmark asks for behavior-preserving feature
extraction into a standalone package, while the current mini-swe-agent baseline
is optimized for issue reproduction, source edits, and patch submission.

This document now defines the context-audit protocol and the reference
FeatureLiftAgent control. The active main experiment direction is OpenHands as
the evaluated agent:

```text
Historical baseline: mini-swe-agent
Main evaluated agent: OpenHands through --agent openhands-agent
Protocol control:     FeatureLiftAgent with exact in-repo context audit
External baselines:   Cline headless / Aider where feasible
```

The first implementation priority remains context audit. The second is making
OpenHands run through the same FeatureLiftBench workspace, submission, Docker,
and reporting contracts as every other agent.

## 1. Problem Statement

FeatureLiftBench evaluates whether an agent can extract a target feature from an
entangled repository into `submission/featurelifted/`.

The current mini-swe-agent setup has three protocol gaps:

1. **Workflow mismatch.** The default prompt is a SWE issue-fixing loop:
   inspect, reproduce, edit source, verify, submit. FeatureLiftBench instead
   needs dependency closure discovery, copying/adapting only necessary runtime
   pieces, import rewriting, standalone packaging, hidden-boundary reasoning,
   and footprint pruning.
2. **Append-only history.** The agent keeps accumulating chat history. This
   makes long tasks expensive and risks crossing a model's context window unless
   every call is audited.
3. **Insufficient context evidence.** Existing `run.json` and `suite.json`
   record cumulative token totals, but the formal protocol does not currently
   enforce or report per-call prompt size, model context window, reserved output
   budget, or context violations.

Important distinction:

```text
Millions of cumulative task tokens do not imply a million-token prompt.
Context-window validity depends on each individual LLM call.
```

Historical runs can be rescued only if post-hoc trajectory audit shows every
call stayed under the claimed window. Future runs must enforce this before each
LLM call.

## 2. Goals

- Make agent experiments reproducible and interpretable under explicit context
  budgets.
- Separate model quality from agent scaffold quality.
- Add a FeatureLift-native agent workflow aligned with extraction tasks.
- Keep `eval` and task format stable; agent changes must remain optional.
- Preserve mini-swe-agent results as a historical baseline, not the final main
  protocol.

## 3. Non-Goals

- Do not expose hidden tests or evaluation secrets to the agent.
- Do not make functional scoring depend on which agent was used.
- Do not fork the benchmark into a new task schema.
- Do not optimize for one proprietary hosted agent product.
- Do not require all users to install OpenHands/Cline/Aider just to run `eval`.

## 4. Agent Roles

| Agent | Role | Why |
| --- | --- | --- |
| `mini-swe-agent` | Historical SWE-style baseline | Existing runs and trajectories already use it; useful to show scaffold mismatch. |
| `openhands-agent` | Main evaluated open-source agent | Runs OpenHands through the normal FeatureLiftBench harness/evaluator. |
| `featurelift-agent` | Protocol reference/control | Purpose-built workflow, bounded context, structured state, exact usage audit. |
| Cline headless | External open-source coding-agent baseline | Good comparison against a real product-like autonomous coding agent. |
| Aider | Lightweight editor-style baseline | Useful for repo-map/editing comparison, less suitable as autonomous main agent. |
| AutoCodeRover / Agentless | Design references | Their localization and staged repair ideas are useful, but their patch-oriented output does not match `submission/featurelifted`. |

The main paper should report at least:

```text
mini-swe-agent baseline
openhands-agent main result
featurelift-agent protocol/control result
one additional external open-source baseline, preferably Cline or Aider
```

## 5. Required Agent Output Contract

Every agent must write normal benchmark output:

```text
workspace/submission/
  pyproject.toml
  featurelifted/
    __init__.py
    ...
```

Every context-audited agent should also write:

```text
agent/usage.json
agent/context_audit.jsonl
agent/state/
  task_brief.md
  repo_map.md
  source_entrypoints.json
  action_schema.json
  closure_plan.md
  dependency_manifest.json
  extraction_plan.md
  extraction_log.md
  test_log.md
  hidden_boundary_check.md
  prune_log.md
  final_checklist.md
  tool_observations.jsonl
```

`usage.json` is the stable machine-readable summary. `context_audit.jsonl` is
the per-call evidence trail. `state/` is the agent's durable working memory and
should be safe to inspect in case studies.

Current implementation status:

- `openhands-agent` is registered in the harness and invokes
  `python -m featureliftbench.openhands_runner`.
- The OpenHands wrapper writes `agent/openhands_task.md`,
  `agent/openhands_command.json`, and standard `agent/usage.json`.
- The OpenHands wrapper accepts the real headless command through
  `--agent-command` or `FEATURELIFTBENCH_OPENHANDS_COMMAND`; the exact
  OpenHands runtime command is intentionally not hard-coded.
- `featurelift-agent` is registered in the harness and can run locally or
  through the existing Docker command path.
- `--enable-llm` runs OpenAI-compatible chat phases with one
  `context_audit.jsonl` row per model call.
- `--execute-actions` executes a bounded action schema:
  `inspect_file`, `copy_file`, `write_file`, `run_public_tests`,
  `prune_submission`, and `final_check`.
- A three-phase mocked-LLM smoke workflow now passes the normal evaluator on
  the sanity fixture.
- A real `deepseek/deepseek-v4-flash` API smoke also passes the sanity fixture:
  `experiments/featurelift-agent/deepseek-v4-flash-sanity-real-004/run.json`.
- For direct DeepSeek API calls, `featurelift-agent` normalizes
  `deepseek/deepseek-v4-flash` to the provider model name
  `deepseek-v4-flash` while preserving the configured model in usage reports.
- `featurelift-agent` remains a conservative standard-library controller and
  should be treated as a protocol/control baseline, not the OpenHands main
  result.

## 6. Usage Schema

Planned `agent/usage.json` shape:

```json
{
  "schema_version": "featureliftbench.agent_usage.v1",
  "agent_name": "featurelift-agent",
  "model": "openai/qwen3-coder",
  "available": true,
  "context_audit": {
    "available": true,
    "context_window_tokens": 131072,
    "reserved_output_tokens": 8192,
    "max_allowed_prompt_tokens": 122880,
    "history_policy": "stateful_bounded",
    "over_context_behavior": "fail_before_call",
    "token_source": "provider_usage",
    "max_prompt_tokens_per_call": 73422,
    "max_total_tokens_per_call": 75102,
    "context_violation": false,
    "usage_unverified": false
  },
  "assistant_steps": 42,
  "api_calls": 42,
  "prompt_tokens": 850000,
  "completion_tokens": 32000,
  "total_tokens": 882000,
  "tool_summary": {
    "available": true,
    "actions_enabled": true,
    "total_actions": 18,
    "success_actions": 18,
    "failed_actions": 0,
    "blocked_actions": 0,
    "timeout_actions": 0,
    "error_actions": 0,
    "final_check_status": "success",
    "public_tests_status": "success"
  }
}
```

`context_audit.jsonl` should contain one record per LLM call:

```json
{
  "call_index": 17,
  "phase": "closure_plan",
  "prompt_tokens": 42120,
  "completion_tokens": 830,
  "total_tokens": 42950,
  "context_window_tokens": 131072,
  "reserved_output_tokens": 8192,
  "max_allowed_prompt_tokens": 122880,
  "over_context": false,
  "token_source": "provider_usage",
  "prompt_sha256": "..."
}
```

Backward compatibility:

- The harness should continue accepting current flat fields:
  `api_calls`, `prompt_tokens`, `completion_tokens`, `total_tokens`,
  `assistant_steps`.
- New parsers should derive those flat fields from `usage.json` v1.
- If an old agent has no `usage.json`, mini trajectories remain the fallback.

## 7. Context Policy

Every official agent run must declare a context track:

| Track | Rule | Use |
| --- | --- | --- |
| `128k-fair` | `prompt_tokens + reserved_output_tokens <= 131072` | Main fair comparison across long-context and normal-context models. |
| `256k-long` | `prompt_tokens + reserved_output_tokens <= 262144` | Long-context comparison for models that officially support it. |
| `1m-long` | `prompt_tokens + reserved_output_tokens <= 1048576` | Optional long-context ablation; expensive and not comparable to 128k-fair. |

Default reservation:

```text
reserved_output_tokens = 8192
max_allowed_prompt_tokens = context_window_tokens - reserved_output_tokens
```

If a call would exceed the budget:

1. The agent must not send the call.
2. It must write a context violation record.
3. The task run should be marked as an agent failure with reason
   `context_violation`.

If the provider does not return usage:

- Use a model-specific tokenizer estimate when available.
- Otherwise mark `usage_unverified=true`.
- `usage_unverified=true` runs can be exploratory, but should not enter the
  final main table.

## 8. FeatureLiftAgent Workflow

`featurelift-agent` should use bounded prompt context plus durable state files.
It should not rely on append-only conversation history.

### Phase 1: Ingest

Read:

- `TASK.md`
- redacted `metadata.json`
- `public_tests/`
- repository tree summary
- `requirements.lock`

Write:

- `agent/state/task_brief.md`
- `agent/state/source_entrypoints.json`
- `agent/state/action_schema.json`

### Phase 2: Repository Map

Use shell search and lightweight static analysis to identify likely source
entrypoints, dependent modules, resources, and forbidden original imports.

Write:

```text
agent/state/repo_map.md
agent/state/source_entrypoints.json
```

### Phase 3: Closure Plan

Produce a planned extraction closure:

```json
{
  "runtime_files": ["..."],
  "resource_files": ["..."],
  "third_party_dependencies": ["..."],
  "excluded_subsystems": ["..."],
  "risk_points": ["..."]
}
```

The plan should distinguish:

- necessary runtime closure;
- public-test-only shortcuts;
- suspected hidden-test behavior;
- copy-heavy fallback.

Write:

```text
agent/state/closure_plan.md
agent/state/dependency_manifest.json
```

### Phase 4: Extract

Create `workspace/submission/featurelifted/`, copy or rewrite required files,
and normalize imports away from the original package.

Expected actions:

- copy source files selectively;
- rewrite imports to `featurelifted.*`;
- include required package data;
- add minimal `pyproject.toml`;
- expose the output API exactly as metadata requires.

Write:

```text
agent/state/extraction_log.md
```

### Phase 5: Validate Public Behavior

Run public tests and import checks locally. The agent may create additional
private probes based on task metadata, but must not access hidden tests.

Write:

```text
agent/state/test_log.md
agent/state/probes/
```

### Phase 6: Hidden-Boundary Reasoning

Before submission, the agent must answer:

- Which behavior is covered by public tests?
- Which included behavior is likely only covered by hidden tests?
- Which edge cases were probed manually?
- Which copied modules are only present because of closure risk?

This phase prevents immediate submission after public tests pass.

Write:

```text
agent/state/hidden_boundary_check.md
```

### Phase 7: Footprint Pruning

Try to remove obvious unrelated files while preserving public and probe tests.

Write:

```text
agent/state/prune_log.md
```

### Phase 8: Final Audit

Before final completion:

- verify `workspace/submission` exists;
- verify output import works;
- scan for forbidden original imports;
- run public tests once more;
- write final usage and context audit.

Write:

```text
agent/state/final_checklist.md
agent/usage.json
```

The current controller also supports one bounded `repair_plan` model call after
failed, blocked, timed-out, or errored tool observations. Repair actions are
recorded in the same `tool_observations.jsonl`, and `usage.json.exit_status`
distinguishes `actions_complete`, `actions_complete_with_repairs`, and
`actions_failed`.

## 9. Prompt Context Layout

Each LLM call should receive a bounded prompt with this structure:

```text
System: FeatureLiftAgent role and output contract
Task brief: compact TASK.md summary
Current phase: one of ingest/repo_map/closure/extract/test/prune/final
State summary: selected state files, compacted
Evidence snippets: only needed file excerpts or command outputs
Budget: context window, prompt budget, remaining step budget
Instruction: produce one bounded action or one structured plan update
```

The prompt must not include raw full history. Prior decisions should be read
from `agent/state/*` and summarized into the next call.

## 10. Harness Changes

### P0: Context Audit for Existing Mini Runs

Add a read-only script:

```bash
PYTHONPATH=harness python harness/scripts/audit_agent_context.py \
  experiments/mini-swe-agent/<run_id> \
  --context-window 131072 \
  --reserved-output 8192 \
  --output experiments/mini-swe-agent/<run_id>-context-audit.json
```

The script should parse:

- `agent/trajectory.json`
- per-message `extra.response.usage`
- top-level `info.model_stats`
- task `run.json` status

It should report:

- max prompt tokens per call;
- max total tokens per call;
- number of calls over 64k / 128k / 256k / 1m;
- tasks with missing per-call usage;
- tasks with context violations for the declared window.

This immediately separates:

```text
usable historical baseline
pilot-only run
context-violating run
usage-unverified run
```

### P1: Extend Agent Usage Collection

Update `harness/featureliftbench/agent_runner.py` usage parsing:

- accept `schema_version = featureliftbench.agent_usage.v1`;
- preserve `context_audit` in `run.json`;
- summarize suite-level context audit fields in `suite.json`;
- keep old flat token fields unchanged.

Suggested suite summary additions:

```json
{
  "agent_context_audit_totals": {
    "available_runs": 100,
    "usage_unverified_runs": 0,
    "context_violation_runs": 0,
    "max_prompt_tokens_per_call": 88210,
    "max_total_tokens_per_call": 90102
  }
}
```

### P2: Add `featurelift-agent` Adapter

Add a new adapter name:

```text
--agent featurelift-agent
```

Initial implementation can be command-backed so the harness contract stabilizes
before the OpenHands SDK dependency is finalized.

Expected command shape:

```bash
featurelift-agent run \
  --workspace "$FEATURELIFTBENCH_WORKSPACE" \
  --task-file "$FEATURELIFTBENCH_TASK_FILE" \
  --submission-dir "$FEATURELIFTBENCH_SUBMISSION_DIR" \
  --agent-output-dir "$FEATURELIFTBENCH_AGENT_OUTPUT_DIR" \
  --model "$MODEL" \
  --context-window 131072 \
  --reserved-output 8192
```

### P3: Add `openhands-agent` Adapter

Run OpenHands as a first-class evaluated agent without binding the harness to a
single OpenHands CLI version:

- runs headlessly inside the existing agent Docker boundary;
- supports OpenAI-compatible model endpoints used by the project;
- allows tool execution logs to be captured;
- allows exact or estimated token accounting per LLM call;
- can write `usage.json` and `context_audit.jsonl`.

The stable adapter name is:

```text
--agent openhands-agent
```

The actual OpenHands invocation is supplied by command template:

```bash
--agent-command '... {prompt_file} ... {workspace} ... {model} ...'
```

### P4: External Agent Baselines

Add optional command recipes for:

- Cline headless;
- Aider;

These should use the same `usage.json` contract when possible. If exact token
usage cannot be captured, label runs as `usage_unverified=true`.

## 11. Experiment Reporting Policy

Future paper tables should classify runs as:

| Class | Requirement | Paper use |
| --- | --- | --- |
| `main` | Docker agent/eval, context audit available, no context violations | Main results. |
| `audited-baseline` | Post-hoc context audit available, no violations, older scaffold | Baseline or pilot comparison. |
| `pilot` | Missing enforced context guard or usage partially unavailable | Qualitative only. |
| `invalid-context` | One or more context violations | Exclude from performance claims. |

For every official run, report:

- agent name and version;
- model and endpoint;
- context track;
- max prompt tokens per call;
- total tokens;
- task success;
- average final score;
- compact / mid / high-extraction pass counts.

## 12. Acceptance Criteria

P0 is complete when:

- `audit_agent_context.py` works on existing mini runs;
- tests cover trajectories with per-call usage, missing usage, and violations;
- a context audit JSON is produced for at least one historical suite.

P1 is complete when:

- `usage.json` v1 is parsed into `run.json`;
- `suite.json` contains context audit totals;
- old mini runs still parse correctly.

P2 is complete when:

- `--agent featurelift-agent` runs one smoke task through the existing harness;
- it writes `usage.json`;
- it fails before calling the model if the configured context budget would be
  exceeded.

P3 is complete when:

- `--agent openhands-agent` passes one smoke task end-to-end with real
  OpenHands;
- agent Docker still hides hidden tests and benchmark root;
- usage audit is available and verified.

P4 is complete when:

- one external baseline can run one task via `--agent command` or a dedicated
  adapter;
- limitations are documented.

## 13. Implementation Order

1. Add post-hoc context audit script for existing trajectories.
2. Extend `usage.json` schema and suite aggregation.
3. Add `featurelift-agent` adapter with a minimal command contract.
4. Implement minimal FeatureLift workflow and state files.
5. Add `openhands-agent` adapter and pin a real OpenHands headless command.
6. Add external baseline recipes.
7. Re-run a small 10-task slice under `128k-fair`.
8. Promote to full 100-task main experiment.

## 14. Open Questions

- Should `context_violation` be a new run status, or an agent failure reason
  under existing status values?
- Should the 128k fair track use `131072` exactly, or a round `128000` budget
  for conservative provider-tokenizer mismatch?
- Should final paper include a long-context track, or keep it as appendix until
  128k-fair results are stable?
- Should FeatureLiftAgent optimize for compactness explicitly, or should it
  optimize functional pass first and prune only after passing public tests?
