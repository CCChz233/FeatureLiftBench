# Go Task Examples

> **Documentation status: reference · Last verified: 2026-08-04**

## Purpose

This document describes Go task patterns and current candidate examples without overstating current progress. As of the current inventory, Go has calibration and seed tasks but no confirmed paper-ready hard split.

## Calibration Example: Semantic Version Parser

Candidate task:

- `semver__version_parse_core__001`

Intended feature:

- Parse and compare semantic versions.

Why useful:

- Tests parser behavior, comparison semantics, and edge cases such as prerelease ordering.

Current status:

- Current planning docs classify it as `gold_verified_calibration`, not paper-ready hard.

Hardening direction:

- Increase symbol-level closure pressure without turning the task into whole-file copying.
- Add hidden tests that force preservation of type methods, errors, and comparison edge cases.

## Calibration Example: Byte Size Formatting

Candidate task:

- `humanize__bytes_format_core__001`

Intended feature:

- Format and parse SI/IEC byte strings.

Why useful:

- Tests shared constants, parser behavior, rounding, and formatting compatibility.

Current status:

- Current planning docs classify it as calibration.

Hardening direction:

- Ensure source contains tempting unrelated formatting functions.
- Confirm copy-all is functional but clearly less compact.

## Redesign Candidate: Mapstructure Decode

Candidate tasks:

- `mapstructure__decode_core__001`
- `mapstructure__decode_core_hard__001`
- `mapstructure__decode_symbol_core__002` (candidate redesign)

Intended feature:

- Decode maps into structs while preserving tags, hooks, metadata, pointer behavior, and reflection semantics.

Why useful:

- Strong Go-specific target for type closure, reflection, interface behavior, and hidden edge cases.

Current status:

- Existing decode tasks are calibration or hardening attempts.
- `mapstructure__decode_symbol_core__002` is a candidate for symbol-level redesign.

Hardening direction:

- Avoid file-boundary extraction.
- Force method/interface/type closure.
- Ensure `go.mod` does not require or replace the original module.

## Seed Placeholder Examples

Current seed placeholders include:

- `bluemonday__sanitize_policy_core__001`
- `gojsonschema__validate_core__001`
- `validator__struct_validate_core__001`
- `copier__deep_copy_core__001`
- `expr__eval_core__001`
- `doublestar__glob_match_core__001`
- `uuid__parse_format_core__001`

Important: current metadata for these tasks still describes `sample.Add`. They
are placeholders, not real Go FeatureLift task examples.

## Desired Future Example Types

- HTML sanitizer policy extraction with rule tables and parser dependencies.
- JSON schema validation subset with reference resolution and typed errors.
- Struct validator with tag parsing, interface hooks, and error aggregation.
- Expression evaluator with AST, environment binding, and typed runtime errors.
- Glob matcher with path normalization and edge-case patterns.

## Open work

- Replace placeholder tasks with real boundary plans.
- Add one paper-ready hard Go example only after gates and evidence packets pass.
- Add examples of compile-time failure modes from agent runs.
