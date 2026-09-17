# Design card: flit__metadata_core__001

**status:** `design_card_ready`
**disposition:** `candidate`
**wave:** `closure50_screened_wave2`
**in_pilot:** yes
**package:** `flit`
**repository_url:** https://github.com/pypa/flit
**planned_lift_type:** Adapted
**final_lift_type:** pending_source_review
**feature_family:** `resource_metadata_loading`
**entanglement.level:** high
**entanglement.types:** *pending review*
**feature_one_liner:** Module metadata discovery and normalization
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
| `core_loc` | **4717** (gate: >= 3000) |
| `test_loc` | 2181 |
| core file count | 41 |
| tree size | 0.47 MB |
| candidate revision | `4.0.2` |
| candidate commit | `60c0b3d97bf095fbdb7671a02e51f8d8aba2fb85` |
| evidence | `reports/closure50/source_screen.json` |

The revision above came from a version tag, never a moving branch. It is a
candidate only: nothing is pinned until it is registered and materialized.

## Planned behavior branches

The Closure-50 recipe puts difficulty in the number of *independent* declared
branches behind a tiny API surface, not in slice size. Each branch becomes one
behavior clause and one hidden test. Every branch that survives verification
must be written into `metadata.public_spec.behaviors`: difficulty comes from the
branches being many and mutually independent, never from withholding them.

1. Module discovery raises ValueError when more than one file or folder could be the module
2. Module discovery raises ValueError when no file or folder matches the module name
3. version_files prefers version.py, _version.py and __version__.py over __init__.py
4. get_info_from_module reads docstring and version from the AST first and only then falls back to import
5. the summary is the first line of the docstring; a missing docstring raises NoDocstringError

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
