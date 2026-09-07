# FeatureLiftBench: Evaluating Repository-Level Feature Extraction by Code Agents

**Headline evaluation.** Freeze v2 Python-150, OpenHands Official Main, one attempt per task, 2026-09-04/06. Functional Pass = build ∧ public ∧ hidden ∧ isolation; empty submissions count as failures. Official Hard-50 is appendix-only.

## Abstract

Extracting a reusable feature from an existing repository is different from fixing a reported issue or generating a new implementation from scratch. An agent must locate relevant implementation evidence, recover its transitive behavioral and resource closure, adapt it into a standalone package, and preserve observable behavior without retaining a runtime dependency on the source repository. Existing code-agent benchmarks do not isolate this combination of repository understanding, behavioral preservation, modularization, and compactness.

We introduce **FeatureLiftBench**, a benchmark for repository-level, behavior-preserving feature extraction by code agents. The released Python suite contains 200 tasks from 176 pinned repositories; the headline leaderboard is the frozen Python-150 split. Under the Full-Repository / No-Hint protocol, an agent receives the complete repository and a complete public behavioral contract, but no source-location hints, benchmark tests, Hidden tests, or reference implementation. Deterministic Dockerized checks evaluate buildability, Public behavior, deeper Hidden behavior, and independence from the source repository. Compactness of passing packages is measured separately.

On six OpenHands backends, Functional Pass ranges from **36/150 (24.0%)** to **115/150 (76.7%)**. The strongest model still leaves 35 tasks unsolved, and 28 tasks are unsolved by every backend. Failures concentrate at Public and Hidden behavior rather than at packaging. On the two strongest models, artifact-level failures are dominated by incomplete contract recovery rather than by missing packages or uninspected source trees. Passing Pro and Flash packages are copy-heavy, while Luna often copies less on the same tasks. FeatureLiftBench provides a reproducible basis for measuring how code agents turn repository evidence into independent, behavior-complete artifacts.

## 1. Introduction

Software maintenance frequently requires engineers to extract an existing capability from a large system: a parser must become a small library, a configuration resolver must be reused in another service, or a plugin registry must be separated from the framework that originally hosted it. This operation is common in modernization, dependency reduction, service decomposition, and reuse of legacy code. It is also deceptively difficult. The target behavior may be distributed across helper functions, stateful registries, resources, configuration defaults, error classes, and third-party dependencies. Copying the most obvious implementation region may produce a package that works on a happy path while silently changing edge behavior or retaining hidden dependencies on the original repository.

Repository-level code agents appear well suited to this task. They can search large workspaces, inspect call sites and tests, edit multiple files, execute tools, and package new artifacts. Current evaluation paradigms do not isolate whether an agent can perform behavior-preserving feature extraction. Issue-resolution benchmarks such as SWE-bench ask an agent to repair a repository until tests pass. Greenfield code-generation benchmarks ask for a new implementation from a specification. Repository-understanding and localization studies test whether the relevant code can be found. None of these settings simultaneously requires an agent to recover an existing feature from an entangled repository, preserve a declared behavioral contract, remove dependence on the original package, and avoid solving the task through broad repository copying.

Feature extraction therefore combines at least three obligations:

1. **Locate:** identify implementation evidence relevant to the requested capability.
2. **Close:** recover the APIs, helpers, state, resources, dependencies, and edge semantics needed for behavioral completeness.
3. **Isolate:** package the recovered feature so that it executes independently of the source repository.

We use this decomposition as an explanatory model rather than a causal factorization. A final failure does not by itself reveal which obligation failed; semantic labels require trajectory and artifact evidence.

We introduce FeatureLiftBench, a benchmark that evaluates these obligations under a controlled Full-Repository / No-Hint protocol. Each task provides a complete repository pinned to an immutable source revision and a complete public contract describing the required package interface and observable behavior. The agent may inspect the entire repository, but it is not given source-location hints, benchmark tests, Hidden tests, or a reference solution. It must produce a standalone `featurelifted` package. A submission passes only when it builds, satisfies both primary and deeper contract tests, and remains functional after access to the original repository is removed.

FeatureLiftBench separates two quality dimensions. **Functional Pass** measures whether the submission satisfies build, Public, Hidden, and isolation gates. **Reference-Relative Extraction Size (RRES)** measures the normalized footprint of a functionally passing package relative to an evaluator-side feasible reference. Correctness and compactness are not combined into one score: a broad vendoring solution may preserve behavior but fail to demonstrate a compact extraction, while a small package may simply be incomplete.

The released Python-200′ suite combines a frozen 150-task baseline with a separately constructed Hard-50 expansion, for 200 tasks from 176 repositories. The headline empirical study is freeze v2 Official Main on **Python-150** with six model backends. Official Hard-50 is reported in the appendix; it is not the paper’s difficulty claim.

