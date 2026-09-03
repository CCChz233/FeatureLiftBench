# Freeze v2 wave 4 — C2 entrypoints — 2026-09-03

> Declaration-only. Hidden / public tests untouched. Freeze IDs not recut.

Twelve C2 violators had `source_entrypoints` pointing at invented `featurelifted`
names or wrong paths. Snapshot `leaf_elsewhere` was empty for every dangling
leaf, so the repair is: real `def`/`class` in `oracle_manifest.required_source_files`
(or a sibling module in the same snapshot when the listed file is a re-export stub).

Mapping: `experiments/validation/c1c2_repair_v2/c2_mapping.md`.
Apply: `scripts/repair_c2_entrypoints.py`.
Oracle image: `featureliftbench-eval:python200-prime-769f2486`.

| Check | Result |
| --- | --- |
| `Snapshot.resolve` of every proposed symbol | `resolved` |
| constitution | empty |
| mechanical C2 on `task/repo` | 12/12 pass |
| Docker oracle 1-rep | 12/12 `functional_gate == 1.0` |

`fs` keeps already-resolved `parse_fs_url` and replaces `FSOpenerRegistry` with
`Registry`. No task was left with an empty entrypoint list.

Local `task/repo` is empty for several C1-only tasks (apispec, beaker, …). Official
C2 uses materialized canonical source, so those empty trees are not new C2 defects.
