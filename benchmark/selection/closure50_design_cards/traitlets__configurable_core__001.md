# Design card: traitlets__configurable_core__001

**status:** `design_card_ready`
**disposition:** `candidate`
**wave:** `hard50_backup_20260827`
**in_pilot:** yes
**package:** `traitlets`
**repository_url:** https://github.com/ipython/traitlets
**planned_lift_type:** Adapted
**final_lift_type:** pending_source_review
**feature_family:** `validate_normalize_construct`
**entanglement.level:** high
**entanglement.types:** `config_environment_coupling`, `framework_coupling`
**feature_one_liner:** *pending review*
**commit:** pending pin

## paper_fit

RQ1+RQ5: Jupyter-stack config objects without jupyter_core overlap.

## why_hard

Trait validation + config merge + help metadata; E50-style one-file extract fails.

## Source gate evidence

The gating metric is `core_loc`: implementation lines outside tests, docs and
examples, counting `.py` plus Cython `.pyx`/`.pxd`. It decides whether an
80-150 LOC slice can be passed by copying, the failure mode that saturated
Hard-50 (pass-conditioned copy median 0.66).

| Field | Value |
| --- | --- |
| `core_loc` | **6477** (gate: >= 3000) |
| `test_loc` | 5437 |
| core file count | 21 |
| tree size | 0.69 MB |
| candidate revision | `v5.16.1` |
| candidate commit | `7beeb105cd8c3adab38631daf2da9524f47166e2` |
| evidence | `reports/closure50/source_probe.json` |

The revision above came from a version tag, never a moving branch. It is a
candidate only: nothing is pinned until it is registered and materialized.

## Planned behavior branches

The Closure-50 recipe puts difficulty in the number of *independent* declared
branches behind a tiny API surface, not in slice size. Each branch becomes one
behavior clause and one hidden test. Every branch that survives verification
must be written into `metadata.public_spec.behaviors`: difficulty comes from the
branches being many and mutually independent, never from withholding them.

1. Int coerces numeric whole values to int and raises TraitError for near-miss types such as the string '1'
2. list/container defaults are created per instance rather than sharing one mutable default
3. constructor kwargs override values coming from config, not the other way around
4. failed trait assignment raises TraitError
5. cross-trait validators run against the fully assigned instance state after __init__ kwargs are applied

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