The study asks four questions. How often do current code agents produce independent, behavior-complete feature packages? When they pass, how compact are the extractions? At which gate do they fail, and which contract obligations remain open? How do executable feedback, process scaffolds, and trajectory cost change outcomes?

The analysis points to a recurring gap between plausible repository work and verifiable feature closure. Strong agents frequently produce buildable packages and pass primary behavior checks, yet fail on required exports, boundary conditions, exception semantics, stateful behavior, resource closure, or preservation details. We call this **contract-closure failure**. It is not inferred from a Hidden failure alone: attribution requires evidence that the relevant requirement was public and that the trajectory or artifact omitted or changed it.

This paper makes three contributions:

1. **Benchmark asset.** We define repository-level, behavior-preserving feature extraction and construct a suite of 200 tasks from 176 pinned Python repositories, with public contracts, source registries, deterministic evaluators, evaluator-side feasible references, isolation checks, and task-level provenance. Freeze v2 contract-completeness labels are 200/0/0 after repairing 32 confirmed surface or entry-point defects from the predecessor freeze, without changing suite membership.
2. **Evaluation protocol.** We introduce a Full-Repository / No-Hint protocol that fixes repository, contract, runtime, budget, and evaluator while varying model backends. We report deterministic Functional Pass separately from pass-conditioned compactness and process cost.
3. **Diagnostic analysis.** We analyze failure stages, semantic contract-closure symptoms, in-suite construction difficulty, and pass-conditioned compactness on freeze v2 Python-150. Historical information-boundary and cost measurements are reported as non-main diagnostics, not as methods that raise the leaderboard.

## 2. Related Work

**Executable software-engineering benchmarks.** SWE-bench asks language models to resolve real GitHub issues in existing repositories. Terminal-Bench evaluates agents on realistic command-line tasks. Their central unit is typically an issue, a failing test, or a requested modification to the original workspace. FeatureLiftBench instead evaluates extraction into a new independent artifact. The source repository is evidence, not the final execution environment, and passing requires behavior preservation after the source package is unavailable. Agent-computer interfaces and runtime design can change executable-agent performance (SWE-agent, Harness-Bench). We therefore fix OpenHands as the Official Main runtime for the model leaderboard. Runtime comparisons, when available, are reported separately rather than mixed into model scores.

**Code generation, repository understanding, and localization.** Function-level suites such as HumanEval, MBPP, DS-1000, BigCodeBench, and LiveCodeBench measure synthesis from a specification. Repository-level completion and retrieval (RepoCoder, RepoBench) study whether a model can use in-repo context to finish or locate code. Feature-location research asks whether a developer or tool can identify files or regions relevant to a concern. Feature lifting requires both inference and artifact construction, but success is not reducible to either. Locating the correct implementation is insufficient if transitive behavior or resources are omitted; generating a behaviorally similar implementation is insufficient if the public contract or independent package boundary is not preserved.

**Program slicing, modularization, and library extraction.** Feature extraction is related to program slicing, multi-dimensional separation of concerns, and refactoring that extracts and modularizes behavior. Classical techniques typically assume a program representation, slicing criterion, or human-specified boundary. FeatureLiftBench evaluates an autonomous agent from a natural-language public contract and a complete repository, and grades the final independent artifact by observable behavior. Frozen references are feasible comparison points; RRES is a compactness proxy rather than a proof of a minimal semantic slice.

**Information boundaries.** Agent performance depends on the model, runtime, tools, context policy, and feedback interface (OpenHands, SWE-agent, Harness-Bench). The main leaderboard fixes OpenHands and varies the model backend. Information ablations instead change what task evidence is visible while preserving model, runtime, evaluator, and budget.

## 3. The FeatureLiftBench Benchmark

### 3.1 Setting

A task consists of a pinned source repository \(R\), a public contract \(S\), an initial workspace \(W\), and a private evaluator \(J\). Given \((R,S,W)\), an agent produces a package \(P\) under a fixed execution protocol:

\[
P = \operatorname{Run}(M, H, R, S, W)
\]

where \(M\) is the model backend and \(H\) is the fixed Official Main runtime. The evaluator assigns:

\[
\operatorname{Functional}(P)
= B(P) \land P_{\mathrm{pub}}(P) \land H_{\mathrm{hid}}(P) \land I(P).
\]

\(B\) checks installation and imports. \(P_{\mathrm{pub}}\) checks primary behavior from the public contract. \(H_{\mathrm{hid}}\) checks deeper combinations and boundary behavior from that same contract. \(I\) checks independence from the source repository. A valid Hidden test must map to a published contract requirement.

The agent receives the complete source tree and contract but no source-location hint. It does not see Public tests, Hidden tests, evaluator code, or the frozen reference. Extraction, adaptation, and behaviorally equivalent reimplementation are allowed. Runtime imports from the source project, forbidden paths, and undeclared dependency channels are disallowed.

