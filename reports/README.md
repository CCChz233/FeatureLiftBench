# FeatureLiftBench Reports

> **Status: reference index · Last verified: 2026-08-04**
> Current release numbers and blockers are maintained in [docs/STATUS.md](../docs/STATUS.md).

`reports/` contains small, reviewable audits and derived analyses. Raw model runs belong under
`experiments/`. Generated summaries never override per-task `run.json` and `eval/result.json`.

## Current Release Audits

| Path | Role |
| --- | --- |
| [Python-200 balance](audits/python200_balance_design.md) | External selection balance and replacements |
| [v3 Main readiness](audits/v3_main_readiness.md) | Frozen baseline task readiness |
| [v3 Oracle revalidation](audits/v3_oracle_revalidation/summary.md) | Repeated Docker reference evidence |
| [Adversarial canaries](audits/v3_adversarial_canaries.json) | Isolation and compactness canaries |
| [Task lifecycle](audits/task_lifecycle_report.md) | Package lifecycle status |
| [New protocol readiness](audits/new_protocol_readiness.md) | Contract/evaluation engineering gates |
| [Python-200 contract audit v1](contract_closure_200/README.md) | Full 200-task closure verdicts and remediation queue |
| [Contract v2 P0 closure](contract_closure_v2_p0/README.md) | Reviewed repair evidence for all 15 contradictory tasks |

Machine authorities include the active baseline freeze, Python-200 suite selection and source
registries under `artifacts/` and `benchmark/`.

## Paper-Candidate Result Audits

| Path | Condition |
| --- | --- |
| [Frozen Python-150 archive audit](paper_analysis/python150_frozen_20260803/README.md) | Task-level recomputation of the supplied frozen result bundle |
| [Paper analysis index](paper_analysis/README.md) | Available generated paper analyses and their boundaries |

Only results classified in [docs/STATUS.md](../docs/STATUS.md) may enter current paper tables.
Historical pass counts must not be relabeled as current Main.

## Historical Model and Process Evidence

| Path | Boundary |
| --- | --- |
| `python150_compliant_20260726/` | mixed-snapshot candidate suites |
| [Failure attribution](failure_attribution_20260720/README.md) | historical trajectory failure analysis |
| [Token efficiency](token_efficiency_20260720/README.md) | historical token/context/process analysis |
| [Repo graph phase 1](repo_graph_phase1/README.md) | infrastructure evidence |
| [Repo graph phase 2](repo_graph_phase2/README.md) | smoke and A/B evidence |
| [Repo graph phase 3](repo_graph_phase3/README.md) | prototype evidence |
| `archive/` | old construction, freeze and run provenance |

Historical classification methods may be reused; absolute results remain tied to their original
task snapshots and experiment conditions.

## New Report Requirements

A paper-candidate report must record:

- suite/task-set and freeze/selection IDs;
- model revision, agent profile, arm and attempt policy;
- agent/evaluator image identities;
- Functional Pass@1 separately from agent completion status;
- exact missing, context, rate-limit, infra and rerun ledger;
- compactness and cost metrics with completeness caveats;
- source archive or suite checksum and reproducible analysis command.

Experiment policy and reporting requirements are defined in
[docs/EVALUATION.md](../docs/EVALUATION.md); current interpretation is maintained in
[docs/STATUS.md](../docs/STATUS.md).
