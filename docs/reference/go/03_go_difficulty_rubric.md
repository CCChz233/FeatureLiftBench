# Go Difficulty Rubric

> **Documentation status: reference · Last verified: 2026-08-04**

## Purpose

The Go difficulty rubric is used to distinguish smoke, calibration, and paper-ready hard tasks. It focuses on type closure, package boundaries, `go.mod`, interface dependency, and compile-time failure modes.

## Core Dimensions

| Dimension | Easy | Medium | Hard | Very Hard |
|---|---|---|---|---|
| Files involved | 1 | 2-3 | 4-6 | 7+ |
| Type closure | local concrete types | exported helper types | transitive methods/interfaces/errors | reflection/generics/deep interface closure |
| Package boundary | single package | import rewrite only | internal/cross-package closure | multiple package reshaping or cycle risk |
| Module work | trivial `go.mod` | module name and one dependency | dependency pruning | forbidden module, replace, or vendor risk |
| Behavior complexity | simple pure function | edge cases | state/errors/interfaces | reflection/global compatibility |
| Pruning difficulty | low | moderate | high | very high |

## Compile-Time Diagnostics

Compile-time failures should be mapped to failure taxonomy labels:

| Compile symptom | Likely failure |
|---|---|
| `undefined: X` | Dependency closure failure |
| `cannot use T as I` | Interface dependency failure |
| `import cycle not allowed` | Package boundary failure |
| `module ... not found` | `go.mod` or dependency failure |
| `forbidden module required` | Forbidden import/module failure |
| `declared and not used` | Mechanical copy/edit failure |

## Scorecard

Score each item 0-2:

| Item | 0 | 1 | 2 |
|---|---|---|---|
| Type closure | none | helper structs/errors | methods, interfaces, reflection, or generics |
| Package closure | one package | simple import rewrite | internal/cross-package restructuring |
| Module independence | no dependencies | simple `go.mod` | dependency pruning and forbidden module risk |
| Behavior depth | happy path | edge cases | hidden interface/error/state behavior |
| Compactness pressure | target isolated | some unrelated code | copy-all tempting but low-quality |

Mapping:

- 0-2: easy.
- 3-5: medium.
- 6-8: hard.
- 9-10: very hard.

## Paper-Ready Hard Requirements

A Go task should be counted as paper-ready hard only if:

- It is not a smoke or placeholder task.
- Oracle passes public and hidden tests.
- Naive baseline exposes hidden-test discrimination when possible.
- Copy-all baseline passes but has much worse reference-relative compactness
  than the reference.
- Public tests do not reveal source filenames.
- Hidden tests exercise type, interface, package, error, reflection, or module behavior.
- A strong agent does not trivially solve it by copying complete files and changing `package`.

## Open work

- Add automated classification of compile-time failures into taxonomy labels.
- Add Go module closure metrics from `go list`.
- Re-score existing Go calibration tasks with this rubric.
