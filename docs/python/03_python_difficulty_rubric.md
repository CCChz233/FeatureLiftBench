# Python Difficulty Rubric

## Purpose

The Python difficulty rubric helps select, audit, and stratify tasks. It should be used for future expansion and for paper analysis. Current Python metadata marks all main tasks as `hard`, so this rubric is primarily an audit tool unless metadata is refined.

Difficulty is conditional on the benchmark input policy. Historical Core-100 and
Hard-50 used mixed snapshot sizes and Agent-visible entrypoint metadata; those
labels cannot define v3 Full-Repository / No-Hint difficulty without recalibration.

## Core Dimensions

| Dimension | Easy | Medium | Hard | Very Hard |
|---|---|---|---|---|
| Files involved | 1 | 2-3 | 4-6 | 7+ |
| Dependency depth | none | shallow | transitive | deep/dynamic |
| Behavior complexity | simple | edge cases | state/errors | dynamic/global |
| Packaging difficulty | low | moderate | high | high |
| Pruning difficulty | low | moderate | high | very high |

## Additional Python Factors

| Factor | Low difficulty | High difficulty |
|---|---|---|
| Imports | Direct imports | Lazy imports, optional imports, import-time side effects |
| State | Stateless functions | Global registries, caches, environment state |
| Data | Inline constants | Resource files, locale tables, generated data |
| API shape | One function | Classes, decorators, context objects, plugin hooks |
| Errors | Simple return values | Custom exceptions, warning behavior, exact messages |
| Hidden tests | Similar to public cases | Edge combinations, invalid inputs, compatibility quirks |

## Suggested Scorecard

Score each item 0-2:

| Item | 0 | 1 | 2 |
|---|---|---|---|
| Source spread | One localized file | A few files | Cross-module closure |
| Dynamic behavior | None | Some runtime dispatch | Dynamic imports/registries/global state |
| Edge behavior | Happy path | Common edge cases | Error/state/compatibility behavior |
| Packaging work | Direct copy | Import rewriting | Dependency pruning and package restructuring |
| Compactness challenge | Copy is already small | Some dead code | Large tempting copy-all region |

For v3, also record localization cost under No-Hint Main (repository files/LOC,
search ambiguity and number of plausible feature locations) separately from the
audited extraction footprint.

Mapping:

- 0-2: easy.
- 3-5: medium.
- 6-8: hard.
- 9-10: very hard.

## Calibration Baselines

For a task to be useful as a hard Python task:

- Oracle should pass public and hidden tests.
- Naive or shallow extraction should pass at least some public tests but fail hidden tests when possible.
- Copy-all should usually pass but receive poor compactness metrics.
- Strong agents should not trivially produce a compact passing solution.

## Review Notes

Difficulty should describe the extraction problem, not the popularity of the source repository. A famous package can yield a weak task if the feature is isolated in one file. A small curated repository can yield a strong task if dynamic behavior, hidden tests, and compactness pressure are realistic.

## Open work

- Keep complete v3 task-footprint statistics synchronized with the frozen
  reference/compactness registry.
- Add optional metadata fields for dependency depth and dynamic behavior tags.
- Reconcile current all-`hard` metadata with the scorecard if paper tables need difficulty buckets.
