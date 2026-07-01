# Go v2 Mini Spec

**Status:** draft for pilot implementation
**Scope:** Go feature-lifting pilot, not yet part of the Python v1 main leaderboard
**Parent design:** [GO_FEATURELIFTBENCH_DESIGN.md](../GO_FEATURELIFTBENCH_DESIGN.md)

This document turns the Go roadmap into an implementation contract. It should be treated as the minimum spec for the first 5 Go pilot tasks.

## 1. Goal

Go v2 measures the same thing as Python v1:

> Can an agent extract an entangled feature from a pinned repository snapshot into a standalone, reusable package that passes automated public and hidden tests?

Go adds language-specific requirements:

- standalone Go module output;
- stable import path for tests;
- offline `go test`;
- forbidden original module/import checks;
- optional deterministic concurrency, stress, and race checks.

The pilot is successful only if evaluator, Docker, oracle, naive, copy-all, and agent calibration all work end to end.

## 2. Non-goals

Do not use the pilot to:

- create 100 Go tasks before the evaluator is proven;
- benchmark Go bug fixing or repository patching;
- depend on live services, network downloads, host Go cache, or external databases;
- include flaky concurrency tests that pass or fail based on host load;
- require agents to reproduce full upstream packages.

## 3. Pilot Directory

During pilot, keep Go tasks outside the Python main board:

```text
benchmark/go_pilot/<task_id>/
  metadata.json
  repo/
  public_tests/
    *_test.go
  hidden_tests/
    *_test.go
  evaluation/
    forbidden_imports.txt
    forbidden_modules.txt
    allowed_modules.txt
    go_deps.lock.json    # optional; only when external modules are allowed
    oracle_manifest.json
```

After the Go evaluator is stable, tasks can be migrated into a unified task catalog. Until then, `benchmark/tasks/` remains Python-only.

## 4. Agent Workspace

`run-agent` should materialize a redacted Go workspace:

```text
workspace/
  repo/
  public_tests/
  metadata.json
  TASK.md
  submission/
```

Hidden tests, oracle files, gate reports, and benchmark root metadata must not be exposed to the agent workspace.

## 5. Submission Contract

The agent must write:

```text
submission/
  go.mod
  featurelifted/
    *.go
```

The module path is fixed per task:

```text
module featurelifted.local/<task_id>
```

Tests import the extracted package as:

```go
import flb "featurelifted.local/<task_id>/featurelifted"
```

Rules:

- `go.mod` is required.
- package name under `submission/featurelifted/` should be `featurelifted`.
- no imports from the original repository module path;
- no `require` on the original repository module;
- no `replace` to the original repository, host paths, workspace paths, or hidden paths;
- no `go.work`;
- no network access during evaluation;
- no generated code unless the task explicitly allows it.

The evaluator may normalize `go.mod` in a runtime copy, but it must not mutate the mounted submission directory.

## 6. Test Injection

Public and hidden tests should use `package featurelifted_test` and import the stable output path:

```go
package featurelifted_test

import flb "featurelifted.local/<task_id>/featurelifted"
```

Evaluator flow:

1. Copy `submission/` to a runtime temp directory.
2. Validate `go.mod`, imports, `require`, `replace`, `go.work`, vendor metadata, and symlinks.
3. Copy public tests and hidden tests into the runtime module.
4. Run offline `go test`.
5. Run optional stress/race commands for marked tasks.
6. Compute Go LOC and scoring fields.
7. Write structured `result.json`.

Recommended runtime test layout:

```text
runtime/
  go.mod
  featurelifted/
    *.go
  featurelifted_public_test.go
  featurelifted_hidden_test.go
```

## 7. Go Environment

Default functional evaluation:

```bash
GOWORK=off
GOPROXY=off
GONOSUMDB=*
GOFLAGS=-mod=mod
CGO_ENABLED=0
GOMAXPROCS=2
go test ./... -count=1 -timeout=30s
```

For pilot tasks, prefer no external dependencies. If a task truly needs dependencies:

- list them in `evaluation/allowed_modules.txt`;
- pin them in `evaluation/go_deps.lock.json` or a checked-in vendor snapshot;
- preinstall or vendor them in the eval image;
- still run eval with `GOPROXY=off`;
- do not mount host Go cache.

## 8. Concurrency Checks

Concurrency tasks must have deterministic tests. Avoid long sleeps and timing-sensitive expectations.

Default concurrency test tools:

- `context.WithCancel` and `context.WithTimeout`;
- channels with explicit barriers;
- `sync.WaitGroup`;
- fake clock or injected clock when time matters;
- bounded goroutine counts.

Optional stress check:

```bash
GOWORK=off GOPROXY=off GOMAXPROCS=2 \
go test ./... -run '<StressPattern>' -count=20 -timeout=120s
```

Optional race check:

```bash
GOWORK=off GOPROXY=off CGO_ENABLED=1 GOMAXPROCS=2 \
go test ./... -race -count=1 -timeout=120s
```

Race checks are allowed only for tasks marked with:

```json
{
  "concurrency": {
    "enabled": true,
    "race_test": true
  }
}
```

Because Go race detection usually needs cgo and a fuller toolchain, race failures must be reported separately from ordinary functional hidden-test failures.

## 9. Docker Contract

Go eval must run in Docker for official results.

Default eval container:

```text
network: none
memory: 8g
memory-swap: 8g
cpus: 2
pids-limit: 512
root filesystem: read-only
/tmp: tmpfs, size=4g
mounts:
  task: ro
  submission: ro
  harness: ro
  output: rw
```

Agent Docker for Go must include the Go toolchain so the agent can run public tests, but it still must not mount hidden tests, benchmark root, `.env`, host home, SSH keys, Docker socket, or host Go cache.

## 10. Forbidden Checks

Static checks:

- parse all `.go` imports;
- parse `go.mod` `module`, `require`, and `replace`;
- reject `go.work`;
- reject vendor metadata that references forbidden modules;
- reject symlinks escaping runtime submission root.

Resolved checks:

```bash
GOWORK=off GOPROXY=off go list -deps -json ./...
```

The evaluator should inspect resolved import paths and module paths for forbidden original repository references.

## 11. Scoring

Functional gate:

```text
FunctionalGate =
  BuildPass
  AND TestPass
  AND ForbiddenImportPass
  AND ForbiddenModulePass
  AND OfflineDependencyPass
```

Extraction ratio:

```text
ExtractionRatio = SubmissionGoLOC / SourceRepoGoLOC
```

Final score:

```text
FinalScore = FunctionalGate * max(0, 1 - ExtractionRatio)
```

LOC rules:

- count `.go` files only;
- exclude `_test.go`;
- exclude `vendor/`;
- exclude generated files only when the file has a standard generated-code header;
- source denominator comes from pinned `repo/`;
- submission numerator comes from runtime `featurelifted/`.

## 12. Result Fields

Go `result.json` should include the Python-compatible top-level fields plus Go diagnostics:

```json
{
  "passed": false,
  "build_pass": false,
  "test_pass": false,
  "original_import_pass": false,
  "forbidden_module_pass": false,
  "offline_dependency_pass": false,
  "race_pass": null,
  "stress_pass": null,
  "functional_gate": 0,
  "extraction_ratio": 0.0,
  "final_score": 0.0,
  "go": {
    "version": "go1.22.x",
    "module_path": "featurelifted.local/<task_id>",
    "source_go_loc": 0,
    "submission_go_loc": 0,
    "forbidden_imports": [],
    "forbidden_modules": [],
    "resolved_modules": []
  },
  "sandbox": {
    "backend": "docker",
    "resource_limited": false,
    "timed_out": false,
    "log_limit_exceeded": false
  }
}
```

## 13. Metadata Additions

Minimum Go metadata fields:

```json
{
  "task_id": "singleflight__group_core__001",
  "language": "go",
  "source": {
    "name": "golang/sync",
    "url": "https://github.com/golang/sync",
    "commit": "<pinned>",
    "license": "BSD-3-Clause",
    "module_path": "golang.org/x/sync"
  },
  "output": {
    "module": "featurelifted.local/singleflight__group_core__001",
    "package": "featurelifted",
    "import": "featurelifted.local/singleflight__group_core__001/featurelifted",
    "symbols": ["Group", "Result"]
  },
  "environment": {
    "go": "1.22",
    "network": false,
    "timeout_seconds": 30,
    "allowed_modules": [],
    "forbidden_modules": ["golang.org/x/sync"],
    "forbidden_imports": ["golang.org/x/sync"]
  },
  "concurrency": {
    "enabled": true,
    "race_test": false,
    "stress_count": 20,
    "timeout_seconds": 120
  }
}
```

## 14. Pilot Acceptance Gates

Each pilot task must pass:

| Gate | Requirement |
| --- | --- |
| G0 shape | metadata/layout validate successfully |
| G1 oracle | oracle passes Docker Go eval |
| G2 naive | naive baseline fails hidden or forbidden gate |
| G3 copy-all | copy-all passes but has clearly higher extraction ratio than oracle |
| G4 forbidden | original repo import/module is rejected |
| G5 offline | oracle passes with `--network none` and `GOPROXY=off` |
| G6 stability | 20 repeated evals pass; concurrency tasks also pass stress/race if marked |
| G7 calibration | at least one strong agent run produces A/B/C label and failure notes |

Do not promote a Go task if any gate is missing. If a metric exception is needed, document it in the task decision file and cap exceptions at pilot review time.

## 15. Implementation Order

1. Add Go task schema support without changing Python task semantics.
2. Add Go evaluator and local unit tests.
3. Add Go eval Docker image and smoke tests.
4. Add Go agent Docker image or extend agent image with Go toolchain.
5. Build the 5 pilot tasks.
6. Generate oracle, naive, copy-all evidence.
7. Run Docker stability and strong-agent calibration.
8. Decide whether to expand to Go alpha 20.
