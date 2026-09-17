# Design card: wcmatch__globmatch_core__001

**status:** `design_card_ready`
**disposition:** `candidate`
**wave:** `hard50_backup_20260827`
**in_pilot:** yes
**package:** `wcmatch`
**repository_url:** https://github.com/facelessuser/wcmatch
**planned_lift_type:** Direct
**final_lift_type:** pending_source_review
**feature_family:** `parse_tokenize_decode`
**entanglement.level:** high
**entanglement.types:** `parser_state_coupling`, `data_model_coupling`
**feature_one_liner:** *pending review*
**commit:** pending pin

## paper_fit

Backup Direct copy-trap if pathspec-like needed; larger than pathspec.

## why_hard

Flag combinations; Hidden brace/negate.

## Source gate evidence

The gating metric is `core_loc`: implementation lines outside tests, docs and
examples, counting `.py` plus Cython `.pyx`/`.pxd`. It decides whether an
80-150 LOC slice can be passed by copying, the failure mode that saturated
Hard-50 (pass-conditioned copy median 0.66).

| Field | Value |
| --- | --- |
| `core_loc` | **3689** (gate: >= 3000) |
| `test_loc` | 4913 |
| core file count | 11 |
| tree size | 0.65 MB |
| candidate revision | `11.0.1` |
| candidate commit | `9f8a9f6b7479e8ee4d033976d0a24faaca4a1830` |
| evidence | `reports/closure50/source_screen.json` |

The revision above came from a version tag, never a moving branch. It is a
candidate only: nothing is pinned until it is registered and materialized.

## Planned behavior branches

The Closure-50 recipe puts difficulty in the number of *independent* declared
branches behind a tiny API surface, not in slice size. Each branch becomes one
behavior clause and one hidden test. Every branch that survives verification
must be written into `metadata.public_spec.behaviors`: difficulty comes from the
branches being many and mutually independent, never from withholding them.

1. flag combinations are masked and transformed per FLAG_MASK / _flag_transform, including PATHNAME being forced on
2. brace expansion runs before negation classification
3. a pattern set that is only negative injects a default ** when NEGATEALL is set
4. CASE / IGNORECASE / platform default decide matching case via get_case
5. PATHNAME makes slash a structural separator rather than a wildcard match

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
