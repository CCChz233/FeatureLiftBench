# Design card: openapi_core__request_validate_core__001

**status:** `design_card_ready`
**disposition:** `candidate`
**wave:** `hard50_backup_20260827`
**in_pilot:** no
**package:** `openapi-core`
**repository_url:** https://github.com/python-openapi/openapi-core
**planned_lift_type:** Adapted
**final_lift_type:** pending_source_review
**feature_family:** `validate_normalize_construct`
**entanglement.level:** high
**entanglement.types:** `data_model_coupling`, `framework_coupling`
**feature_one_liner:** *pending review*
**commit:** pending pin

## paper_fit

RQ4 unmarshalling vs jsonschema-only (jsonschema already in 150).

## why_hard

Spec+request+unmarshal types; naive jsonschema.validate misses media types.

## Source gate evidence

The gating metric is `core_loc`: implementation lines outside tests, docs and
examples, counting `.py` plus Cython `.pyx`/`.pxd`. It decides whether an
80-150 LOC slice can be passed by copying, the failure mode that saturated
Hard-50 (pass-conditioned copy median 0.66).

| Field | Value |
| --- | --- |
| `core_loc` | **8843** (gate: >= 3000) |
| `test_loc` | 14705 |
| core file count | 159 |
| tree size | 1.3 MB |
| candidate revision | `0.23.1` |
| candidate commit | `21f62cecf53a218e0f3066c55eb7c9bad5373ff5` |
| evidence | `reports/closure50/source_screen.json` |

The revision above came from a version tag, never a moving branch. It is a
candidate only: nothing is pinned until it is registered and materialized.

## Planned behavior branches

The Closure-50 recipe puts difficulty in the number of *independent* declared
branches behind a tiny API surface, not in slice size. Each branch becomes one
behavior clause and one hidden test. Every branch that survives verification
must be written into `metadata.public_spec.behaviors`: difficulty comes from the
branches being many and mutually independent, never from withholding them.

1. media-type selection falls back per the declared rule
2. parameter style/explode handling for the declared subset
3. type unmarshalling of declared formats
4. missing required parameter raises the declared error
5. additional properties handling follows the declared policy

**These are design intent to check against the pinned snapshot; they are not claims about current upstream behavior.**

## Recipe targets

| Dimension | Target |
| --- | --- |
| `required_api` | 1-2 callables, 2-4 members |
| behavior clauses | 4-5 semantic + 1 api_surface + 1 isolation |
| `public_tests` | 1-2 shallowest smoke only |
| `hidden_tests` | 4-5, one per semantic clause |
| reference solution | 80-150 LOC, single file preferred |
| Flash calibration band | 25%-45% functional pass |

## Risks

- *none recorded yet*

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
recipe_targets:
  required_api_size: 1-2 callables, 2-4 members
  behavior_clauses: 4-5 semantic + 1 api_surface + 1 isolation
  public_tests: 1-2 shallow smoke
  hidden_tests: 4-5, one per semantic clause
  reference_loc: 80-150
acceptance:
  closure_review: pending
  reference_pass: pending
  isolation_pass: pending
  no_original_import: pending
  overlap_check: pass_name_screen
  flash_band_25_45: pending
```

## Gate Status

- design card: ready for pin
- package completeness: pending
- oracle N=3 / isolation: pending
- naive and copy-all baselines: pending
- Flash Official Main calibration: pending
- promotion to `benchmark/closure50`: blocked until the Pilot gate, then 50/50, passes
