# Batch-1 Benchmark Quality Rubric

**Purpose:** review Cursor/agent-generated batch-1 tasks before they are accepted as leaderboard tasks.

This document is the quality standard used after a task has been generated in `benchmark/staging/`. The execution workflow lives in [BATCH1_PLAYBOOK.md](../BATCH1_PLAYBOOK.md). This rubric answers one question:

> Is this benchmark task useful, hard, deterministic, and discriminative enough to enter `benchmark/tasks/`?

Cursor or another agent may generate the task. A separate review pass must judge it from evidence, not from confidence in the generator.

---

## Review Rule

Do not generate a large batch and review only at the end. Use this cadence:

```text
produce 3-5 staging tasks
  -> run gate reports
  -> review quality
  -> promote/redesign/drop
  -> only then produce the next 3-5
```

This keeps iteration fast while preventing a weak pattern from being copied into many tasks.

---

## Required Evidence

Every reviewed task must have:

```text
benchmark/staging/<task_id>/
benchmark/submissions/<task_id>/oracle/
benchmark/submissions/<task_id>/naive/
benchmark/submissions/<task_id>/copy_all/
docs/task_designs/<task_id>.md
experiments/batch1/<task_id>/review/gate_report.json
experiments/batch1/<task_id>/review/decision.md
```

`gate_report.json` is the source of truth for mechanical gates. `decision.md` explains the final human/agent review decision and must cite evidence paths.

---

## Immediate Rejects

Any item below means `redesign` or `drop`, never `promote`:

| Reject | Meaning |
| --- | --- |
| Weak source repo | repo is obscure/toy, too small, unpinnable, license unclear, or has no credible standalone reuse slice |
| Overused source repo | batch-1 already has 2 tasks from this repo and the new task lacks a strong exception |
| No oracle | `benchmark/submissions/<task_id>/oracle/` missing or failing |
| No shallow discriminator | naive does not pass public and fail hidden |
| No copy-heavy discriminator | copy_all fails, or copy_all extraction is too close to oracle |
| Non-deterministic tests | network, wall-clock, random, platform, locale, or real tzdata dependence |
| Hidden repeats public | hidden tests mostly duplicate public happy paths |
| Thin toy task | oracle is a one-file wrapper or under the hard threshold without a strong reason |
| Unbounded scope | oracle needs most of the source package or broad excluded subsystems |
| Forbidden import/dependency | output imports original package or disallowed dependency |
| Weak Flash outcome | Flash passes with low extraction, or public-hardcoded behavior passes hidden |
| Missing evidence | no `gate_report.json`, no module probe log, or incomplete result files |

---

## Mechanical Gates

These are objective and should be generated from `gate_report.json`.

| Gate | Promote requirement |
| --- | --- |
| G0 task shape | `validate-task` and `audit_output_imports.py --fail-on-gap` pass |
| G1 oracle | public + hidden pass; `functional_gate=1.0`; `0.20 <= extraction_ratio <= 0.60`, unless a documented `low_oracle_extraction_A_tier_exception` applies |
| G2 naive | public pass; hidden fail; `functional_gate=0.0`; `extraction_ratio <= 0.10` |
| G3 copy_all | pass; `extraction_ratio >= 0.85`; `copy_all - oracle >= 0.25`, unless a documented `copy_all_metric_exception` applies |
| G4 probes | at least 3 module probes verified |
| G5 Flash | calibration label recorded; A/B/C distribution must be disclosed |
| G6 docs | design note and backlog updated |

If any G0-G4 gate fails without a documented metric exception, the task cannot be promoted.

Allowed metric exceptions:

| Exception | Meaning |
| --- | --- |
| `low_oracle_extraction_A_tier_exception` | Oracle extraction is below 0.20, but Flash is A-tier, copy_all is high, naive fails hidden, and the design note explains why the useful feature closure is naturally small rather than toy. |
| `copy_all_metric_exception` | copy_all passes and remains well separated from oracle, but extraction is below 0.85 due to LOC/source-size accounting; the decision must explain why this still tests compact extraction. |

Every exception must appear in `gate_report.json`, `decision.md`, and the acceptance report.

---

## Repository Selection Rubric

Repo quality is reviewed before task quality. A strong repo is not merely popular; it must support a useful, bounded, testable extraction.