Pipeline: pinned repository + public contract → Full-Repository / No-Hint execution → standalone `featurelifted` package → Build → Public → Hidden → Isolation → Functional Pass, then pass-conditioned compactness.

### 3.2 Suite

Python-200′ contains 200 tasks from 176 repositories. Headline scores use the frozen Python-150 split.

| Split | Tasks | Repositories | Role |
| --- | ---: | ---: | --- |
| Frozen Python-150 | 150 | 127 | Headline evaluation |
| Hard-50 | 50 | 50 | Appendix split |
| Python-200′ | 200 | 176 | Released suite |

The suite emphasizes Python libraries, developer tools, and framework components. One source repository may support multiple distinct tasks in the baseline split. Every task pins its upstream revision in a canonical registry.

Three descriptive axes are not shown to the agent and do not affect Functional Pass:

- **Feature family:** parsing, serialization, configuration, validation, resources, registries, caching, protocols, algorithms, workflows.
- **Primary entanglement:** data-model, parser-state, framework, configuration/environment, resource, or third-party dependency entanglement.
- **Lift type:** Direct, Adapted, or Composite.

Python-200′ contains 68 Direct, 100 Adapted, and 32 Composite tasks. Python-150 itself is 56 Direct, 76 Adapted, and 18 Composite. Hard-50 increases coverage of registry/plugin dispatch, workflow and session orchestration, configuration discovery, validation boundaries, deep parsing, and copy traps. Construction-time Flash calibration on Hard-50 was 29/50, inside a predeclared 40–65% band. That figure is design evidence. Freeze v2 Official Main on the same 50 IDs is in the appendix; in-suite hard3 on Python-150 is the difficulty contrast used in the main analysis.

An earlier External-50 expansion is a side split, not part of Python-200′. Strong-model pass rates of 90–94% and pass-conditioned footprints near one reference-relative unit showed an easy, copy-heavy construction.

### 3.3 Construction and validation

A candidate is retained only if it is realistic, solvable from the pinned repository and public contract, checkable with deterministic build/behavior/isolation tests, and integrity-preserving (no credit from protected tests or forbidden source dependencies).

Each task records a source revision and digest, public contract (`public_spec` rendered to `TASK.md`), required API, locked dependencies, Public/Hidden mapping, evaluator, and a feasible reference. References are never exposed to agents. Gates check source materialization, imports, reference behavior, isolation, forbidden dependencies, and freeze identity.

Independently of agent scores, freeze v2 labels whether Hidden tests stay inside the published `required_api` and whether declared source entry points resolve. The published labels are **200 meets_standard / 0 violates / 0 undetermined**. This is contract-completeness of the asset, not a Functional Pass table and not Hidden-fairness gold. Predecessor-freeze scores must not be transferred onto freeze v2.

### 3.4 Metrics

**Functional Pass@1.** One point only if all four gates pass. Failures receive an exclusive first stage: missing submission → build → public → hidden → isolation. An empty submission is a functional failure. Runner `status` is not the score.

**Compactness.** For a passing submission \(P\) and feasible reference \(P_{\mathrm{ref}}\):

\[
\operatorname{RRES}(P)
= \frac{\operatorname{normalized\_size}(P)}
       {\operatorname{normalized\_size}(P_{\mathrm{ref}})}.
\]

Reported only on functional passes, with copy fraction and class (copy-heavy vs compact). Cross-model compactness uses the same-task intersection on which both pass.

**Process and cost.** Tokens, steps, latency, and empty submissions are diagnostics. On historical passing trajectories, \(T^*\) is the earliest unique package tree that passes the evaluator. It is undefined for failures and is not a stopping rule. It is not recomputed on freeze v2.

## 4. Experiments

### 4.1 Setup

The headline study evaluates six backends on freeze v2 Python-150 (`6c20ff0307762503a73cbb9ff32e9992c6446e4b17483a68373027be58cbf419`). Official Hard-50 is appendix-only.

| Factor | Official Main treatment |
| --- | --- |
| Task contract and repository snapshot | Fixed per task (freeze v2) |
| Agent runtime | OpenHands Official Main |
| Envelope | 120 steps, 128k context, No-Hint |
| Images | `featureliftbench-agent/eval:python200-prime-212930ea` |
| Model backend | Varied |
| Public tests, Hidden tests, reference | Never exposed in Main |

Each cell is one attempt. We report Wilson 95% intervals and exact McNemar tests on discordant tasks. One attempt does not estimate run-to-run variance.

Backends: DeepSeek V4 Pro, DeepSeek V4 Flash, gpt-5.6-luna (OpenLux), GLM-5.3-Flash, Qwen3.6-35B-A3B-FP8, GPT-OSS 120B. Pro was run on `python150-prime-v2-main-r1`. The other five were run on `python200-prime-v2-main-r1` and then restricted to the same 150 task IDs. Dates: 2026-09-04/06. Timeout: 3600s. Flagship GLM-5.3 abort directories are excluded.

