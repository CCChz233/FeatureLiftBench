# Python-200′ freeze v2 OpenHands Main — mechanical readout

> **Status: analysis snapshot · Generated: 2026-09-04**  
> Follows [08_experimental_analysis_chapter.md](../../../docs/paper/08_experimental_analysis_chapter.md).  
> **5.3 semantic taxonomy is not done.** Findings 1–2 and 5 can be drafted; Finding 3 cannot.

Freeze `6c20ff0307762503a73cbb9ff32e9992c6446e4b17483a68373027be58cbf419`, candidate `212930ea`, protocol Full-Repository / No-Hint.
GLM-5.3-Flash is excluded (incomplete). Do not mix with freeze `474862c2` 132/200.

## 5.1 Overall Capability

We evaluate all three completed model–agent configurations on the frozen Python-200′ suite under the same Full-Repository / No-Hint protocol.

| Model | Functional Pass@1 | Python-150 | Hard-50 | Wilson 95% CI (200) |
| --- | ---: | ---: | ---: | --- |
| DeepSeek V4 Flash | **143/200 (71.5%)** | 94/150 (62.7%) | 49/50 (98.0%) | 64.9–77.3 |
| gpt-5.6-luna (OpenLux) | **132/200 (66.0%)** | 90/150 (60.0%) | 42/50 (84.0%) | 59.2–72.2 |
| Qwen3.6-35B-A3B-FP8 | **80/200 (40.0%)** | 57/150 (38.0%) | 23/50 (46.0%) | 33.5–46.9 |

**Assigned-200 vs launched-176.** The same **24 Python-150** tasks never launched on any model (`active benchmark freeze spec hash mismatch`). They are infrastructure, not agent failures. Protocol still records them as non-pass in the 200-row dump. Capability among launched tasks:

| Model | Functional Pass on launched 176 | Python-150 launched (126) | Hard-50 (50) |
| --- | ---: | ---: | ---: |
| DeepSeek V4 Flash | **143/176 (81.2%)** | 94/126 (74.6%) | 49/50 (98.0%) |
| gpt-5.6-luna (OpenLux) | **132/176 (75.0%)** | 90/126 (71.4%) | 42/50 (84.0%) |
| Qwen3.6-35B-A3B-FP8 | **80/176 (45.5%)** | 57/126 (45.2%) | 23/50 (46.0%) |

Strict `run.status=passed` is not the paper metric: DeepSeek 17/200, Luna 47/200, Qwen 32/200.

**Ceiling.** On the assigned 200, DeepSeek solves 71.5% (**57** non-passes, of which 24 never launched). On the 176 launched tasks it reaches 81.2%. The suite is not saturated.

**Discrimination.** DeepSeek exceeds Qwen by **31.5 percentage points** on assigned 200 (143/200 vs 80/200; 81.2% vs 45.5% on 176). Luna (OpenLux) sits in between.

**Hard-50 is not harder.** Even after removing the 24 Python-150 freeze blocks, DeepSeek is 98.0% on Hard-50 vs 74.6% on launched Python-150; Luna 84.0% vs 71.4%; Qwen is essentially flat (46.0% vs 45.2%). Do not write “all models drop on Hard-50.”

> **Finding 1.** Current coding agents exhibit substantial but incomplete feature-lifting capability, with large performance differences across model backends. Absolute 200-row rates are pulled down by 24 shared freeze-preflight blocks.

## 5.2 Failure Stage

| Stage | DeepSeek | Luna (OpenLux) | Qwen |
| --- | ---: | ---: | ---: |
| freeze_preflight_blocked | 24 | 24 | 24 |
| missing_submission | 0 | 0 | 28 |
| build | 0 | 3 | 5 |
| public | 19 | 27 | 40 |
| hidden | 13 | 14 | 23 |
| isolation | 1 | 0 | 0 |
| pass | 143 | 132 | 80 |
| other | 0 | 0 | 0 |

Build failures are thin for DeepSeek (0) and Luna (3); Qwen has 5 build fails plus 28 post-launch empty submissions. Isolation-only fails are rare (DeepSeek 1, Luna 0, Qwen 0). The shared freeze_preflight_blocked row is 24 on every model.

On launched tasks, DeepSeek’s remaining fails are almost all behavioral: public 19 + hidden 13 (plus isolation 1) out of 33 launched non-passes. Luna: public 27 + hidden 14. Qwen’s extra mass is post-launch missing_submission (TVE); interpret with §5.2.1.

