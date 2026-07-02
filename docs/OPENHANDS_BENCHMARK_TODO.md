# OpenHands Benchmark TODO

This is the OpenHands implementation checklist. **Run commands:** [RUN.md](../RUN.md). **Architecture:** [ARCHITECTURE.md](ARCHITECTURE.md).

## Done

- `openhands-agent` adapter registered in the harness.
- OpenHands wrapper writes `agent/openhands_task.md`.
- Headless command template:

```bash
openhands --headless --override-with-envs --exit-without-confirmation -f {prompt_file} --json
```

- Docker agent image can install OpenHands with Python 3.12.
- Eval defaults to direct `PYTHONPATH` import of `submission/featurelifted`.
- OpenHands stdout/stderr capture is bounded.
- JSON events are split into `agent/openhands_events.jsonl`.
- `.env` forwarding is restricted to the selected profile and safe harness variables.
- Local OpenAI-compatible usage proxy records provider usage into `agent/context_audit.jsonl`.
- Context window and reserved output tokens come from profile/env.
- `suite.json` includes `failure_class` counts.
- `featureliftbench` CLI: `setup`, `run`, `smoke`, `resume` + `flb.local.toml` local config.
- Smoke and main are **separate** suites (`smoke` vs `main`); no embedded smoke-first in main.
- `run_openhands.sh` / `run_openhands_pilot5.sh` thin-wrap the CLI.
- `FEATURELIFTBENCH_OPENHANDS_MAX_STEPS` caps OpenHands action steps.

## Remaining P1

- Run pilot5: `featureliftbench run --suite pilot5` and confirm:
  - `summary.total == 5`
  - `agent_failures == 0`
  - `docker_sandbox_failures == 0`
  - `log_limit_failures == 0`
  - no `agent_setup_failed`
  - no `eval_infra_failed`
- Confirm `assistant_steps` is nonzero on real OpenHands JSONL after the event detector update.
- Decide whether `120` is the default step cap for all mainline runs or whether hard tasks need `150`.

## Remaining P2

- Add suite-level provider throttling for RPM/TPM instead of relying only on retry-after behavior.
- Add a small report summarizing `failure_classes`, token totals, max prompt tokens, and step counts after each run.
- Add bad-output-dir checks for resume, especially empty `batch2/` or missing merged pilot summaries.
- Consider key-file mounting for agent Docker if `.env` passthrough needs to be tightened further.

## Reporting Rules

- OpenHands is the main evaluated agent only when real execution and token/context evidence are available.
- Results with `usage_unverified=true` are pilot evidence, not formal long-context claims.
- `model_failed` is a model/agent outcome.
- `agent_setup_failed`, `rate_limited`, `eval_infra_failed`, and `agent_step_limited` are infrastructure/control failures and must be reported separately.
