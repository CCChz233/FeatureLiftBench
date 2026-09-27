# Execution continuation: detailed manuscript values

These values were moved from the main manuscript during the 18-page compression
on 2026-09-22. They are transcribed from the preceding manuscript, without new
experiments, recalculation, or inspection of raw experimental records.

All values are configuration-level medians. Token and response measurements use
separate available samples of finally successful runs: 317 runs for tokens and
403 runs for responses. The final column uses the same token samples as the
first token column but requires every subsequent reconstructed checkpoint to
remain passing.

| Configuration | Tokens after first observed pass (%) | Subsequent main-agent responses | Tokens after first stable observed pass (%) |
|---|---:|---:|---:|
| Pro | 66.9 | 20.5 | 66.6 |
| Flash | 73.0 | 32.5 | 71.1 |
| Luna | 58.1 | 11 | 57.9 |
| GLM | 67.1 | 39.5 | 54.8 |
| Qwen | 53.7 | 17.5 | 52.1 |
| OSS | 37.1 | 5 | 37.1 |

Token fractions include cached input. An earlier manuscript additionally
reported median post-checkpoint fractions of 34.2% and 43.9% for Pro and Flash
under an alternative uncached-input accounting. That sentence was removed on
2026-09-22. The current main table counts input including cached input plus
output, so these alternative fractions do not describe its accounting.

Continuation need not be unproductive. In the inspected Pro JSONPath trajectory,
subsequent actions run tests, inspect dependencies, and clean generated files
without changing the evaluated artifact. These retrospective checkpoints do not
provide an online stopping signal or quantify avoidable cost or computation.

The manuscript also points to outcome-level token distributions for 764
recoverable ledgers. Their incomplete coverage and mixed directions across
configurations do not support an efficiency ranking.