### 4.2 Overall capability

**Table 1.** Functional Pass@1 on freeze v2 Python-150. Core-100 / hard3 is the in-suite construction split, not official Hard-50.

| Model | Pass | Rate | Wilson 95% | Core-100 | hard3 | Empty |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| DeepSeek V4 Pro | 115/150 | 76.7% | 69.3–82.7 | 94/100 | 21/50 | 0 |
| DeepSeek V4 Flash | 108/150 | 72.0% | 64.3–78.6 | 90/100 | 18/50 | 0 |
| gpt-5.6-luna (OpenLux) | 102/150 | 68.0% | 60.2–74.9 | 82/100 | 20/50 | 6 |
| GLM-5.3-Flash | 68/150 | 45.3% | 37.6–53.3 | 62/100 | 6/50 | 38 |
| Qwen3.6-35B | 63/150 | 42.0% | 34.4–50.0 | 55/100 | 8/50 | 25 |
| GPT-OSS 120B | 36/150 | 24.0% | 17.9–31.4 | 25/100 | 11/50 | 2 |

The benchmark is not saturated: Pro still fails 35/150, and 28 tasks are unsolved by all six models (22 of them hard3). Backends separate clearly. Pro exceeds Qwen by 34.7 points, GLM by 31.3 points, and OSS by 52.7 points (McNemar \(p \ll 0.001\)). Pro versus Luna is 18/5 (\(p=0.011\)). Pro versus Flash is 10/3 (\(p=0.092\)) with overlapping Wilson intervals, so we do not claim that Pro is significantly stronger than Flash. Flash versus Luna is not significant (\(p=0.33\)). Luna versus GLM is 43/9 (\(p \approx 2\times 10^{-6}\)). GLM versus Qwen is 27/22 (\(p=0.57\)); we do not claim that GLM is stronger than Qwen. Qwen’s 25 empty submissions and GLM’s 38 empty submissions remain functional failures; we do not rewrite those rows as 63/125 or 68/112.

**Finding 1.** Current coding agents exhibit substantial but incomplete feature-lifting capability on frozen Python-150, with large performance differences across model backends.

### 4.3 Failure stages

**Table 2.** Mutually exclusive first outcomes on freeze v2 Python-150.

| Model | Pass | Missing | Build | Public | Hidden | Isolation |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| DeepSeek V4 Pro | 115 | 0 | 0 | 25 | 10 | 0 |
| DeepSeek V4 Flash | 108 | 0 | 0 | 26 | 15 | 1 |
| gpt-5.6-luna (OpenLux) | 102 | 6 | 3 | 27 | 12 | 0 |
| GLM-5.3-Flash | 68 | 38 | 3 | 31 | 8 | 2 |
| Qwen3.6-35B | 63 | 25 | 6 | 35 | 21 | 0 |
| GPT-OSS 120B | 36 | 2 | 18 | 70 | 23 | 1 |

Pro and Flash never fail to deliver a package and never fail Build. Isolation-first failure occurs four times in the matrix. Residual failure is Public then Hidden. OSS fails Public 70 times. Qwen’s 25 missing submissions and GLM’s 38 missing submissions are process events (Section 4.4).

**Finding 2.** Functional failures concentrate primarily at the behavioral gates: producing a buildable package is substantially easier than recovering complete required behavior.

### 4.4 Process versus capability

Functional Pass does not change with process status. Some failures occur before a gradable package exists.

**Table 3.** Empty submissions on Python-150. These rows are functional failures and are excluded from Section 5.1.

| Model | Empty | Of which TVE / encrypted |
| --- | ---: | ---: |
| DeepSeek V4 Pro | 0 | 0 |
| DeepSeek V4 Flash | 0 | 0 |
| gpt-5.6-luna (OpenLux) | 6 | 5 |
| GLM-5.3-Flash | 38 | 1 |
| Qwen3.6-35B | 25 | 25 |
| GPT-OSS 120B | 2 | 2 |

Qwen’s 25 empty rows are OpenHands `security_risk` tool-validation errors, typically within tens of seconds; they do not demonstrate Hidden semantic failure. GLM’s 38 empty rows are mostly early session ends with no files under `submission/` (one tool-validation error); they are not TVE-dominated like Qwen. Luna has six empty rows (three tool-validation errors, two invalid encrypted-content events, and one file-less workspace). Flash records 82 functional passes whose runner status is not `passed`; GLM records 23; those rows remain passes.

**Table 3b.** Python-150 process cost diagnostics from `agent/usage.json`. Cumulative `total_tokens` sums provider usage across calls; for Pro/Flash this includes cached prompts. Incremental tokens are uncached prompt plus completion when cache accounting exists. Luna and GLM returned no token fields (`usage_unverified`); we do not impute them. This table is not a leaderboard.

