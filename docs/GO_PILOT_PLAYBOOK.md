# Go Pilot Playbook

**Purpose:** make the first 5 Go tasks objectively runnable before expanding to 20 or 100.
**Spec:** [GO_V2_MINI_SPEC.md](GO_V2_MINI_SPEC.md)
**Design:** [GO_FEATURELIFTBENCH_DESIGN.md](../GO_FEATURELIFTBENCH_DESIGN.md)

## 0. Operating Rule

Do not start mass-producing Go tasks until the first 5 tasks pass the full evidence loop:

```text
task shape -> oracle -> naive -> copy_all -> Docker eval -> stability -> agent calibration -> acceptance
```

The pilot is an evaluator and process validation phase. A runnable but uncalibrated task is not accepted.

## 1. Phase Plan

### Phase A: Harness Skeleton

Implement the minimum Go path without changing Python v1 behavior:

- add `metadata.language == "go"` validation;
- add Go evaluator dispatch;
- add Go local evaluator unit tests;
- add Go Docker eval image;
- add Go agent Docker image or Go-enabled agent image;
- add language grouping in suite summaries;
- keep Python `benchmark/tasks/` untouched.

Acceptance:

- existing Python tests still pass;
- a dummy Go task can be evaluated locally and in Docker;
- Docker eval uses `--network none`, resource limits, read-only mounts, and structured sandbox errors.

### Phase B: Five Pilot Tasks

Create exactly 5 pilot tasks first:

| Priority | Task id | Source | Type | Why this is in pilot |
| --- | --- | --- | --- | --- |
| P0 | `semver__constraint_core__001` | `Masterminds/semver` | parser / data model | small, stable, good first module-path test |
| P0 | `doublestar__glob_match_core__001` | `bmatcuk/doublestar` | matcher / path | hidden tests can separate shallow matching from real glob behavior |
| P0 | `mapstructure__decode_hook_core__001` | `mitchellh/mapstructure` | reflection / tags | Go-specific reflection closure |
| P0 | `singleflight__group_core__001` | `golang/sync` | concurrency | compact but real synchronization semantics |
| P0 | `go_vibe_app__pubsub_core__001` | curated | channel lifecycle | controlled concurrency task for close/cancel/leak cases |

Acceptance:

- each task has public and hidden tests;
- each task has a human design note;
- each task has oracle, naive, and copy-all submissions;
- each task has a gate report and decision file.

### Phase C: Evidence Packets

For each task, collect:

```text
evaluation/gate_report.json
evaluation/decision.md
oracle eval result
naive eval result
copy_all eval result
module/import probe result
stability result
agent calibration result
```

Acceptance:

- 5/5 oracle pass in Docker;
- 5/5 forbidden original import/module probes work;
- 5/5 copy-all pass or has a documented reason why copy-all is not meaningful;
- 5/5 naive fail hidden or forbidden gate;
- 0 undocumented gate mismatch.

### Phase D: Stability and Calibration

For every pilot task:

```bash
go test ./... -count=20 -timeout=120s
```

For race-marked tasks:

```bash
CGO_ENABLED=1 go test ./... -race -count=1 -timeout=120s
```

For agent calibration:

- run one strong agent profile once across all 5 tasks;
- assign A/B/C labels;
- keep B-tier tasks if they are useful and extraction quality remains informative;
- do not claim the pilot mostly defeats the strong agent unless the numbers support it.

## 2. Task Authoring Checklist

For each task:

- pin upstream commit and license;
- define practical reuse story;
- identify exact source entrypoints;
- define included and excluded behaviors;
- write public tests for basic API shape;
- write hidden tests for behavior closure;
- define forbidden imports and forbidden modules;
- ensure no live network, DB, service, or host-specific path;
- design oracle before writing agent prompt;
- design naive baseline to expose hidden-test value;
- design copy-all baseline to measure extraction pressure;
- run Docker eval before promoting.

## 3. Pilot Task Templates

### `semver__constraint_core__001`

Goal:

Extract semantic version parsing and constraint checking into a standalone Go package.

Expected symbols:

- `Version`
- `NewVersion`
- `Constraint`
- `NewConstraint`
- `Check`

Hidden tests should cover:

- prerelease ordering;
- build metadata handling;
- constraint ranges;
- invalid input errors;
- sorting/comparison edge cases.

Risk:

- if scope is too broad, oracle becomes copy-heavy. Keep the feature slice to parsing, comparison, and constraint evaluation.

### `doublestar__glob_match_core__001`

Goal:

Extract `**`-aware glob matching for slash-separated paths.

Expected symbols:

- `Match`
- `PathMatch`
- `ValidatePattern`

Hidden tests should cover:

- `**` across zero or more path segments;
- escaped metacharacters;
- character classes;
- invalid patterns;
- path separator normalization.

Risk:

- avoid filesystem walking in the first task. Keep this to matching semantics.

### `mapstructure__decode_hook_core__001`

Goal:

Extract map-to-struct decoding with selected decode hooks.

Expected symbols:

