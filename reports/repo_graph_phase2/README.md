# Repository Semantic Graph Phase 2 Checkpoint

> Historical RSG prototype evidence. Task-private entrypoint overlays described
> below are incompatible with v2 Main and are retained only for ablation provenance.

Date: 2026-07-22

Phase 2 connects the deterministic graph to the Agent runner without changing
existing profiles. It is an integration checkpoint, not an Agent-effectiveness
result.

Implemented and tested:

- opt-in `disabled/static/closure/evidence` policy with validated precedence;
- pre-model fail-fast initialization from the redacted workspace only;
- cache key derived before parsing and private run materialization outside the
  Agent-visible cache;
- byte-identical bootstrap/tool contract for OpenHands, mini-swe-agent, and
  FeatureLiftAgent;
- host and `/flb/agent/state/repo_graph` Docker path resolution;
- task-private behavior/entrypoint/public-test overlay, with hidden,
  evaluation, and reference-solution input counters fixed at zero;
- exact-edge closure candidate separated from uncertain risks;
- content-addressed submission revisions and source/submission comparison;
- bounded query audit, graph-context character accounting, and immutable graph
  artifact post-run checks;
- disabled-mode regression: no graph artifacts and no prompt mutation.

The three-Agent smoke is offline/mocked at the provider boundary, so it verifies
adapter and protocol behavior without spending model tokens. A real paid causal
comparison belongs to Phase 4.
