# FeatureLiftBench FSE LaTeX Draft

> **Status: draft · Last verified: 2026-08-30**

This directory contains the ACM `acmart` LaTeX zero draft derived from the
paper evidence under `docs/paper/`.

## Build

From this directory:

```bash
latexmk -pdf -interaction=nonstopmode -halt-on-error main.tex
```

Clean generated files without removing the PDF:

```bash
latexmk -c
```

## Evidence boundary

- Red `Draft note` text marks claims or metadata that must be filled only from
  the frozen paper bundle.
- `132/200` is a received-suite audit headline, not the paper leaderboard.
- `21.5%--72.5%` belongs to the superseded Python-150 + External-50 suite and
  appears only as historical context.
- The main table must use eligible Python-200′ runs with attested source,
  context, dependency, model, agent image, and evaluator image identities.

The Markdown argument draft is
[../00_manuscript_zero_draft.md](../00_manuscript_zero_draft.md). The structural
mapping to Harness-Bench is
[../01_harness_bench_structure_mapping.md](../01_harness_bench_structure_mapping.md).
Generated numeric tables live in [tables/](tables/) and are filled from the
Python-150 exploratory CSVs plus the Python-200′ received-suite summary. They
are not the eligible leaderboard.

