# Paper writing materials

> **Status: current · Last verified: 2026-09-11**

Edit [main.tex](../main.tex) and [references.bib](../references.bib). The outline is [PAPER_OUTLINE.md](../PAPER_OUTLINE.md). All five figures are present; older placeholder notes are historical.

The current data selection is [paper_sources.json](../paper_sources.json). Shared paths, model order and labels come from [paper_inputs.py](../paper_inputs.py). Start with [WORKFLOW.md](../WORKFLOW.md).

## Active code

| File | Role |
| --- | --- |
| `update_tables.py` | Five numeric tables and two numeric text blocks; preserves other prose |
| `comprehensive_table.py` | Correctness, artifact and efficiency panels in the main table |
| `update_structure_results.py` | Appendix structure table from the common 150 tasks |
| `chapter2_evidence.py` | Rebuilds saved construction evidence and the 200-task index; run only when intentionally refreshing those derived files |

The standard entrypoint is `python -B scripts/paper.py check` from the project root. It checks the 200-task benchmark and 150-task common comparison against the current tables. Use `tables` to update generated blocks. Neither command runs models, task code, or LaTeX.

The table generator checks task membership, duplicate cells, functional gates, denominators, paired values and recorded run profiles. Historical sensitivity analysis and historical environment reconciliation are separate records, not prerequisites for producing current numeric tables.

## Current supporting material

- `chapter2_task_inventory.json` and `chapter2_evidence.json`: task identities and construction evidence. The repair-round fields in the latter do not describe the later author review.
- `author_review_statement.json`: author's confirmation of review of all 200 retained tasks.
- `chapter5_case_evidence.json` and [case discussion notes](CHAPTER5_CASE_EVIDENCE.md): selected saved-artifact illustrations.
- `controlled_difficulty_evidence.json`: construction-cohort analysis.
- `structure_results.json`: category denominators and outcome counts.
- [BIBLIOGRAPHY_REVIEW.md](BIBLIOGRAPHY_REVIEW.md): current bibliography decisions.

## Historical code and notes

`assemble_initial_draft.py` is a one-time historical assembler that overwrites prose; it is not part of the current workflow. `manuscript.tex`, original draft copies, older repair/sensitivity scripts, image-identity checks and dated revision notes remain for traceability. Their statements describe their dates and scopes, not automatically the current paper.

No task definitions or raw results are changed by this cleanup. Earlier README text is preserved in the [documentation snapshot](../../archive/snapshots/paper_workflow_20260911/README.md).
