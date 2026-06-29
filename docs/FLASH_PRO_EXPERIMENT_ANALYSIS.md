# Flash/Pro Experiment Analysis

**Date:** 2026-06-28

This document analyzes only the experiment data currently present on this machine:

- `experiments/mini-swe-agent/benchmark-50-hard-flash-001`
- `experiments/mini-swe-agent/benchmark-50-hard-pro-20260625-125553`
- partial batch-1 single-task Flash calibration runs under `experiments/mini-swe-agent/*-flash-*`

Other model results referenced in older docs are not assumed available.

## Paper Readiness Verdict

The current Flash/Pro data is enough for a **pilot / baseline analysis on the original 50 hard tasks**.

It is **not enough** for the final paper's main 100-task experiment yet, because no complete Flash/Pro full-suite run exists over the current 100-task benchmark.

Recommended paper use:

| Use case | Current data status |
| --- | --- |
| Describe original 50-task baseline behavior | usable |
| Compare Flash vs Pro on the same 50 tasks | usable, but single-run only |
| Analyze extraction quality vs functional pass | usable |
| Study copy-heavy vs compact solutions | usable |
| Analyze failure overlap and per-task case studies | usable |
| Claim final 100-task leaderboard results | not supported yet |
| Claim statistically robust model ranking | not supported yet |
| Analyze batch-1 as a complete suite | not supported yet |

## Complete Full-Suite Runs Available

| Suite | Model | Tasks | Passed | Avg final score | Missing submissions | Generated |
| --- | --- | ---: | ---: | ---: | ---: | --- |
| `benchmark-50-hard-flash-001` | `deepseek/deepseek-v4-flash` | 50 | 41 | 0.471647 | 0 | 2026-06-25T04:35:19Z |
| `benchmark-50-hard-pro-20260625-125553` | `deepseek/deepseek-v4-pro` | 50 | 42 | 0.480619 | 0 | 2026-06-25T10:11:26Z |

Both runs cover the original 50 hard tasks. They overlap with 50 tasks in the current 100-task benchmark and miss the 50 new batch-1 tasks.

Important caveat: the Pro result is the re-evaluated result after evaluator flake fixes. This is acceptable if the paper states that submissions were not rerun, only evaluation was recomputed with the fixed evaluator.

## Main Result

Flash and Pro are effectively tied on the original 50-task suite.

| Metric | Flash | Pro |
| --- | ---: | ---: |
| Functional pass | 41/50 | 42/50 |
| Pass rate | 82% | 84% |
| Avg final score | 0.471647 | 0.480619 |
| Compact passes (`extraction_ratio <= 0.25`) | 16 | 16 |
| Mid-band passes | 16 | 17 |
| High-extraction passes (`extraction_ratio >= 0.8`) | 9 | 9 |
| Median total tokens/task | 819,280 | 810,973 |
| Mean total tokens/task | 1,238,331 | 1,216,023 |
| Max total tokens/task | 6,347,309 | 5,642,432 |

Interpretation:

- Pro is +1 task over Flash and +0.009 average final score.
- That difference is too small to support a strong model-ranking claim from one run.
- The important finding is not "Pro beats Flash"; it is that both models frequently solve functionality while still producing copy-heavy extractions.

## Head-to-Head

| Outcome | Count |
| --- | ---: |
| Both pass | 39 |
| Both fail | 6 |
| Flash only | 2 |
| Pro only | 3 |

Flash-only passes:

- `redis__resp_parser_core__001`
- `vibe_app__plugin_registry_core__001`

Pro-only passes:

- `rich__markup_parse_core__001`
- `vibe_app__rules_engine_core__001`
- `vibe_app__session_registry_core__001`

Both fail:

- `networkx__dag_topo_core__001`
- `pygments__lexer_core__001`
- `pytest__fixture_resolve_core__001`
- `pytest__ini_markers_core__001`
- `pytest__skipif_eval_core__001`
- `vibe_app__orm_query_ast_core__001`

Good paper angle: both models fail the same pytest internals and graph/lexer tasks, suggesting those tasks stress deeper framework state or parser behavior rather than simple API copying.

## Extraction Quality Is The Stronger Signal

Functional pass alone is too weak:

- Flash passes 41 tasks, but 9/41 passed tasks are high-extraction.
- Pro passes 42 tasks, but 9/42 passed tasks are high-extraction.
- Both models have only 16 compact passes.

This supports the benchmark's central thesis: **feature lifting should be scored by functionality and extraction compactness together**.

High-extraction Flash passes:

- `attrs__validators_core__001`
- `click__option_parser__001`
- `lark__grammar_loader_core__001`
- `lark__parse_tree_core__001`
- `lark__visitor_transform_core__001`
- `markdown_it__commonmark_render__001`
- `marshmallow__schema_core__001`
- `pyyaml__safe_load_dump__001`
- `typer__command_parser_core__001`

High-extraction Pro passes:

- `attrs__validators_core__001`
- `click__option_parser__001`
- `lark__visitor_transform_core__001`
- `markdown_it__commonmark_render__001`
- `marshmallow__schema_core__001`
- `pluggy__hook_call_order__001`
- `pluggy__hook_specs_core__001`
- `pyyaml__safe_load_dump__001`
- `typer__command_parser_core__001`

Case-study candidates:

| Case | Why useful |
| --- | --- |
| `marshmallow__schema_core__001` | both pass but nearly whole-package extraction; clear copy-heavy example |
| `pytest__mark_expression_core__001` | both compact pass; clear successful feature lift |
| `pluggy__hook_specs_core__001` | Pro passes with extraction ratio >1.0; useful metric/pathology discussion |
| `vibe_app__rules_engine_core__001` | Pro-only compact pass; useful head-to-head contrast |
| `redis__resp_parser_core__001` | Flash-only compact pass; useful head-to-head contrast |

## Group-Level Patterns

By `entanglement.primary`:

| Primary | Flash pass / total | Pro pass / total |
| --- | ---: | ---: |
| `parser_state_coupling` | 14/16 | 14/16 |
| `framework_coupling` | 9/12 | 9/12 |
| `data_model_coupling` | 5/6 | 5/6 |
| `legacy_vibe_clutter` | 4/6 | 5/6 |
| `config_environment_coupling` | 4/5 | 4/5 |
| `resource_coupling` | 4/4 | 4/4 |
| `third_party_dependency_coupling` | 1/1 | 1/1 |

By repeated source:

| Source | Flash pass / total | Pro pass / total |
| --- | ---: | ---: |
| `coveragepy` | 5/5 | 5/5 |
| `jinja2` | 5/5 | 5/5 |
| `sqlparse` | 4/4 | 4/4 |
| `lark` | 3/3 | 3/3 |
| `vibe_app` | 4/7 | 5/7 |
| `pytest` | 1/4 | 1/4 |
| `pygments` | 1/2 | 1/2 |
| `pluggy` | 2/2 | 2/2 |

Interpret carefully: these are small grouped samples and should not be reported as statistically stable. They are useful for qualitative interpretation and case selection.

## Token Observations

For these two runs, passed tasks used more tokens on median than failed tasks:

| Suite | Passed median tokens | Failed median tokens |
| --- | ---: | ---: |
| Flash | 877,074 | 380,997 |
| Pro | 824,491 | 470,053 |

Do not overinterpret this. Token use depends on task size, source package size, agent loop behavior, and early failures. It is safe to report as descriptive cost data, not as causal evidence.

## Partial Batch-1 Flash Calibration

There are 20 unique batch-1 single-task Flash calibration runs available.

| Status | Count |
| --- | ---: |
| Passed | 17 |
| Failed | 3 |
| Compact passed (`<=0.25`) | 6 |
| High-extraction passed (`>=0.8`) | 1 |

Failed single-task calibrations:

- `httpx__request_model_core__001`
- `sortedcontainers__sorted_list_core__001`
- `xmltodict__xml_parse_core__001`

This data is useful for **task calibration notes**, but it is not a full-suite experiment:

- no Pro batch-1 counterpart;
- no full 50-task batch-1 run;
- only 20/50 batch-1 tasks have Flash calibration run files;
- single-task runs may not match full-suite scheduling and resource behavior.

## Data Quality Gaps Before Paper Submission

Minimum needed for a clean paper experiment section:

1. Run Flash and Pro on the current full 100-task suite.
2. Record exact git commit, harness version, model/profile, endpoint, date, worker count, memory limits, and evaluator mode.
3. Keep `suite.json`, each `run.json`, each `eval/result.json`, and each `agent/trajectory.json`.
4. Rebuild analysis from raw files, not from hand-maintained markdown tables.
5. Decide whether to run 1x or 3x per model:
   - 1x is enough for a baseline snapshot;
   - 3x is needed for pass variance, pass@k, and stronger model comparison.
6. Keep old 50-task Flash/Pro results as historical baseline or pilot, not as final 100-task leaderboard.

## Recommended Paper Framing Now

Use current data to support these claims:

- The original 50-task benchmark is executable end-to-end with strong agents.
- Functional pass is insufficient because a non-trivial share of passes are copy-heavy.
- `final_score` and extraction buckets expose qualitatively different solution strategies.
- Flash and Pro are very close on the original 50 tasks; differences are task-specific rather than global.

Avoid these claims until full 100-task experiments exist:

- "FeatureLiftBench-100 results show ..."
- "Model A is statistically better than Model B"
- "Batch-1 reduces pass rate by ..."
- "The final benchmark has calibrated difficulty against Flash/Pro"

## Commands Used

```bash
python3 harness/scripts/analyze_benchmark_suite.py \
  experiments/mini-swe-agent/benchmark-50-hard-flash-001

python3 harness/scripts/analyze_benchmark_suite.py \
  experiments/mini-swe-agent/benchmark-50-hard-pro-20260625-125553
```

Additional summary numbers were recomputed directly from each suite's `suite.json` and per-task `run.json`.