| Model | Tokens recorded | Median total | Median incremental | Median completion | Median API calls | Median steps | Median duration |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| DeepSeek V4 Pro | 150/150 | 2.42M | 88.0k | 32.8k | 43 | 42 | 8.0 min |
| DeepSeek V4 Flash | 150/150 | 4.23M | 123.6k | 55.8k | 65 | 63 | 7.8 min |
| gpt-5.6-luna (OpenLux) | 0/150 | — | — | — | 29 | 36 | 8.0 min |
| GLM-5.3-Flash | 0/150 | — | — | — | 84 | 86 | 21.2 min |
| Qwen3.6-35B | 150/150 | 1.82M | — | 30.2k | 51 | 42 | 13.2 min |
| GPT-OSS 120B | 150/150 | 0.53M | — | 12.9k | 24 | 19 | 1.6 min |

Process failures affect some model–harness configurations, but they are analytically distinct from artifact-level feature-lifting failures.

## 5. Analysis

### 5.1 Failure mechanism

Mechanical stages locate the first failing gate. They do not name a cause. We close-read artifact-level failures: the public contract, the first-failure evaluator log, and the submitted package, plus a trajectory screen for whether the agent inspected `repo/`. Hidden test names, inputs, and assertions are not reported. Coding is an assistant first pass (L1), not independent human dual review, and is not gold.

The census is Pro and Flash artifact-level failures (\(n=63\); Pro 28, Flash 35). Other backends, including GLM’s 44 artifact-level failures, are not merged into this denominator.

**Table 4.** Symptom vocabulary.

| Symptom | Observable manifestation | Required evidence |
| --- | --- | --- |
| Localization | No inspection of the relevant source region | Trajectory + package |
| Contract/API completion | Required symbol, member, or branch is absent | Public contract + package |
| Dependency / resource closure | Helper, registry, config, or resource omitted | Source evidence + failing case |
| Behavioral drift | API present; return, exception, or edge semantics differ | Contract + evaluator + package |
| Packaging / modularization | Logic exists but is not independently installable | Package tree + isolation evidence |
| Copy-heavy pass | Gates pass through broad vendoring | Passing result + RRES/copy |

**Table 5.** Primary semantic cause on Pro and Flash artifact failures (L1, \(n=63\)). Not independent human gold.

| Primary cause | Total | Pro | Flash |
| --- | ---: | ---: | ---: |
| Behavior drift | 54 | 26 | 28 |
| Contract/API completion | 7 | 2 | 5 |
| Packaging / modularization | 2 | 0 | 2 |
| Dependency / resource closure | 0 | 0 | 0 |
| Localization | 0 | 0 | 0 |
| Unknown | 0 | 0 | 0 |
| Coded artifact failures | 63 | 28 | 35 |

Closure classes (API completion plus behavior drift) account for 61/63 rows. The modal label is behavior drift: the required surface is present, but observable semantics are not. Localization is 0 after the trajectory screen: every remaining failure issued a deep read of `repo/` (find, grep, cat, or file view). Packaging appears twice on Flash. We do not treat localization as solved suite-wide; on this Pro+Flash artifact-fail slice, the dominant residue is incomplete contract recovery rather than missing packages or uninspected source trees.

A stratified L1 sample of Luna, Qwen, and OSS artifact failures (45 draws, 32 coded rows; seed `python150-postsample-v1`) is **not** pooled into the 63.

**Table 6.** Stratified L1 sample of Luna/Qwen/OSS artifact failures (32 coded rows).

| Primary cause | Total | Luna | Qwen | OSS |
| --- | ---: | ---: | ---: | ---: |
| Behavior drift | 14 | 4 | 7 | 3 |
| Contract/API completion | 9 | 4 | 0 | 5 |
| Dependency / resource closure | 4 | 0 | 3 | 1 |
| Packaging / modularization | 5 | 0 | 1 | 4 |
| Localization | 0 | 0 | 0 | 0 |
| Coded sample rows | 32 | 8 | 11 | 13 |

Luna remains in the same direction (drift and missing exports). Qwen and OSS additionally fail Build by omitting transitive dependencies or by importing the original package. That is a weaker-backend packaging story, not a five-model pie chart.

**Finding 3.** On the Pro+Flash artifact-fail slice, failures are dominated by incomplete recovery of the required behavioral contract (a contract-closure gap), rather than by inability to emit an installable package or by failing to inspect the source tree. A stratified sample of the other backends does not reverse that direction on Luna, but adds packaging and missing-helper failures on the weaker backends. The proportions are an L1 first pass, not gold.

### 5.2 Task difficulty

**Table 7.** Functional Pass by in-suite construction split. hard3 is not official Hard-50.

