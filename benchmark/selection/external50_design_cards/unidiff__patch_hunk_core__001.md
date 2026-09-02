# Design card: unidiff__patch_hunk_core__001

**status:** `staging_validated`  
**wave:** W2  
**package:** `unidiff`  
**repository_url:** https://github.com/matiasb/python-unidiff  
**planned_lift_type:** Composite  
**final_lift_type:** Composite  
**reclassification_reason:** None (W2 backup replacing libcst)  
**feature_family:** parse_tokenize_decode  
**entanglement:** parser_state_coupling  
**feature_one_liner:** patch parse + hunk model  
**lift_review_flag:** none

> Skim pass + pin resolved. Replaces `libcst__parse_transform_core__001` (native rename blocked). Staging only (no promote).  
> Spec authority: `docs/TASK_DESIGN_RULES.md`. Workflow: `docs/archive/plans/PLAN_EXTERNAL50_EXPANSION.md`.

## target_api

```yaml
module: featurelifted
signatures:
  - "featurelifted.PatchSet(diff: str)"
  - "featurelifted.PatchedFile path/added/removed; iterable of Hunk"
  - "featurelifted.Hunk iterable of lines with line_type/value"
  - "featurelifted.LINE_TYPE_ADDED / LINE_TYPE_REMOVED / LINE_TYPE_CONTEXT"
  - "featurelifted.UnidiffParseError"
returns:
  - "PatchSet of PatchedFile; hunk lines"
exceptions:
  - "UnidiffParseError on malformed/short hunks"
defaults:
  - "declare"
state_effects:
  - "none"
```

## upstream_mapping

```yaml
primary_symbols:
  - "unidiff.PatchSet"
  - "unidiff.PatchedFile"
  - "unidiff.Hunk"
supporting_components:
  - "unidiff.constants line types"
semantic_delta:
  - "Patch parse + hunk/line model composed as one task surface"
```

## oracle_basis

```yaml
basis: upstream
notes: |
  Composite file/hunk/line model.
```

## scope

```yaml
included:
  - "unified diff parse, multi-file, line types, parse errors"
excluded:
  - "git apply, binary diffs"
```

## feasibility

```yaml
commit: "5ff054b218a345b6322bdd3cdd8ca4670ddcd6ad"  # tag v1.0.0
license: "MIT"
python_versions:
  - "3.10"
  - "3.11"
  - "3.12"
native_or_heavy_dependencies: "none"
offline_resources: "diff strings"
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

- Staging path: `benchmark/staging/unidiff__patch_hunk_core__001/`
- Skim pass @ v1.0.0 (`5ff054b218a3…`).
- Do not promote to `benchmark/tasks/` in this wave.
