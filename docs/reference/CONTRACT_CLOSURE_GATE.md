# Public Contract Closure Gate

> **Documentation status: reference · Last verified: 2026-08-17**

`contract_closure_gate` is an opt-in, Python-only agent experiment arm. It keeps
Main unchanged and never mounts benchmark evaluator tests.

## Run

```bash
featureliftbench run-agent benchmark/tasks \
  --contract-closure-gate \
  --agent openhands-agent \
  --agent-profile openhands_deepseek_v4_flash_contract_closure_gate \
  --output experiments/methods/contract_closure_gate/pilot
```

The equivalent environment switch is
`FEATURELIFTBENCH_CONTRACT_CLOSURE_GATE=1`.

## Agent-visible inputs

The arm adds three workspace artifacts:

- `PUBLIC_CONTRACT.json`, generated exclusively from `metadata.public_spec`;
- `contract_cases/`, where the agent maps executable evidence to public `Bxxx`
  clauses;
- `flb-contract-check`, the local checker command.

`evaluation_spec`, benchmark tests, reference solutions, and previous evaluator
feedback are never copied into the workspace. The visible upstream `repo/` may
be used for differential behavior cases.

## Gate semantics

Missing APIs, wrong kinds/signatures, compile failures, and forbidden
imports/paths are hard findings. Stable differential mismatches and failing
direct assertions are actionable behavior findings. Behavior coverage,
unstable or unavailable upstream probes, and invalid evidence remain soft
telemetry and do not trigger repair by themselves. Actionable findings trigger
at most one repair round, capped at 900 seconds and 20 OpenHands steps.

Harness-side checks use the same agent Docker image as the coding run when the
agent backend is Docker. This prevents host dependency versions from becoming
false upstream observations. Local agent runs continue to check locally.

The checker supports staged use:

```bash
./flb-contract-check --structure-only --summary
./flb-contract-check --behavior-only --summary
./flb-contract-check --summary
```

The final evaluator always runs when a submission exists, even if the gate
remains open. Gate evidence does not replace Functional Pass.

Each task output records `contract_closure_initial.json`,
`contract_closure_final.json`, and `contract_closure_phase.json`; the phase
payload is also included under `run.json.contract_closure`.
The audit includes `usage_totals`, which combines primary and repair phases.

## Low-token Lite V2.1 arm

`contract_closure_gate_lite` keeps only the deterministic structural gate. It
does not create `contract_cases/`, does not ask the agent to author behavior
evidence, and runs the checker in `--structure-only` mode. Its prompt requires
an importable package immediately, a minimal API skeleton within roughly six
agent steps, and the first structure check by roughly step twelve. After about
70% of the budget, the agent is told to stop broad exploration and finish the
implementation. The private evaluator still always determines Functional Pass.

Repair is selective in V2.1. Empty submissions, non-compiling submissions,
non-local failure categories, more than three hard findings, or more than two
missing APIs are recorded but do not launch another model phase. Only a small
local API, signature, or dependency gap receives one bounded repair.

The bundled DeepSeek profile condenses at a 64k context window, limits one
observation to 16,000 characters, and uses independent phase budgets:

- primary: 2,000,000 tokens and 45 OpenHands steps;
- eligible repair: 200,000 tokens and 5 OpenHands steps.

V2.1 also hardens OpenHands execution without granting another ordinary model
attempt. The usage proxy normalizes the single known terminal-tool schema alias
`security_rule` to `security_risk`. If OpenHands still emits an explicit early
`AgentErrorEvent` for tool validation, exits within eight steps, and leaves no
Python submission, the harness permits one fresh primary retry. Both attempts
are retained under the task output and fully included in
`run.json.contract_closure.usage_totals`. Step exhaustion, token exhaustion,
ordinary empty submissions, evaluator failures, and non-empty partial
submissions do not receive this retry.

```bash
featureliftbench run-agent benchmark/tasks \
  --contract-closure-gate-lite \
  --agent openhands-agent \
  --agent-profile openhands_deepseek_v4_flash_contract_closure_gate_lite \
  --output experiments/methods/contract_closure_gate_lite/pilot
```

Override the phase budgets without editing a profile:

