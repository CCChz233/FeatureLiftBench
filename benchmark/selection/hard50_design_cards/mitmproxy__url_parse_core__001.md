# Design card: mitmproxy__url_parse_core__001

**status:** `materialized_candidate`  
**disposition:** `selected`  
**wave:** `copyheavy_swap`  
**package:** `mitmproxy`  
**repository_url:** https://github.com/mitmproxy/mitmproxy  
**planned_lift_type:** Direct  
**final_lift_type:** pending_source_review  
**reclassification_reason:** Replaces `respx__route_mock_core__001` (Flash copy_heavy_pass, RRES≈0.94 on a slice-sized repo).  
**feature_family:** `direct_tooling_copytrap`  
**entanglement.level:** high  
**entanglement.types:** `data_model_coupling`, `resource_coupling`  
**feature_one_liner:** URL parse/unparse without proxy, addons, or network  
**commit:** `2ac5b089d953585c66026a53f678270e094e48e5`  

## paper_fit

RQ2: URL parse slice inside a large proxy/addon tree. Copy-all of the rewritten mitmproxy package is unused decoy, not padding.

## why_hard

Must extract `net.http.url.parse` plus host checks; copying addons/proxy fails isolation and inflates RRES.

## Balance Role

direct_tooling_copytrap / Direct / high entanglement. Swap-in for a small-repo copy-heavy Flash pass.

## Pinned Source

- commit: `2ac5b089d953585c66026a53f678270e094e48e5`
- license: MIT
- source kind: real external OSS repository
- network during evaluation: forbidden
- overlap_check: not in Python-150 or External-50 registries (2026-08-28 name/url screen)

## Gate Status

- design card: pinned
- package completeness: materialized in `benchmark/hard50_pilot/mitmproxy__url_parse_core__001`
- local oracle/naive/copy-all: pass / fail / pass (RRES ≈ 93.5; true rewritten mitmproxy package, not padding)
- Docker / Flash calibration: pending on this swapped-in task
- promotion to `benchmark/hard50`: blocked until Flash on swapped tasks then release rebuild
