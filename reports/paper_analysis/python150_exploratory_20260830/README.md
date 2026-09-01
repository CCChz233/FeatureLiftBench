# Frozen Python-150 exploratory analysis

> **Status: exploratory · Last verified: 2026-08-30**

This directory analyzes the four-model frozen Python-150 result matrix as a
trial run for the paper's later Python-200′ analysis. It does not replace the
final Python-200′ leaderboard.

## Scope

- 150 frozen tasks.
- Four OpenHands model configurations.
- 600 unique model-task rows.
- Functional Pass@1 is the primary metric.
- Correctness, interaction volume, and compactness are reported separately.

## Outputs

- `python150_analysis.ipynb`: executed, reproducible analysis notebook.
- `figures/`: PNG previews and PDF paper figures.
- `tables/`: exact machine-readable result tables.
- `export_latex_tables.py`: writes `docs/paper/fse26/tables/*.tex` from those CSVs.
- `analysis_summary.json`: headline results and data-quality status.
- `data_quality.json`: input grain, completeness, and eligibility checks.
- `chart_map.md`: question, chart family, supported claim, and caveat per figure.
- `analysis.sqlite`: queryable snapshot of source and derived analysis tables.
- `artifact.json`: bounded report payload used by the Data Analytics reader.

## Reproduce

From the repository root:

```bash
MPLCONFIGDIR=/tmp/featureliftbench-mpl-cache \
  python3.12 reports/paper_analysis/python150_exploratory_20260830/analyze_python150.py

cd reports/paper_analysis/python150_exploratory_20260830
python3.12 export_latex_tables.py

MPLCONFIGDIR=/tmp/featureliftbench-mpl-cache \
  python3.12 -m jupyter nbconvert --execute --to notebook --inplace \
  reports/paper_analysis/python150_exploratory_20260830/python150_analysis.ipynb
```

## Evidence boundary

The archived Python-150 matrix is suitable for exploratory analysis and figure
development, but not for the final Python-200′ main table. The evaluator image
identity differs from the active paper freeze, and 48 rows trigger the archived
context-policy audit. Missing evaluator records are counted as non-passes in
accordance with the archived result contract.
