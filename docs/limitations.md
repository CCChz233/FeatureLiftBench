# Known Limitations

This file records current limitations that affect interpretation of FeatureLiftBench runs.

## Experiment Protocol

- The current mainline is OpenHands because it has context management. Old mini-swe-agent append-only runs are legacy baselines and should not be used as formal long-context evidence.
- Token/context evidence is valid only when `usage.context_audit.usage_unverified == false` or when a result is explicitly labeled as unverified pilot evidence.
- Provider APIs differ in model name handling, usage fields, rate limits, and quota behavior. Cross-provider rankings need careful caveats.

## OpenHands

- OpenHands has a larger tool surface than the benchmark strictly needs. FeatureLiftBench mostly needs code search, file editing, public-test execution, and submission writing.
- `FEATURELIFTBENCH_OPENHANDS_MAX_STEPS` defaults to 120. This is a safety cap, not a proven optimal budget for hard tasks.
- The local usage proxy depends on provider `usage` fields. If a provider omits usage, token evidence remains unverified.
- Suite-level TPM/RPM throttling uses optional inter-task cooldown (`FEATURELIFTBENCH_SUITE_TASK_COOLDOWN_SECONDS`, default 0). Per-task `retry_rate_limit` still applies on 429. For 100-task runs, use `NUM_WORKERS=1`, `RETRY_RATE_LIMIT=5`, and cooldown 10–30s.

## Evaluator

- Docker eval is the official safety boundary. Non-Docker local eval is for debugging only.
- Eval Docker has memory/CPU/pid/log/time limits. `docker_sandbox_error=true` is an infrastructure failure and must not be counted as model capability failure.
- The evaluator primarily measures behavior and extraction footprint. It does not yet enforce source similarity or prove that a submission was copied from the original implementation rather than rewritten.

## Benchmark Tasks

- Main benchmark scale is 100 hard tasks plus 3 smoke tasks.
- Hidden tests reduce public-test overfitting but do not eliminate all narrow rewrites.
- Entanglement labels are human-curated and should be used for grouped analysis, not as mathematically exact ground truth.
- Some historical task-design notes may contain exploratory reasoning. The executable task directory and [TASK_FORMAT.md](TASK_FORMAT.md) are the source of truth.

## Results

- Historical Flash/Pro/vLLM/SiliconFlow reports were produced under earlier protocols and should be treated as reference material.
- Future main results should report:
  - pass rate,
  - final score,
  - extraction ratio,
  - failure classes,
  - token totals,
  - max prompt tokens per call,
  - context violations,
  - infrastructure failures separately from model failures.

## Operational Risks

- API keys live in `.env`; never commit it.
- The selected profile key/base is forwarded to agent Docker; unrelated provider secrets are filtered out by current config loading.
- If using local vLLM with `127.0.0.1`/`localhost`, agent Docker needs `FEATURELIFTBENCH_AGENT_DOCKER_NETWORK=host`.
- Large runs can be expensive. Start with pilot5 and fixed 5-10 task slices.
