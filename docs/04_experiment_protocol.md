# Experiment Protocol

## Goal

The experiment protocol measures end-to-end FeatureLift performance and diagnoses the roles of localization, dependency closure recovery, behavior preservation, packaging, and compactness. It is shared by Python and Go language splits.

## Agents and Baselines

Recommended systems:

- Single-shot LLM: prompt-only baseline without iterative tool use.
- LLM with public test feedback: basic repair loop over visible tests.
- mini-swe-agent: lightweight code-agent baseline.
- OpenHands or SWE-agent: stronger repository-level agent baseline.
- Oracle-locate agent: receives reference-related file hints to reduce localization burden.
- Copy-all baseline: copies broad source packages or relevant repo regions to test compactness scoring.

Do not report copy-all as a normal agent. It is a diagnostic baseline for RQ4.

## Models

Use a small but diverse model set:

- Strong closed model.
- Strong open code model.
- Medium open model.
- Local baseline model if operationally feasible.

For published results, record exact model identifiers, dates, decoding settings, agent commit, harness commit, Docker image hash, and environment flags.

## Settings

| Setting | Description | RQ use |
|---|---|---|
| Standard | Agent receives task prompt, public tests, and full source repo | RQ1 |
| Hint | Agent receives a small list of likely relevant files | RQ3 |
| Oracle-Locate | Agent receives reference-related files or closure hints | RQ3 |
| Copy-All | Baseline copies large source regions or packages | RQ4 |

The same setting names should be used for Python and Go.

## Main Comparisons

- Standard versus hint versus oracle-locate.
- Pass rate versus final score.
- Public pass versus hidden pass.
- Copy-all versus normal agents.
- Easy, medium, hard, and very hard slices when calibrated.
- Python versus Go as language splits, reported side by side only after each split has stable task quality.

## Reporting Tables

Minimum paper tables:

- Overall performance by agent and model.
- Public-hidden gap by agent.
- Oracle-locate ablation.
- Compactness analysis with copy-all baseline.
- Failure taxonomy distribution.
- Task difficulty or property analysis.

Language split tables should use the same metric names. Avoid a mixed leaderboard if one split is mature and another is pilot-only.

## Run Protocol

For each official run:

1. Freeze benchmark task list and harness commit.
2. Validate all task metadata and task directories.
3. Build or verify oracle submissions where required by construction workflow.
4. Run agents in clean workspaces without hidden tests.
5. Evaluate submissions in Docker or an equivalent clean environment.
6. Save per-task `run.json`, trajectory logs, submission, and eval `result.json`.
7. Generate suite-level summaries.
8. Separate infrastructure failures from agent/model failures.

## Data Hygiene

- Never expose hidden tests, oracle manifests, scoring references, or evaluator configs to the agent.
- Do not tune prompts on hidden failures from the final test split.
- Keep public tests strong enough to specify the API but weak enough that hidden tests remain meaningful.
- Report retries and failed infrastructure attempts explicitly.

## Operational pointers

- Living experiment inventory and gaps: [EXPERIMENTS.md](EXPERIMENTS.md)
- Frozen paper run IDs: [paper_runs_frozen.md](paper_runs_frozen.md)
- Server commands for hard50 / Python-150: [RUN.md](../RUN.md) §6.1
- Result interpretation: [FINDINGS.md](FINDINGS.md)

## TODO

- Complete matched hard-extension-50 for the three non-Flash models (see EXPERIMENTS.md).
- Decide whether additional seeds/repeats are required beyond Pass@1 for paper tables.
- Mark RQ3 Hint / Oracle-Locate as implemented only after harness settings exist and Pilot/ablation runs land.
