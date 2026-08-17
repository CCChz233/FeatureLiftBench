# Failure Taxonomy

> **Documentation status: current · Last verified: 2026-08-17**

## Labeling policy

Separate three layers:

1. **Evaluator outcome**：build/public/hidden/isolation/functional pass；
2. **Agent process**：completion、step/context/rate limit、missing submission；
3. **Semantic cause**：localization、closure、behavior、packaging、copy-heavy。

Mechanical fields are generated automatically. Semantic causes require
trajectory/code evidence and may remain `unknown`; do not force a narrative from
the last error line.

## Functional stages

对每道 assigned task 使用下列固定优先级产生一个互斥 primary outcome：

```text
missing_submission
  > build_failure
  > public_failure
  > hidden_failure
  > isolation_failure
  > functional_pass
```

各 gate 的原始状态可为 `pass / fail / not_evaluated / infra_unknown`。缺少逐题
evaluator 证据时使用 `stage_evidence_unavailable`；它是证据完整性标记，不是
第六种 agent 失败原因。

### 1. Missing or unusable submission

No deliverable was collected, or it cannot be parsed as a submission tree.
Distinguish model non-delivery from runner/transport loss.

### 2. Build/import failure

The package cannot install/import or the required API cannot be loaded.
Common causes:

- wrong package layout；
- missing export；
- dependency install failure；
- import-time side effects；
- invalid build metadata。

### 3. Public regression failure

Basic observable contract behavior fails. This can indicate an early semantic
miss, packaging defect or a narrow stub.

### 4. Hidden behavior failure

Public passes but hidden fails on deeper combinations、state sequences、edge
inputs、exception semantics or resource behavior. Hidden must still map to the
published contract；otherwise the task is defective.

### 5. Isolation failure

Behavior may pass, but submission imports the original project、uses forbidden
dependencies、reads the source workspace or depends on forbidden paths/resources.

## Semantic causes

### Localization failure

The Agent does not identify the relevant implementation region or misidentifies
another feature. Evidence should come from searches/reads and the submitted code,
not from a private entrypoint checklist alone.

### Contract/API completion failure

The Agent finds the general implementation but omits required exports、members、
defaults、exceptions or state behavior.

### Dependency closure failure

Necessary helpers、types、constants、resources、configuration、registries or
transitive dependencies are missing.

### Behavior drift

The submission implements a similar but observably different feature. Typical
differences include ordering、normalization、error type/message、parser state、
global state and compatibility behavior.

### Packaging/modularization failure

Correct logic is present but cannot be exposed as the required independent
`featurelifted` package.

### Over-copy

Functional gates pass, but reference-relative LOC/file/copy/dependency metrics
show a broad vendoring solution. Over-copy is a quality label, not a functional
failure.

### Test gaming or narrow reimplementation

Code hard-codes known samples、branches on fixtures or implements only a prompt-
level toy behavior. Requires code/trajectory evidence; hidden failure alone is
not sufficient proof.

## Process and infrastructure

Report separately:

- agent step limit；
- context limit；
- rate limit/API error；
- timeout；
- OOM/resource limit；
- Docker/build infrastructure；
- corrupted/missing logs；
- manual rerun or intervention。

If an Agent hits step-limit but leaves an evaluator-passing submission, label:

```text
functional_pass = true
agent_completion = false
process_failure = step_limit
```

Do not turn this into a functional failure or hide the process failure.

## Compactness classes

For functionally passing submissions:

- compact pass；
- functional mixed footprint；
- copy-heavy pass；
- unapproved dependency；
- path/source leakage。

Thresholds must be declared and sensitivity-tested. The frozen reference is a
comparison point, not a unique optimum.

## Task-defect labels

Some failures belong to the benchmark:

- hidden-only requirement；
- incomplete `required_api`；
- incorrect reference；
- non-deterministic test；
- missing dependency/resource in locked environment；
- source digest/materialization mismatch；
- evaluator infrastructure defect。

These must be quarantined or fixed and re-frozen, not counted as model failures.

## Reporting

At minimum publish:

- 互斥首败阶段及 evidence-unavailable 计数；
- mechanical funnel；
- process/infra counts；
- primary semantic cause + unknown rate；
- annotation provenance；
- representative evidence；
- task-defect exclusions；
- inter-rater agreement only if independent human raters were actually used。

Historical labeled evidence is in
[`reports/failure_attribution_20260720/`](../../reports/failure_attribution_20260720)
and [TRAJECTORY_FINDINGS.md](../reference/research_analysis/TRAJECTORY_FINDINGS.md), both under
`mixed_snapshot_v1` conditions.
