# Functional non-pass attribution

> **Status: complete evidence-level audit · No new experiment executed**

The received suite has **68 nominal non-passes**, but **33 (48.5%) are infrastructure outcomes** rather than model-behavior evidence. The remaining 35 consist of two no-submission outcomes, 25 public-behavior failures, and eight hidden-only failures.

## Audited attribution

| Audit class | Tasks | Paper treatment |
| --- | --- | --- |
| Freeze preflight blocked | 17 | rerun after infrastructure repair |
| Offline dependency unavailable | 16 | rerun after infrastructure repair |
| Agent produced no submission | 2 | retain as observed model/output evidence |
| Public behavior | 25 | retain as observed model/output evidence |
| Hidden-only behavior | 8 | retain as observed model/output evidence |

## Key corrections

- The 17 freeze-preflight blocks all occur in Python-150 and never launched an agent.
- The 16 nominal build failures all occur in Hard-50 and are dependency-install failures, not invalid generated Python packages.
- All dependency failures report an unavailable locked requirement in the offline wheel set.
- No task first fails isolation.
- Public and hidden failures remain valid behavioral evidence, subject to the separate context-window eligibility flag on affected runs.

The task-level audit is in `failure_audit.csv`. Test names are intentionally omitted; the file retains counts and exception types without exposing hidden-test content.
