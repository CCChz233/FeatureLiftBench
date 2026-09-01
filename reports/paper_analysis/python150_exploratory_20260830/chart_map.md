# Python-150 chart map

| Figure | Analytical question | Family / form | Supported claim | Required caveat |
| --- | --- | --- | --- | --- |
| `fig01_functional_pass_ci` | How do the four configurations compare on Functional Pass@1? | Horizontal bar + Wilson interval | DeepSeek leads; the Qwen configurations tie in aggregate; GPT-OSS is lower | Historical Python-150 evidence; configuration-level result |
| `fig02_evaluator_gate_rates` | At which evaluator gates do models separate? | Grouped dot plot | Most separation appears at Public and Hidden behavior | Gates are independent indicators, not a causal funnel |
| `fig03_pairwise_task_advantage` | Do equal totals hide task-level differences? | Diverging matrix | Qwen3.5 and Qwen3.6 trade 20 exclusive passes each | Pairwise difference is descriptive; exact tests are in the table |
| `fig04_task_solve_count_by_lift` | How many models solve tasks of each lift type? | 100% stacked bar | Direct tasks are more broadly solved; Composite tasks concentrate unsolved cases | Task selection is non-random; labels are AI-assisted |
| `fig05_pass_rate_vs_api_calls` | How does capability relate to interaction volume? | Labeled scatter | Higher interaction volume does not uniquely determine success | Four intentionally labeled configurations; descriptive only |
| `fig06_pass_conditioned_compactness` | Are correct packages compact? | Two-panel box plot | Correctness and compactness are distinct; DeepSeek passes are often copy-heavy | Survivor sets differ by model; copied fraction is heuristic |
| `fig07_feature_family_solvability` | Which feature families are least broadly solved? | Dot + task-bootstrap interval | Resource, validation, and registry families are less broadly solved in this sample | Multiple descriptive cuts; not a causal difficulty estimate |
