# C4 overlap trial — 2026-09-02

> **Status: complete · Scope: six Hard-50 hidden tests plus this note. Public
> tests, `public_spec`, C1/C2 packages, and freeze IDs were not updated.**

Six Python-200′ tasks had one public/hidden test body that was byte-for-byte
the same after C4 normalization. Trial: rewrite only the hidden test, keep
function names so `evaluation_spec` mappings stay valid, do not touch public
tests or `public_spec`.

Oracle eval image: `featureliftbench-eval:python200-prime-769f2486`.
Reference: `benchmark/hard50_pilot/<id>/reference_solution`.
Raw eval: `experiments/validation/c4_overlap_trial_20260902/`.

| Task | Hidden change (still inside the mapped clause) | C4 | constitution | oracle `functional_gate` |
| --- | --- | --- | --- | ---: |
| `anyio__task_group_core__001` | B003 with a different deadline pair (`0.01` / `0.2`) | clear | pass | 1.0 |
| `copier__template_answers_core__001` | B003 on a different question, two invalid answers | clear | pass | 1.0 |
| `mitmproxy__url_parse_core__001` | B003 via `bytes` URL (`parse` is `str \| bytes`) | clear | pass | 1.0 |
| `pika__channel_spec_core__001` | B001 plus remmarshal equality | clear | pass | 1.0 |
| `pre_commit__config_load_core__001` | B002 from a differently named file, also assert `repos == []` | clear | pass | 1.0 |
| `pylint__config_find_core__001` | B003 with a before/after enablement check | clear | pass | 1.0 |

All six are Hard-50 packages. Static C4 over the whole 200 is now **0 hits**.
The published gate ledger `python200_hard_20260902_p1_l4l5` still records the
pre-fix 6 advisory hits until the gate is rerun.

Landing these hidden files changes the on-disk task tree; it is **not** a new
freeze. `task_set_sha256` / freeze IDs are not updated here. C1/C2 (32 tasks)
are untouched.
