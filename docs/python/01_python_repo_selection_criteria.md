# Python Repository Selection Criteria

## Goal

Python repositories should support realistic, bounded, behavior-preserving feature extraction. Repo selection should happen before task generation so that the benchmark does not become a collection of convenient but weak snippets.

## Ideal Repository Properties

- 1k-30k LOC for the relevant package or module region.
- Has tests, examples, or docs that clarify expected behavior.
- Installable in a clean environment.
- No heavy external services.
- Clear reusable feature candidates.
- Moderate coupling: enough to require closure recovery, not so much that extraction becomes whole-framework vendoring.
- Acceptable license.
- Pinned commit is stable.
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

Reject repositories or slices that:

- Require database, Redis, browser, cloud service, or other heavy external systems.
- Have tests that cannot run offline.
- Have unclear feature boundaries.
- Are mostly generated code.
- Are too small or too monolithic.
- Require large binary assets or platform-specific services.
- Make hidden tests depend on network, wall-clock time, locale, or random state.
- Produce a task that is mostly greenfield reimplementation from a short prompt.

## Recommended Repo Mining Workflow

1. Collect candidate repositories from real Python OSS packages and curated legacy-style apps.
2. Filter by installation stability, license, offline behavior, and testability.
3. Identify reusable feature candidates such as parsers, validators, serializers, config loaders, or rule engines.
4. Create candidate task designs with included and excluded behavior.
5. Build public and hidden tests plus oracle, naive, and copy-all baselines when available.
6. Calibrate difficulty with strong agents.
7. Select final main split tasks based on evidence, not repository popularity alone.

## Feature Selection Checklist

- The target feature has a realistic standalone user.
- The target API can be stated without naming internal files.
- The source implementation contains both target and non-target code.
- The hidden tests can check behavior preservation without adding requirements.
- The dependency closure is recoverable within task time limits.
- The copy-all solution is clearly larger than a good extraction.

## Current Python Split Notes

Local metadata scan on 2026-07-06:

- `benchmark/tasks/`: 100 Python tasks.
- Unique source names: 75.
- Metadata difficulty: all 100 tasks marked `hard`.
- Concentrated sources include `vibe_app` with 7 tasks, `coveragepy` with 5, `jinja2` with 5, `pytest` with 4, `sqlparse` with 4, and `lark` with 3.

TODO: compute repository LOC and installation score consistently for all accepted sources.
