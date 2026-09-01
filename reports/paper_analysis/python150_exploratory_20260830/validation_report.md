# Python-150 analysis validation report

> **Decision: share with caveats · Verified: 2026-08-30**

## Checks passed

- The source has 600 unique model-task rows: four model configurations by the
  same 150 task IDs, with no duplicate key pairs.
- The taxonomy contains 150 unique task IDs and joins to every analyzed task.
- Headline Functional Pass totals independently recompute to 99, 59, 59, and
  27; the total is 244 passing model-task rows.
- The task-solvability distribution recomputes to 42 tasks solved by zero
  models, 29 by one, 33 by two, 35 by three, and 11 by all four.
- Lift-type and feature-family task counts each sum to 150.
- The SQLite snapshot agrees with the generated CSV summaries.
- The notebook executes from top to bottom with no error outputs.
- All seven PNG figures passed visual inspection at publication-scale
  resolution. Each corresponding PDF is a valid single-page vector figure.
- The interactive report artifact passed schema and bounded-snapshot validation
  before rendering.

## Evidence boundary

The result matrix is appropriate for exploratory analysis and paper-figure
development, but it is not eligible for the final Python-200′ main table:

- 12 rows have no evaluator output and are counted as non-passes under the
  archived result contract.
- 48 rows violate the declared context allowance.
- The archived evaluator image identity differs from the active paper freeze.
- Feature-family and lift-type comparisons are descriptive because task
  selection is non-random and the taxonomy labels are AI-assisted.
- Compactness statistics are conditioned on Functional Pass, so models are
  compared over different survivor sets.

## Recommended use

Use the analysis to select hypotheses, tables, and figure forms for the paper.
Replace the underlying matrix with fully eligible Python-200′ results before
claiming a final leaderboard or population-level task-difficulty effect.