> **Finding 2.** For backends that reliably emit a package, functional failures concentrate at the behavioral gates (Public/Hidden) rather than Build or Isolation. Qwen’s headline distribution is not yet a behavioral-gate result until empty submissions are separated.

## 5.2.1 Process vs capability

| Process | DeepSeek | Luna | Qwen |
| --- | ---: | ---: | ---: |
| freeze spec mismatch (never launched) | 24 | 24 | 24 |
| missing_submission after launch | 0 | 0 | 28 |
| empty TVE (no package) | 0 | 0 | 28 |
| rc=86 TVE (any) | 141 | 109 | 110 |
| rc=86 and Functional Pass | 114 | 78 | 43 |
| rc=123 step limit | 18 | 7 | 17 |
| rc=123 and Pass | 12 | 7 | 4 |
| rc=124 timeout | 0 | 0 | 3 |
| artifact-level fails (has package, gate=0) | 33 | 44 | 68 |

Qwen’s **28** post-launch empty submissions are empty-TVE (28/28). Official assigned score remains **80/200**, not 80/148. The 28 TVE empties must not be cited as Hidden-semantic failures. The 24 freeze blocks are shared and are not Qwen-specific.

DeepSeek records many rc=86 (141) but **114 still Functional Pass**. Luna post-launch missing_submission is 0 (encrypted-content retry recovered empties).

> Process failures materially affect Qwen (empty TVE) and inflate DeepSeek’s non-zero return codes, but they are analytically distinct from artifact-level feature-lifting failures.

## 5.3 Failure Mechanism

**Not computed.** Semantic labels require artifact/trajectory coding on the artifact-level failure sets (DeepSeek 33, Luna 44, Qwen 68). Mechanical Public/Hidden counts are not a Contract-Closure Gap.

Artifact-level first stages (denominator = has package ∧ gate=0):

| Stage | DeepSeek | Luna | Qwen |
| --- | ---: | ---: | ---: |
| build | 0 | 3 | 5 |
| public | 19 | 27 | 40 |
| hidden | 13 | 14 | 23 |
| isolation | 1 | 0 | 0 |
| other | 0 | 0 | 0 |

## 5.4 Task Difficulty

### Lift type

| Lift type | DeepSeek | Luna | Qwen |
| --- | ---: | ---: | ---: |
| Adapted | 71/100 (71%) | 69/100 (69%) | 38/100 (38%) |
| Composite | 19/32 (59%) | 16/32 (50%) | 8/32 (25%) |
| Direct | 53/68 (78%) | 47/68 (69%) | 34/68 (50%) |

### Entanglement level (`metadata.entanglement.level`)

All 200 frozen tasks are labeled `high`. This field currently **does not discriminate** and must not be used for Finding 4.

Lift type: Direct > Adapted > Composite on all three models (small Composite n=32). Hard-50 is *easier* than launched Python-150 for DeepSeek/Luna (§5.1), so “calibrated expansion is harder” is **not** supported by these Main runs.

## 5.5 Extraction Quality (pass subset only)

| Model | n pass | Median RRES | Median copied_fraction | RRES Python-150 | RRES Hard-50 |
| --- | ---: | ---: | ---: | ---: | ---: |
| DeepSeek V4 Flash | 143 | 0.927 | 0.949 | 1.000 | 0.219 |
| gpt-5.6-luna (OpenLux) | 132 | 0.323 | 0.103 | 0.837 | 0.044 |
| Qwen3.6-35B-A3B-FP8 | 80 | 0.728 | 0.519 | 0.988 | 0.104 |

Paired subset where **all three** Functional Pass: n=68, median RRES DeepSeek=0.947654, Luna=0.462401, Qwen=0.7738025.

> **Finding 5 (provisional).** Correctness and compactness are distinct: Functional Pass does not imply a compact extraction. Cross-model RRES rankings use only the triple-pass subset.

## Cross-model agreement (task-level Functional Pass)

The 24 freeze-blocked tasks appear in `D0L0Q0`. Launched-only all-fail is 23 tasks.

| Pattern | Tasks |
| --- | ---: |
| D0L0Q0 | 47 |
| D1L0Q0 | 12 |
| D1L1Q0 | 54 |
| D1L0Q1 | 9 |
| D1L1Q1 | 68 |
| D0L1Q0 | 7 |
| D0L1Q1 | 3 |

## 5.6 Case Studies

Not written. Candidate IDs (mechanical shortlist) are in `case_candidates.json`.

## Next

1. Code semantic labels on artifact-level failures (5.3).
2. Pick 3–4 cases from `case_candidates.json`.
3. Keep GLM-Flash off the main table until complete.

