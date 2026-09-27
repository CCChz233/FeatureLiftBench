# Successful-artifact footprint analysis: replication details

This note preserves statistical implementation details moved from the manuscript
in the scoped writing revision. It introduces no new analysis or results.

The analysis retains tasks with successful artifacts from at least two
configurations. Task fixed-effects models use log2(RRES) and Copy as outcomes,
with configuration coefficients centered to sum to zero. Ordinary least squares
gives each successful artifact equal weight. Reported effects are 2^beta for RRES
and 100 beta percentage points for Copy. Their reference centers represent the
center of configuration effects, not an adjusted median or a raw size ratio to
the reference implementation.

Pointwise 95% percentile intervals use 10,000 accepted task-cluster bootstrap
resamples. Each sampled task retains all its successful artifacts; both models
are refitted and centered on every resample. The six-configuration co-success
graph must remain connected. A disconnected draw would be rejected and redrawn;
no disconnected draws occurred.

Two sensitivity checks each use 10,000 accepted resamples:

- Task-equal weighting gives each artifact weight 1/k_t, where k_t is the number
  of successful configurations on task t.
- Repository-level resampling samples whole source repositories while retaining
  the artifact weights of the main analysis.

No disconnected draws occurred in either sensitivity scheme. Both checks
preserve the qualitative footprint profiles reported in the manuscript.
Intervals describe variation across task or repository clusters, not repeated
agent runs. All comparisons condition on functional success.

## Descriptive footprints from the previous main-table layout

Values below are transcribed from the manuscript before this layout revision.
All measures condition on functional success.

| Configuration | RRES mean | RRES median | RRES [Q1,Q3] | Copy mean | Copy median | Copy [Q1,Q3] |
|---|---:|---:|---|---:|---:|---|
| DeepSeek V4 Pro | 1.78 | 0.99 | [0.77, 1.29] | 0.78 | 0.96 | [0.72, 0.99] |
| DeepSeek V4 Flash | 1.73 | 1.00 | [0.89, 1.22] | 0.81 | 0.97 | [0.84, 0.99] |
| GPT-5.6 Luna | 0.95 | 0.81 | [0.31, 1.00] | 0.41 | 0.16 | [0.05, 0.97] |
| GLM-5.3-Flash | 2.47 | 1.01 | [0.92, 1.16] | 0.84 | 0.95 | [0.81, 0.98] |
| Qwen3.6-35B-A3B | 1.56 | 0.97 | [0.65, 1.23] | 0.64 | 0.76 | [0.33, 0.97] |
| GPT-OSS 120B | 1.18 | 0.98 | [0.29, 1.65] | 0.31 | 0.18 | [0.01, 0.53] |
