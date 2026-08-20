# RQ6 Public-feedback: Main's information boundary

> **Documentation status: current · Last verified: 2026-08-20**
> Flash-12 same-day pair is complete. Not a Python-200 main-table result.
> Not a new agent method.
> Protocol: [METHOD_RQ6_PUBLIC_FEEDBACK.md](../METHOD_RQ6_PUBLIC_FEEDBACK.md).

**Claim.** Under Full-Repository / No-Hint Main, Flash already has the public
contract text but not executable benchmark tests. Mounting `public_tests/`
recovers the public gate on all six public-failure tasks (6/6). Hidden stays
hard on most tasks that already passed public (4/5 paired hidden-failure
tasks unchanged). Two hidden 0→1 flips (yamale, wheel) are not a wholesale
public≈Hidden leak. Test-blind Main is neither free nor generally leaky.

Do not write “Public-feedback raises Flash from 145/200 to *x*”.

## Protocol

Same task / spec / model / agent / evaluator / 128k envelope / 120 steps /
No-Hint / no 2M cap. Only change: mount `public_tests/`. Hidden never mounted.
Same-day Main on the same 12 tasks is the control. Integrity: Main 12/12 not
mounted; Public-feedback 12/12 mounted.

Slice: 6 `public_failure` + 6 `hidden_failure` from Flash Main-200 (local ∩
API). Snapshot:
[`rq6_public_feedback_flash12_20260820.json`](../../artifacts/research_analysis/current_results/rq6_public_feedback_flash12_20260820.json).
Suite: `experiments/ablations/public_feedback/flash12-deepseek-v4-flash-20260819-220335/`.

## Result — Flash-12, DeepSeek API

`functional_gate`: Main **0/12** → Public-feedback **4/12**. `bleach` has no
Main eval (missing submission).

| Pattern | Tasks | Readout |
| --- | --- | --- |
| public 0→1, hidden still 0 | alembic, click, flask | feedback useful; Hidden still hard |
| public 0→1, hidden already 1 → gate 0→1 | decorator, filelock | closed a public-only gap, not Hidden leakage |
| public 0→1 and hidden 0→1 | yamale | one public-failure task also flipped Hidden |
| public already 1, hidden 0→1 → gate 0→1 | wheel | one hidden-failure task flipped Hidden |
| neither stage moved | parse, pygments, python_decouple, schema | seeing public tests does not lift Hidden |
| unpaired | bleach | Main missing; PF still public 0 / hidden 0 |

## What the paper may say

1. Withholding executable public tests is a real Main bottleneck: every
   public-failure task flipped public 0→1.
2. Public pass is not Hidden pass. Three public-failure tasks remain hidden 0.
   Four of five paired hidden-failure tasks stay public 1 / hidden 0.
3. Functional-gate +4 must be split: decorator / filelock already had hidden=1
   on same-day Main; yamale and wheel are the only hidden 0→1 flips.
4. Two hidden flips do not license “public tests ≈ Hidden”. Inspect those two
   if claiming leakage; the other four hidden-failure pairs argue against it.
5. Place this in RQ6 / discussion of Main's information boundary, not in the
   Python-200 leaderboard and not as a better agent.

## What the paper must not say

- any substitution of 4/12 for uncapped Main 145/200;
- Entrypoint-Hint, Pruned-Context, or Short-prompt numbers;
- that Hidden leakage is the typical outcome.
