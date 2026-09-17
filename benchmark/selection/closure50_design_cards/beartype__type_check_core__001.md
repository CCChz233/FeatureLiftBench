# Design card: beartype__type_check_core__001

**status:** `design_card_ready`
**disposition:** `candidate`
**wave:** `closure50_screened_wave2`
**in_pilot:** no
**package:** `beartype`
**repository_url:** https://github.com/beartype/beartype
**planned_lift_type:** Direct
**final_lift_type:** pending_source_review
**feature_family:** `validate_normalize_construct`
**entanglement.level:** high
**entanglement.types:** *pending review*
**feature_one_liner:** Runtime type checks over a declared hint subset
**commit:** pending pin

## paper_fit

*pending: assign an RQ once the slice is fixed*

## why_hard

*pending: state the specific declared-but-easily-missed branches once the pinned upstream has been read*

## Source gate evidence

The gating metric is `core_loc`: implementation lines outside tests, docs and
examples, counting `.py` plus Cython `.pyx`/`.pxd`. It decides whether an
80-150 LOC slice can be passed by copying, the failure mode that saturated
Hard-50 (pass-conditioned copy median 0.66).

| Field | Value |
| --- | --- |
| `core_loc` | **69533** (gate: >= 3000) |
| `test_loc` | 16402 |
| core file count | 680 |
| tree size | 7.4 MB |
| candidate revision | `v0.22.9` |
| candidate commit | `9430c6515af3b158acacdc47fe7b1adb646f6624` |
| evidence | `reports/closure50/source_screen.json` |

The revision above came from a version tag, never a moving branch. It is a
candidate only: nothing is pinned until it is registered and materialized.

## Planned behavior branches

The Closure-50 recipe puts difficulty in the number of *independent* declared
branches behind a tiny API surface, not in slice size. Each branch becomes one
behavior clause and one hidden test. Every branch that survives verification
must be written into `metadata.public_spec.behaviors`: difficulty comes from the
branches being many and mutually independent, never from withholding them.

*Not yet enumerated.* This candidate cleared the source gate on repository statistics alone. The 4-5 independent branches must be read out of the pinned upstream before the contract is written; listing plausible-sounding branches here would be fabricating upstream behavior.

Status: `pending_source_read`

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

- design card: needs source read before pin
- package completeness: pending
- oracle N=3 / isolation: pending
- naive and copy-all baselines: pending
- Flash Official Main calibration: pending
- promotion to `benchmark/closure50`: blocked until the Pilot gate, then 50/50, passes
