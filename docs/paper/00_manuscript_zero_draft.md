# FeatureLiftBench: Evaluating Repository-Level Feature Extraction by Code Agents

> **Status: draft · Last verified: 2026-09-06**  
> **Manuscript stage:** argument draft aligned with `fse26/` LaTeX.  
> **Headline:** freeze v2 Python-150 Official Main (Pro 115/150 … OSS 36/150).  
> Official Hard-50 is appendix-only. Functional Pass = build ∧ public ∧ hidden ∧ isolation.

## Abstract

Extracting a reusable feature from an existing repository is different from fixing a reported issue or generating a new implementation from scratch. An agent must locate the relevant implementation, recover its transitive behavioral and resource closure, adapt it into a standalone package, and preserve externally observable behavior without retaining a runtime dependency on the source repository. Existing code-agent benchmarks do not isolate this combination of repository understanding, behavioral preservation, modularization, and compactness.

We introduce **FeatureLiftBench**, a benchmark for repository-level, behavior-preserving feature extraction by code agents. Its main Python suite contains 200 tasks drawn from 176 pinned open-source repositories. Under the Full-Repository / No-Hint protocol, an agent receives the complete repository and a complete public behavioral contract, but no source-location hints, benchmark tests, Hidden tests, or reference implementation. Submissions are evaluated with deterministic Dockerized checks for buildability, public behavior, deeper Hidden behavior, and independence from the source repository. We separately measure the compactness of functionally passing packages relative to frozen reference solutions.

Under a frozen OpenHands Official Main protocol, current agents achieve **36/150 (24.0%) to 115/150 (76.7%)** Functional Pass on freeze v2 Python-150. The strongest backend still fails 35 tasks, and 28 tasks are unsolved by all five models. Failures concentrate at Public and Hidden behavior. On the two strongest models, artifact-level failures are dominated by incomplete contract recovery rather than missing packages. Compactness is a second dimension: Pro and Flash passes are copy-heavy, while Luna often copies less on the same tasks. FeatureLiftBench provides a reproducible basis for measuring repository-level feature extraction and for diagnosing how code agents turn repository evidence into independent, behavior-complete artifacts.

## 1. Introduction

Software maintenance frequently requires engineers to extract an existing capability from a large system: a parser must become a small library, a configuration resolver must be reused in another service, or a plugin registry must be separated from the framework that originally hosted it. This operation is common in modernization, dependency reduction, service decomposition, and reuse of legacy code. It is also deceptively difficult. The target behavior may be distributed across helper functions, stateful registries, resources, configuration defaults, error classes, and third-party dependencies. Copying the most obvious implementation region may produce a package that works on a happy path while silently changing edge behavior or retaining hidden dependencies on the original repository.

Repository-level code agents appear well suited to this task. They can search large workspaces, inspect call sites and tests, edit multiple files, execute tools, and package new artifacts. However, current evaluation paradigms do not isolate whether an agent can perform behavior-preserving feature extraction. Issue-resolution benchmarks ask an agent to repair a repository until tests pass. Greenfield code-generation benchmarks ask for a new implementation from a specification. Repository-understanding and localization benchmarks test whether the relevant code can be found. None of these settings simultaneously requires an agent to recover an existing feature from an entangled repository, preserve a declared behavioral contract, remove dependence on the original package, and avoid solving the task through broad repository copying.

Feature extraction therefore combines at least three obligations:

1. **Locate:** identify the implementation evidence relevant to the requested capability;
2. **Close:** recover the APIs, helpers, state, resources, dependencies, and edge semantics needed for behavioral completeness;
3. **Isolate:** package the recovered feature so that it executes independently of the source repository.

We use this decomposition as an explanatory model rather than a causal factorization. In particular, a final failure does not by itself reveal which obligation failed; semantic labels require trajectory and artifact evidence.

