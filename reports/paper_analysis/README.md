# Paper analysis

> **Status: current index · Last verified: 2026-09-11**

The paper uses one 200-task benchmark, with a common 150-task comparison across six configurations and an additional 50-task evaluation across five configurations.

Start with [the paper workflow](../../docs/paper/WORKFLOW.md). Its [input manifest](../../docs/paper/paper_sources.json) selects exact files; directory names and dates alone do not define current evidence.

## Inputs used by the current paper

| File or directory | Current use |
| --- | --- |
| `python150_prime_v2_analysis_20260905/task_results.csv` | 900 retained model–task outcomes, 150 common tasks, six configurations |
| `python150_paper_analysis_final/json/stats.json` | Saved paired statistics and solve-frequency counts |
| `python150_paper_analysis_final/csv/main_table.csv` | Saved summary checked against task-level calculations |
| Model run directories listed in the input manifest | Recorded run profiles and evaluator outputs for the remaining 50 tasks |

Main passing counts, in the manifest's model order, are 115 / 108 / 102 / 68 / 63 / 36. The current numeric generators use all 150 common tasks and do not apply a historical exclusion set.

## Historical analyses

Earlier campaign summaries, pilots, sensitivity analyses, task audits and draft README narratives remain at their original paths. Only files selected by the manifest feed the current numeric workflow. A directory used for a numeric CSV can also contain historical prose that has not been updated; treat those files by their own scope.

The previous index is preserved in the [documentation snapshot](../../docs/archive/snapshots/paper_workflow_20260911/README.md). Current results and naming are summarized in [STATUS.md](../../docs/STATUS.md).
