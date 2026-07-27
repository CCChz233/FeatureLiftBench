# Full-Repository Source Policy

**Policy ID:** `featureliftbench.full_repository_source.v2`

**Adopted:** 2026-07-27
**Applies to:** Python v3 External Main and every result labeled `Full-Repository`

## 1. Main input

For an external OSS task, `repo/` MUST be a reproducible materialization of the
complete upstream tracked source tree at one immutable commit. The Agent sees
that tree, a complete public functional contract, dependency/runtime metadata,
and an empty `submission/`. It does not receive task-specific source paths,
symbols, entrypoints, dependency closures, or target-file lists.

The following upstream material is retained when tracked:

- source and native-extension code;
- tests, documentation, examples, configuration, schemas, templates, grammars,
  locale/data files, generated source, and build metadata;
- license and notice files;
- tracked submodules, recursively materialized at their recorded gitlink
  commits.

The following are excluded uniformly:

- `.git/` history and credentials;
- untracked build outputs, caches, virtual environments, editor state, and
  package-manager download caches;
- benchmark-authored evaluator tests, reference solutions, gold closures, and
  task-specific source hints.

Tracked files MUST NOT be removed because they are large, irrelevant to one
task, reveal tests, or make localization harder. If a repository cannot satisfy
the declared resource, license, network, or determinism policy, the task is
rejected or placed in a separately named split; it is not silently pruned.

## 2. Revision resolution

Every source snapshot has two immutable identifiers:

1. `requested_revision`: the commit/tag/version recorded by task metadata;
2. `resolved_commit`: the exact 40-hex Git commit actually materialized.

An existing `*-installed-snapshot` label is historical provenance, not an
immutable revision. It MUST be resolved to an upstream commit before a task can
enter v3 Main. Moving branches such as `main`, `master`, or `latest` are
forbidden as frozen revisions.

One canonical snapshot may serve multiple tasks from the same repository and
commit. Different commits remain different source snapshots even when their
repository URL is the same.

## 3. Canonical source registry

[`benchmark/sources/registry.json`](../benchmark/sources/registry.json) is the
single registry for repository identity and source revisions. It is generated
from task metadata by
[`scripts/build_source_registry.py`](../scripts/build_source_registry.py) and
validated against
[`benchmark/sources/registry.schema.json`](../benchmark/sources/registry.schema.json).

The registry separates:

- `source_repo_id`: canonical upstream repository identity;
- `source_snapshot_id`: one requested/resolved revision of that repository;
- acquisition method and resolution status;
- target/current snapshot scope;
- archive/tree digests, file counts, LOC, license provenance, and associated
  task IDs.

Missing evidence is represented by `null` or an explicit pending status. A
legacy task-local slice is never labeled as a full tree.

## 4. Content and archive digests

Each accepted snapshot records:

- `archive_sha256`: SHA-256 of the distributed source archive bytes;
- `source_tree_sha256`: content digest independent of archive timestamps and
  compression;
- tracked file count, Python file count, Python LOC, total bytes, and maximum
  path depth.

The canonical tree digest is SHA-256 over sorted records. For every regular file
or symlink, encode:

```text
kind NUL git_mode NUL UTF-8_POSIX_relative_path NUL byte_size NUL blob_sha256 LF
```

Records are sorted by UTF-8 path bytes. A regular file hashes its exact bytes; a
symlink hashes its link-target bytes. Empty directories are omitted because Git
does not track them. Submodule files are recorded beneath their materialized
paths. Non-UTF-8 paths, inaccessible submodules, case-colliding paths, or digest
mismatches block the snapshot.

## 5. Materialization and workspace boundary

The canonical build process:

1. resolve URL aliases to `source_repo_id`;
2. fetch the registered immutable commit;
3. checkout the full tracked tree and pinned submodules;
4. apply only the uniform exclusions in §1;
5. compute statistics and digests;
6. package the tree without `.git/`;
7. materialize the same verified archive into each task workspace.

The source registry and archives are benchmark assets. Agent workspace
construction is a separate step and MUST pass the No-Hint audit. Public and
hidden evaluator tests remain outside the Main workspace until submission.
Functional evaluation receives a separate source-free capsule and MUST NOT
mount this registry, its archives, the materialized source tree, reference code
or compactness records.

## 6. Curated sources

Curated repositories such as `benchmark/curated/sources/vibe_app/` are reported separately from
external OSS. They require the same content digest, license provenance,
No-Hint, isolation, and evaluator rules, but do not claim an upstream Git
commit. Curated tasks never enter the External-150 headline; they are reported
as an independent extension split.

## 7. Admission gates

A task may be promoted to v3 External Main only when:

- its registry snapshot has `status: ready`;
- `resolved_commit`, both digests, license evidence, and repository statistics
  are populated;
- the task workspace is byte-derived from that registered snapshot;
- the No-Hint workspace audit passes;
- contract/hidden mapping, Oracle, isolation, forbidden-path, and determinism
  checks pass after migration;
- compactness uses a reference-relative metric, not full-repository LOC as the
  direct denominator.

Independent human review is not an admission or release gate. Existing
AI-assisted/maintainer review records remain provenance and must not be
described as independently adjudicated human gold.