We introduce **FeatureLiftBench**, a benchmark that evaluates these obligations under a controlled Full-Repository / No-Hint protocol. Each task provides a complete repository pinned to an immutable source revision and a complete public contract describing the required package interface and observable behavior. The agent may inspect the entire repository, but it is not given source-location hints, benchmark tests, Hidden tests, or a reference solution. It must produce a standalone `featurelifted` package. A submission passes only when it builds, satisfies both basic and deeper contract tests, and remains functional after access to the original repository is removed.

FeatureLiftBench separates two quality dimensions. **Functional Pass** measures whether the submission satisfies build, Public, Hidden, and isolation gates. **Reference-Relative Extraction Size (RRES)** measures the normalized footprint of a functionally passing package relative to a frozen feasible reference. Correctness and compactness are not combined into one score: a broad vendoring solution may preserve behavior but fail to demonstrate a compact extraction, while a small package may simply be incomplete.

The released Python-200′ suite combines a frozen 150-task baseline with a separately constructed Hard-50 expansion, for 200 tasks from 176 repositories. The headline empirical study is freeze v2 Official Main on Python-150 with five model backends. Official Hard-50 is reported in the appendix.

Our empirical study is organized around three questions. First, how often do current code agents produce independent, behavior-complete feature packages, and how does performance vary across model backends? Second, when agents pass, how compact are their extractions and which task properties are associated with success and cost? Third, where do unsuccessful trajectories lose alignment with the public contract, and which legal information or process interventions change those failures?

Our analysis points to a recurring gap between plausible repository work and verifiable feature closure. Strong agents frequently produce buildable packages and pass basic behavior checks, yet fail on required exports, boundary conditions, exception semantics, stateful behavior, resource closure, or preservation details. We refer to this recurring symptom as **contract-closure failure**. It is not inferred from a Hidden failure alone: attribution requires evidence that the relevant requirement was public and that the trajectory or artifact omitted or changed it. The current evidence also suggests that executable Public feedback and Hidden behavioral completeness are distinct layers. Revealing Public tests repairs the Public gate on a selected set of Public failures, while most paired Hidden failures remain unchanged.

This paper makes three main contributions:

1. **Benchmark asset.** We define repository-level, behavior-preserving feature extraction and construct a suite of 200 tasks from 176 pinned Python repositories, with public contracts, source registries, deterministic evaluators, evaluator-side feasible references, isolation checks, and task-level provenance.
2. **Evaluation protocol.** We introduce a Full-Repository / No-Hint protocol that fixes the repository, contract, runtime, budget, and evaluator while varying model backends. We report deterministic Functional Pass separately from pass-conditioned compactness and process cost.
3. **Diagnostic analysis.** We analyze failure stages, semantic contract-closure symptoms, task factors, information boundaries, and trajectory cost. We also report negative results from legal self-testing, repair, checkpoint, context, and budget-control interventions rather than presenting them as successful methods.

## 2. Related Work

### 2.1 Executable Software-Engineering Benchmarks

Executable software-engineering benchmarks such as issue-resolution and terminal-agent suites have established the importance of real repositories, tool use, sandboxed execution, and test-based verification. Their central unit is typically an issue, a failing test, or a user-requested modification to the original workspace. FeatureLiftBench instead evaluates extraction into a new independent artifact. The source repository is evidence, not the final execution environment, and passing requires behavior preservation after the source package is unavailable.

**TODO(BIB):** remaining secondary citations (API-migration surveys, additional
agent-harness papers) can still be added; primary positioning against
SWE-bench, Terminal-Bench, HumanEval/BigCodeBench/LiveCodeBench, RepoCoder,
RepoBench, slicing/refactoring, and OpenHands/Harness-Bench is in
`FeatureLiftBench_draft.tex` / `fse26/sections/02_related_work.tex`.

### 2.2 Code Generation, Repository Understanding, and Localization