| Repo check | Promote expectation |
| --- | --- |
| Real usage | Real Python OSS or explicitly curated legacy/vibe app; realistic downstream importer |
| Good extraction surface | At least one feature can stand alone as `featurelifted` without becoming a toy API |
| Natural entanglement | Coupling comes from parser/data model/config/resource/registry/framework behavior |
| Stable evidence | Source snapshot can be pinned; license recorded; tests can run offline and deterministically |
| Right size | Not a one-file utility; not so broad that oracle must vendor most of the repo |
| Non-duplicative | Does not repeat an existing task's source slice, API, hidden behavior, or oracle closure |

Source concentration limits:

| Scope | Limit |
| --- | --- |
| batch-1 default | 1 task per repo |
| batch-1 exception | 2 tasks per repo, only with clearly different reusable slices |
| batch-1 hard limit | 3 tasks per repo with written exception |
| full 100-task board | 5 tasks max per real OSS repo |

For same-repo exceptions, require all of:

- different output API;
- different primary entanglement or clearly different behavior family;
- low oracle overlap, preferably under 30-40% shared runtime LOC;
- different hidden tests and module probes;
- design note explicitly says why this is not duplicate coverage.

---

## Quality Scorecard

Use the scorecard only after mechanical gates pass. A task needs **80/100** for normal promote. A B-tier Flash task needs **85/100** because its functional discriminator is weaker.

| Area | Points | Objective checks |
| --- | ---: | --- |
| Reuse value | 15 | source repo and extracted package have realistic standalone users; design note answers who imports it and why |
| Boundary clarity | 15 | included/excluded behavior lists are concrete; output API covers public and hidden usage; no hidden-only surprise API |
| Hardness | 15 | oracle is 6+ runtime files or 1200+ LOC; at least two entanglement types; closure is not a thin utility |
| Test quality | 20 | public guides the main path; hidden covers combinations/errors/boundaries; tests are deterministic and offline |
| Baseline separation | 20 | oracle/naive/copy_all outcomes separate cleanly; copy_all final is much lower than oracle; probes fail for specific hidden behavior |
| Agent calibration | 10 | Flash tier is recorded; B-tier has stress-test evidence and is reported as a calibration label |
| Documentation | 5 | design note, candidate backlog, benchmark catalog, and decision.md are consistent |

Score below 80 means redesign. Score below 60 means drop unless there is a clear bounded redesign.

---

## Flash Tiers

| Tier | Meaning | Default decision |
| --- | --- | --- |
| A | Flash fails hidden after public pass, or passes only by copy-heavy low-final strategy | promote if other gates pass |
| B | Flash passes with near-oracle extraction | promote if mechanical gates pass; report as B-tier |
| C | Flash passes with low extraction, public-hardcoded behavior, or weak hidden coverage | redesign/drop |

B-tier is not a hard acceptance budget. A high B-tier share weakens the functional-discriminator story, so the paper and acceptance report must disclose the A/B/C distribution and avoid claiming that batch-1 mostly defeats Flash.

---

## Review Decision Template

`experiments/batch1/<task_id>/review/decision.md` should use this shape:

```markdown
# Review: <task_id>

Decision: promote | redesign | drop
Flash tier: A | B | C | not_run
Quality score: <n>/100

## Evidence

- gate report: experiments/batch1/<task_id>/review/gate_report.json
- oracle: experiments/batch1/<task_id>/review/oracle/result.json
- naive: experiments/batch1/<task_id>/review/naive/result.json
- copy_all: experiments/batch1/<task_id>/review/copy_all/result.json
- flash: experiments/batch1/<task_id>/review/flash/run.json

## Blocking Gates

- none

## Scorecard

| Area | Points | Notes |
| --- | ---: | --- |
| Reuse value | 0/15 | |
| Boundary clarity | 0/15 | |
| Hardness | 0/15 | |
| Test quality | 0/20 | |
| Baseline separation | 0/20 | |
| Agent calibration | 0/10 | |
| Documentation | 0/5 | |

## Required Follow-up

- none
```

---

## Cursor Workflow

Cursor can be the producer, but not the final authority.

Recommended division:

| Role | Tool | Responsibility |
| --- | --- | --- |
| Producer | Cursor | create staging task, tests, oracle/naive/copy_all, docs |
| Gate runner | script/agent | run commands and write `gate_report.json` |
| Reviewer | separate agent/thread | apply this rubric and write `decision.md` |

The reviewer should treat Cursor output as untrusted until the evidence packet passes.

---

## Promotion Rule

A task may enter `benchmark/tasks/` only when all are true:

- no immediate reject applies;
- G0-G4 pass;
- Flash tier is recorded and not C;
- quality score meets threshold;
- `decision.md` says `Decision: promote`;
- `gate_report.json` says `"decision": "promote"`.

Anything else stays in staging or is dropped.
