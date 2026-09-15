# Failure-analysis feasibility — 2026-09-15

This is a material inventory, not semantic annotation. No paper changes or experiments were performed.

The proposed sample is 241 behavioral-first failures with confirmed explicit entrypoint source reads (89 unique tasks). Current indexed raw files support 65 runs: Pro 29/29, Flash 34/34, Luna 0/33, GLM 2/36, Qwen 0/43, OSS 0/66. All 241 task contract/test packages remain available. For these 65 runs, run/evaluator JSONs parse, submission Python files and first-gate logs are non-empty, and event files exist. This is not a guarantee of evidence sufficiency on close reading.

The retained `experiments/paper-results-full-20260913T154543Z.tar.gz` was scanned without extraction and ends with `ReadError: unexpected end of data`. Its readable portion contains Pro/Flash and only the start of GLM; it does not supply the missing later suites.

176 run directories need recovery; see `missing_run_directories.txt`. Recover original run.json, eval/result.json, eval/logs, submission, and agent events for the exact retained runs; do not substitute rerun results or older suites. No alternate raw run.json/result.json/events files for the missing Luna/Qwen/OSS suites were found in the searched experiments/archive/reports trees.

Prior L1 annotations contain 122 rows (77 Pro/Flash census plus 45 Luna/Qwen/OSS postsample), of which 89 intersect the 241-run scope. Do not mix the historical postsample into a census. None of these intersecting rows has independent human review. Prior evidence packets contain truncated clauses/logs and selected implementation snippets; they do not replace raw submissions for a new close-read study.

18 intersecting historical annotation rows across five tasks carry benchmark-invalid-candidate flags. These are prior unresolved/adjudication-dependent flags, not new defect verdicts. The later seven-task audit is also assistant first-pass and reports both supported and ambiguous candidates. Revisit validity before assigning agent-cause denominators; 241 is a candidate count, not an established valid-agent denominator.

Practical path: begin an explicitly scoped Pro/Flash study of all 63 source-exposed behavioral failures while recovering the other 176 original run directories. Do not present the 65 available records as a representative six-model sample. Use the existing protocol's observable primary categories and separate secondary contract-dimension tags; review each retained artifact independently. Keep unknown and validity candidates visible.

The local SOP defines L1 as assistant_first_pass and requires L2 independent human dual review before main-text root-cause proportions (20–30% sample plus all unknown, defect and Hidden-only cases). Repeated AI passes are not independent human review. The assistant can prepare L1 annotations, evidence packets, summaries, figures and tables; author review must be accurately attributed.

Outputs: `feasibility.json`, `material_inventory.csv`, `missing_run_directories.txt`, `archive_check.json`. Re-run `python -B reports/paper_analysis/failure_feasibility_20260915/check_materials.py` after restoring evidence. The referenced older chapter gate document was not found in the current docs file inventory; the present SOP and Protocol still specify the applicable evidence tiers.