Function-level and repository-level code-generation benchmarks measure whether a model can synthesize code from natural-language or executable specifications. Repository-understanding and localization tasks measure whether a model can identify files, symbols, or regions relevant to a change. Feature lifting requires both inference and artifact construction, but success is not reducible to either. Locating the correct implementation is insufficient if transitive behavior or resources are omitted; generating a behaviorally similar implementation is insufficient if the public contract is not preserved.

**TODO(BIB):** optional extras only; HumanEval/MBPP/DS-1000/BigCodeBench/LiveCodeBench and RepoQA-style localization (RepoCoder, RepoBench) are cited in the LaTeX draft.

### 2.3 Program Slicing, Modularization, and Library Extraction

Feature extraction is related to program slicing, concern separation, refactoring, dependency analysis, and library migration. Classical techniques typically assume a program representation, slicing criterion, or human-specified boundary. FeatureLiftBench instead evaluates an autonomous agent from a natural-language public contract and a complete repository, and grades the final independent artifact by observable behavior. The benchmark does not claim to compute a minimal semantic slice; its frozen references are feasible comparison points, and RRES is a compactness proxy rather than a proof of optimality.

**TODO(BIB):** optional extras only; slicing, concern separation, and refactoring survey citations are in the LaTeX draft.

### 2.4 Agent Execution and Information Boundaries

Agent performance depends on the model, execution runtime, tools, context policy, and feedback interface. FeatureLiftBench fixes OpenHands as the Official Main runtime so that the main leaderboard varies the model backend under one execution protocol. Runtime comparisons, when available, are reported separately. Our information ablations instead change what task evidence is visible while preserving the model, runtime, evaluator, and budget. This separates model comparison from questions such as whether executable Public tests or source-location hints alter task performance.

## 3. The FeatureLiftBench Benchmark

### 3.1 Repository-Level Feature-Lifting Setting

A task consists of a pinned source repository \(R\), a public contract \(S\), an initial workspace \(W\), and a private evaluator \(J\). Given \((R,S,W)\), an agent produces a package \(P\) under a fixed execution protocol:

\[
P = \operatorname{Run}(M, H, R, S, W),
\]

where \(M\) is the model backend and \(H\) is the fixed Official Main agent runtime. The evaluator then observes the collected package and assigns gate-level outcomes:

\[
\operatorname{Functional}(P)
= B(P) \land P_{\mathrm{pub}}(P) \land H_{\mathrm{hid}}(P) \land I(P).
\]

Here, \(B\) checks installation and imports, \(P_{\mathrm{pub}}\) checks primary behavior from the public contract, \(H_{\mathrm{hid}}\) checks deeper combinations and boundary behavior from that same contract, and \(I\) checks independence from the source repository. Hidden tests must not introduce requirements absent from the public contract.

The agent receives the complete source tree and contract but no source-location hint. It does not see Public tests, Hidden tests, evaluator code, or the frozen reference solution. Extraction, adaptation, and behaviorally equivalent reimplementation are allowed. Runtime imports from the source project, forbidden paths, and undeclared dependency channels are disallowed.

### 3.2 Task Suite Design

The paper suite, Python-200′, contains 200 tasks from 176 repositories:

| Split | Tasks | Source repositories | Role |
| --- | ---: | ---: | --- |
| Frozen Python-150 | 150 | 127 | Baseline task set |
| Hard-50 | 50 | 50, disjoint from Python-150 repositories | Calibrated hard expansion |
| **Python-200′** | **200** | **176** | Main paper suite |

The suite emphasizes Python libraries, developer tools, and framework components. One source repository may support multiple distinct tasks in the baseline split. Every task pins its upstream revision and records source identity in a canonical registry.

Tasks are organized along three descriptive axes. **Feature family** records the requested behavior, such as parsing, serialization, configuration, validation, resource handling, registry behavior, caching, protocols, algorithms, or workflows. **Primary entanglement** records the dominant mechanism that makes independent extraction difficult: data-model, parser-state, framework, configuration/environment, resource, or third-party dependency entanglement. **Lift type** describes the relationship between the requested artifact and the source implementation: Direct, Adapted, or Composite. These labels support sampling and analysis; they are not shown to the agent and are not part of the functional score.

