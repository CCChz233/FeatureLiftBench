# Agentic Evidence Calibration — 2026-08-20

> **Status: generated/reference · Evidence moved to `experiments/validation/agentic_evidence/` on 2026-08-29**

## Scope

- Model: `deepseek-v4-flash`
- Canary freeze: `canaries_v1_20260820`
- Cases: 40 total; 10 each for `explicit`, `recoverable`, `ambiguous`, and `underdetermined`
- Agent-visible inputs: each case's `TASK.md`, `metadata.json`, `audit_packet.json`, and `repo/`
- Private input: `private_manifest.json` was used only by the deterministic scorer
- Hidden tests and evaluator source were not exposed to the Agent

## Results

| View | Valid records | Correct | Strict accuracy | Macro-F1 |
| --- | ---: | ---: | ---: | ---: |
| R1, one call per case at 8k max output | 29/40 | 27/40 | 67.5% | 0.772059 |
| R1 plus truncation-only R2 | 31/40 | 29/40 | 72.5% | 0.810049 |

The final merged view has 31 schema- and citation-valid records. Of those, 29 are correctly classified, for 93.5% conditional classification accuracy. Strict accuracy remains 72.5% because invalid outputs count as missing.

Final per-class recall:

- `explicit`: 70%
- `recoverable`: 60%
- `ambiguous`: 60%
- `underdetermined`: 100%

The two valid classification errors both map `explicit` to `recoverable`. There are no valid false positives for `ambiguous` or `underdetermined` in this run.

## Output reliability

R1 produced 11 invalid records:

- 2 truncated/malformed JSON responses at exactly 8,000 completion tokens
- 3 non-numeric confidence values
- 6 citations whose requested end line exceeded the source file by one or two lines

Only the two output-limit truncations were retried. Both became valid at a 16k maximum. The other nine remain failures in the final strict score.

Token usage:

- R1: 33,488 prompt + 134,102 completion = 167,590 total tokens
- R2: 1,747 prompt + 5,743 completion = 7,490 total tokens
- Overall: 175,080 total tokens

## Interpretation

The Agent's classification is strong once it emits a valid evidence record, but protocol reliability is not yet high enough to remove the human gate outright. The next method change should target constrained output and deterministic repair: enforce numeric confidence, clamp or reject citation ranges before finalization, and require a schema-valid JSON response before accepting a vote. Calibration should then be rerun on the same frozen suite and on a second unseen freeze.

## Evidence directories

- One-shot run: `../../experiments/validation/agentic_evidence/runs/deepseek-v4-flash-direct-r1_20260820/`
- Truncation-only retry: `../../experiments/validation/agentic_evidence/runs/deepseek-v4-flash-direct-r2-truncation_20260820/`
- Final merged scoring view: `../../experiments/validation/agentic_evidence/runs/deepseek-v4-flash-direct-r1-plus-r2_20260820/`
