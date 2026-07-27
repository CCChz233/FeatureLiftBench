# Go Design Principles

## Scope

This document defines Go-specific design principles for the Go language split of FeatureLiftBench. It does not create a separate benchmark. Go shares the core FeatureLift task definition, RQs, evaluator philosophy, and compactness goals.

## What Makes a Good Go FeatureLift Task

Good Go tasks should stress type closure:

- The extracted package must include all required structs, interfaces, methods, constants, errors, and helper functions.
- Missing dependencies should produce meaningful compile-time failures or hidden behavior failures.
- The closure should include behavior, not just a set of files.

Good Go tasks should stress package boundaries:

- The source repository should contain internal packages, package-level state, or cross-package helpers that require careful boundary decisions.
- The agent should need to rewrite imports and package names without relying on the original module path.
- A good solution should expose a clean `featurelifted` package.

Good Go tasks should stress `go.mod` correctness:

- The submission must be a standalone Go module.
- It must not `require` or `replace` the original module path.
- Third-party dependencies must be explicit, bounded, and allowed by the task.

Good Go tasks should stress interface dependency:

- Hidden tests should cover interface conformance, method sets, pointer/value receivers, error interfaces, and behavior behind exported functions.
- The task should force agents to preserve type relationships, not only function outputs.

Good Go tasks should use compile-time errors as a diagnostic signal:

- Undefined identifiers suggest dependency closure failure.
- Import cycles suggest poor package boundary rewriting.
- Unused imports suggest mechanical copying without integration.
- Module resolution errors suggest `go.mod` or forbidden module issues.

## Preferred Feature Types

- Parser or tokenizer.
- Validator.
- Serializer / deserializer.
- Config decoder.
- Rule engine or expression evaluator.
- Glob/path matcher.
- URL or version parser.
- Data structure core.
- Error wrapping or aggregation semantics.

## Avoided Task Types

- Trivial one-file helper extraction.
- Slices where oracle is just copying complete `.go` files and changing `package`.
- Tasks requiring cgo in early Go phases.
- Tasks requiring network, database, cloud service, browser, or system-level privileges.
- Full framework extraction.
- Tasks whose hidden tests add requirements not implied by the feature spec.

## Hard Boundary Rule

Go hard tasks must use a symbol or behavior boundary, not a file boundary.

Requirements:

- At least two source files should contain both target and non-target code, or the task should otherwise require symbol-level pruning.
- Oracle should require cutting, reorganizing, or rewriting code, not merely copying files.
- Copy-all should be functional but clearly less compact than the reference.
- The public contract must not reveal target filenames; benchmark public and
  hidden tests are Agent-invisible in Main.
- Hidden tests should force preservation of cross-function state, ordering, error types, reflection/tag behavior, interface contracts, or module semantics.

## Difficulty Criteria

| Dimension | Easy | Medium | Hard | Very Hard |
|---|---|---|---|---|
| Files involved | 1 | 2-3 | 4-6 | 7+ |
| Type closure | local types | exported helper types | transitive method/interface closure | reflection/generic/interface-heavy |
| Package boundary | one package | import rewrite | internal/cross-package closure | package cycles or deep module split |
| `go.mod` work | none | module name only | dependency pruning | replace/vendor/forbidden module risk |
| Behavior complexity | simple | edge cases | errors/state | reflection/global/compatibility |

## Open work

- Promote only paper-ready hard Go tasks after evidence packets prove they are not file-boundary copies.
- Update seed tasks whose metadata still describes `sample.Add`.
- Add Go-specific dynamic metrics for compile errors, module errors, and interface/type closure failures.