The combined suite contains 68 Direct, 100 Adapted, and 32 Composite tasks. The Hard-50 expansion increases coverage of registry/plugin dispatch, workflow and session orchestration, configuration discovery, validation boundaries, deep parsing, and direct tooling copy traps. It was calibrated using a strong model at 29/50 functional passes, within the predeclared 40–65% target band. This calibration is benchmark-design evidence, not a substitute for the final main-table evaluation.

### 3.3 Task Construction and Validation

Each candidate task is retained only when it satisfies four requirements:

1. **Realism:** the requested feature corresponds to a plausible reuse or modularization need in a real repository;
2. **Solvability:** a feasible independent implementation can be produced from the pinned repository and public contract;
3. **Oracle-checkability:** success can be verified with deterministic build, behavior, and isolation checks;
4. **Integrity:** the agent cannot obtain credit by reading protected tests, retaining a forbidden source dependency, or bypassing the intended artifact boundary.

Task construction records a source revision and digest, public contract, required API, locked dependencies, Public and Hidden contract mapping, deterministic evaluator, and a feasible reference solution. Reference solutions are removed from released Hard-50 task packages and are never exposed to agents. Automated and manual gates check source materialization, package imports, reference behavior, test isolation, forbidden dependencies, resource access, and freeze identity.

The benchmark intentionally separates the task package from mutable working-tree state. Paper results must be evaluated against the frozen materialization identified by the active suite manifest. Any source mismatch, unavailable locked dependency, evaluator defect, or context-policy violation is treated as an eligibility or infrastructure outcome rather than silently counted as model failure.

### 3.4 Run Protocol and Evidence Collection

Each run follows a setup–execution–evaluation pipeline. Setup materializes the pinned task workspace and records task, source, model, runtime, prompt, budget, and container identity. During execution, the agent may inspect the full repository, use shell and editing tools, run legal self-tests, and modify its submission workspace. The runner collects the final submission tree, model usage, actions, errors, and workspace snapshots. Evaluation installs the submission in a Dockerized offline environment and applies build, Public, Hidden, and isolation checks.

Each task attempt produces four evidence layers:

- the final `featurelifted` artifact;
- the agent trajectory and process status;
- token, step, time, context, and resource statistics;
- the task-level deterministic evaluator result.

The evaluator result is authoritative for Functional Pass. Agent completion or runner status is reported separately because an agent may hit a step limit after leaving a functionally passing package, or may report completion while its artifact fails evaluation.

### 3.5 Metrics

**Functional Pass@1.** A task receives one functional point only if all four gates pass. Functional failures are assigned an exclusive first-failure stage:

```text
missing submission → build → public → hidden → isolation
```

Infrastructure and evidence-availability flags are reported separately from semantic model outcomes.

**Compactness.** For a functionally passing submission \(P\) with frozen feasible reference \(P_{\mathrm{ref}}\), we report:

\[
\operatorname{RRES}(P)
= \frac{\operatorname{normalized\_size}(P)}
       {\operatorname{normalized\_size}(P_{\mathrm{ref}})}.
\]

RRES is accompanied by file, copied-code, and dependency-footprint diagnostics where evidence is available. It is reported only on functional passes. Cross-method compactness comparisons use the same-task subset on which both methods pass.

**Process and cost.** We report tokens, steps, latency, completion status, and resource failures as diagnostics. On passing trajectories with replayable package snapshots, \(T^*\) is the earliest cumulative token point at which a unique package tree passes the evaluator. \(T^*\) is undefined for failing trajectories and is not itself a deployable stopping rule.

## 4. Experiments

### 4.1 Setup

The Official Main experiment fixes the external task and execution conditions and varies only the model backend.

