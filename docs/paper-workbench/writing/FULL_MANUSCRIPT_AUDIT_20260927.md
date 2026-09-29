# Full manuscript audit — 2026-09-27

Scope: `docs/paper/main.tex` and its eight figures, under the current `acmsmall`
template. The manuscript is based on the user-supplied 2026-09-26 ZIP. The
pre-audit snapshot is
`docs/archive/paper_cleanup_20260929/package_snapshots/paper_pre_full_audit_20260927_100422.zip`.

## Changes made

- Removed the DSE Table 5. It duplicated Fig. 4(c) and grouped Luna Contract
  Only with the non-agent relocation procedure. The same counts now appear in
  the Fig. 4(c) caption and RQ2 text. The source-exposure table becomes Table 5
  after automatic LaTeX renumbering.
- Replaced “Spec-only” in Fig. 4(c) with “Luna CO” and explained the abbreviation
  in the caption. Fig. 4(c) now uses the same 0–100% pass-rate scale as Fig. 4(a).
  The three panels remain separate PDF assets assembled in LaTeX.
- Changed Table 2’s RRES and Copy summaries from “Median [IQR]” to
  “Median [Q1, Q3]”; the displayed numbers are the first and third quartiles.
- Clarified that Fig. 8(b)’s negative adjusted Copy values are below the
  configuration-effect center, and added per-configuration sample counts.
- Recast Table 1 as a five-dimension qualitative comparison at the author's
  request. It now preserves the original concepts of source availability,
  explicit task information, cross-boundary transfer, output independence, and
  evaluation context without forcing ambiguous binary classifications. It
  separates SWE-bench from SWE-bench Pro and distinguishes FeatureBench L2's
  source-restored tests from FeatureLiftBench's source-free package evaluation.
  Primary references checked include [SWE-bench Pro](https://arxiv.org/abs/2509.16941),
  [FeatureBench](https://arxiv.org/pdf/2602.10975),
  [FeatBench](https://arxiv.org/pdf/2509.22237), and
  [RepoZero](https://arxiv.org/pdf/2605.07122).
- Corrected the DSE failure paragraph to distinguish the first failed gate
  from independent error observations. Softened causal language around the
  diagnostic comparison.
- Expanded Threats to Validity to cover single-run pass rates, the 40-task
  ablation, finite test coverage, purposive case review, checkpoint recovery
  samples, success conditioning, and token provenance.
- Replaced the unresolved anonymous URL with truthful draft wording in Data
  Availability and left a source comment to insert a verified URL before
  submission.
- Excluded three unreferenced legacy figure PDFs with outdated model labels
  from the Overleaf package manifest. Their local copies and the pre-audit
  snapshot remain available for provenance.

## Evidence and validation

- Main evaluation: 150 tasks × 6 configurations = 900 model–task cells; the
  stored pass counts are Pro 115, Flash 108, Luna 102, GLM 68, Qwen 63, OSS 36.
- Table 2 and Table 3 values were reconciled with the selected task-level and
  saved summary data. Table 4’s 40-task paired counts, intervals, and adjusted
  p-values were reconciled with the retained ablation statistics.
- Fig. 4(c): DSE 10/40, Luna Contract Only 9/40, Full Source Luna 23/40,
  Pro 25/40, Qwen 12/40. DSE’s 30 first failures are Build 11, Primary 16,
  Extended 3. Its all-artifact overlap median is 99.14%.
- Source-exposure table: source-mapped entrypoints 607/641; 145/150 tasks have
  at least one mapping. Primary/Extended-first failures with confirmed reads
  are 241/303 (79.5%).
- Fig. 7 uses separate recoverable samples of 317 and 403. Fig. 8 includes
  485 successful artifacts across 115 tasks; model counts 113, 107, 99, 68,
  63, and 35 sum to 485.
- The bibliography has 29 cited keys, 32 entries, no missing or duplicate
  citation keys. `scripts/paper.py check` validates 13 referenced figure assets
  and no unresolved LaTeX references. The 2026-09-27 full-project PDF compiled
  to 20 pages with no overfull boxes, undefined references, or citation warnings.
  After the later Table 1 expansion, a no-PDF `pdflatex -draftmode` check found
  no source error or overfull box. The built-in editor compiler could not load
  `figures/fig01_overview.png` from this multi-file project, so the expanded
  Table 1 has not been verified in its rendered PDF preview.

## Items still requiring author action

1. Supply and verify the anonymous artifact URL, then update Data Availability.
   The current paragraph explicitly says the package is being prepared.
2. Preserve or supply corrected per-run provider-usage records for Luna and GLM
   if independent recomputation of their token totals is required. Current
   quantiles use author-confirmed aggregate totals; the retained local data do
   not contain complete corrected per-run records for those two configurations.
3. If space permits, enlarge small internal labels in the author-created raster
   Figures 1, 2, and 6. Their text was checked for terminology, but it remains
   small at the printed `acmsmall` size.

These checks support internal consistency of the selected evidence and rendered
paper; they do not establish that protected tests are complete or that every
external benchmark has exactly the same evaluation contract.
