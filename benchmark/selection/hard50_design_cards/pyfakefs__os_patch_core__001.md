# Design card: pyfakefs__os_patch_core__001

**status:** `eval_runtime_blocked`  
**disposition:** `backup`  
**wave:** `selected`  
**package:** `pyfakefs`  
**repository_url:** https://github.com/pytest-dev/pyfakefs  
**planned_lift_type:** Direct  
**final_lift_type:** pending_source_review  
**reclassification_reason:**  
**feature_family:** `direct_tooling_copytrap`  
**entanglement.level:** high  
**entanglement.types:** `resource_coupling`, `framework_coupling`  
**feature_one_liner:** Patch os/open path operations onto a fake filesystem  
**commit:** pending pin  

## paper_fit

RQ2: large fake-os tree; feature is Patcher+FakeFilesystem, rest is decoy.

## why_hard

Must patch the right modules; copying tests/examples leaks real FS.

## Balance Role

direct_tooling_copytrap / Direct / high entanglement.

## Pinned Source

- commit: *pending pin — do not materialize until a real revision is recorded*
- license: *pending pin*
- source kind: real external OSS repository
- network during evaluation: forbidden
- overlap_check: not in Python-150 or External-50 registries (2026-08-27 name/url screen)

## Required API (draft)

Patcher; FakeFilesystem; create_file; os.path existence

## Included Behavior (draft)

create file; read; exists; isolate from real cwd

## Excluded Behavior

full pytest plugin surface beyond declared

## YAML contract (to fill at pin time)

```yaml
target_api:
  module:
  signatures:
  returns:
  exceptions:
  defaults:
  state_effects:
upstream_mapping:
  primary_symbols:
  supporting_components:
  semantic_delta:
oracle_basis:
  basis: upstream
scope:
  included:
  excluded:
feasibility:
  commit:
  license:
  python_versions:
  native_or_heavy_dependencies:
  offline_resources:
acceptance:
  closure_review: pending
  reference_pass: pending
  isolation_pass: pending
  no_original_import: pending
  overlap_check: pass_name_screen
```

## Gate Status

- design card: ready for pin
- package completeness: materialized then **eval_runtime_blocked** (Patcher 劫持 `os.path`，评测 sitecustomize 在 `open` 审计里调 `os.path.realpath` 导致 RecursionError)
- intended swap: `webob__request_response_core__001`
- Docker / Flash calibration: skipped
- promotion to `benchmark/hard50`: blocked