| Factor | Official Main treatment |
| --- | --- |
| Task contract and repository snapshot | Fixed per task |
| Initial workspace and source registry | Fixed per task |
| Agent runtime | Fixed to OpenHands Official Main |
| Prompt, action budget, and context envelope | Fixed |
| Evaluator and Docker images | Fixed and digest-attested |
| Model backend | Varied in the main matrix |
| Public-test visibility | Withheld in Main; varied only in RQ6 |
| Source-location hint | Withheld in Main |
| Reference solution and Hidden tests | Never exposed to the agent |

Each main-table cell uses one attempt per task. We report Wilson 95% confidence intervals for aggregate pass rates and exact task-level outcomes for paired comparisons. Because one attempt does not estimate repeated-run stochastic variance, seed sensitivity is evaluated separately on a stratified subset or stated as a limitation.

**Setup (freeze v2).** OpenHands Official Main, 120 steps, 128k envelope, images `python200-prime-212930ea`, freeze `6c20ff03…`, runs 2026-09-04/05. Pro on `python150-prime-v2-main-r1`; other backends sliced from `python200-prime-v2-main-r1`. GLM excluded.

### 4.2 Functional Capability

Headline: freeze v2 Python-150 Functional Pass@1. Core-100 / hard3 is the in-suite construction split, not official Hard-50.

| Model backend | Pass | Rate | Wilson 95% | Core-100 | hard3 | Empty |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| DeepSeek V4 Pro | 115/150 | 76.7% | 69.3–82.7 | 94/100 | 21/50 | 0 |
| DeepSeek V4 Flash | 108/150 | 72.0% | 64.3–78.6 | 90/100 | 18/50 | 0 |
| gpt-5.6-luna (OpenLux) | 102/150 | 68.0% | 60.2–74.9 | 82/100 | 20/50 | 6 |
| Qwen3.6-35B | 63/150 | 42.0% | 34.4–50.0 | 55/100 | 8/50 | 25 |
| GPT-OSS 120B | 36/150 | 24.0% | 17.9–31.4 | 25/100 | 11/50 | 2 |

The suite is not saturated (Pro fails 35; 28 tasks unsolved by all five). Pro vs Flash McNemar 10/3, p≈0.092 — do not claim Pro is significantly stronger than Flash. Do not rewrite Qwen as 63/125.

**Finding 1.** Current coding agents exhibit substantial but incomplete feature-lifting capability on frozen Python-150, with large performance differences across model backends.

### 4.3 Failure Stages

| Model | Pass | Missing | Build | Public | Hidden | Isolation |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| DeepSeek V4 Pro | 115 | 0 | 0 | 25 | 10 | 0 |
| DeepSeek V4 Flash | 108 | 0 | 0 | 26 | 15 | 1 |
| gpt-5.6-luna (OpenLux) | 102 | 6 | 3 | 27 | 12 | 0 |
| Qwen3.6-35B | 63 | 25 | 6 | 35 | 21 | 0 |
| GPT-OSS 120B | 36 | 2 | 18 | 70 | 23 | 1 |

**Finding 2.** Functional failures concentrate primarily at the behavioral gates.

Qwen's 25 empty rows are process non-delivery. Luna has 6 empty rows. Empty submissions are excluded from the mechanism census.

### 4.4 Compactness and Task Dependence

Pass-conditioned only. Pro/Flash median copy ≈0.96–0.97; Luna 0.16. On 97 paired Pro∩Luna passes, copy is 0.97 vs 0.19. Official Hard-50 has no `reference_solution/`, so no RRES there. Difficulty contrast is in-suite hard3 (Pro 94/100 vs 21/50).

**Finding 5.** Correctness and compactness are distinct.

## 5. Analysis

### 5.1 Observed Failure Symptoms

Mechanical evaluation stages explain where a package first fails, but not why. We therefore code semantic symptoms from the submitted artifact and, where available, the trajectory. The coding scheme separates localization failure, contract/API completion, dependency or resource closure, behavior drift, packaging/modularization, over-copy, and test gaming. Labels may remain unknown when evidence is insufficient. Hidden failure alone is not treated as proof of any semantic cause.

