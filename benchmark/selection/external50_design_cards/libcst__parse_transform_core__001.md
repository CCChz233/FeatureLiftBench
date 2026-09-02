# Design card: libcst__parse_transform_core__001

**status:** `blocked_native`  
**wave:** W2  
**package:** `libcst`  
**repository_url:** https://github.com/Instagram/LibCST  
**planned_lift_type:** Composite  
**final_lift_type:** Composite  
**reclassification_reason:** None  
**feature_family:** parse_tokenize_decode  
**entanglement:** parser_state_coupling  
**feature_one_liner:** Parse module + transform visitor + codegen  
**lift_review_flag:** none

> Skim pass + pin resolved. Materialize next; staging only (no promote).  
> Spec authority: `docs/TASK_DESIGN_RULES.md`. Workflow: `docs/archive/plans/PLAN_EXTERNAL50_EXPANSION.md`.

## target_api

```yaml
module: featurelifted
signatures:
  - "featurelifted.parse_module(source: str) -> Module"
  - "featurelifted.Module.code / code_for_node"
  - "featurelifted.CSTTransformer visit_* methods used in tests"
  - "featurelifted.RemovalSentinel / SkipChildren as needed"
  - "featurelifted.ensure_type helpers if used"
returns:
  - "Module CST; codegen returns str"
exceptions:
  - "ParserSyntaxError"
defaults:
  - "declare"
state_effects:
  - "transformer returns new trees"
```

## upstream_mapping

```yaml
primary_symbols:
  - "libcst.parse_module"
  - "libcst.CSTTransformer"
supporting_components:
  - "libcst._nodes"
  - "libcst.metadata optional excluded"
semantic_delta:
  - "parse + transform + codegen pipeline"
```

## oracle_basis

```yaml
basis: upstream
notes: |
  Keep transforms tiny (rename/remove node).
```

## scope

```yaml
included:
  - "parse_module, simple transformer, codegen"
excluded:
  - "full metadata providers, codemod CLI"
```

## feasibility

```yaml
commit: "c029c17bf45a3737fc8d1347001ab2422f42ae58"  # tag v1.9.0
license: "MIT"
python_versions:
  - "3.10"
  - "3.11"
  - "3.12"
native_or_heavy_dependencies: "none"
offline_resources: "source strings"
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

- Staging path: `benchmark/staging/libcst__parse_transform_core__001/`
- Skim pass @ v1.9.0 (`c029c17bf45a…`).
- Do not promote to `benchmark/tasks/` in design_card phase.

## block_note

- **Blocked:** `libcst.native` extension hardcodes module name `libcst`; featurelifted rename breaks parse.
- **Replaced by:** `unidiff__patch_hunk_core__001`
