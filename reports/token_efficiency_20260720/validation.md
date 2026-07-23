# Validation notes

Assessment: **share with caveats**.

## Checks passed

- 550 analysis rows and 550 unique model-task pairs.
- Token records complete for 550/550 rows.
- Event trajectories complete for 550/550 rows.
- Evaluator records present for 533/550 rows; the 17 missing submissions remain in the formal denominator.
- `total_tokens == prompt_tokens + completion_tokens` for every row.
- Formal pass is consistently defined as `run_status == passed`, not evaluator-only public or hidden status.
- The notebook executed from the first cell through the last without an error.
- The interactive report manifest and bounded data snapshot passed the Data Analytics artifact validator before rendering.

## Spot checks

- Prompt share: `1,077,322,378 / 1,092,030,197 = 98.653%`.
- Non-pass tokens: 63.717% of all verified tokens.
- Repeated-read affected runs: `359 / 550 = 65.273%`.
- Formal passes: 225/550.
- At the 3M total-token cap, 29/225 observed passes exceed the cap; 196/225 (87.1%) are within it.

## Known limitations

- Associations between repeated reads, outcomes, and token totals are not causal.
- The history-growth estimate treats repeated inclusion of the first prompt footprint as an upper-bound baseline; it includes useful state as well as avoidable replay.
- Per-call context-cap simulations do not model semantic compression or behavioral changes.
- Cross-tokenizer comparisons are descriptive; matched Qwen27B/Qwen35B task-family comparisons are more interpretable but still single-run observations.
- Dollar cost, cached/uncached token accounting, and wall-clock time are not normalized in the current dataset.
- Candidate hard50 provenance still needs immutable harness commit and image digest before a paper freeze.
