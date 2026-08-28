# Design card: pika__channel_spec_core__001

**status:** `materialized_candidate`  
**disposition:** `selected`  
**wave:** `copyheavy_swap`  
**package:** `pika`  
**repository_url:** https://github.com/pika/pika  
**planned_lift_type:** Direct  
**final_lift_type:** pending_source_review  
**reclassification_reason:** Replaces `bytecode__code_roundtrip_core__001` (Flash copy_heavy_pass, RRES≈0.88 on a slice-sized repo). Family kept as parse_tokenize_decode.  
**feature_family:** `parse_tokenize_decode`  
**entanglement.level:** high  
**entanglement.types:** `parser_state_coupling`, `data_model_coupling`  
**feature_one_liner:** AMQP method framing encode/decode without a broker  
**commit:** `2126d43a76c14fb8d365d96bd1bdcef13dad75b5`  

## paper_fit

RQ2: Frame codec slice inside adapters/connection. Copy-all of rewritten Pika is a real unused decoy.

## why_hard

Must marshal/decode frames from spec types; copying BlockingConnection is the isolation fail.

## Balance Role

parse_tokenize_decode / Direct / high entanglement. Swap-in for bytecode copy-heavy Flash pass.

## Pinned Source

- commit: `2126d43a76c14fb8d365d96bd1bdcef13dad75b5`
- license: BSD-3-Clause
- source kind: real external OSS repository
- network during evaluation: forbidden
- overlap_check: not in Python-150 or External-50 registries (2026-08-28 name/url screen)

## Gate Status

- design card: pinned
- package completeness: materialized in `benchmark/hard50_pilot/pika__channel_spec_core__001`
- local oracle/naive/copy-all: pass / fail / pass (RRES ≈ 5.5; true rewritten Pika package, not padding)
- Docker / Flash calibration: pending on this swapped-in task
- promotion to `benchmark/hard50`: blocked until Flash on swapped tasks then release rebuild
