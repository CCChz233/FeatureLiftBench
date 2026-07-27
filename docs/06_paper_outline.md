# Paper Outline

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
2. **Benchmark**：150 external Python OSS tasks、126 repositories、132
   immutable snapshots，Full-Repository / No-Hint。
3. **Specification discipline**：generated public contract、private
   public/hidden mapping、No-Hint leak gates。
4. **Evaluation**：Functional Pass@1 separated from reference-relative
   compactness and process cost。
5. **Empirical study**：cross-model correctness、compactness、cost and failure
   mechanisms（v3 baseline 待跑）。

## Research questions

- **RQ1 — Capability:** How often do code agents produce functionally correct,
  isolated feature packages?
- **RQ2 — Compactness:** When they pass, how compact are solutions relative to
  frozen references?
- **RQ3 — Cost:** How many tokens、steps and seconds are required?
- **RQ4 — Failure mechanisms:** Where do localization、closure recovery、
  behavior preservation、packaging and isolation fail?
- **RQ5 — Task factors:** How do repository size、domain、entanglement and task
  footprint relate to outcomes?
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
- 150-task distribution and task footprint。

The replacement selection ledger and complete reference file/LOC footprint are
frozen; the original 143-task historical selection protocol must still be
described candidly before paper submission.

### 4. Evaluation

- Functional Pass@1；
- reference-relative LOC/file/copy/dependency vector；
- agent completion、step/context/infra failures；
- token、step and latency；
- statistical comparison and paired ablations。

### 5. Experimental setup

- exact OpenHands/model profiles；
- agent/eval Docker；
- active benchmark freeze and image digests；
- one attempt per task；
- baselines and ablation definitions。

### 6. Results

Do not populate with historical mixed-snapshot numbers as the main table.
Required v3 tables:

1. cross-model Python-150 Functional Pass@1；
2. correctness funnel；
3. compactness among functional passes；
4. tokens/steps/latency；
5. repository/domain/entanglement/task-footprint slices；
6. paired information ablations。

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
- tension between behavior completeness and compactness；
- how upstream evidence quality affects agents；
- implications for repository-aware agent design。

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

## Current evidence boundary

Engineering:

- v3 readiness 150/150；
- source snapshots 132/132；
- Docker Oracle 450/450；
- active freeze recorded。

Empirical:

- v3 model baseline absent；
- historical mixed-snapshot runs available only as development evidence。

See [STATUS.md](STATUS.md)、[EXPERIMENTS.md](EXPERIMENTS.md) and
[REPORTS_INDEX.md](REPORTS_INDEX.md)。
