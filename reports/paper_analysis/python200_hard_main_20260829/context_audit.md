# Context-window eligibility audit

> **Status: complete offline audit · No replacement runs executed**

There are **59** context-violation runs; **37** currently pass. The configured maximum is 122,880 prompt tokens per call.

## Overage severity

| Overage band | Tasks | Share of violations |
| --- | --- | --- |
| ≤1k | 2 | 3.4% |
| 1–4k | 3 | 5.1% |
| 4–8k | 10 | 16.9% |
| >8k | 44 | 74.6% |

Median overage is **11,028 tokens**; maximum overage is **16,563**. Most violations are not borderline events: 44/59 exceed the allowance by more than 8k tokens.

## Eligibility sensitivity

After removing the union of context violations, freeze-preflight blocks, and dependency-install failures, **116 tasks / 95 passes** remain fixed. Before replacement runs, the purely logical final range is 95/200 to 179/200 (47.5%–89.5%). This is a stress range, not a performance estimate.

## Frozen replacement policy

- Replace exactly the union in `strict_replacement_task_ids.txt`; do not select by outcome.
- Use the same model, OpenHands profile, 120-step budget, prompt, task selection, and image pins.
- Enforce the prompt allowance rather than merely auditing it.
- Repair the offline dependency cache before the run and verify it in preflight.
- Preserve the received results and publish both original and replacement provenance.
- Merge by task ID with the frozen rule: replacement for union tasks, original for all others.
