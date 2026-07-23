# Repository Semantic Graph Phase 3 Checkpoint

Date: 2026-07-22

Phase 3 adds run-local semantic claims, runtime evidence, revision freshness,
risk-triggered probe suggestions, and a native FeatureLiftAgent stopping guard.

Mechanism guarantees covered by tests:

- claims start as `hypothesis`;
- `observed` requires one supporting evidence record at the current revision;
- `verified` requires two independent evidence classes at the current revision;
- failed/inconclusive probes remain in the append-only ledger;
- evidence stores bounded summaries and hashes, not complete command output or
  credentials;
- a submission content change increments revision and marks prior claims stale;
- stale claims/evidence cannot satisfy the stopping guard;
- detectors expose source cues, a suggested probe, and a rationale; unmatched
  low-precision cues are not exposed;
- repeated identical FeatureLiftAgent graph queries at one revision are marked
  `deprioritized`;
- FeatureLiftAgent syncs after write/copy/prune, records public/final evidence,
  and requires a fresh final verification before completion;
- OpenHands/mini-swe-agent remain advisory; their post-run audit is explicitly
  labeled and is not reported as online enforcement.

This checkpoint demonstrates state-machine correctness, not causal benchmark
gain. P4 versus N1 effects must remain separate in the Phase 4 analysis.
