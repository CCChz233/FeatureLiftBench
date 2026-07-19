# Research analysis docs

v1.1 硬化、Pilot、taxonomy 与论文门禁相关文档。生成型 JSON/CSV 在 `artifacts/research_analysis/`；本目录是人类可读规范与状态摘要。

**Living status：** [../STATUS.md](../STATUS.md) · 生成表格 [V11_IMPLEMENTATION_STATUS.md](V11_IMPLEMENTATION_STATUS.md)（`python tools/research_analysis/build_v11_audit_status.py`）

## Protocol & gates

| Doc | Role |
| --- | --- |
| [V11_HARDENING_PROTOCOL.md](V11_HARDENING_PROTOCOL.md) | Normative v1.1 gate definitions |
| [PILOT_DECISION_RULES.md](PILOT_DECISION_RULES.md) | ECSM Pilot 决策与 stage 规则 |
| [EXPERIMENT_SCOPE_AND_ARM_RATIONALE.md](EXPERIMENT_SCOPE_AND_ARM_RATIONALE.md) | 实验 arm 与 scope 理由 |

## Status & execution

| Doc | Role |
| --- | --- |
| [V11_IMPLEMENTATION_STATUS.md](V11_IMPLEMENTATION_STATUS.md) | **Generated** gate table |
| [ORACLE_REVALIDATION_REPORT.md](ORACLE_REVALIDATION_REPORT.md) | **Generated** Oracle freeze summary |
| [NEXT_WEEK_ACTIONS.md](NEXT_WEEK_ACTIONS.md) | Current action checklist |
| [expert_review/](expert_review/) | **Expert AI adjudication docs**（工程质检；非独立人工 gold） |

## Taxonomy & benchmark structure

| Doc | Role |
| --- | --- |
| [BENCHMARK_TAXONOMY_SPEC.md](BENCHMARK_TAXONOMY_SPEC.md) | Taxonomy schema |
| [BENCHMARK_TAXONOMY_REPORT.md](BENCHMARK_TAXONOMY_REPORT.md) | Taxonomy findings on Python150 |

## Mechanism & findings

| Doc | Role |
| --- | --- |
| [ECSM_METHOD_SPEC.md](ECSM_METHOD_SPEC.md) | ECSM prompting protocol |
| [MECHANISM_HYPOTHESES.md](MECHANISM_HYPOTHESES.md) | Mechanism hypotheses |
| [TRAJECTORY_FINDINGS.md](TRAJECTORY_FINDINGS.md) | Trajectory analysis findings |
| [CAUSAL_EXPERIMENT_PLAN.md](CAUSAL_EXPERIMENT_PLAN.md) | Causal experiment plan |

## Paper planning

| Doc | Role |
| --- | --- |
| [ICLR_INNOVATION_ROADMAP.md](ICLR_INNOVATION_ROADMAP.md) | Innovation roadmap |
| [../06_paper_outline.md](../06_paper_outline.md) | Paper outline |
| [../paper_runs_frozen.md](../paper_runs_frozen.md) | Frozen run IDs |
| [../paper_tables.md](../paper_tables.md) | Table drafts |

## Regenerate key artifacts

```bash
python tools/research_analysis/build_v11_audit_status.py
python tools/research_analysis/build_v11_repair_ledger.py
```

Oracle freeze pointer: `artifacts/research_analysis/v1_1/current_oracle_freeze.json`
