# Agentic Evidence Audit

> **Status: archived · Last verified: 2026-09-02**
> This is an automated provenance audit. It is not yet a coding-agent method
> arm and does not enter the Python-200 leaderboard.

## Goal

Replace manual Hidden-contract provenance labeling with a fail-closed Agent
pipeline. The audited property is repository recoverability: whether one
evaluator behavior is explicit in the public task contract or uniquely
recoverable from the full repository under that contract.

The verdicts are `explicit`, `recoverable`, `ambiguous`, `underdetermined`, and
`abstain`. Agent-adjudicated labels are not described as human gold.

## Implemented Boundary

The current implementation provides:

- assertion-level JSON validation;
- line-range citations whose SHA256 is recomputed from public task files;
- citations restricted to `TASK.md`, `metadata.json`, and `repo/`;
- a fail-closed firewall for future evidence packs;
- conservative consensus requiring both label agreement and a shared citation;
- 40 opaque, construction-labeled canaries, ten per verdict class;
- one-Agent canary runner using the existing FeatureLiftBench AgentAdapter;
- independent early-stop validation once a stable audit record is written;
- optional direct structured canary runner for environments without a local
  Mini-SWE-Agent/OpenHands installation;
- deterministic calibration scoring.

The canary runner copies only one public case into a temporary workspace. The
private expected-label manifest is not copied into the Agent workspace. Agent
changes to public audit inputs invalidate the record.

## Generate Canaries

Choose a new output directory; the generator never replaces a non-empty one.

```bash
PYTHONPATH=harness python3.12 \
  harness/scripts/generate_agentic_evidence_canaries.py \
  --output experiments/validation/agentic_evidence/canaries_v1

PYTHONPATH=harness python3.12 \
  harness/scripts/generate_agentic_evidence_canaries.py \
  --output experiments/validation/agentic_evidence/canaries_v1 \
  --check
```

## Run a Two-Case Smoke

Remote profiles require `FEATURELIFTBENCH_API_KEY` and
`FEATURELIFTBENCH_API_BASE`. A local OpenAI-compatible endpoint may use its own
profile and a placeholder key if its client requires a non-empty value.

```bash
PYTHONPATH=harness python3.12 \
  harness/scripts/run_agentic_evidence_canaries.py \
  experiments/validation/agentic_evidence/canaries_v1 \
  experiments/validation/agentic_evidence/runs/auditor-r1 \
  --agent-profile deepseek_v4_flash \
  --agent-id deepseek-v4-flash-auditor-r1 \
  --limit 2
```

If the tool Agent is not installed, use the small-case direct auditor. This is
only a canary calibration path; Flash-33 and full-repository auditing still
require a tool-capable Agent that can search the repository.

```bash
PYTHONPATH=harness python3.12 \
  harness/scripts/run_agentic_evidence_canaries_direct.py \
  experiments/validation/agentic_evidence/canaries_v1 \
  experiments/validation/agentic_evidence/runs/direct-auditor-r1 \
  --agent-profile deepseek_v4_flash \
  --agent-id deepseek-v4-flash-direct-auditor-r1 \
  --limit 2
```

Resume skips only cases whose existing validation record is successful; provider
or schema failures are retried:

```bash
PYTHONPATH=harness python3.12 \
  harness/scripts/run_agentic_evidence_canaries.py \
  experiments/validation/agentic_evidence/canaries_v1 \
  experiments/validation/agentic_evidence/runs/auditor-r1 \
  --agent-profile deepseek_v4_flash \
  --agent-id deepseek-v4-flash-auditor-r1 \
  --resume
```

The tool runner polls a newly written record until its contents are stable and
then applies the same independent schema, identity, and citation validation used
at finalization. A valid record terminates the Agent early. `run.json` reports
record validity separately from normal Agent exit, early-stop completion, and
timeout counts. Mini-SWE-Agent audits also enforce a 24-step hard limit by
default; override it with `--max-agent-steps`, or use `0` to disable it. Use
`--no-early-stop` only for diagnostics. The final allowed model call receives
an audit-specific instruction to stop searching and write the complete record
in one action. Reaching the step limit without a record is a non-zero Agent
exit, not a normal completion.

## Score

```bash
PYTHONPATH=harness python3.12 \
  harness/scripts/score_agentic_evidence_canaries.py \
  experiments/validation/agentic_evidence/canaries_v1 \
  experiments/validation/agentic_evidence/runs/auditor-r1 \
  --output experiments/validation/agentic_evidence/runs/auditor-r1/calibration.json
```

The repaired 40-case synthetic freeze reached 40/40 valid and 40/40 correct.
The Flash-33 public audit suite is materialized, but a full multi-Agent run is
still pending. A 2026-08-26 one-case tool smoke produced a valid record but also
showed that unconstrained searching can consume the entire 900-second budget. A
second independent run reached its 24-step limit after creating citations but
before writing the record; the preserved invalid run motivated fail-closed
headless limit handling and the audit-specific final-call instruction. The
action budget and independently validated early stop now address both failure
modes. Miner, Critic/Judge, metamorphic-transition scoring, and the Hidden-blind
coding-agent evidence arm are not implemented yet.

## Safety Rule

Hidden-aware audit output must never become coding-agent input. A future evidence
pack must be generated by a separate Hidden-blind Miner from only `TASK.md`,
`metadata.public_spec`, and `repo/`, then pass the deterministic firewall before
workspace installation.