- `DecoderConfig`
- `Decoder`
- `NewDecoder`
- `Decode`
- selected hook helpers

Hidden tests should cover:

- struct tags;
- weak typing behavior if included;
- decode hook ordering;
- embedded structs;
- error paths with field names.

Risk:

- reflection scope can balloon. Exclude unrelated metadata, squash edge cases, or unused hook helpers unless tests require them.

### `singleflight__group_core__001`

Goal:

Extract duplicate suppression for concurrent calls with the same key.

Expected symbols:

- `Group`
- `Result`
- `Do`
- `DoChan`
- `Forget`

Hidden tests should cover:

- many concurrent callers share one execution;
- distinct keys do not block each other;
- `Forget` forces a later call to re-execute;
- panic/error behavior if included;
- no goroutine leak after `DoChan`.

Risk:

- race detector support requires cgo. Keep ordinary functional tests deterministic and make race check an extra diagnostic.

### `go_vibe_app__pubsub_core__001`

Goal:

Extract a small in-memory pub/sub broker from intentionally messy app code.

Expected symbols:

- `Broker`
- `Subscribe`
- `Publish`
- `Unsubscribe`
- `Close`

Hidden tests should cover:

- slow subscriber does not block all publishers forever;
- unsubscribe closes only the right channel;
- publish after close returns a defined error;
- concurrent subscribe/unsubscribe/publish;
- no send-on-closed-channel panic.

Risk:

- curated tasks can become artificial. The repo must include realistic surrounding clutter, not just the clean broker implementation.

## 4. Gate Report Shape

Each task should write `evaluation/gate_report.json`:

```json
{
  "task_id": "singleflight__group_core__001",
  "language": "go",
  "decision": "promote",
  "gates": {
    "shape": "pass",
    "oracle": "pass",
    "naive": "pass",
    "copy_all": "pass",
    "forbidden": "pass",
    "offline": "pass",
    "stability": "pass",
    "agent_calibration": "pass"
  },
  "metrics": {
    "oracle_extraction_ratio": 0.0,
    "copy_all_extraction_ratio": 0.0,
    "naive_hidden_pass": false,
    "stability_runs": 20
  },
  "exceptions": []
}
```

If exceptions are needed, they must be named and justified. Do not use exceptions to hide flaky tests.

## 5. Acceptance Document Shape

The pilot acceptance report should answer:

- Are all 5 tasks runnable in Docker eval?
- Are all 5 oracle submissions passing?
- Are all 5 naive baselines failing the intended gate?
- Does copy-all demonstrate extraction pressure?
- Are concurrency tests deterministic?
- Did any task require a metric exception?
- What did the first strong agent run solve, fail, or copy heavily?
- Should we expand to Go alpha 20?

Recommended decision labels:

```text
accept_go_alpha_20
hold_fix_evaluator
hold_replace_task
reject_go_track_for_now
```

## 6. Commands After Harness Exists

Go evaluator dispatch uses the existing `eval` command. The evaluator chooses Python or Go from `metadata.language`.

```bash
export PYTHONPATH=harness

python -B -m featureliftbench.cli validate-task benchmark/go_pilot/<task_id>/
python -B -m featureliftbench.cli eval \
  benchmark/go_pilot/<task_id>/ \
  benchmark/submissions/<task_id>/oracle \
  --output /tmp/flb-go-eval \
  --docker
python -B harness/scripts/verify_go_oracles.py --task-root benchmark/go_pilot
python -B harness/scripts/verify_go_module_probes.py --task-root benchmark/go_pilot --min-probes 3
python -B harness/scripts/run_go_stability.py --task-root benchmark/go_pilot --count 20
```

Do not add these commands to `run.sh` until the Go path is implemented and isolated.

Current harness smoke:

```bash
docker/build_go_eval_image.sh featureliftbench-eval-go:latest
docker/build_go_agent_image.sh featureliftbench-agent-go:latest
PYTHONPATH=harness python -B -m featureliftbench.cli eval \
  benchmark/go_pilot/go_dummy__adder_core__001 \
  benchmark/submissions/go_dummy__adder_core__001/oracle \
  --output /tmp/flb-go-dummy-eval \
  --docker
```

## 7. Stop Conditions

Stop expansion and fix the process if:

- Docker eval cannot run offline;
- any oracle only passes on the host but not in Docker;
- concurrency tests flake across 20 runs;
- forbidden module checks miss an original repo dependency;
- agent Docker requires mounting benchmark root, hidden tests, host home, or Docker socket;
- more than one pilot task needs a metric exception;
- the pilot cannot produce a clear oracle vs copy-all extraction gap.

## 8. Expansion Rule

Only expand to Go alpha 20 after:

- 5/5 pilot tasks accepted;
- Go evaluator has unit tests;
- Go Docker eval smoke tests pass;
- Go agent Docker smoke tests pass;
- pilot acceptance report is written;
- Python v1 run scripts remain unchanged for official Python experiments.

For alpha 20, keep repository selection conservative: one task per repo first, then add second tasks only after the first passes all gates.
