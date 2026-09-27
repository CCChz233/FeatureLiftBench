# Prospective 100-task RQ2 extension: selection and reporting plan

Status: task membership frozen on 2026-09-27; no 100-task agent evaluation has been run. This document records how to describe a possible extension of the current 40-task paired ablation. The decision to consider expansion was made after the 40-task results were known. The identities of the 60 additional tasks were selected from frozen task metadata without using model or evaluator outcomes.

## Population and selection

The population is the same fixed Python-150 task set as the main comparison. Preserve the original six strata: construction cohort (`earlier` core100; `later` hard50) crossed with lift type (Direct, Adapted, Composite). For target size 100, allocate each stratum proportionally to its size in 150 using floor allocation, then distribute remaining places by descending fractional remainder, breaking ties by stratum key. Within each stratum, order task IDs by SHA-256 of the original seed, purpose `selection`, and task ID. Select the first `sample_n` entries. No success, failure, model output, DSE outcome, or test result enters the ranking or quota computation.

The current paper inventory file is not byte-identical to the inventory in the original 40-task manifest. The selector verifies that all six population stratum sizes match and that cohort, lift type, and source snapshot agree for every original 40-task record. Both inventory hashes and the original manifest hash are saved in `source_ablation_100.json`.

| Stratum | Population | Original 40 | New target 100 | Additional |
| --- | ---: | ---: | ---: | ---: |
| Earlier · Adapted | 44 | 12 | 30 | 18 |
| Earlier · Composite | 3 | 1 | 2 | 1 |
| Earlier · Direct | 53 | 14 | 35 | 21 |
| Later · Adapted | 32 | 8 | 21 | 13 |
| Later · Composite | 15 | 4 | 10 | 6 |
| Later · Direct | 3 | 1 | 2 | 1 |
| **Total** | **150** | **40** | **100** | **60** |

The resulting sample contains 37 Direct, 51 Adapted, and 12 Composite tasks from 86 repositories. All original 40 tasks are nested in the 100. The machine-readable task IDs and file identities are in `source_ablation_100.json`; `source_ablation_100.txt` lists just the IDs. Reproduce and check with `python -B docs/paper-workbench/experiments/select_tasks_100.py --check`.

## Experimental and reporting rule

If Luna is the 100-task primary ablation, run **both** Full Source and Contract Only anew on all selected 100 tasks with frozen, identical model–harness settings within each pair. The 40-task outcomes remain a separate historical analysis; they are not substituted into the new 100-task campaign. Existing Pro and Qwen 40-task paired outcomes provide cross-configuration evidence at a different sample size. The 100-task sample was selected before its new runs, but after the 40-task findings; do not call the entire study outcome-blind or preregistered.

The primary statistic is the within-task Full Source minus Contract Only functional-pass difference on 100 tasks. Report the two pass counts, Full-only and Contract-only discordant pairs, the paired effect and uncertainty, and undelivered submissions separately. Show effects by construction cohort and lift type descriptively; Composite has only 12 tasks. A repository-cluster resampling sensitivity check addresses multiple tasks from some repositories. The interval describes variation across tasks/repositories, not repeated-run stochasticity. Predefine handling of provider or infrastructure failures and preserve all attempts. Do not compare the new Contract Only runs against historical main-comparison Full Source cells as if they were matched experimental arms.

The paper's current RQ2 wording, table, and Fig. 4 describe the historical 40-task three-configuration study. Update them only after the 100-task campaign is completed and independently checked. Separate sample sizes clearly in captions and tables; DSE remains the 40-task diagnostic unless a new DSE-100 study is explicitly frozen and run.

## Suggested Methods text after completion

> To examine the breadth of the repository-evidence effect, we expanded the original 40-task ablation sample to 100 tasks from the fixed Python-150 population. We stratified tasks by construction cohort and lift type and allocated places proportionally using the largest-remainder rule. Within each stratum, we used the original fixed SHA-256 ranking of task IDs; the resulting sample retains all 40 original tasks and adds 60. The expansion decision followed inspection of the 40-task findings, while selection of the additional task IDs used only frozen task metadata. For the 100-task analysis, we ran both Full Source and Contract Only conditions anew on every selected task under matched model–harness settings. The original 40-task, three-configuration results are reported separately.

Use the final sentence only if both arms really are rerun for all 100 tasks. If only the additional 60 are run, change it to describe a two-campaign combined analysis and report old/new cohort sensitivity; do not claim a uniform new campaign.
