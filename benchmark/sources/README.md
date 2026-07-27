# Canonical Source Registry

This directory records source repository identities and immutable snapshots for
FeatureLiftBench v3 Main.

- `registry.json`: generated canonical inventory.
- `registry.schema.json`: machine-readable shape.
- [`../../docs/FULL_REPOSITORY_SOURCE_POLICY.md`](../../docs/FULL_REPOSITORY_SOURCE_POLICY.md):
  normative inclusion, revision, digest, and admission rules.

Regenerate or verify:

```bash
python3 scripts/build_source_registry.py
python3 scripts/build_source_registry.py --check
python3 scripts/materialize_full_sources.py
python3 scripts/materialize_full_sources.py --check
```

Current External Python-150 state: **126 external OSS repositories, 132
immutable snapshots, 150 task mappings, 132/132 snapshots ready**. Archive bytes are a reproducible local or
server cache and are intentionally not committed; the registry tracks their
SHA-256 values and the materializer rebuilds them from pinned revisions.

`pending_*` remains a fail-closed lifecycle state for future additions. It
means an upstream tree has not yet been resolved/materialized and cannot enter
v3 Main.

Regeneration derives identities and task membership from task metadata while
preserving audited registry enrichment (resolved commits, digests, statistics,
license paths, status, organization, and ecosystem family). Immutable identity
changes are rejected.
