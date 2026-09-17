# Design card: bytecode__code_roundtrip_core__001

**status:** `design_card_ready`
**disposition:** `candidate`
**wave:** `hard50_backup_20260827`
**in_pilot:** yes
**package:** `bytecode`
**repository_url:** https://github.com/MatthieuDartiailh/bytecode
**planned_lift_type:** Direct
**final_lift_type:** pending_source_review
**feature_family:** `parse_tokenize_decode`
**entanglement.level:** high
**entanglement.types:** `parser_state_coupling`, `data_model_coupling`
**feature_one_liner:** *pending review*
**commit:** pending pin

## paper_fit

RQ4 instruction-stream state, not a string parser.

## why_hard

Label/jump and opcode versions; copy dis.dis wrappers fail Hidden.

## Source gate evidence

The gating metric is `core_loc`: implementation lines outside tests, docs and
examples, counting `.py` plus Cython `.pyx`/`.pxd`. It decides whether an
80-150 LOC slice can be passed by copying, the failure mode that saturated
Hard-50 (pass-conditioned copy median 0.66).

| Field | Value |
| --- | --- |
| `core_loc` | **3384** (gate: >= 3000) |
| `test_loc` | 5259 |
| core file count | 7 |
| tree size | 0.45 MB |
| candidate revision | `0.19.0` |
| candidate commit | `9eea62692be09d07a454aa5244029cc5434096d7` |
| evidence | `reports/closure50/source_probe.json` |

The revision above came from a version tag, never a moving branch. It is a
candidate only: nothing is pinned until it is registered and materialized.

## Planned behavior branches

The Closure-50 recipe puts difficulty in the number of *independent* declared
branches behind a tiny API surface, not in slice size. Each branch becomes one
behavior clause and one hidden test. Every branch that survives verification
must be written into `metadata.public_spec.behaviors`: difficulty comes from the
branches being many and mutually independent, never from withholding them.

1. Label jump targets survive Bytecode.from_code / to_code roundtrip
2. compute_stacksize on branching code matches the assembled code object
3. add_const de-duplicates constants via const_key rather than identity

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

- pin the evaluator Python 3.11; do not claim 3.12-3.15 opcode coverage

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
