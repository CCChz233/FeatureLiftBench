# FeatureLiftBench FSE LaTeX Draft

> **Status: draft · Last verified: 2026-09-06**

This directory contains the ACM `acmart` LaTeX draft derived from the
paper evidence under `docs/paper/`.

## Build

From this directory:

```bash
latexmk -pdf -interaction=nonstopmode -halt-on-error main.tex
```

## Evidence boundary

- Headline leaderboard: freeze~v2 **Python-150**, Official Main, five
  OpenHands backends (Pro 115/150 \ldots OSS 36/150).
- Freeze ID
  `6c20ff0307762503a73cbb9ff32e9992c6446e4b17483a68373027be58cbf419`,
  images `python200-prime-212930ea`.
- Official Hard-50 is appendix-only and is not the difficulty claim.
- Functional Pass = build ∧ public ∧ hidden ∧ isolation; empty submissions
  fail; do not use `run.status`.
- Finding 3 is an assistant L1 close-read on Pro+Flash ($n=63$), not gold.

The Markdown argument draft is
[../00_manuscript_zero_draft.md](../00_manuscript_zero_draft.md).
Numeric tables live in [tables/](tables).