| Model | Core-100 | hard3 |
| --- | --- | --- |
| DeepSeek V4 Pro | 94/100 (94.0%) | 21/50 (42.0%) |
| DeepSeek V4 Flash | 90/100 (90.0%) | 18/50 (36.0%) |
| gpt-5.6-luna (OpenLux) | 82/100 (82.0%) | 20/50 (40.0%) |
| GLM-5.3-Flash | 62/100 (62.0%) | 6/50 (12.0%) |
| Qwen3.6-35B | 55/100 (55.0%) | 8/50 (16.0%) |
| GPT-OSS 120B | 25/100 (25.0%) | 11/50 (22.0%) |

**Table 8.** Functional Pass by lift type. Composite \(n=18\).

| Model | Direct | Adapted | Composite |
| --- | --- | --- | --- |
| DeepSeek V4 Pro | 51/56 (91.1%) | 55/76 (72.4%) | 9/18 (50.0%) |
| DeepSeek V4 Flash | 50/56 (89.3%) | 51/76 (67.1%) | 7/18 (38.9%) |
| gpt-5.6-luna (OpenLux) | 45/56 (80.4%) | 50/76 (65.8%) | 7/18 (38.9%) |
| GLM-5.3-Flash | 40/56 (71.4%) | 24/76 (31.6%) | 4/18 (22.2%) |
| Qwen3.6-35B | 31/56 (55.4%) | 27/76 (35.5%) | 5/18 (27.8%) |
| GPT-OSS 120B | 16/56 (28.6%) | 16/76 (21.1%) | 4/18 (22.2%) |

Of 28 tasks unsolved by every model, 22 are hard3. OSS barely moves (25% versus 22%). Entanglement level is uniformly high on this split, so it cannot be tested. Lift type is directional but weaker; Composite cells are small. Qwen’s Adapted cell includes 16 empty submissions and GLM’s Adapted cell includes 27; those are process events rather than a lift-type effect.

**Finding 4.** Feature-lifting difficulty on Python-150 varies with the in-suite hard3 construction split and, more weakly, with lift type. Entanglement level is uniformly high and cannot be tested here.

### 5.3 Extraction quality

Compactness is reported only on functional passes. Survivor sets differ by model, so medians are not a second ranking of the same 150 tasks. Cross-model comparisons use paired intersections.

**Table 9.** Pass-conditioned compactness on freeze v2 Python-150. RRES = submission LOC / reference LOC.

| Model | \(n\) | Median RRES | Median copy | Copy-heavy | Compact |
| --- | ---: | ---: | ---: | ---: | ---: |
| DeepSeek V4 Pro | 115 | 0.993 | 0.957 | 108 | 4 |
| DeepSeek V4 Flash | 108 | 0.998 | 0.968 | 105 | 1 |
| gpt-5.6-luna (OpenLux) | 102 | 0.815 | 0.164 | 54 | 37 |
| GLM-5.3-Flash | 68 | 1.013 | 0.947 | 64 | 0 |
| Qwen3.6-35B | 63 | 0.975 | 0.757 | 43 | 9 |
| GPT-OSS 120B | 36 | 0.983 | 0.180 | 18 | 12 |

Pro and Flash passing packages are almost entirely copy-heavy (median copy 0.96–0.97). GLM’s passing set is also copy-heavy (median copy 0.95; 0 compact). Luna’s passing set has median copy 0.16 at median RRES 0.82. On the 97 tasks both Pro and Luna pass, median copy is 0.97 versus 0.19. On the 59 tasks both GLM and Luna pass, median copy is 0.94 versus 0.28. On the 17 tasks all six models pass, Pro/Flash copy remains ≈0.96–0.98 while Luna is 0.51. Official Hard-50 has no evaluator-side `reference_solution/`, so we do not report RRES there.

**Finding 5.** Correctness and compactness are distinct: a functional pass does not imply a compact extraction relative to the frozen reference.

### 5.4 Case studies

We describe observable behavior, not Hidden test identifiers.

**Process non-delivery.** Qwen on `babel__plural_core__001` ends without a package (tool validation). GLM on `alembic__revision_map_core__hard3_001` also ends without a package after a short repository inspect, which is not a Hidden mismatch; Pro and Flash fail that same task at Public drift.

**Public drift after inspecting the repository.** On `alembic__revision_map_core__hard3_001`, Pro and Flash implement `get_revision` but treat the argument `'base'` as the symbolic base of the map, shadowing a revision whose identifier is literally `base`. The API is present; the contract case is not.

**Hidden completion with an open branch.** On `aiohttp__url_params_core__hard3_001`, exception types and token checks exist, yet an invalid-name path required by the public contract still does not raise. Localization is not the residue.

