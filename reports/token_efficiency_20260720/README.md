# Token Efficiency and Method Innovation — 2026-07-20

> Historical analysis of v1/mixed-snapshot trajectories. It is useful for
> resource diagnosis but does not report a Full-Repository / No-Hint v2 run.
> Budgeted ECSM is a retired proposal, not the current benchmark method.

## Decision

FeatureLiftBench should optimize token use, but token reduction should be a measurable secondary objective of the method rather than the paper's standalone novelty.

The stronger method claim is a **Budgeted Executable Closure State Machine (Budgeted ECSM)**:

- maintain an obligation–artifact–evidence state graph;
- store executable repository memory with content hashes, freshness, and invalidation;
- choose inspect, expand, probe, prune, or stop by expected hidden-risk reduction per token;
- reserve budget for fresh final verification after the submission changes.

This differs from ordinary context summarization because every retained claim remains tied to executable evidence and becomes stale when its supporting artifact changes.

## Current baseline already compresses context

The existing OpenHands baseline is not a no-compression agent. It inherits OpenHands' default `LLMSummarizingCondenser`. In the 550 analyzed runs, 288 runs (52.4%) contain at least one real `Condensation` event, with 552 condensation events in total.

This generic condenser forgets older event IDs and replaces them with a free-text summary. It does reduce live prompt size, but it is triggered by conversation size rather than evidence freshness or residual task risk. It has no repository content hashes, claim invalidation, or reliable repeated-read cache. Therefore the paper comparison must use the default OpenHands condenser as the strong baseline; the research question is whether evidence-aware compression improves its correctness–token Pareto frontier.

## Evidence from 550 Python runs

| Metric | Observed value | Interpretation |
|---|---:|---|
| Verified tokens | 1,092,030,197 | The existing evidence base is large enough for a resource diagnosis. |
| Prompt-token share | 98.65% | Input/history replay, not completion verbosity, dominates token cost. |
| Non-pass token share | 63.72% | Most tokens were spent on runs that did not achieve the composite pass outcome. |
| Runs with a repeated file read | 65.27% | Strong diagnostic signal; not a causal estimate because task difficulty confounds it. |
| History-growth upper bound | 67.34% of prompt tokens | Opportunity ceiling for externalized state and context compression, not removable waste. |

Core-100 failures use a median 2.40M tokens versus 1.30M for passes. Hard50 failures use 1.26M versus 1.48M for passes, so one universal early-stop cap would treat the two regimes incorrectly.

At a 3M total-token budget, 29 of 225 observed successes lie above the cap; the cap covers 87.1% of observed successful trajectories and is a reasonable provisional resource gate. A simulated 32k per-call prompt cap has a 25.2% theoretical prompt-saving ceiling, but it touches 179 of 225 observed successes. Hard truncation therefore requires a rerun and cannot substitute for evidence-aware memory.

## Experiment sequence

| Stage | Design | Purpose |
|---|---|---|
| T0 | 550-run offline audit (complete) | Locate plausible waste mechanisms and freeze metrics. |
| T1 | 4 frozen tasks × 4 arms × 1 seed, 3M guard = 16 cells | Resource gate: default OpenHands condenser, tuned generic condenser, evidence memory, ECSM+memory. |
| T2 | Pilot-10 × 3 arms × 2 seeds, 3M guard = 60 cells | Paired hidden-pass and token-efficiency test. |
| T3 | Pilot-10 × 2 arms × 2 seeds × 3 budgets = 120 cells | Estimate the pass–token Pareto frontier at 1.5M, 3M, and 6M. |
| T4 | 24 tasks × 3 arms × 3 seeds = 216 cells | Confirm the paper claim on a stratified task set. |

T1 advances only if hidden correctness is non-inferior and median verified tokens fall by at least 20%. This threshold is provisional and should be frozen before starting the runs. Oracle arms remain mechanism ceilings and should not be averaged into the final method result.

## Metrics to freeze before T1

Primary outcomes:

- FormalPass@B and HiddenPass@B at a fixed budget B, paired by model, task, and seed;
- final score and extraction ratio as correctness/compactness guardrails;
- verified prompt, completion, and total tokens;
- Pareto frontier rather than a single gameable quality-per-token score.

Mechanism diagnostics:

- prompt replay ratio and repeated exploration;
- evidence-memory cache hit and invalidation counts;
- fresh-evidence finish rate;
- newly satisfied or contradicted obligations per 100k tokens;
- tokens by phase: inspect, edit, probe, re-inspect, and final verification.

## Validation status

**Share with caveats.** The notebook executes top-to-bottom and all 550 rows have complete token and event records. There are 550 unique model-task pairs and zero prompt-plus-completion identity mismatches. Evaluator output exists for 533 rows; missing submissions remain in the formal-outcome denominator.

The analysis is observational. Repeated reads and high token use can both be consequences of task difficulty. Cross-model token totals are descriptive because tokenizers/endpoints can differ. Context-cap values are theoretical upper bounds, not predicted savings or pass rates after compression. The current ECSM pilot contains 0/70 completed cells, so the method is a proposal awaiting causal evaluation.

## Reproduce

The executed notebook is `token_efficiency_analysis.ipynb`. It reads `trajectory_records_550.csv` and the selected run audit logs, then writes all summary CSV/JSON files in this directory. Regenerate the notebook source with `build_notebook.py` when the analysis logic changes.
