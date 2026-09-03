# Archived harness scripts

> **Status: archived · Last verified: 2026-09-02**
> Historical task scaffolding, killed-method comparators, and superseded suite
> runners. Not the Python-200′ Main entry. Live inventory:
> [../README.md](../README.md).

## Superseded suite runners

These still work if you need to replay an old suite. They are **not** the
paper Main command. Use `./scripts/run_benchmark.sh --benchmark python200_hard`.

| Script | Suite |
| --- | --- |
| `run_python150_paper.sh` | Frozen Python-150 |
| `run_python200_paper.sh` | Superseded 150 + External-50 |
| `run_python200_prime_paper.sh` | Earlier 200′ wrapper |
| `run_python_hard50_paper.sh` | Hard-50-only |
| `run_python_hard50_compliant_ablation.sh` | Hard-50 ablation |
| `run_benchmark.sh` | mini-swe-agent; collides with `scripts/run_benchmark.sh` |

## Task scaffolding

| Script | Use case |
| --- | --- |
| `setup_vibe_app_tasks.py` | Copy `benchmark/sources/vibe_app/` into vibe_app tasks |
| `generate_vibe_app_source.py` | Regenerate vibe_app source |
| `setup_m3_tasks.py` | One-time jinja2×4 / pytest×3 scaffold |
| `setup_batch*.py` / `scaffold_batch*.py` / `bootstrap_batch2_tasks.py` | Batch 1–6 construction |
| `materialize_external50_w*.py` / `materialize_external50_pilot.py` | External-50 waves |

## Killed-method / one-shot comparators

`flb_test_first.py`, `run_cgcc_warm_repair.py`, `compare_core12_*.py`,
`compare_spec_adversarial_hidden4.py`, `compare_distill24_main_2m_cap.py`,
`replay_contract_closure_gate.py`, `calibrate_vct_stall.py`,
`probe_upstream_differential.py`.

## Still live despite living here

`run_agentic_evidence_canaries.py` is **not** a killed one-shot. It is the
runner for Hidden-provenance **Gate 0 and Gate 1**, both still open paper DoD
items ([07_top_conference_readiness_plan.md](../../../docs/paper/07_top_conference_readiness_plan.md)).
It stays in this directory only because
`retry_invalid_agentic_evidence_cases.py` resolves it as a same-directory
sibling. Current status:
[GATE_CHECK_20260902.md](../../../reports/agentic_evidence/GATE_CHECK_20260902.md).

## Deprecated wrappers (use live scripts instead)

| Script | Replacement |
| --- | --- |
| `list_extreme_tasks.py` | `python3 harness/scripts/list_tasks.py --tag extreme` |
| `analyze_extreme_suite.py` | `python3 harness/scripts/analyze_benchmark_suite.py <suite_dir>` |
