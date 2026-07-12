# Paper Tables (Draft)

## Table 1: Cross-model performance (RQ1) — shared core-100

| Model | Functional pass | Pass rate | Avg final score | Median extraction (passed) | Copy-heavy pass | Median tokens (passed) |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| DeepSeek-V4-Flash | 83/100 | 83.0% | 0.520 | 0.3196 | 9 | 1520588 |
| Qwen3.6-27B-FP8 | 54/100 | 54.0% | 0.324 | 0.3435 | 8 | 1058528.5 |
| Qwen3.6-35B-A3B-FP8 | 49/100 | 49.0% | 0.303 | 0.3029 | 8 | 1256467 |
| Qwen3-Coder-30B | 24/100 | 24.0% | 0.173 | 0.2186 | 1 | 1120668.5 |

## Table 2: Python-150 coverage and hard-extension calibration (Flash)

| Scope | Functional pass | Pass rate | Avg final score |
| --- | ---: | ---: | ---: |
| Full Python-150 | 91/150 | 60.7% | 0.359 |
| Hard extension (50) | 8/50 | 16.0% | 0.037 |


## Table 3: Failure taxonomy — Flash 100-hard (RQ2)

| Mechanical label | Count | % |
| --- | ---: | ---: |
| passed | 83 | 83.0% |
| public_only_fail | 11 | 11.0% |
| build_fail | 2 | 2.0% |
| missing_submission | 2 | 2.0% |
| other_fail | 2 | 2.0% |

## Table 4: Compactness baselines (RQ4)

| Metric | Value |
| --- | --- |
| Gate reports | 52 |
| Median oracle extraction | 0.3642 |
| Median copy-all extraction | 0.9924 |
| Median Flash extraction (passed, gate set) | 0.2762 |

## Table 5: Pass rate by entanglement primary (RQ5, Flash)

| Entanglement primary | Tasks | Passed | Pass rate |
| --- | ---: | ---: | ---: |
| config_environment_coupling | 12 | 10 | 83.3% |
| data_model_coupling | 24 | 20 | 83.3% |
| framework_coupling | 13 | 10 | 76.9% |
| legacy_vibe_clutter | 6 | 6 | 100.0% |
| parser_state_coupling | 39 | 32 | 82.0% |
| resource_coupling | 5 | 4 | 80.0% |
| third_party_dependency_coupling | 1 | 1 | 100.0% |

## Table 6: Batch3 hard3 by entanglement (Flash merged)

| Entanglement primary | Tasks | Passed | Pass rate |
| --- | ---: | ---: | ---: |
| config_environment_coupling | 3 | 0 | 0.0% |
| data_model_coupling | 17 | 3 | 17.6% |
| framework_coupling | 14 | 3 | 21.4% |
| parser_state_coupling | 5 | 2 | 40.0% |
| resource_coupling | 9 | 0 | 0.0% |
| third_party_dependency_coupling | 2 | 0 | 0.0% |