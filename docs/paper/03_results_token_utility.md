# Where functional sufficiency occurs (RQ3), by lift type (RQ5)

> **Documentation status: current · Last verified: 2026-08-18**
> Manuscript-ready results. Offline gold on existing Main trajectories.
> Not a new method. Do not derive a stopping rule from these tables.
> Capability pass rates remain [RQ1](02_research_questions.md). This section is
> the cost slice: *when* a passing package first exists versus *when* the
> agent stops spending.

**Claim.** On trajectories that eventually Functional-Pass, a behavior-complete
`featurelifted` package typically exists well before the agent stops. The
remaining tokens are mostly self-tests the agent cannot ground in Hidden.
This is a property of passing trajectories, stratified by model and lift type.
It is not a proof that extra tokens would have saved failures.

## Gold label

\(T^\*\) is the **earliest unique** `submission/featurelifted/` tree whose
evaluator `functional_gate` is 1.0. Token time is cumulative billed
`prompt + completion` from `context_audit.jsonl`. Last package write is a
proxy only and is **not** the paper token-utility metric.

Replay requires the last reconstructed tree to hash-match the on-disk
package; unmatched passing tasks have no gold. Failures have no \(T^\*\).
Qwen V1-200 has no Phase 1 gold. For tasks that pass before 2M, default
snapshot sampling means reported \(T^\*/T_{\mathrm{total}}\) is an **upper
bound**; those upper bounds are still below 2M, so the 2M-cap question is
unaffected.

Analysis: [TOKEN_UTILITY.md](../TOKEN_UTILITY.md). Snapshots:
[`token_utility_phase1_20260818.json`](../../artifacts/research_analysis/current_results/token_utility_phase1_20260818.json),
[`token_utility_phase1_cross_e50_20260818.json`](../../artifacts/research_analysis/current_results/token_utility_phase1_cross_e50_20260818.json),
[`token_utility_characterize_20260818.json`](../../artifacts/research_analysis/current_results/token_utility_characterize_20260818.json).

## Result 1 — Passing packages appear early; spend continues

Pass-conditioned medians. Flash / Qwen / OSS are not pooled.

| Model | Gold passes | Median \(T^\*/T\) | Median \(T^\*\) | Median post-\(T^\*\) tokens | Post-\(T^\*\) share | Self-test share of tail | \(T^\* \ge 2\mathrm{M}\) |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| DeepSeek-V4-Flash local Main-200 | 138/145 | **0.40** | 0.47M | **0.75M** | 60% | 55% | 7 |
| DeepSeek-V4-Flash API External-50 | 42/45 | **0.36** | 0.53M | **0.95M** | 64% | 57% | 5 |
| Qwen3.6-35B External-50 | 34/36 | 0.54 | 0.95M | 0.86M | 46% | 49% | 5 |
| Qwen3.5-122B External-50 | 37/37 | 0.51 | 0.49M | 0.51M | 49% | 48% | 1 |
| GPT-OSS 120B External-50 | 16/16 | 0.49 | 0.17M | **0.10M** | 51% | 33% | 0 |

Flash local Main: IQR of \(T^\*/T\) is 0.27–0.55. 87/138 gold passes spend at
least half their tokens after sufficiency. Last package write on the same
Flash passing set sits at median 0.59 of total tokens, so later writes often
happen **after** a sufficient tree already exists.

A 2M cap on this Flash Main run would drop the 7 tasks whose earliest
sufficient tree is itself \(\ge 2\mathrm{M}\), not the 21 tasks whose *last*
write is after 2M. The same distinction holds on Qwen External-50 Main vs V1:
of 18 Main-pass / V1-fail pairs, only 5 Main trajectories need tokens after
2M. The other 12 already have a sufficient tree before 2M; V1 failure is
another sample, not truncation of the same path.

## Result 2 — Lift type moves \(T^\*\); informal difficulty does not

Lift labels are Direct / Adapted / Composite from the frozen Python-200
contract-closure ledger (200/200). Flash local Main-200 is the only split
with gold on the full 200-task mix.

| Lift | n | Median \(T^\*/T\) (p25–p75) | Median \(T^\*\) | Median post-\(T^\*\) | Post-\(T^\*\) share | Self-test share of tail |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| Direct | 58 | **0.36** (0.25–0.54) | 0.39M | 0.74M | 64% | 58% |
| Adapted | 52 | 0.40 (0.26–0.54) | 0.58M | 0.79M | 60% | 53% |
| Composite | 28 | **0.51** (0.33–0.58) | 0.62M | 0.70M | 49% | 54% |

The Flash “median 40%” headline is Direct and Adapted. Composite reaches
sufficiency later, but still leaves a ~0.70M post-sufficiency tail that is
about half self-test. Early sufficiency is not “only easy tasks.” Composite
is not “spend until the budget ends, then stop testing.”

`metadata.difficulty` is **not** a scientific easy/medium/hard label
(Python-150 is all `hard`, External-50 all `medium`). Construction cohorts
on the same Flash gold set: python150 \(n=82\), median \(T^\*/T=0.35\);
hard3 \(n=10\), 0.39; External-50 \(n=46\), 0.42. `entanglement.level` also
does not separate: high 0.40 (\(n=105\)), medium 0.39 (\(n=28\)). **Do not
tell a difficulty story for \(T^\*\).** Tell a lift-type story.

