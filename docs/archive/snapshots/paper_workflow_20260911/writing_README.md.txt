# Paper writing working materials

> **Documentation status: reference · Last verified: 2026-09-08**

The current writing plan is [PAPER_OUTLINE.md](../PAPER_OUTLINE.md).
The user approved proceeding directly to LaTeX with populated data tables and
figure placeholders. The current editable draft is `../main.tex`, which follows
the eight-section outline. `manuscript.tex` is an earlier intermediate, retained
only as assembly history. Edit `../main.tex` for all further prose revisions.

`original_main_20260907.tex` and `original_references_20260907.bib` preserve the
user's starting files. `related_work.tex`, `verified_references.bib`, and
`sources.md` preserve related-work source material and verification notes.

The active bibliography is `../references.bib`. Its latest metadata and version
decisions are documented in [BIBLIOGRAPHY_REVIEW.md](BIBLIOGRAPHY_REVIEW.md);
`bibliography_validation.json` records citation and field checks. Historical
bibliography copies above are not synchronized with the active file.

`update_tables.py` regenerates six marked tables and four short result-text blocks from saved evidence;
`--check` verifies agreement without modifying the paper. It also audits all
900 retained run profiles. `table_validation.json` records input hashes and QA.
The current manuscript additionally contains one authored related-work table
(`tab:positioning`), giving seven tables in total: three main and four appendix.
The updater preserves that authored table.
`assemble_initial_draft.py` is the historical one-time assembler; do not rerun it
after editing the paper, because it overwrites the prose from the intermediate.

`known_defect_sensitivity.py` and its JSON output summarize existing results
after excluding seven task IDs flagged by the existing first-pass analysis.
They do not run agents or alter frozen results. Their original provenance caveat
describes the earlier audit scope; the historical JSON is preserved.

The [2026-09-08 offline audit](../../../reports/paper_analysis/python150_offline_audit_20260908/README.md)
adds per-task input alignment: 900 initial prompts, recorded source identities
and locks align with v2, and all 838 saved functional-capsule digests match.
Runtime image IDs remain unreconciled with the release/oracle manifest; the
full local task-tree check also has 25 exceptions. The paper states these limits.
The separate 14-artifact defect recheck supports six candidates and leaves the
pytest accessor policy ambiguous. It adds a 144-task sensitivity beside the
original 143-task view without overwriting old annotations. All semantic review
remains L1, not independent human L2.

The table updater checks the audit's source hashes before using its alignment
claim and records the new audit files in `table_validation.json`. Do not rerun
the historical assembler. The current workflow edits LaTeX only and does not
compile or render the document.

The subsequent narrative revision follows the user's priority to complete the
outline before further detail audits. It rewrites the abstract, introduction,
contributions and conclusion, adds section transitions, and expands related work
around source evidence, output boundaries and evaluation targets. It retains the
five figure placeholders and all existing numeric results. Primary-source checks
for the literature comparison are appended to `sources.md`.

Chapter 2 now expands task construction, validation layers, and dataset coverage.
`CHAPTER2_EVIDENCE.md` maps its claims to local sources.
`chapter2_evidence.py` generates a complete 200-task JSON index and aggregate
evidence without running evaluations. It keeps current frozen identities separate
from historical taxonomy, including 44 source-commit mismatches and the extension's
planned lift-label status. The dataset table adds snapshot counts and distinguishes
38 LLM-reviewed repairs from six maintainer-proxy adjudications.

Chapter 5 now develops two cases from four separately inspected Pro/Flash
artifacts: incomplete project-metadata input coverage in poetry-core and a
call path bypassing brace expansion in tox. `CHAPTER5_CASE_EVIDENCE.md` explains
the selection and links each discussion direction to an existing finding;
`chapter5_case_evidence.json` indexes code locations and source digests.
Historical annotations, exclusion sets, and all data tables remain unchanged.
The expanded discussion distinguishes observed implementation mismatches from
unverified agent interventions and process-cause claims.

The [table information-density review](TABLE_INFORMATION_DENSITY_REVIEW.md)
records the earlier table revisions. The 2026-09-09 naming revision supersedes
its group-based presentation: the paper uses FeatureLiftBench, with 200 release
tasks and a common 150-task evaluation coverage. No temporary batch names define
benchmark difficulty tiers. The composition cross-tab and group-based regression
leave the paper; lift-type counts use text, and Fig. 4 shows overall solve frequency.
The generated main tables are `main` and `paired`, plus the authored literature
comparison. Four appendix tables provide exact outcomes and footprint summaries.
Original results, annotation records, and historical statistical fits are preserved.

The task taxonomy revision adds four entanglement categories to Section 2.4:
code dependencies, data and state, framework mechanisms, and environment and
resources. Lift types describe the requested transformation; entanglement
categories describe dependencies and allow multiple labels per task. Appendix A
and `CHAPTER2_EVIDENCE.md` record the mapping from the ten existing mechanism
labels. This revision adds definitions and examples without changing annotations
or introducing category counts or performance comparisons.
