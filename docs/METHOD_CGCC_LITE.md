# Counterexample-Guided Closure Contracts (CGCC-lite)

**Status:** method-development pilot  
**Baseline:** Exec-Contract clean3  
**Visibility:** Full-Repository / No-Hint / test-blind

## Hypothesis

Executable contracts help only when they distinguish the intended behavior from
plausible omissions and over-generalizations. CGCC-lite keeps the clean3
execution-guided workflow, then adds evidence-grounded contrastive closure
obligations before contracts are frozen.

## Allowed evidence

- Tier A: `TASK.md` / `public_spec`
- Tier B: upstream source, AST, tests, and runtime observations
- Tier C: pre-registered consistency operators
- Forbidden: benchmark public/hidden test content or formal-evaluation feedback

## Pre-registered operator families

- API/member deletion
- symbolic-token over-generalization and concrete-id collision
- eager loading and cache omission
- context/default propagation omission
- dependency/down-revision edge-role collapse
- branch-label propagation omission
- ordered-output collapse, only with upstream ordering evidence
- declared error-path omission

Each run writes:

- `OBLIGATIONS.json`
- `MUTATION_AUDIT.json`
- `exec_contract_phase.json`

The CGCC contract gate is green only when all applicable registered mutation
families have a distinguishing frozen contract.

## Focus protocol

```bash
./run_experiment.sh --arm cgcc_lite \
  --task-file experiments/cgcc_lite_pilot/task_ids_focus.txt \
  --run-id cgcc-lite-focus-<seed> \
  --workers 1 --timeout 3600 --docker
```

Run one diagnostic seed first. Continue to three seeds only if the contract
gate is substantive and public behavior does not regress. The focus go gate is:

- public pass on both tasks in at least two of three seeds;
- at least one Functional pass;
- the flip is attributable to a pre-registered
  `mutation family -> contract -> implementation` chain.

Exact hidden error wording or casing is not an admissible optimization target.

## CGCC-ROC development extension

`cgcc_roc` adds one general operator to CGCC-lite:
**representation/observation closure**. When an upstream implementation keeps
an alias binding separate from later state propagation, frozen contracts must
distinguish:

- the entity originally bound by the alias;
- the descendant where propagated state is observable;
- the compact public projection (for example, revision ids rather than
  internal graph objects).

This extension remains eval-blind: applicability requires TASK plus upstream
source/AST evidence. It does not add exact exception wording or casing.

```bash
./run_experiment.sh --arm cgcc_roc \
  --task-file experiments/cgcc_lite_pilot/task_ids_focus.txt \
  --run-id cgcc-roc-focus-<seed> \
  --workers 1 --timeout 3600 --docker
```

The focus tasks are a method-development set after the first formal inspection;
subsequent ROC runs must be labeled post-hoc/development evidence, not clean
held-out evidence.

## CGCC-RMC development extension

`cgcc_rmc` composes ROC with **required-method closure**. A TASK-required method
cannot be considered covered by `hasattr` or `callable` alone: when TASK and
upstream source provide a sound behavioral witness, the frozen suite must
exercise its return shape and at least one boundary contrast. For the RevisionMap
focus task this adds vector lookup and the upstream default lower-exclusive
traversal boundary.

```bash
./run_experiment.sh --arm cgcc_rmc \
  --tasks alembic__revision_map_core__hard3_001 \
  --run-id cgcc-rmc-alembic-<seed> \
  --workers 1 --timeout 3600 --docker
```

No diagnostic wording/casing contract is added for the Click task.

## Monotone delta repair

The one-shot ROC and RMC runs show a second failure mode: regenerating the
implementation from scratch can fix one covered dimension while regressing
another. The monotone variant therefore:

1. keeps the prior candidate that passed the earlier frozen contract set;
2. synthesizes the expanded contract set without formal feedback;
3. verifies the candidate against the expansion;
4. gives the agent only the new contract failures and repairs in place;
5. runs formal evaluation only after the repair is frozen.

The reproducible runner is:

```bash
PYTHONPATH=harness python harness/scripts/run_cgcc_warm_repair.py \
  --task-id alembic__revision_map_core__hard3_001 \
  --seed-run experiments/ablation/cgcc-roc-focus-s1-20260730-codex01 \
  --output experiments/ablation/cgcc-mdr-alembic-<seed> \
  --variant cgcc_rmc
```

On the focus development set, Alembic passed public and hidden in 3/3 repair
seeds. This is post-hoc mechanism evidence; it must be frozen and validated on
untouched tasks before being presented as a clean method result.