**Isolation versus copy-heavy success.** Flash on `typer__command_parser_core__001` fails Isolation via `forbidden_imports`. On `blinker__signal_registry_core__001`, Pro, Flash, and Luna all pass with copy-heavy packages (RRES 9.0 / 18.4 / 4.6). Passing is not compact.

### 5.5 Information boundary and cost (not freeze v2 Main)

These two measurements diagnose mechanism. They are not freeze v2 Main scores.

**Public feedback.** A paired ablation on 12 historical DeepSeek V4 Flash tasks mounts `public_tests/` while keeping Hidden private. Main is 0/12; Public-feedback is 4/12. All six selected Public failures flip Public to 1; Hidden usually does not. Executable Public tests are a real bottleneck and not a general Hidden oracle.

**Earliest sufficiency \(T^*\).** On replayable historical Flash passing trajectories (superseded 150+External-50 suite), 138 of 145 passes have gold. Median \(T^*/T_{\mathrm{total}}\) is 0.40, with a median 0.75M tokens after a sufficient package first exists (Direct 0.36, Adapted 0.40, Composite 0.51). Post-sufficiency spend is mostly self-testing the agent cannot ground in Hidden. This is not a stopping rule and is not recomputed on freeze v2.

**Process scaffolds.** Development interventions did not produce a stable Functional gain over legal Main on the subsets where they were tried. They are negative diagnostics, not methods in the leaderboard.

| Hypothesis | Interventions | Observed outcome |
| --- | --- | --- |
| Better self-verification is sufficient | Self-generated probes, test-first extraction, verification ledger | No stable Functional gain; some variants cost more or regress |
| Executable contract checklists close behavior | Self-Contract, Exec-Contract, spec-adversarial checks | Can repair Public; evaluated Hidden subsets do not improve reliably |
| Correct intermediate packages are overwritten | Repair loops, Rescue+, best-so-far replay | No stable gain; 0/51 failed trajectories contain an earlier pass |
| Tighter budget/context control improves quality | 2M cap, adaptive stop, compressed context, structure guidance | Token savings trade off against Functional Pass |

## 6. Discussion

Feature lifting asks a different question from issue repair. A repair agent succeeds inside the original repository and can rely on its package layout, resources, and test harness. A feature-lifting agent must infer which parts of that environment are semantically necessary and reconstruct them behind a new package boundary. It must satisfy an output contract after the original repository is removed.

The task is also different from code localization. Finding a relevant symbol can be necessary, but the Alembic revision-map and aiohttp parameter cases show why it is insufficient: agents inspect the repository and still miss declared semantics. Conversely, a behaviorally equivalent rewrite can pass even if it copies little upstream code. FeatureLiftBench therefore evaluates delivered behavior and artifact independence, not whether the agent followed one prescribed extraction strategy.

Correctness and compactness should remain separate. A broad vendoring solution may preserve behavior but offer little reusable modularization. A very small package may omit rare behavior. On freeze v2 Python-150 the split appears inside the passing set: Pro, Flash, and GLM are copy-heavy, Luna is not, on large paired intersections. In-suite hard3, not official Hard-50, is the difficulty contrast used in the main analysis.

A useful agent workflow must improve the evidence available for contract closure rather than merely add procedural steps. Promising directions include explicit obligation tracking tied to public requirements, generation of boundary cases from exception and state semantics, provenance-aware dependency closure, and calibrated uncertainty when a requirement cannot be verified legally. Executable Public tests can expose basic mismatches; deeper Hidden behavior remains a generalization problem under the Main information boundary.

Main scores characterize model backends embedded in a fixed OpenHands Official Main configuration. They are not measurements of base models independent of runtime, prompt, context policy, or provider behavior. Task-factor and semantic-failure analyses are descriptive. Harness-Bench argues that executable-agent capability should be reported at the model–harness configuration level; FeatureLiftBench adopts that reporting discipline while studying a different task construct.

## 7. Limitations

**Construct.** Functional Pass is a deterministic but finite operationalization of behavioral completeness. Finite tests cannot prove semantic equivalence. Freeze v2 200/0 labels measure undeclared Hidden members and dangling entry points; they are not Hidden-fairness gold. RRES and copy fraction are proxies.

**Internal.** Results depend on source materialization, locked dependencies, prompt and context policy, containers, model endpoints, and runner state. The Python-150 matrix uses freeze v2 and the attested `python200-prime-212930ea` images. Method pilots differ in subset and date and are not pooled into a causal estimate.

**External.** Python-200′ is a maintainer- and AI-assisted selection of Python libraries, tooling, and framework components. It is not a random sample and does not establish performance on large product applications, GUI, GPU, distributed, or non-Python systems. Popular upstream projects may appear in training data. Entanglement level is uniformly high on Python-150, so we do not claim an entanglement effect.

**Reliability.** One attempt per task does not estimate run-to-run variance. Wilson intervals and McNemar tests do not replace repeated-run sensitivity. Model APIs may change despite stable names.