The central symptoms expected in the final analysis include:

| Symptom | Observable manifestation | Evidence required |
| --- | --- | --- |
| Missing API/export | Required symbol or member is absent | Public contract + submitted package |
| Exception or boundary drift | Return value, exception type, message, timing, or edge behavior differs | Contract mapping + evaluator case + artifact |
| State/resource closure | Registry, global state, templates, schemas, or data resources are omitted | Source evidence + package + failing contract case |
| Dependency closure | Required helper or legal third-party dependency is absent or misused | Build/import evidence + lockfile + artifact |
| Packaging/modularization | Correct logic exists but is not independently installable | Submission tree + evaluator evidence |
| Copy-heavy pass | Functional gates pass through broad vendoring | Passing result + RRES/copy diagnostics |

Semantic coding provenance and disagreement must be disclosed. Independent human review is preferred. AI-assisted coding is labeled as such and is not reported as human-gold inter-rater agreement.

### 5.2 Contract-Closure Failure

L1 close-read of Pro+Flash artifact failures ($n=63$; assistant first pass, not gold): behavior drift 54, contract/API completion 7, packaging 2, localization 0. Every remaining failure inspected `repo/`. Closure classes are 61/63. A stratified Luna/Qwen/OSS sample ($n=32$ coded) is not pooled; Luna is in the same direction, Qwen/OSS add packaging and missing helpers.

**Finding 3.** On the Pro+Flash artifact-fail slice, failures are dominated by incomplete recovery of the required behavioral contract rather than by missing packages or uninspected source trees.

Cases: Qwen `babel` empty package (process); Pro/Flash `alembic` `get_revision('base')` shadows a revision id (Public drift); `aiohttp` missing invalid-name raise (Hidden completion); Flash `typer` isolation; `blinker` copy-heavy pass (RRES 9.0 / 18.4 / 4.6).

### 5.3 Public Feedback Separates Two Information Layers

To test whether Main failures are caused simply by the absence of executable feedback, we ran a paired information ablation on 12 DeepSeek V4 Flash tasks. The task, repository, specification, model, runtime, evaluator, context envelope, and step budget are fixed. The only intervention mounts `public_tests/`; Hidden tests remain private.

| Condition | Functional Pass |
| --- | ---: |
| Full-Repository / No-Hint Main | 0/12 |
| Public-feedback | 4/12 |

All six selected Public-failure tasks flip the Public gate from 0 to 1. However, three of those tasks remain Hidden failures, and four of five paired tasks that already passed Public retain their Hidden failure. Only two tasks flip Hidden from 0 to 1. The result shows that withholding executable Public tests is a real bottleneck, but Public feedback is not a general Hidden oracle. We therefore treat Public and Hidden as two evaluation depths of the same published contract whose outcomes can move separately.

This ablation is not freeze v2 Main and does not enter the Python-150 leaderboard. It diagnoses the information boundary of Official Main.

### 5.4 Functional Sufficiency Often Precedes Agent Termination

On replayable trajectories that eventually pass, we evaluate every unique `featurelifted` package tree and identify the earliest passing tree \(T^*\). On the historical DeepSeek V4 Flash local Main run, 138 of 145 passing tasks have replayable gold. Median \(T^*/T_{\mathrm{total}}\) is 0.40, with a median 0.75M tokens spent after a sufficient package first exists. Direct tasks reach sufficiency at a median fraction of 0.36, while Composite tasks reach it at 0.51.

Post-sufficiency behavior is dominated by additional self-testing and repository inspection. This does not imply that a legal early-stopping rule is available. The agent cannot observe \(T^*\), self-test novelty is weakly related to Hidden success, and 46% of passing tasks still produce a new unique package after the earliest passing tree. Some later edits break and subsequently recover a passing package.

