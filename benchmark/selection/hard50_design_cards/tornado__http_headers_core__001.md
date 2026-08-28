# Design card: tornado__http_headers_core__001

**status:** `materialized_candidate`  
**disposition:** `selected`  
**wave:** `copyheavy_swap`  
**package:** `tornado`  
**repository_url:** https://github.com/tornadoweb/tornado  
**planned_lift_type:** Adapted  
**final_lift_type:** pending_source_review  
**reclassification_reason:** Replaces `docutils__rst_transform_core__001` (Flash copy_heavy_pass, RRES≈0.91 because oracle≈whole package).  
**feature_family:** `parse_tokenize_decode`  
**entanglement.level:** high  
**entanglement.types:** `parser_state_coupling`, `data_model_coupling`  
**feature_one_liner:** HTTPHeaders parse without IOLoop/web/httpclient  
**commit:** `0096f2897c98facdcd9716009ee934a7381af5ef`  

## paper_fit

RQ2: Header parser slice inside a large async HTTP/web tree. Copy-all of rewritten Tornado is unused decoy, not a near-whole-package oracle.

## why_hard

HTTP-header case, multi-value cookies, malformed lines; copying IOLoop/web is the wrong closure.

## Balance Role

parse_tokenize_decode / Adapted / high entanglement. Swap-in for docutils fat-oracle copy-heavy Flash pass.

## Pinned Source

- commit: `0096f2897c98facdcd9716009ee934a7381af5ef`
- license: Apache-2.0
- source kind: real external OSS repository
- network during evaluation: forbidden
- overlap_check: not in Python-150 or External-50 registries (2026-08-28 name/url screen)

## Gate Status

- design card: pinned
- package completeness: materialized in `benchmark/hard50_pilot/tornado__http_headers_core__001`
- local oracle/naive/copy-all: pass / fail / pass (RRES ≈ 18.2; true rewritten Tornado package, not padding)
- Docker / Flash calibration: pending on this swapped-in task
- promotion to `benchmark/hard50`: blocked until Flash on swapped tasks then release rebuild
