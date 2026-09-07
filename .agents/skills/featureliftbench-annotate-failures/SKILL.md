---
name: featureliftbench-annotate-failures
description: Annotate FeatureLiftBench artifact-level failures into semantic root causes for paper section 5.3 / Finding 3. Use when labeling functional failures, contract-closure vs localization, failure taxonomy, FAILURE_ANALYSIS_PROTOCOL, FAILURE_ANALYSIS_SOP, or writing F3-compliant annotation CSVs.
---

# FeatureLiftBench Annotate Failures

Canonical operator SOP (Chinese): `docs/FAILURE_ANALYSIS_SOP.md`.  
Label definitions and denominators: `docs/FAILURE_ANALYSIS_PROTOCOL.md`.  
Finding 3 write-gate: `docs/paper/08_experimental_analysis_chapter.md` §5.3.

## Guardrails

- Do not mutate `suite.json`, eval logs, submissions, or frozen task packages.
- Do not treat empty submissions as 5.3 rows; they stay in 5.2.1.
- Do not infer `root_cause_primary` from the last evaluator line or from evidence-packet summaries alone.
- Do not publish Hidden test names, inputs, or assertions.
- Do not write Finding 3 from an L0 residual bucket. Record evidence tier (L0 screen / L1 close-read / L2 dual review) in the report.
- AI doing two passes is not independent human dual review.
- Record task/evaluator defects; do not silently edit the freeze to make this suite look cleaner.

## Workflow

Copy and track:

```text
- [ ] 4.1 Identity: freeze, image, suite dirs, split, models in scope
- [ ] 4.2 Mechanical funnel (no semantic labels)
- [ ] 4.3 L0 public-test vs required_api defect screen
- [ ] 4.4 L1 close-read every valid artifact failure in scope
- [ ] 4.5 Trajectory layer only if claiming process mechanism
- [ ] 4.6 Aggregate with tiers; apply Finding 3 gate
- [ ] 4.7 L2 human review or explicitly leave first-pass
```

Default scope for a paper 5.3 pass: **all artifact failures of the strongest 1–2 models**. Other models are a later sample. Unfinished suites stay out.

### L0 defect screen

For each `public_failure`:

```bash
python3 .agents/skills/featureliftbench-annotate-failures/scripts/screen_public_vs_required_api.py <task_id>
```

If the first failing public test calls an undeclared API, extra normalization rule, or output marker: `task_or_evaluator_defect` + `validity_override=benchmark_invalid_candidate`. Exclude from the agent-cause denominator.

### L1 close-read (required for every remaining row)

Open, in order: first-failure log, `submission/` around the failing call, public clause text. Then stop at the first Protocol §5.1 hit:

1. no submission → `agent_process_non_delivery`
2. failure outside submission / contract clash → defect
3. missing export/member/required branch → `contract_api_completion`
4. missing helper/resource/registry → `dependency_closure`
5. API present, observable semantics differ → `behavior_drift`
6. cannot expose standalone package → `packaging_modularization`
7. trajectory **and** submission prove wrong region → `localization`
8. else → `unknown`

Do not copy labels across models without reading both submissions. Empty parse results are not automatically `dependency_closure`. ABC/`@overload` stubs are not missing implementations. `localization=0` because it was not assigned is not “localization is solved”.

`evidence_summary`: one observable sentence. Ban `hidden_tests/`, `test_hidden`, `::test_`.

### Finding 3 gate

Write Finding 3 only if L1 (not L0) shows closure classes clearly exceed localization, failures are not missing packages, and unknown is reported rather than forced into the pie. Otherwise leave 5.3 as a tiered factual table.

## Outputs

Write under `reports/paper_analysis/<split>_..._<YYYYMMDD>/`:

- `failure_root_cause_annotations.csv`
- `f3_annotation_summary.json`
- README §5.3 with the evidence-tier table

Validate:

```bash
python3 .agents/skills/featureliftbench-annotate-failures/scripts/validate_annotation_csv.py \
  reports/paper_analysis/<dir>/failure_root_cause_annotations.csv
```

CSV must include Protocol §7 fields plus `validity_override`, `validity_reason`, `independent_human_review`. Clause IDs look like `B001;B003`.

The 2026-09-06 Python-150 CSV under `reports/paper_analysis/python150_prime_v2_analysis_20260905/` is an **L1 assistant close-read** of Pro+Flash artifact failures plus a stratified Luna/Qwen/OSS postsample (`postsample_annotations.csv`). Not L2 gold. Do not merge postsample counts into the Pro+Flash census valid denominator.
