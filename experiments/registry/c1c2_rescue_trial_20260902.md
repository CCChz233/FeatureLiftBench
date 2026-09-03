# C1/C2 rescue trial — 2026-09-02

> **Status: complete · Scope: two trial copies only. Frozen Python-200′
> packages, freeze IDs, and the 168/32 labels were not changed.**

Two blocking violators, one per class, copied to
`experiments/validation/c1c2_rescue_trial_20260902/tasks/` and repaired by
**declaration only** (no Hidden rewrite, no public rewrite).

| Task | Defect | Repair | C1/C2 | constitution | oracle |
| --- | --- | --- | --- | --- | ---: |
| `jsonpointer__resolve_core__001` | C1: Hidden uses `ptr in JsonPointer` (`__contains__`) | Add `JsonPointer.__contains__` to `required_api.members`; refresh B005 / coverage / `TASK.md` / surface test | pass | pass | 1.0 |
| `installer__wheel_record_core__hard3_001` | C2: `installer.records.parse_wheel_record` is a `featurelifted` name | Point `source_entrypoints` at real `installer.records.parse_record_file` | `resolved` | pass | 1.0 |

Oracle image: `featureliftbench-eval:python200-prime-769f2486`.

## Is the rest of the 32 worth saving?

Yes, for almost all of them. They are already in the freeze, already have
passing oracles, and fail only because the **contract text does not match what
Hidden / provenance already do**. Exclusion to 168 is a paper-hygiene move, not
a sign the tasks are unusable.

Rough split from [PLAN_FREEZE_V2.md](../../docs/PLAN_FREEZE_V2.md):

| Bucket | n | Looks like this trial? |
| --- | ---: | --- |
| C1 protocol dunders | 13 | Yes — same patch as jsonpointer |
| C1 named members | 6 | Same mechanical patch (`APISpec.components`, `Response.body`, …) |
| C1 dynamic `__getattr__` keys | 2 | Harder — `oslo_config`, `python_configuration`; must enumerate spec-fixed names or revise the standard |
| C2 invented `featurelifted` names stored as upstream | 7 | Yes — same as installer: find the real snapshot symbol |
| C2 wrong module/leaf | 5 | Medium — search the snapshot; delete the pointer only if there is no upstream anchor |

Saving them requires a new freeze (spec_hash changes). It does **not** require
rewriting Hidden tests or re-calibrating difficulty.
