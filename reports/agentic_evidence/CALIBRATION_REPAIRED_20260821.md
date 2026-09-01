# Agentic Evidence Calibration — repaired protocol 2026-08-21

> **Status: generated/reference · Evidence moved to `experiments/validation/agentic_evidence/` on 2026-08-29**

## Scope

- Model: `deepseek-v4-flash` (OpenAI-compatible API; model name normalized from profile `deepseek/deepseek-v4-flash`)
- Canary freeze: `experiments/validation/agentic_evidence/canaries_v1_20260820`
- Protocol repairs relative to 2026-08-20:
  - default `max_output_tokens=16384` with truncation/JSON failure retry at 32768
  - `coerce_confidence` for non-numeric confidence strings
  - `clamp_line_range` when building citations that overshoot file length

## Results

| View | Valid records | Correct | Strict accuracy | Macro-F1 |
| --- | ---: | ---: | ---: | ---: |
| Repaired direct R1 (+ truncation retry) | 40/40 | 40/40 | **100%** | **1.000** |

Gate for Flash-33 (≥80% strict accuracy): **PASS**.

## Evidence directory

`experiments/validation/agentic_evidence/runs/direct-auditor-r1-repaired_20260821/`