The cost result therefore supports a diagnostic claim: current agents often continue spending after functional sufficiency, largely because their legal tests do not reveal Hidden completeness. It does not show that failing tasks would pass with more tokens or that one stopping heuristic generalizes across models.

### 5.5 Process Scaffolds Do Not Produce a Stable Main Improvement

We evaluated several legal interventions during benchmark development. Rather than selecting only favorable pilots, we summarize them by the hypothesis they test:

| Hypothesis | Interventions | Observed outcome |
| --- | --- | --- |
| Agents need better self-verification | Self-generated probes, test-first extraction, verification ledger | No stable Functional improvement; some variants cost more or regress |
| Agents need an executable contract checklist | Self-Contract, Exec-Contract, spec-adversarial checks | Can reject empty packages or repair Public behavior; evaluated Hidden subsets do not improve reliably |
| Agents lose a previously correct intermediate package | Repair loops, Rescue+, best-so-far checkpoint replay | No stable gain; exhaustive replay of 51 failed DeepSeek trajectories finds no previously passing package |
| Agents need tighter budget or context control | 2M cap, adaptive stopping, compressed context, structural guidance | Token savings trade off against Functional Pass; no stable superiority over uncapped Main |

These results are heterogeneous in task subset and development date, so they are not pooled into a single effect size and do not enter the main leaderboard. Their common value is diagnostic: process scaffolding does not automatically close behavior that is unsupported by the agent's legal feedback.

## 6. Discussion

### 6.1 Feature Lifting Is a Distinct Agent Capability

Feature lifting asks a different question from issue repair. A repair agent succeeds inside the original repository and can rely on its package layout, resources, and test harness. A feature-lifting agent must infer which parts of that environment are semantically necessary and reconstruct them behind a new package boundary. It must satisfy an output contract after the original repository is removed. This combination makes dependency closure and modularization part of correctness rather than implementation style.

The task is also different from code localization. Finding a relevant symbol can be necessary, but the Alembic revision-map and aiohttp parameter cases show why it is insufficient. Conversely, a behaviorally equivalent rewrite can pass even if it copies little upstream code. FeatureLiftBench therefore evaluates the delivered behavior and independence of an artifact, not whether the agent followed one prescribed extraction strategy.

### 6.2 Correctness and Compactness Should Remain Separate

A broad vendoring solution may preserve behavior but offer little reusable modularization. A very small package may omit rare behavior. Combining these dimensions into one scalar would obscure both failure modes and make tradeoffs difficult to interpret. FeatureLiftBench instead treats Functional Pass as the eligibility gate for compactness analysis. RRES is then a descriptive reference-relative measure, not a proof of minimality or semantic authenticity.

The earlier External-50 expansion demonstrates the importance of this separation. High pass rates alone suggested that the task was nearly solved, while pass-conditioned footprints revealed that many solutions were close to whole-repository copying. On freeze v2 Python-150 the same split appears inside the passing set: Pro and Flash are copy-heavy, Luna is not. In-suite hard3, not official Hard-50, is the difficulty contrast.

### 6.3 Implications for Agent Design

The negative method results do not imply that agent workflows are irrelevant. They suggest that a useful workflow must improve the evidence available for contract closure rather than merely add more procedural steps. Promising directions include explicit obligation tracking tied to public requirements, generation of boundary cases from exception and state semantics, provenance-aware dependency closure, artifact-level completeness checks, and calibrated uncertainty when a requirement cannot be verified legally.

The Public-feedback ablation also suggests a layered view of feedback. Executable Public tests can expose basic mismatches efficiently. Deeper Hidden behavior remains a generalization problem under the Main information boundary. A robust agent must therefore use repository evidence and the public specification to anticipate unobserved but declared combinations, without hard-coding to benchmark examples.

### 6.4 Scope of the Claims

