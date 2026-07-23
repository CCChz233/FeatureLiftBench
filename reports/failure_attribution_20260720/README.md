# Failure attribution audit — 2026-07-20

This directory contains the strict failure-attribution analysis for the frozen 550-run Python OpenHands corpus.

Primary deliverables:

- `failure_attribution_report.md` — answer-first technical report in Chinese.
- `failure_attribution_analysis.ipynb` — executed, reproducible notebook.
- `trajectory_stage_labels_550.csv` — A–N stage evidence and earliest-failure labels.
- `representative_case_dossiers.md` — 16 trajectory/evaluator case reviews.
- `build_failure_attribution.py` — deterministic dataset and summary builder.
- `build_notebook.py` — notebook generator/executor.
- `artifact.json` and `build_artifact.py` — validated MCP report payload and builder.
- `validation.md` and `validate_failure_attribution.py` — independent consistency checks.

Supporting tables:

- `outcome_funnel.csv` and `failure_funnel.csv`
- `failure_stage_distribution.csv` and `failure_stage_by_model.csv`
- `dynamic_comparison.csv`, `dynamic_by_model_split.csv`, and `dynamic_tier_comparison.csv`
- `task_type_outcomes.csv`, `hypothesis_summary.csv`, and `regression_results.csv`
- `data_quality.json` and `analysis_summary.json`

Reproduce from the repository root:

```bash
python reports/failure_attribution_20260720/build_failure_attribution.py
python reports/failure_attribution_20260720/build_notebook.py
```

Starting a Jupyter kernel can require permission to bind local loopback ports in a restricted sandbox.
