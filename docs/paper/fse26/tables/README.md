# Generated analysis tables for the FSE draft

> **Status: derived · Last regenerated: 2026-09-02**
>
> **Not the Python-200′ leaderboard.** Regenerated from exploratory CSVs.

## Regenerate

From the repository root, with a Python that has `pandas`:

```bash
cd reports/paper_analysis/python150_exploratory_20260830
python3.12 export_latex_tables.py
```

Sources:

- `reports/paper_analysis/python150_exploratory_20260830/tables/*.csv`
- `reports/paper_analysis/python200_hard_main_20260829/summary.json`

## Contents

| File | Role |
| --- | --- |
| `tab_python150_*.tex` | Frozen Python-150 four-model exploratory matrix |
| `tab_python200_*.tex` | 2026-08-29 received package, eligibility-blocked |
| `tab_python200_standard_labels.tex` | freeze v2 contract labels **200/0**; not a leaderboard |
| `tab_python200_eligibility_slice.tex` / `tab_python200_fixed116_*.tex` / `tab_python200_violators.tex` | predecessor freeze `474862c2` labels × 2026-08-29 received package; 81/96 stays here |
| `tab_python200_c4_advisory.tex` | predecessor advisory overlaps vs freeze v2 C4 = 0 |
