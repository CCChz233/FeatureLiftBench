# hard50_pilot

Materialize **only** after a card has a pinned commit.

Pilot 10 (ledger `pilot_candidates`, after 2026-08-27 swaps):

1. `zope_interface__adapter_registry_core__001`
2. `cliff__command_dispatch_core__001`
3. `hydra_core__compose_initialize_core__001`
4. `dogpile_cache__region_backend_core__001`
5. `paste__dispatch_map_core__001` (replaced confuse; waitress failed isolation)
6. `oslo_config__opt_group_core__001`
7. `polyfactory__model_factory_core__001` (replaced injector)
8. `luigi__task_requires_core__001`
9. `taskiq__broker_task_core__001`
10. `graphene__schema_execute_core__001` (replaced openapi_core)

Swapped-out packages: `_swapped_out/`. Do not discover them as Pilot tasks.

Protocol: [docs/PLAN_HARD50_EXPANSION.md](../../docs/PLAN_HARD50_EXPANSION.md) Phase 1.  
Do not write packages into `benchmark/tasks/` or `benchmark/external50/`.

Calibration (required before opening the remaining 40):

| Baseline | Expectation |
| --- | --- |
| validate-task / oracle / isolation | pass |
| naive/shallow | hidden fail |
| copy-all | functional may pass; RRES worse than reference |
| Flash | replace if >85% or RRES≈1.0; keep 40–65%; keep 20–40% if paper_fit is strong |
