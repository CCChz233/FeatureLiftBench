# Repository Semantic Graph Phase 1 Checkpoint

> Historical RSG prototype evidence. RSG is not part of the v2 Main baseline,
> and this checkpoint does not certify the current benchmark freeze.

Date: 2026-07-22

Phase 1 implements an offline Tree-sitter repository graph. It does not inject the
graph into OpenHands, mini-swe-agent, or FeatureLiftAgent, and therefore does not
change any frozen experiment profile.

## Automated result

The authoritative machine-readable report is
[`python150_audit.json`](python150_audit.json). The final run reports:

- Python tasks built: 150 / 150;
- Tree-sitter parse-error files: 0;
- class/function/import capture recall against Python AST: 100%;
- metadata source-entrypoint exact/probable mapping: 621 / 642 (96.73%);
- deterministic rebuild failures in five samples: 0;
- absolute host-path leaks: 0;
- warm query P95: 0.002650 seconds;
- largest snapshot: 7,278 nodes, 33,956 edges, 13.37 MB JSON;
- isolated peak RSS across the three largest snapshots: at most 167,559,168 bytes;
- full harness regression: 272 passed, 7 skipped.

The much larger `audit_process_max_rss_bytes` value in the report is not a snapshot
measurement. That process sequentially builds all 150 graphs and also creates full
Python AST inventories. The acceptance metric is the isolated subprocess snapshot
RSS sample.

## Additional gates

Both remaining Phase 1 gates passed:

1. [`docker_digest_check.json`](docker_digest_check.json) records identical
   implementation, snapshot, and graph digests for a Python 3.12/macOS host and a
   Python 3.11/Linux Agent image;
2. [`exact_edge_audit.json`](exact_edge_audit.json) records a deterministic,
   stratified 100-edge sample from 2,167 non-structural exact edges across ten
   representative tasks. All 100 have independent AST/source provenance and no
   exact kind was unsupported.

The exact-edge audit establishes static provenance precision, not task-specific
causal necessity. Likewise, Phase 1 does not establish Agent success or token gains.
Those questions belong to the controlled Phase 2/Phase 4 experiments.
