# Design card: pyrsistent__pmap_pvector_core__001

**status:** `design_card_ready`  
**wave:** W5  
**package:** `pyrsistent`  
**repository_url:** https://github.com/tobgu/pyrsistent  
**planned_lift_type:** Direct  
**final_lift_type:** Direct  
**reclassification_reason:** None  
**feature_family:** algorithm_data_structure  
**entanglement:** data_model_coupling  
**feature_one_liner:** PMap/PVector persistent collections  
**lift_review_flag:** none

> Filled for design_card phase. `feasibility.commit` still unresolved until pin.  
> Spec authority: `docs/TASK_DESIGN_RULES.md`. Workflow: `docs/PLAN_EXTERNAL50_EXPANSION.md`.

## target_api

```yaml
module: featurelifted
signatures:
  - "featurelifted.pmap(initial=None) / pvector(initial=())"
  - "PMap.set/remove/get; PVector.append/set/extend"
  - "evolution transform() if included"
  - "thaw/freeze helpers if included"
returns:
  - "persistent structures; updates return new objects"
exceptions:
  - "KeyError/IndexError"
defaults:
  - "empty structures"
state_effects:
  - "persistent \u2014 old versions unchanged"
```

## upstream_mapping

```yaml
primary_symbols:
  - "pyrsistent.pmap"
  - "pyrsistent.pvector"
supporting_components:
  - "pyrsistent.PMap"
  - "pyrsistent.PVector"
semantic_delta:
  - "Direct"
```

## oracle_basis

```yaml
basis: upstream
notes: |
  Direct persistent collections.
```

## scope

```yaml
included:
  - "pmap/pvector core ops"
excluded:
  - "pset/pdeque/pclass unless listed"
  - "optional C extension requirement"
```

## feasibility

```yaml
commit: null  # resolve at pin/materialize
license: "MIT"
python_versions:
  - "3.10"
  - "3.11"
  - "3.12"
native_or_heavy_dependencies: "optional C ext; allow pure"
offline_resources: "pure"
```

## acceptance

```yaml
closure_review: pending
reference_pass: pending
isolation_pass: pending
no_original_import: pending
overlap_check: pending
```

## agent_notes

- Staging path: `benchmark/staging/pyrsistent__pmap_pvector_core__001/`
- Do not materialize until human skim of target_api + lift (esp. reclassified cards).
- Do not promote to `benchmark/tasks/` in design_card phase.
