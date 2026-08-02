# Design card: anytree__tree_resolve_render_core__001

**status:** `staging_validated`  
**wave:** W2  
**package:** `anytree`  
**repository_url:** https://github.com/c0fec0de/anytree  
**planned_lift_type:** Composite  
**final_lift_type:** Composite  
**reclassification_reason:** None  
**feature_family:** algorithm_data_structure  
**entanglement:** data_model_coupling  
**feature_one_liner:** Node tree + Resolver + RenderTree  
**lift_review_flag:** none

> Skim pass + pin resolved. Materialize next; staging only (no promote).  
> Spec authority: `docs/TASK_DESIGN_RULES.md`. Workflow: `docs/PLAN_EXTERNAL50_EXPANSION.md`.

## target_api

```yaml
module: featurelifted
signatures:
  - "featurelifted.Node(name, parent=None, children=None, **kwargs)"
  - "featurelifted.Resolver(pathattr='name').get(node, path)"
  - "featurelifted.RenderTree(node) yields Row(pre, fill, node)"
  - "featurelifted.PreOrderIter / findall if included"
returns:
  - "Node; Resolver.get returns Node; RenderTree yields rows with words"
exceptions:
  - "Resolver error types (RootResolverError, ChildResolverError) declare"
defaults:
  - "pathattr='name'"
state_effects:
  - "parent/children mutation on Node"
```

## upstream_mapping

```yaml
primary_symbols:
  - "anytree.Node"
  - "anytree.Resolver"
  - "anytree.RenderTree"
supporting_components:
  - "anytree.iterators"
semantic_delta:
  - "Node + resolve + render composed in one task surface"
```

## oracle_basis

```yaml
basis: upstream
notes: |
  Three APIs, one tree domain.
```

## scope

```yaml
included:
  - "build tree, path resolve, ASCII render"
excluded:
  - "dot export, dict attachment persistence"
```

## feasibility

```yaml
commit: "2e0a1b956172654d75aff93277ce3d883355e0bf"  # tag 2.13.0
license: "Apache-2.0"
python_versions:
  - "3.10"
  - "3.11"
  - "3.12"
native_or_heavy_dependencies: "none"
offline_resources: "in-memory trees"
```

## acceptance

```yaml
closure_review: pass
reference_pass: pass
isolation_pass: pass
no_original_import: pass
overlap_check: pass
```

## agent_notes

- Staging path: `benchmark/staging/anytree__tree_resolve_render_core__001/`
- Skim pass @ 2.13.0 (`2e0a1b956172…`).
- Do not promote to `benchmark/tasks/` in design_card phase.
