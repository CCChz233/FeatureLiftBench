# Task-adjusted footprint analysis

115 tasks; 485 successful artifacts; 97 repositories. Six configurations in Table 1 order.
Reference lines are the sum-to-zero center of configuration effects. Intervals are pointwise 95% percentile CIs.
Success-conditional descriptive analysis; no causal or failed-task extrapolation.

## task_bootstrap

10,000 accepted draws; 0 disconnected draws rejected; seed 20260915.

| Configuration | Included n | RRES ratio [95% CI] | Copy pp [95% CI] |
| --- | ---: | ---: | ---: |
| Pro | 113 | 1.178 [1.088, 1.288] | +15.42 [+12.35, +18.56] |
| Flash | 107 | 1.314 [1.212, 1.439] | +16.81 [+13.61, +20.17] |
| Luna | 99 | 0.612 [0.537, 0.693] | -20.64 [-26.07, -15.28] |
| GLM | 68 | 1.555 [1.387, 1.754] | +14.20 [+10.57, +17.73] |
| Qwen | 63 | 1.109 [1.016, 1.227] | -1.79 [-5.89, +2.45] |
| OSS | 35 | 0.612 [0.462, 0.767] | -24.00 [-31.40, -17.03] |

## task_equal_weight

10,000 accepted draws; 0 disconnected draws rejected; seed 20260915.

| Configuration | Included n | RRES ratio [95% CI] | Copy pp [95% CI] |
| --- | ---: | ---: | ---: |
| Pro | 113 | 1.205 [1.100, 1.333] | +15.57 [+12.49, +18.78] |
| Flash | 107 | 1.348 [1.235, 1.488] | +16.98 [+13.78, +20.29] |
| Luna | 99 | 0.583 [0.501, 0.674] | -21.24 [-26.84, -15.66] |
| GLM | 68 | 1.581 [1.410, 1.782] | +14.83 [+11.11, +18.33] |
| Qwen | 63 | 1.119 [1.024, 1.239] | -1.37 [-5.43, +2.78] |
| OSS | 35 | 0.597 [0.450, 0.753] | -24.77 [-32.09, -17.83] |

## repository_bootstrap

10,000 accepted draws; 0 disconnected draws rejected; seed 20260916.

| Configuration | Included n | RRES ratio [95% CI] | Copy pp [95% CI] |
| --- | ---: | ---: | ---: |
| Pro | 113 | 1.178 [1.083, 1.293] | +15.42 [+12.16, +18.86] |
| Flash | 107 | 1.314 [1.214, 1.436] | +16.81 [+13.36, +20.35] |
| Luna | 99 | 0.612 [0.535, 0.694] | -20.64 [-26.18, -15.17] |
| GLM | 68 | 1.555 [1.387, 1.751] | +14.20 [+10.49, +17.89] |
| Qwen | 63 | 1.109 [1.010, 1.216] | -1.79 [-6.24, +2.53] |
| OSS | 35 | 0.612 [0.476, 0.761] | -24.00 [-30.97, -17.25] |

## Verification

```json
{
  "task_bootstrap_dense_max_error": 2.4424906541753444e-15,
  "task_equal_weight_dense_max_error": 5.051514762044462e-15,
  "comparison_graph_connected": true,
  "disconnected_guard_checked": true,
  "within_design_rank": 5,
  "sum_centered_all_replicates": true,
  "task_equal_same_sign": [
    [
      true,
      true
    ],
    [
      true,
      true
    ],
    [
      true,
      true
    ],
    [
      true,
      true
    ],
    [
      true,
      true
    ],
    [
      true,
      true
    ]
  ],
  "task_equal_rank_order_same": [
    false,
    true
  ],
  "task_equal_max_ratio_relative_change": 0.047041615634782374,
  "task_equal_max_copy_pp_change": 0.7711793476740114
}
```

Changing centering or including additional configurations changes the reference center.
CI overlap is not a pairwise comparison test. Point-estimate ranks do not establish population ordering.
The additive model summarizes configuration-by-task heterogeneity; fixed effects do not remove success selection.