External-50 is Composite-heavy and is not the same mix as Python-200. On the
shared External-50 Main tasks:

| Model | Direct | Adapted | Composite |
| --- | ---: | ---: | ---: |
| Flash API | 0.35 (\(n=12\)) | 0.44 (11) | 0.36 (19) |
| Qwen3.6-35B | 0.49 (11) | **0.61** (11) | 0.56 (12) |
| Qwen3.5-122B | 0.46 (11) | 0.44 (10) | **0.60** (16) |
| GPT-OSS 120B | 0.57 (8) | 0.49 (6*) | 0.48 (2*) |

Cells with \(n<8\) are marked \*. OSS passes are Direct-heavy (8/16); that is
selection, not evidence that Composite is easier for OSS. Flash API Composite
has median \(T^\*/T=0.36\) but median \(T^\*=0.88\mathrm{M}\) and a
**2.08M** post-sufficiency tail: an early *fraction* is not a cheap run.

## Result 3 — After \(T^\*\) the agent keeps inventing probes

Flash local Main, 138 gold passes, tokens after \(T^\*\):

| Activity | Share of post-\(T^\*\) tokens |
| --- | ---: |
| Run self-tests (`python -c`, heredoc, pytest, upstream shims) | **48%** |
| Write self-test files | 5% |
| Read package / upstream tests / repo | 18% |
| Patch `featurelifted` | 6% |
| Isolation / forbidden-import checks | 4% |
| Finish / tracker / cleanup | 9% |
| Other | 10% |

99% of these tasks still self-test after sufficiency; 44% still patch the
package (6% of tail tokens). 46% grow a new unique tree after \(T^\*\).
Those writes are not harmless polish: isort passed at 0.90M, broke, and
recovered at 1.49M.

The mechanism is substitution for Hidden. The agent cannot see Hidden, so it
keeps running probes that look like progress. Flash additionally reads
`repo/tests/` after pass (43–52% of External-50 gold passes). Qwen3.6-35B
does so on 3% of gold passes. Do not write “upstream tests as hidden oracle”
as a cross-model mechanism.

Probe-level split (command skeleton + pytest outcome fingerprint):

| | Flash Main-200 | Qwen3.6-35B External-50 |
| --- | ---: | ---: |
| Self-tests before / after \(T^\*\) | 334 / **1482** | 92 / **228** |
| After \(T^\*\): new probe, no new tree within 250K | **85%** | **72%** |
| After \(T^\*\): identical command+outcome rerun | 1.8% | **14%** |
| Repeat-read rate before → after \(T^\*\) | 0.8% → 11% | **21% → 51%** |

Flash waste is **new probes that do not change the package**. Qwen repeats
commands and re-reads more. A single “stop on repeated pytest” rule would
not describe both models.

## Result 4 — Legal signals do not justify a stop rule

Predict \(t \ge T^\*\) from history-only features (consecutive self-tests,
probe novelty, time since last unique tree, repeat command/read, windowed
tree churn). No Hidden, no evaluator, no future trees, no \(T^\*\) in
features. Flash and Qwen are fit separately. Unfitted hypothesized
combination:

| Slice | Flash combo AUC | Flash time-since-unique-tree | Flash tokens-so-far (control) | Qwen combo | Qwen time-since-tree | Qwen tokens-so-far |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| All actions | 0.63 | 0.86 | 0.84 | 0.64 | 0.88 | 0.81 |
| Matched 0.5–1.5M band | 0.67 | **0.79** | **0.57** | 0.63 | **0.81** | 0.69 |

On self-test rows, novelty is near chance (Flash `self_test_out_novel` AUC
0.45). The combination is too weak for a stopping rule. Time since the last
**unique tree** survives the matched-token control; that is stall-after-edit,
not verification novelty, and it is close to V2’s “no recent submission
write.” It is still not a policy: 46% of gold passes grow a new unique tree
after \(T^\*\), some of which break a passing package.

## What this is allowed to say

- On Flash passing Main-200 trajectories, median sufficiency is at 40% of
  billed tokens; most of the remainder is self-testing.
- Lift type shifts that fraction (Direct 0.36, Composite 0.51) without
  removing the post-sufficiency tail.
- Qwen reaches sufficiency later in the trajectory; OSS tails are small in
  absolute tokens.
- A 2M cap’s true Flash tax on this run is 7 late-sufficient tasks, not
  every last write after 2M.

## What this is not allowed to say

- Failures would have passed with more tokens (no \(T^\*\) on fails; public
  green is not proximity to Hidden).
- Last-write fraction is token utility.
- Main vs V1 yes/no pairs are truncations of one trajectory.
- Informal difficulty or `metadata.difficulty` explains \(T^\*\).
- One early-stopping rule should be shipped, including stall-after-edit.
- Core-12 condenser/audit numbers belong in the Python-200 main table.

## Figure list (for the manuscript)

1. CDF of \(T^\*/T_{\mathrm{total}}\) on Flash Main-200 gold passes, one
   curve per lift type.
2. Grouped bars: median post-\(T^\*\) tokens by model on External-50 Main
   (Flash API / Qwen-35B / Qwen-122B / OSS), not a pooled ranking.
3. Stacked composition of post-\(T^\*\) billed tokens (Flash Main-200).
