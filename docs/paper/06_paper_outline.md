# Paper Outline

> **Documentation status: current · Last verified: 2026-08-28**

## Working title

**FeatureLiftBench: Evaluating Repository-Level Feature Extraction by Code
Agents**

## Core claim

FeatureLiftBench isolates a software-engineering capability not captured by
bug-fixing or greenfield generation benchmarks: extracting an existing feature
from an entangled repository into an independent, behavior-complete and compact
module.

The evaluation gives agents a complete public contract and a complete pinned
repository, but no source-location hints or benchmark tests before submission.

## Contributions

1. **Task formulation**：repository-level behavior-preserving feature
   extraction。
2. **Benchmark**：200 Python OSS tasks（frozen 150 + Hard-50）、176
   repositories，Full-Repository / No-Hint。旧 150 + External-50 为 superseded
   对照，不进新主表。
3. **Specification discipline**：generated public contract、private
   public/hidden mapping、No-Hint leak gates。
4. **Evaluation**：Functional Pass@1 separated from reference-relative
   compactness and process cost。
5. **Empirical study**：论文主表是 Python-200'（150+Hard-50）的跨模型 Main，
   **尚未跑**。已有的 21.5%–72.5% 是旧 150+E50。DeepSeek 旧 200 上的 Main vs
   已退役 Lite V1、Qwen3.6-35B V1=Main+2M、以及 \(T^\*\) 成本切片
   （[03_results_token_utility.md](03_results_token_utility.md)）仍是机制证据，
   换套件后数字要重标。脚手架方法已停，负结果作 RQ4，**不要**单列 Active
   Dynamic Exploration 为核心贡献。RQ6 Public-feedback 是 Main 的信息消融，
   Flash-12 同日成对已齐（Main 0/12 → 4/12）；数字不进主表。DeepSeek Harness /
   Codex 是可选 runtime 附录，见
   [METHOD_AGENT_RUNTIME.md](../METHOD_AGENT_RUNTIME.md)。

## Research questions

- **RQ1 — Capability:** How often do code agents produce functionally correct,
  isolated feature packages?
- **RQ2 — Compactness:** When they pass, how compact are solutions relative to
  frozen references?
- **RQ3 — Cost:** How many tokens、steps and seconds are required, and where
  on a passing trajectory does functional sufficiency first occur?
- **RQ4 — Failure mechanisms:** Where do localization、closure recovery、
  behavior preservation、packaging and isolation fail?
- **RQ5 — Task factors:** How do lift type、repository size、domain、
  entanglement and task footprint relate to outcomes?
- **RQ6 — Information ablations:** What changes under Entrypoint-Hint、
  Public-feedback and Pruned-Context?

## Recommended structure

### 1. Introduction

- motivate code reuse、legacy/vibe-code cleanup and modularization；
- distinguish extraction from issue repair and greenfield implementation；
- state the information boundary and contributions。

### 2. Task definition

- full repository + complete public contract；
- No-Hint and evaluator-test-blind Main；
- `featurelifted` submission；
- independence and allowed extraction/adaptation；
- public/hidden as two private depths of the same contract。

### 3. Benchmark construction

- repository selection protocol and attrition；
- canonical source registry and immutable snapshots；
- task/spec/evaluator construction；
- source、contract、reference、isolation and freeze gates；
- 200-task distribution（150 baseline + Hard-50）and task footprint；
  External-50 only as an easy / copy-heavy side split。

The replacement selection ledger and complete reference file/LOC footprint are
frozen; the original 143-task historical selection protocol must still be
described candidly before paper submission.

### 4. Evaluation

- Functional Pass@1；
- reference-relative LOC/file/copy/dependency vector；
- agent completion、step/context/infra failures；
- token、step and latency；
- earliest-sufficient \(T^\*\) on passing trajectories（offline replay of
  unique `featurelifted` trees；not last write；not a stopping rule）；
- statistical comparison and paired ablations。

### 5. Experimental setup

- Official Main：exact OpenHands/model profiles and agent/eval Docker；
- optional runtime ablation：pinned DeepSeek Harness / Codex after `./setup.sh`
  ([METHOD_AGENT_RUNTIME.md](../METHOD_AGENT_RUNTIME.md)；not the main table)；
- active benchmark freeze and image digests；
- one attempt per task；
- baselines and ablation definitions。

### 6. Results

Do not populate with historical mixed-snapshot numbers as the main table.
Required v3 tables:

1. cross-model Python-200' Functional Pass@1（含 150 / Hard-50 分解；**未出**）；
   旧 150+E50 表只作 superseded 对照；
2. correctness funnel（互斥首败）；
3. compactness among functional passes（拆 150 / Hard-50；报 copy 比例；E50 旁路）；
4. tokens/steps/latency（只做同模型方法对比）；
5. \(T^\*/T_{\mathrm{total}}\) on gold passing trajectories, by model and
   lift type（[03_results_token_utility.md](03_results_token_utility.md)；
   不是 last-write fraction，不是停机规则）；
6. repository/domain/entanglement/task-footprint slices；
7. paired information ablations（RQ6 Public-feedback Flash-12 已齐。稿
   [04_results_rq6.md](04_results_rq6.md)；不进主表）。

Do not put Core-12 / Rescue+ / V2 / TFL / DeepSeek Harness / Codex runtime
rates in the main tables. Historical scaffolding negative results belong in
failure analysis / discussion.

Historical v1 results may appear only in a clearly labeled development-history
or source-context comparison.

### 7. Failure analysis

- missing API/export；
- hidden behavior mismatch；
- dependency/resource/registry omissions；
- packaging/isolation；
- copy-heavy；
- step/context/infra failures；
- representative task dossiers。

### 8. Discussion

- why localization alone is insufficient；
- why legal self-tests、upstream dual-run and structure gates do not close hidden
  behavior；
- Public-feedback recovers the public gate without automatically recovering
  Hidden（[04_results_rq6.md](04_results_rq6.md)）；
- tension between behavior completeness and compactness；
- cost of a 2M token cap on conversion tails（true tax is earliest-sufficient
  \(\ge 2\mathrm{M}\), not last write after 2M）；
- post-sufficiency self-testing cannot see Hidden, so legal novelty signals
  do not yield a stopping rule
  ([03_results_token_utility.md](03_results_token_utility.md))；
- implications for repository-aware agent design；
- 不把脚手架或 ADE 写成稳定提升 Functional 的方法贡献。

### 9. Limitations and ethics

Use [limitations.md](limitations.md): selection bias、library/tool skew、
training contamination、AI-assisted annotation、licensing、test completeness、
proxy compactness and missing non-Python coverage。

### 10. Reproducibility

- source URL/revision/digest；
- benchmark freeze；
- image/model/profile/arm；
- task-level results and checksums；
- archive acquisition instructions。

## Current Evidence Boundary

Do not copy release counts or run completion into this outline. Engineering readiness and
empirical completeness are maintained in [STATUS.md](../STATUS.md); result eligibility is defined
in [STATUS.md](../STATUS.md), and evidence locations in
[reports/README.md](../../reports/README.md).
