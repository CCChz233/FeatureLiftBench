# Design card: stdnum__isbn_validate_core__001

**status:** `materialized_candidate`  
**disposition:** `selected`  
**wave:** `copyheavy_swap`  
**package:** `stdnum`  
**repository_url:** https://github.com/arthurdejong/python-stdnum  
**planned_lift_type:** Adapted  
**final_lift_type:** pending_source_review  
**reclassification_reason:** Replaces `fastjsonschema__compile_validate_core__001` (Flash copy_heavy_pass, RRES≈0.93 on a slice-sized repo).  
**feature_family:** `validate_normalize_construct`  
**entanglement.level:** high  
**entanglement.types:** `data_model_coupling`, `resource_coupling`  
**feature_one_liner:** ISBN validate/compact without country-code modules  
**commit:** `006192e59be8ed6e08fd680256868a6c31eb2ba9`  

## paper_fit

RQ2: ISBN slice versus hundreds of unused country validators. Copy-all of rewritten stdnum is a real unused decoy.

## why_hard

Checksum and ISBN-10/13 conversion; copying IBAN/country modules is the wrong closure.

## Balance Role

validate_normalize_construct / Adapted / high entanglement. Swap-in for fastjsonschema copy-heavy Flash pass.

## Pinned Source

- commit: `006192e59be8ed6e08fd680256868a6c31eb2ba9`
- license: LGPL-2.1-or-later
- source kind: real external OSS repository
- network during evaluation: forbidden
- overlap_check: not in Python-150 or External-50 registries (2026-08-28 name/url screen)

## Gate Status

- design card: pinned
- package completeness: materialized in `benchmark/hard50_pilot/stdnum__isbn_validate_core__001`
- local oracle/naive/copy-all: pass / fail / pass (RRES ≈ 27.5; true rewritten stdnum package, not padding)
- Docker / Flash calibration: pending on this swapped-in task
- promotion to `benchmark/hard50`: blocked until Flash on swapped tasks then release rebuild
