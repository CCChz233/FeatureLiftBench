# Go Repository and Task Inventory

## Purpose

This inventory tracks the Go language split. Go is part of FeatureLiftBench, not a separate benchmark. The current state is mixed: the repository contains Go task directories, but current Go planning notes still distinguish smoke, seed, and calibration tasks from paper-ready hard tasks.

## Status Enum

- `idea`
- `candidate`
- `seed_placeholder`
- `smoke`
- `calibration`
- `paper_ready_hard`
- `redesign`
- `rejected`

## Current Metadata Snapshot

Scanned on 2026-07-26:

- `benchmark/go/tasks/`: 12 directories with `metadata.json`.
- `benchmark/go_pilot/`: 1 dummy pilot metadata file.
- Several `benchmark/go/tasks/*` entries have metadata that still describes `sample.Add`; these are treated as seed placeholders, not real hard tasks.
- Current Go backlog/planning docs list 0 hard paper-ready Go tasks.

## Repository Pool

| Repo ID | Repo | LOC | Tests | Install | Candidate Features | Score | Decision | Notes |
|---|---|---:|---|---|---|---:|---|---|
| mapstructure | https://github.com/go-viper/mapstructure | TBD | yes | go.mod | decode core, hard decode redesign, symbol-level decode candidate | TBD | calibration/redesign | Existing tasks are calibration; `mapstructure__decode_symbol_core__002` is active hard redesign candidate |
| semver | https://github.com/Masterminds/semver | TBD | yes | go.mod | version parse and compare | TBD | calibration | Verified calibration, not hard paper-ready |
| go-humanize | https://github.com/dustin/go-humanize | TBD | yes | go.mod | byte size format and parse | TBD | calibration | Verified calibration, not hard paper-ready |
| bluemonday | https://github.com/microcosm-cc/bluemonday | TBD | TBD | TODO | sanitize policy core | TBD | seed_placeholder | Metadata currently describes `sample.Add`; needs redesign |
| gojsonschema | https://github.com/xeipuuv/gojsonschema | TBD | TBD | TODO | JSON schema validation core | TBD | seed_placeholder | Metadata currently describes `sample.Add`; needs redesign |
| validator | https://github.com/go-playground/validator | TBD | TBD | TODO | struct validation core | TBD | seed_placeholder | Metadata currently describes `sample.Add`; needs redesign |
| copier | https://github.com/jinzhu/copier | TBD | TBD | TODO | deep copy core | TBD | seed_placeholder | Metadata currently describes `sample.Add`; needs redesign |
| expr | https://github.com/expr-lang/expr | TBD | TBD | TODO | expression eval core | TBD | seed_placeholder | Metadata currently describes `sample.Add`; needs redesign |
| doublestar | https://github.com/bmatcuk/doublestar | TBD | TBD | TODO | glob match core | TBD | seed_placeholder | Metadata currently describes `sample.Add`; needs redesign |
| google/uuid | https://github.com/google/uuid | TBD | TBD | TODO | UUID parse/format core | TBD | seed_placeholder | Metadata currently describes `sample.Add`; needs redesign |

## Task Inventory

| Task ID | Repo | Commit | Feature | Type | Difficulty | Ref LOC | Files | Status | Notes |
|---|---|---|---|---|---|---:|---:|---|---|
| hello_featurelifted__001 | hello-sample | 000000000000 | Integer addition | implicit_dependency_coupling | easy | TBD | TBD | smoke | Harness smoke only |
| go_dummy__adder_core__001 | go-dummy-adder | TBD | integer adder | TBD | easy | TBD | TBD | smoke | Located under `benchmark/go_pilot/` |
| humanize__bytes_format_core__001 | go-humanize | v1.0.1 | Byte size format and parse | data_model_coupling, parser_state_coupling | medium | TBD | TBD | calibration | Current docs mark as `gold_verified_calibration`; not hard paper-ready |
| mapstructure__decode_core__001 | mapstructure | v2.2.1 | Map to struct decode | reflection_coupling, implicit_dependency_coupling | medium | TBD | TBD | calibration | Current docs mark as `gold_verified_calibration`; not hard paper-ready |
| mapstructure__decode_core_hard__001 | mapstructure | v2.2.1-hard-slice | Map to struct decode hard slice | reflection_coupling, data_model_coupling, global_state_registry_coupling | medium | TBD | TBD | calibration | Hardening attempt still classified as calibration |
| mapstructure__decode_symbol_core__002 | mapstructure | TODO | symbol-level decode core redesign | type closure, reflection, metadata | TODO | TBD | TBD | candidate | In backlog/design notes, not present as benchmark task metadata |
| semver__version_parse_core__001 | semver | v3.2.1 | Semantic version parse and compare | parser_state_coupling, data_model_coupling | medium | TBD | TBD | calibration | Current docs mark as `gold_verified_calibration`; not hard paper-ready |
| bluemonday__sanitize_policy_core__001 | bluemonday | v1.0.26 | sanitize policy core | implicit_dependency_coupling | hard | TBD | TBD | seed_placeholder | Metadata currently says `sample.Add`; must be redesigned before use |
| copier__deep_copy_core__001 | copier | v0.4.0 | deep copy core | implicit_dependency_coupling | hard | TBD | TBD | seed_placeholder | Metadata currently says `sample.Add`; must be redesigned before use |
| doublestar__glob_match_core__001 | doublestar | v4.6.1 | glob match core | implicit_dependency_coupling | hard | TBD | TBD | seed_placeholder | Metadata currently says `sample.Add`; must be redesigned before use |
| expr__eval_core__001 | expr | v1.16.9 | eval core | implicit_dependency_coupling | hard | TBD | TBD | seed_placeholder | Metadata currently says `sample.Add`; must be redesigned before use |
| gojsonschema__validate_core__001 | gojsonschema | v1.2.0 | validate core | implicit_dependency_coupling | hard | TBD | TBD | seed_placeholder | Metadata currently says `sample.Add`; must be redesigned before use |
| uuid__parse_format_core__001 | google/uuid | v1.6.0 | UUID parse/format core | implicit_dependency_coupling | hard | TBD | TBD | seed_placeholder | Metadata currently says `sample.Add`; must be redesigned before use |
| validator__struct_validate_core__001 | validator | v10.19.0 | struct validate core | implicit_dependency_coupling | hard | TBD | TBD | seed_placeholder | Metadata currently says `sample.Add`; must be redesigned before use |

## Open work

- Decide whether seed placeholders belong in `benchmark/go/tasks/` or should move to staging/calibration.
- Replace placeholder `sample.Add` metadata before any task is considered a real Go FeatureLift task.
- Add `Ref LOC`, source file counts, and evidence paths after oracle/copy-all/naive gates run.
- Promote only tasks with `paper_ready_hard` evidence into the Go hard split.
