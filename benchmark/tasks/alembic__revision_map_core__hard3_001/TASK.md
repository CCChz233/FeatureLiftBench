# FeatureLift Task: RevisionMap graph, branch labels, and head resolution

Status: materialized_candidate.

Official upstream repo: `https://github.com/sqlalchemy/alembic.git`

Exact commit: `c88fa5afaf2b9783a58a918f3fc73abc44daa0a9`

License: `MIT`

## Feature Specification

Implement a small standalone revision graph package that preserves the core Alembic `Revision` and `RevisionMap` semantics needed for dependency-aware migration graph resolution.

The implementation must build a revision map from explicit `Revision` objects, calculate bases and heads, resolve branch labels, track dependency revisions separately from versioned down-revision edges, and raise explicit errors for missing revisions, multiple heads, and cycles.

## Expected Output Package/API

The submitted package must expose `featurelifted` with:

- `Revision(revision, down_revision=None, branch_labels=None, dependencies=None)`
- `RevisionMap(revisions)`
- `RevisionMap.heads`
- `RevisionMap.bases`
- `RevisionMap.branch_labels`
- `RevisionMap.get_revision(identifier)`
- `RevisionMap.get_revisions(identifiers)`
- `RevisionMap.get_heads()`
- `RevisionMap.get_current_head(branch_label=None)`
- `RevisionMap.ancestors(revision_id, include_dependencies=True)`
- `RevisionMap.iterate_revisions(upper, lower=None)`
- `MissingRevision`
- `MultipleHeads`
- `CycleDetected`

## Constraints

- Do not import `alembic` or `sqlalchemy`.
- Do not read from `repo/`, `alembic/`, or any source checkout path at runtime.
- Do not use network, database, browser, Redis, or other external services.
- Keep the implementation self-contained in the output package.

## Public Test Intent

Public tests cover linear graph construction, merge-head calculation, branch-label resolution, and basic topological traversal from an upper revision toward a lower revision.

## Hidden Test Intent

Hidden tests cover multiple-head rejection, branch-label propagation to descendants, dependency-aware ancestry, missing revision errors, cycle detection, and symbolic `head` / `base` resolution.

<!-- featureliftbench:behavior-clauses:start -->
## Public Behavior Contract

The stable clause IDs below define the public behavior contract. Hidden tests may exercise
these clauses but do not introduce additional requirements.

- **B001** — Revision object normalization
- **B002** — RevisionMap graph construction
- **B003** — versioned head and base calculation
- **B004** — branch label resolution and propagation
- **B005** — dependency-aware ancestry
- **B006** — symbolic head/base lookup
- **B007** — missing revision, multiple head, and cycle errors
- **B008** — the declared target API remains importable and preserves upstream-observable semantics within the included and excluded feature scope
- **B009** — the submitted package does not import forbidden upstream packages: alembic, sqlalchemy
<!-- featureliftbench:behavior-clauses:end -->
