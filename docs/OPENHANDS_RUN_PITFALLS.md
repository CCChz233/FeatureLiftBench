# OpenHands Pitfalls

This file is a condensed record of server issues already encountered while integrating OpenHands. It is not the runbook. Use [OPENHANDS_SERVER_RUNBOOK.md](OPENHANDS_SERVER_RUNBOOK.md) for current commands.

## Fixed In Code

| Issue | Fix |
| --- | --- |
| OpenHands stdout could grow without bound | Wrapper streams output with `FEATURELIFTBENCH_COMMAND_OUTPUT_LIMIT_BYTES` and kills the process group on overflow |
| JSON events mixed with terminal text | Wrapper writes JSON events to `agent/openhands_events.jsonl` and non-JSON text to stdout log |
| Usage parsing loaded large logs at once | Usage parser streams line by line |
| Bad `pyproject.toml` could turn into slow install failures | Evaluator prefers direct `PYTHONPATH` import of `submission/featurelifted` |
| `.env` leaked unrelated provider keys into agent Docker | Agent config forwards only selected profile key/base plus safe harness variables |
| Pilot5 script stopped after 3 sanity tasks when one benchmark failed | Script now continues on benchmark failure and only aborts on infrastructure exits `>=2` |
| Suite summary could not separate model failure from infra failure | `failure_class` added to compact entries and summary |
| OpenHands context evidence was unavailable from JSONL alone | Local OpenAI-compatible proxy records provider usage and context audit |
| Context window was hardcoded to 128k | Profiles can set `context_window_tokens` and `reserved_output_tokens` |
| Step cap did not recognize current OpenHands action events | Detector now counts `source="agent"` with `action={...}` |
| DeepSeek preflight health check sent `deepseek/deepseek-v4-flash` | Preflight uses `normalize_api_model_name` for the probe; profile model unchanged for OpenHands |
| Eval failed on tasks with `allowed_dependencies` but empty lock | `sync_task_locks.py` + `audit_task_dependencies.py`; dual-arch wheels in repo; eval image preinstalls `benchmark_requirements.lock` |
| Resume could merge dirty runs (`passed` with `api_calls=0`) | `validate_suite_resume.py` blocks resume; `run_openhands.sh` calls it automatically |
| 100-task runs hit 429 without suite-level spacing | `FEATURELIFTBENCH_SUITE_TASK_COOLDOWN_SECONDS` (default 0; recommend 15 for main suite) |
| No single infra acceptance report | `summarize_suite_infra.py` writes `infra-summary.json` with `infra_clean` |

## Common Server Failures

| Symptom | Likely Cause | Response |
| --- | --- | --- |
| `api_calls == 0` | Bad key, bad model name, profile/env mismatch, OpenHands startup failure | Run preflight with `--llm-health-check --strict`; inspect `agent/stderr.log` |
| `rate_limited` | Provider RPM/TPM/quota | Use `NUM_WORKERS=1`, lower retry pressure, or switch quota/key |
| `docker_sandbox_error=true` | Eval container OOM/timeout/Docker failure | Treat separately from model quality; inspect `eval/result.json` |
| `missing_submission` with nonzero calls | Model/tool loop failed to produce `submission/featurelifted` | Model failure unless logs show infra errors |
| `log_limit_exceeded` | OpenHands produced excessive text/events | Keep failure class; optionally raise output limit for debugging |
| `usage_unverified=true` | Provider did not return usage or proxy disabled | Mark as pilot only |
| local vLLM works on host but not in Docker | Docker bridge cannot reach host loopback | Set `FEATURELIFTBENCH_AGENT_DOCKER_NETWORK=host` |

## Pilot5 Interpretation

Pilot5 must contain all 5 tasks. If only `sanity3/` exists and `batch2/` is empty, the run is incomplete. This was caused by an old `set -e` behavior in `run_openhands_pilot5.sh`; rerun with the fixed script.

Infrastructure-clean pilot5 means:

- `total == 5`
- `agent_failures == 0`
- `docker_sandbox_failures == 0`
- `log_limit_failures == 0`
- no `agent_setup_failed`
- no `eval_infra_failed`

`model_failed` is acceptable in pilot. It means the benchmark found an actual task failure.

## Resource Starting Point

```bash
export FEATURELIFTBENCH_AGENT_DOCKER_MEMORY=8g
export FEATURELIFTBENCH_AGENT_DOCKER_CPUS=2
export FEATURELIFTBENCH_AGENT_DOCKER_PIDS=512
export FEATURELIFTBENCH_DOCKER_EVAL_TIMEOUT_SECONDS=600
export FEATURELIFTBENCH_COMMAND_OUTPUT_LIMIT_BYTES=8388608
export FEATURELIFTBENCH_OPENHANDS_MAX_STEPS=180
export FEATURELIFTBENCH_SUITE_TASK_COOLDOWN_SECONDS=15
export RETRY_RATE_LIMIT=5
```

Start with `NUM_WORKERS=1`. Use 120 steps for pilot5; use **180** for the main 100-task suite.

## Current Open Questions

- Whether `FEATURELIFTBENCH_SUITE_TASK_COOLDOWN_SECONDS=15` is sufficient for your provider TPM window on hard tasks.
- Whether OpenHands tool surface should be restricted further for FeatureLiftBench tasks.