**Annotation.** Task taxonomy and Section 5.1 labels include AI-assisted curation. Finding 3 is an assistant L1 close-read, not independent human dual review.

**Runtime.** Official Main fixes OpenHands. Scores may change under another runtime. DeepSeek Harness and Codex adapters are not paired into the model leaderboard.

**Licensing.** Upstream licenses are heterogeneous. Large archives may be distributed by checksummed acquisition rather than committed to git.

## 8. Conclusion

We presented FeatureLiftBench, a benchmark for repository-level, behavior-preserving feature extraction by code agents. The benchmark asks agents to turn a complete but entangled repository into an independent package under a public behavioral contract, without source-location hints or access to benchmark tests. Its deterministic evaluator separates functional correctness from the compactness of passing solutions.

On freeze v2 Python-150 under Official Main, six backends span 24.0% to 76.7% Functional Pass. The suite is not saturated. Failures concentrate at Public and Hidden behavior. On the two strongest models, artifact-level failures are dominated by incomplete contract recovery rather than by missing packages or uninspected source trees. Passing is not the same as compact extraction. By releasing tasks, source provenance, evaluators, traces, and reproducibility metadata, FeatureLiftBench aims to support research on agents that extract reusable software rather than only modify it in place.

## Appendix A. Reproducibility configuration

Headline evaluation: freeze v2 Python-150, OpenHands Official Main, one attempt per task, 2026-09-04/06.

- Freeze ID: `6c20ff0307762503a73cbb9ff32e9992c6446e4b17483a68373027be58cbf419`
- Candidate ID: `212930ea5363f21824afd5454c4da125052ad7a7d7186886e3dddef145811254`
- Agent image: `featureliftbench-agent:python200-prime-212930ea`  
  `sha256:0a05b2e797e1e39ee0630131cfd9e670403ce684cd74c8375ecf7e8d444f7595`
- Evaluator image: `featureliftbench-eval:python200-prime-212930ea`  
  `sha256:bacb3078db5e9558e9953575b5eb52f247b112dc63b7705ad7c48a7b4d864cae`
- Envelope: 120 steps, 128k context, No-Hint, Public/Hidden withheld
- Timeout: 3600s per task
- Pro suite: `experiments/python/openhands/deepseek-v4-pro/python150-prime-v2-main-r1`
- Other backends: `experiments/python/openhands/<model>/python200-prime-v2-main-r1`, restricted to the 150 Python-150 task IDs

Analysis tables: `reports/paper_analysis/python150_prime_v2_analysis_20260905/`.

## Appendix B. Paired McNemar tests (Python-150)

Exact tests on discordant tasks. “A wins” means A passes and B fails.

| A | B | A wins | B wins | \(p\) |
| --- | --- | ---: | ---: | ---: |
| Pro | Flash | 10 | 3 | 0.092 |
| Pro | Luna | 18 | 5 | 0.011 |
| Pro | Qwen | 52 | 0 | \(<10^{-15}\) |
| Pro | GLM | 48 | 1 | \(<10^{-12}\) |
| Pro | OSS | 82 | 3 | \(<10^{-20}\) |
| Flash | Luna | 16 | 10 | 0.33 |
| Flash | Qwen | 47 | 2 | \(<10^{-11}\) |
| Flash | GLM | 44 | 4 | \(<10^{-8}\) |
| Luna | GLM | 43 | 9 | \(2.0\times10^{-6}\) |
| GLM | Qwen | 27 | 22 | 0.57 |
| GLM | OSS | 44 | 12 | \(2.1\times10^{-5}\) |
| Qwen | OSS | 38 | 11 | \(1.4\times10^{-4}\) |

## Appendix C. Official Hard-50

Functional Pass on the official Hard-50 expansion, with Python-150 and 200-task totals. Pro was not run on Hard-50. Hard-50 packages have no `reference_solution/`, so we do not report RRES. These rates are not the paper’s difficulty claim.

| Model | Hard-50 | Python-150 | Python-200′ |
| --- | ---: | ---: | ---: |
| DeepSeek V4 Flash | 49/50 | 108/150 | 157/200 |
| gpt-5.6-luna (OpenLux) | 42/50 | 102/150 | 144/200 |
| GLM-5.3-Flash | 30/50 | 68/150 | 98/200 |
| Qwen3.6-35B | 23/50 | 63/150 | 86/200 |
| GPT-OSS 120B | 25/50 | 36/150 | 61/200 |

## Appendix D. LLM usage

Large language models assisted with task curation, annotation, analysis code, statistical summarization, and manuscript editing. Reported scientific claims, task contracts, evaluator behavior, quantitative summaries, and conclusions are reviewed by the authors. AI-assisted semantic labels are marked as such and are not reported as independent human gold.
