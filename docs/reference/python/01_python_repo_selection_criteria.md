# Python Repository Selection Criteria

> **Documentation status: reference · Last verified: 2026-08-04**

## Goal

Python repositories should support realistic, bounded, behavior-preserving feature
extraction. Repo selection must happen before model runs and Main must expose the
complete pinned source tree; target-aware file pruning is not an admissible way to
make a repository convenient.

## Ideal Repository Properties

- Repository size remains tractable for the fixed agent budget and offline workspace.
- Has tests, examples, or docs that clarify expected behavior.
- Installable in a clean environment.
- No heavy external services.
- Clear reusable feature candidates.
- Moderate coupling: enough to require closure recovery, not so much that extraction becomes whole-framework vendoring.
- Acceptable license.
- Pinned commit is stable.
- Canonical URL, immutable revision, archive SHA-256 and license are auditable.
- Feature behavior can be tested offline and deterministically.
- Source has enough unrelated code to make compactness meaningful.

## Repository Scoring Rubric

| Criterion | Score |
|---|---:|
| Installation stability | 0-2 |
| Test availability | 0-2 |
| Clear feature modules | 0-2 |
| Moderate dependency complexity | 0-2 |
| Hidden-test design feasibility | 0-2 |

Interpretation:

- 8-10: high priority.
- 6-7: candidate.
- 4-5: use only if feature is excellent.
- 0-3: reject.

## Exclusion Rules

Reject repositories that:

- Require database, Redis, browser, cloud service, or other heavy external systems.
- Have tests that cannot run offline.
- Have unclear feature boundaries.
- Are mostly generated code.
- Are too small or too monolithic.
- Cannot be redistributed or deterministically materialized as a complete pinned
  source archive under a uniform, non-target-aware exclusion policy.
- Require large binary assets or platform-specific services.
- Make hidden tests depend on network, wall-clock time, locale, or random state.
- Produce a task that is mostly greenfield reimplementation from a short prompt.

## Recommended Repo Mining Workflow

1. Collect candidate repositories from a fixed real-Python-OSS package snapshot;
   curated legacy-style apps may enter only a separate Curated split.
2. Filter by installation stability, license, offline behavior, and testability.
3. Identify reusable feature candidates such as parsers, validators, serializers, config loaders, or rule engines.
4. Create candidate task designs with included and excluded behavior.
5. Build public and hidden tests plus oracle, naive, and copy-all baselines when available.
6. Calibrate difficulty with strong agents.
7. Select final main split tasks based on evidence, not repository popularity alone.
8. Freeze the canonical source registry before formal model runs; record all
   candidate exclusions and post-selection failures.

## Feature Selection Checklist

- The target feature has a realistic standalone user.
- The target API can be stated without naming internal files.
- The source implementation contains both target and non-target code.
- The hidden tests can check behavior preservation without adding requirements.
- The dependency closure is recoverable within task time limits.
- The copy-all solution is clearly larger than a good extraction.
- The feature remains localizable from the functional contract without source
  entrypoints, file paths or symbol hints.

## Current Python Split Notes

Registry/task scan on 2026-07-27:

- `benchmark/tasks/`: 150 Python tasks.
- 126 external OSS repositories，132 immutable snapshots；Main 中 0 curated。
- Metadata difficulty: all 150 tasks marked `hard`.
- Concentrated sources include `jinja2`, `pytest`, and `coveragepy` with 5 tasks
  each, `sqlparse` with 4, and `lark`, `pluggy`, and canonical `dateutil` with 3.
- The former 7 `vibe_app` tasks are isolated under `benchmark/curated/tasks/`;
  they are not part of the External-150 headline.
- Smoke tasks: 3 in `benchmark/sanity/` (not counted in main split).

Full source materialization、No-Hint 和 source-size audit 已完成。7 个
replacement 的 21-candidate ledger 已冻结；论文仍需如实描述原有 143 题的
历史选择过程，并可补 popular-vs-long-tail 敏感性分析。
