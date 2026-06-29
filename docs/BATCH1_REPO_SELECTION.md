# Batch-1 Repository Selection

**Purpose:** keep the selected repository pool separate from per-task implementation status.

Batch-1 should be repo-first, not task-first:

```text
select strong repos
  -> choose one reusable feature slice per repo
  -> build staging task
  -> review with BATCH1_QUALITY_RUBRIC
```

The candidate backlog tracks task ideas. This file tracks whether the **repository itself** is worth spending benchmark budget on.

This is the source of truth for repo-level decisions:

- `benchmark/tasks/*/metadata.json` is the source of truth for accepted formal tasks;
- this file is the source of truth for accepted repo concentration and future repo-pool planning;
- `docs/candidate_backlog.md` is the source of truth for task ideas after a repo passes the repo gate.

---

## Target Counts

Final target:

| Scope | Target |
| --- | ---: |
| Main board | 100 tasks |
| Batch-0 frozen | 50 tasks |
| Batch-1 new tasks | 50 tasks |
| Batch-1 unique repos | **45-50** preferred |
| Batch-1 minimum unique repos | **45** |
| Full-board unique sources | **75+** preferred |

Planning target:

| Need | Repo pool size |
| --- | ---: |
| Build 50 accepted batch-1 tasks from scratch | 60 repo candidates |
| Current remaining 19 accepted tasks | 25 repo candidates |

Rationale: some repos will fail oracle, determinism, hidden-test, or Flash calibration gates. Keep roughly 20-25% spare candidates so agents can drop weak repos quickly without stalling.

---

## Concentration Limits

| Scope | Limit |
| --- | --- |
| Batch-1 default | 1 task per repo |
| Batch-1 exception | 2 tasks per repo, only for clearly different reusable slices |
| Batch-1 hard cap | 3 tasks per repo with written exception |
| Full 100-task board | 5 tasks max per real OSS repo |

Same-repo exceptions must have:

- different output APIs;
- different behavior families;
- different primary entanglement or a strong written reason;
- low oracle overlap, preferably under 30-40% shared runtime LOC;
- different hidden tests and module probes.

---

## Current State

Snapshot from `benchmark/tasks/*/metadata.json`:

| Metric | Current |
| --- | ---: |
| Main-board tasks | 100 |
| Batch-0 tasks | 50 |
| Batch-1 tasks | 50 |
| Full-board unique sources | 75 |
| Remaining batch-1 tasks to 100 | 0 |

Batch-specific repo counts are not derived from `metadata.json`; use [benchmark_tasks.md](benchmark_tasks.md) for the current live catalog and source distribution.

Interpretation:

- The current batch-1 repo distribution is healthy: 31 tasks from 30 repos.
- The repo pool is **not complete**: choose roughly 25 more repo candidates to safely produce the remaining 19 accepted tasks.
- Existing docs are not fully synchronized; use `benchmark/tasks/*/metadata.json` as the source of truth for current accepted tasks.

---

## Current Batch-1 Repos

| Repo | Accepted tasks | Notes |
| --- | ---: | --- |
| bidict | 1 | bidirectional map |
| boltons | 1 | iterutils |
| cachetools | 1 | cache eviction |
| cattrs | 1 | structuring |
| cerberus | 1 | schema validation |
| configobj | 1 | round-trip config |
| croniter | 1 | cron parsing |
| dataclasses-json | 1 | dataclass serde |
| email-validator | 1 | email validation |
| environs | 1 | typed env parsing |
| httpx | 1 | request model |
| intervaltree | 1 | interval tree |
| jsonpath-ng | 1 | JSONPath evaluator |
| jsonpointer | 1 | JSON Pointer resolve/set |
| mako | 1 | lexer/expression parsing |
| msgpack-python | 1 | pack/unpack |
| pathvalidate | 1 | path sanitization |
| pendulum | 1 | datetime parse/format |
| pydantic | 1 | validation error core |
| python-dateutil | 2 | rrule + relativedelta; valid same-repo exception |
| python-dotenv | 1 | env parser |
| python-frontmatter | 1 | front matter round-trip |
| python-multipart | 1 | multipart parser |
| sortedcontainers | 1 | sorted list |
| tabulate | 1 | table formatting |
| urllib3 | 1 | retry/backoff |
| voluptuous | 1 | schema validation |
| websockets | 1 | handshake parser |
| xmltodict | 1 | XML parse |
| yarl | 1 | URL model |

---

## Not-Yet-Accepted Repo Pool

Status: not filled yet. Before the next Cursor/agent generation batch, choose at least **25** repo candidates here. A repo can move into `candidate_backlog.md` only after it passes the repo gate.

| Repo | Status | Candidate feature slice | Why useful | Hardness / testability risk | Decision note |
| --- | --- | --- | --- | --- | --- |
| TBD | `candidate` | TBD | TBD | TBD | Fill during repo-selection pass |

---

## Repo Pool Status Values

Use these statuses in this file and mirror task-level status in [candidate_backlog.md](candidate_backlog.md):

| Status | Meaning |
| --- | --- |
| `candidate` | repo looks plausible but no feature slice approved |
| `selected` | repo passed repo gate; one feature slice should be designed |
| `staging` | task exists in `benchmark/staging/` |
| `accepted` | at least one task is in `benchmark/tasks/` |
| `backup` | good repo, lower priority or riskier |
| `rejected` | repo failed repo-level gate |

---

## Next Selection Rule

For the remaining batch-1 work:

1. Maintain a repo pool of at least 25 not-yet-accepted candidates.
2. Prefer new repos over second tasks from an existing repo.
3. Pick repos with clear standalone module value first: parsers, validators, config loaders, schedulers, serializers, data structures.
4. Reject repos that only produce thin wrappers, network-dependent behavior, or tiny single-file utilities.
5. Every 5 generated tasks, re-count repo concentration before selecting the next batch.

Do not let Cursor invent repo choices ad hoc without updating this file.
