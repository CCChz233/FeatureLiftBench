# FeatureLiftBench v1.1 execution protocol

This protocol turns the four-week hardening plan into executable gates. It does not claim that human review is complete when only scaffolding exists.

## Current execution snapshot

The live status is generated in `V11_IMPLEMENTATION_STATUS.md`; this protocol remains the normative gate definition. As of the current repository state:

- Oracle freeze `5f9012f6dc748c90` produced 450/450 results: 150 stable passes and 0 versioned quarantine tasks, with no unstable or incomplete tasks. Prior freeze `607e70aee2394d48` (137+13 quarantine) is superseded; see `benchmark/quarantine/python_v1_1_revision_3.json` and [ORACLE_REVALIDATION_REPORT.md](ORACLE_REVALIDATION_REPORT.md).
- Diagnostic-40 has file-level closure marked complete by AI-assisted review, but 0/40 has completed the required independent human adjudication. Symbol/runtime/minimality conclusions remain scope-limited.
- All 150 behavior contracts map public and hidden test nodeids to public clauses; all 150 still require independent human review for paper release.
- The engineering Pilot is frozen at revision 5 (`c94764ed110992a6`) with provisional AI-assisted annotations. This permits pipeline diagnostics, not paper-ready annotation claims.
- No Pilot cell has run. Execution is separately blocked pending explicit authorization for exporting the Pilot-10 public assets and condition prompts to the configured DeepSeek/OpenHands services.

## Scope and immutable compatibility

- Python150 is the full evaluator/specification audit population.
- Representative-20 and Challenge-20 are reported separately; Challenge-20 must not estimate Python150 prevalence.
- Pilot-10 supports mechanism diagnosis, not population performance estimation.
- `Hard50`, task IDs, split values, paths, manifests, and historical run IDs remain unchanged. Hard50 metadata adds only `split_role: mechanism_challenging`.
- `ECSM-Prompt` denotes a structured prompting protocol, not a native controller.

## Reproducible asset generation

```bash
python tools/research_analysis/build_v11_diagnostic_subset.py
python tools/research_analysis/materialize_v11_audit_assets.py --check
python tools/research_analysis/build_v11_audit_status.py
```

`representative20_constraint_audit.json` repeats taxonomy version/hash and selection mode on every constraint row. After taxonomy adjudication it must be regenerated. A failed constraint changes `selection_mode` to `maximum_coverage`; reports must then name uncovered values rather than claim full coverage.

Behavior clauses are authored from `metadata.feature.included_behaviors` before test-node mapping. `evaluation/behavior_contract.json` is evaluator-private: hidden nodeids, inputs, examples, and assertions must never enter prompts or public reports. Automatic token matching is only a review queue.

Diagnostic closure assets import legacy file hints. The current AI-assisted pass marks file scope complete for 40/40 tasks, but that status is provisional: two human reviewers must still independently decide necessity, replaceability, runtime/resource state, accepted substitutes, evidence, and closure variants before paper adjudication. Symbol/runtime/minimality claims may only use tasks whose corresponding annotation scope is complete.

## Closure score semantics

The shared loader in `harness/featureliftbench/closure_gold.py` uses:

1. `evaluation/closure_gold.json`;
2. `oracle_manifest.required_source_files`;
3. legacy `oracle_manifest.source_files`;
4. an unavailable result, never an empty gold set.

Recall is counted over requirement groups. One original symbol, approved adapter, or approved reimplementation may each fully satisfy the same requirement, but the requirement enters the denominator once. Extra satisfied alternatives increase `redundant_alternative_count`; optional requirements do not enter recall. Only a complete annotation scope produces P/R/F1, and multiple variants are scored independently with the best variant and evidence retained.

## Oracle freeze and gate

Create one immutable evaluator/task/oracle/image manifest:

```bash
python tools/research_analysis/run_v11_oracle_validation.py freeze
python tools/research_analysis/run_v11_oracle_validation.py canary \
  experiments/v1_1_oracle_validation/<freeze_id>/freeze_manifest.json --workers 1
```

The canary is exactly five tasks × three fresh Docker work directories. Full revalidation is refused unless the same freeze has a passing 15-run summary. Then:

```bash
python tools/research_analysis/run_v11_oracle_validation.py full \
  experiments/v1_1_oracle_validation/<freeze_id>/freeze_manifest.json --workers 1
```

Canary runs never count toward the 450 full runs. Outputs are versioned beneath the freeze ID; historical experiment directories are not edited. Unstable tasks enter `quarantine_manifest.json`, not physical deletion.

The 62 historical infrastructure failures are enumerated by `build_infra_reeval_manifest.py` and must be reevaluated into a new output root with `harness/scripts/reeval_suite.py --output-dir ...`. The source suite digest is recorded.

## Control feasibility preflight

```bash
python tools/research_analysis/build_control_preflight_submissions.py --force
python tools/research_analysis/analyze_control_preflight.py
```

The automated gate checks three stable alternative passes per task, functional copy-heavy controls recognized by the footprint vector, and public-runnable narrow controls rejected by hidden behavior. Person-hours and non-environment rework rounds require human time logs; the analyzer records them as NA rather than inferring effort.

## Pilot freeze and invalidation

Two freeze levels are distinguished:

1. An **engineering Pilot freeze** may be created when automated integrity, Oracle stability, Pilot-10 contract checks, provisional Diagnostic closure, control functionality, and the release-gate script all permit it. Its `evidence_status` must remain `provisional_ai_assisted_annotations`, and it cannot support paper-ready annotation claims.
2. A **paper-ready freeze** additionally requires all independent-human review gates. Only this level may be cited as adjudicated benchmark evidence.

Immediately before the first cell, verify or create the engineering freeze:

```bash
python experiments/ecsm_pilot/pilot_freeze.py create
python experiments/ecsm_pilot/run_pilot.py --stage A --execute
```

Every cell verifies the freeze. A task-local asset change requires `pilot_freeze.py revise --scope task --task-id ...` and supersedes all seven arms for that task. Evaluator, Docker, tools, or global protocol changes require `--scope global` and supersede all completed cells. Revisions never overwrite old results.

Before any actual cell, the operator must also have explicit authorization covering the Pilot-10 public `TASK.md`, metadata, public source snapshots, public tests, condition prompts, and non-hidden Oracle hints. Hidden tests, hidden nodeids, behavior contracts, hidden inputs, examples, and assertions remain excluded. Authorization is an execution/privacy gate and is independent of engineering or paper readiness.

Stage A runs 14 cells. Stage B runs 20 cells and its threshold controls resource allocation only. `run_pilot.py --stage C --execute` refuses to run unless the analyzer has written a passing resource decision. Failure to trigger the four-task gate is not evidence that a mechanism is false.