```bash
FEATURELIFTBENCH_CONTRACT_CLOSURE_PRIMARY_TOKEN_LIMIT=1800000 \
FEATURELIFTBENCH_CONTRACT_CLOSURE_REPAIR_TOKEN_LIMIT=200000 \
FEATURELIFTBENCH_CONTRACT_CLOSURE_PRIMARY_MAX_STEPS=40 \
FEATURELIFTBENCH_CONTRACT_CLOSURE_REPAIR_MAX_STEPS=5 \
FEATURELIFTBENCH_CONTRACT_CLOSURE_INFRA_RETRY_LIMIT=1 \
FEATURELIFTBENCH_CONTRACT_CLOSURE_INFRA_RETRY_MAX_TRIGGER_STEPS=8 \
featureliftbench run-agent ... --contract-closure-gate-lite
```

When the provider reports prompt-cache accounting, `usage.json`, suite totals,
and `run.json.contract_closure.usage_totals` include all primary and repair
usage, including
`prompt_cache_hit_tokens`, `prompt_cache_miss_tokens`, and
`effective_uncached_prompt_tokens`. Raw token totals remain available so cache
savings are not confused with algorithmic token reduction.

## Frozen Lite V1 release arm

`contract_closure_gate_lite_v1_frozen` is the release candidate for the
Python-200 method run. It preserves the prompt and budgets used by the paired
12-task Lite V1 pilot rather than silently reusing the later V2.1 prompt:

- structure-only checker and no behavior cases;
- primary budget of 2,000,000 tokens and 45 OpenHands steps;
- one repair round of at most 500,000 tokens and 10 steps for any deterministic
  hard public-contract finding;
- 65,536-token context, 8,192-token output reserve, and 16,000-character
  observation cap.

Evaluator-blind runtime corrections are retained: terminal tool alias
normalization, one narrowly classified early empty-submission infrastructure
retry, complete attempt usage aggregation, and the corrected implicit
`self`/`cls` signature comparison. These corrections do not add task semantics
or evaluator information. The exact release settings are stored in
`harness/config/methods/contract_closure_gate_lite_v1_frozen.json`.

```bash
featureliftbench run-agent benchmark/python200_tasks \
  --contract-closure-gate-lite-v1-frozen \
  --agent openhands-agent \
  --agent-profile openhands_deepseek_v4_flash_contract_closure_gate_lite_v1_frozen \
  --output experiments/python/openhands/deepseek-v4-flash/<run-id>
```

The equivalent environment switch is
`FEATURELIFTBENCH_CONTRACT_CLOSURE_GATE_LITE_V1_FROZEN=1`.

## Focused behavior V3 arm

`contract_closure_gate_v3` keeps the V2.1 primary and repair budgets, early
implementation checkpoints, tool-alias compatibility, and narrow
infrastructure retry. It adds a bounded behavior layer instead of returning to
V1's exhaustive Bxxx coverage requirement:

- the primary agent writes exactly two focused public-behavior smoke cases and
  may never create more than three;
- cases prioritize nested or multi-segment inputs, public exception types,
  state transitions, and delegation or recursion paths;
- `./flb-contract-check --micro --summary` runs both deterministic structure
  checks and at most three behavior cases;
- missing Bxxx coverage and unavailable upstream behavior remain telemetry;
- only a concrete executable mismatch or an eligible small structural gap can
  trigger the single five-step repair.

The micro behavior gate closes when at least one valid case executes the
submission successfully and no case reports an actionable mismatch. This is a
development signal only; the private evaluator remains the formal outcome.

```bash
featureliftbench run-agent benchmark/tasks \
  --contract-closure-gate-v3 \
  --agent openhands-agent \
  --agent-profile openhands_deepseek_v4_flash_contract_closure_gate_v3 \
  --output experiments/methods/contract_closure_gate_v3/pilot
```

The equivalent environment switch is
`FEATURELIFTBENCH_CONTRACT_CLOSURE_GATE_V3=1`. The V1, Lite V2.1, V3, and
equal-budget control arms are mutually exclusive.

## Equal-budget control

`contract_closure_budget_control` is the causal control for Lite. It uses the
same 64k context, 45-step limit, 2M primary token cap, and 16,000-character
observation limit, but it does not materialize `PUBLIC_CONTRACT.json`, install
`flb-contract-check`, run a structural gate, or receive a checker report. Its
only method prompt is a generic final implementation review.

```bash
featureliftbench run-agent benchmark/tasks \
  --contract-closure-budget-control \
  --agent openhands-agent \
  --agent-profile openhands_deepseek_v4_flash_contract_closure_budget_control \
  --task-id <task_id> \
  --output experiments/methods/contract_closure_budget_control/<run-id>
```

This primary-only control is intended to isolate the value of machine-readable
structural feedback on tasks where Lite does not trigger repair. Repair-triggered
Lite tasks must be reported as a separate stratum rather than treated as an
equal-realized-budget comparison.