Our main scores characterize model backends embedded in a fixed OpenHands Official Main protocol. They are not measurements of base models independent of runtime, prompt, context policy, or provider behavior. If no second-runtime experiment is completed, all model and trajectory claims are explicitly scoped to this protocol. Likewise, task-factor and semantic-failure analyses are descriptive and do not establish causal effects of repository properties.

## 7. Limitations and Responsible Release

**Dataset scope.** Python-200′ is a maintainer- and AI-assisted selection of Python libraries, tooling, and framework components. It is not a random sample of software repositories and does not establish performance on large product applications, GUI software, GPU systems, or distributed services.

**Contract and evaluator completeness.** Public and Hidden tests are mapped to one published contract, but finite tests cannot prove complete semantic equivalence. Hidden fairness requires independent audit and sensitivity reporting. Any requirement not observable from the public contract is a task defect, not an agent failure.

**Reference and compactness.** Frozen references are feasible solutions, not unique optima. RRES, copy fraction, files, and dependency footprint are proxies that can miss semantic copying or penalize legitimate alternative implementations.

**Annotation provenance.** Task taxonomy, closure records, and semantic failure labels include AI-assisted curation. We do not report these as independent human gold. Inter-rater agreement is reported only when raters are genuinely independent humans.

**Experimental stability.** The main table initially uses one attempt per task. Without repeated trials, it does not quantify stochastic run-to-run variance. Model APIs and serving stacks may also change despite stable model names. We therefore record exact run dates, profiles, source freezes, and image identities, and plan a stratified repeated-run sensitivity study.

**Runtime dependence.** Official Main fixes OpenHands. Scores may change with another runtime, tool interface, context policy, or recovery strategy. Runtime comparisons are kept separate from the model leaderboard unless evaluated under a controlled paired protocol.

**Licensing and redistribution.** Upstream repositories retain heterogeneous licenses. Release packaging, source acquisition, reference handling, and generated submissions must preserve license obligations. Large result archives may be distributed by checksummed acquisition instructions rather than committed directly to the repository.

## 8. Conclusion

We presented FeatureLiftBench, a benchmark for repository-level, behavior-preserving feature extraction by code agents. The benchmark asks agents to turn a complete but entangled repository into an independent package under a public behavioral contract, without source-location hints or access to benchmark tests. Its deterministic evaluator separates functional correctness from the compactness of passing solutions.

The emerging evidence suggests that current agents can often navigate repositories and construct plausible packages while still failing to close required APIs, boundary semantics, state, resources, and preservation behavior. Controlled feedback and trajectory analyses further indicate that Public repair, Hidden generalization, and post-sufficiency self-testing are distinct phenomena. The final paper will quantify these observations on a fully attested Python-200′ cross-model evaluation. By releasing tasks, source provenance, evaluators, traces, and reproducibility metadata, FeatureLiftBench aims to support more reliable research on agents that extract reusable software rather than only modify it in place.

## Appendix Plan

### A. Declaration of LLM Usage

Disclose LLM assistance in task curation, annotation, analysis, and manuscript editing. State which scientific claims and quantitative summaries received human verification.

### B. Models, Runtime, and Reproducibility Configuration

List exact model endpoints, OpenHands revision, profiles, prompt hash, budgets, context policy, provider dates, hardware where applicable, and agent/evaluator image digests.

### C. Full Results and Sensitivity Tables

Provide task-level outcomes, confidence intervals, split and taxonomy cuts, observable-only Hidden analysis, context-policy sensitivity, repeated-run subset, and any runtime appendix.

### D. Representative FeatureLift Task Cards

For each representative task, report source repository/revision, public objective, expected package, primary entanglement, allowed dependencies, evaluator gates, reference footprint, and one audited failure example.

### E. Negative Intervention Registry

Report task subsets, dates, exact protocol differences, paired outcomes, cost, stopping decisions, and evidence limitations for each development intervention.

### F. Reproduction and Artifact Manifest

Provide suite SHA, freeze ID, source registry, wheel closure, image identities, task-level checksums, analysis commands, and verified result-bundle acquisition instructions.
