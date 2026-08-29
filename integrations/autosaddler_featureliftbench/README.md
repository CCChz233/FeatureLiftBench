# AutoSaddler-FLB

External prompt-only integration between AutoSaddler V2 and FeatureLiftBench's existing OpenHands runner.
It does not modify AutoSaddler, OpenHands, benchmark tasks, or the FeatureLift evaluator.

## Frozen and mutable surfaces

- Frozen: AutoSaddler core, OpenHands core/version, task packages, evaluator, model/profile, runtime budget.
- Mutable: four bounded prompt text components rendered through
  `FEATURELIFTBENCH_OPENHANDS_PROMPT_APPEND_FILE`.
- Optimizer-visible: public task excerpts, sanitized OpenHands trace excerpts, Functional Pass, coarse failure stage,
  rollout usage.
- Never optimizer-visible: Hidden tests, assertions, expected outputs, evaluator logs, reference solutions.

The seed stores `__AUTOSADDLER_FLB_INACTIVE__` in each required non-empty component. The renderer emits
no appendix for that sentinel, so the seed is behaviorally identical to the existing Official Main prompt.

## Local contract smoke

Use Python 3.12. Install this package, the sibling AutoSaddler checkout, and FeatureLiftBench in one environment.

```bash
uv venv .venv --python 3.12
uv pip install --python .venv/bin/python -e ../../AutoSaddler -e ../.. -e '.[dev]'
.venv/bin/python -m pytest tests -q
.venv/bin/python -m autosaddler.v2.cli --config configs/smoke_fixture.yaml --run-id fixture-smoke-v1
.venv/bin/python -m autosaddler_featureliftbench.summarize \
  ../../experiments/methods/autosaddler_flb/fixture_runs/fixture-smoke-v1
```

The fixture smoke exercises plugin discovery, prompt mutation, train acceptance, development ranking,
durable events, rollout accounting, and token accounting without making an API call.

## Real rollout-path smoke

`configs/real_rollout_smoke_fixed_patch.yaml` runs one sanity train case and one repo-disjoint sanity
development case through the real OpenHands and Docker-evaluator path. It uses the fake optimizer only
to emit one fixed generic prompt update, so it requires no second optimizer credential and must not be
reported as learned-method effectiveness. Four task-agent rollouts are expected: seed development,
train before, train after, and accepted-candidate development.

## Real smoke

`configs/real_template.yaml` uses two train and two repo-disjoint development tasks. It requires both:

1. the existing FeatureLiftBench/OpenHands model credentials from `.env`; and
2. credentials for an AutoSaddler-supported optimizer provider.

Copy the template to an untracked config, select a supported optimizer provider, and run it with a new run ID.
All paid outputs remain under `experiments/methods/autosaddler_flb/`.

## Minimal causal pilot

`configs/causal_pilot_deepseek.yaml` keeps AutoSaddler and OpenHands core frozen while registering an
integration-owned OpenAI-compatible DeepSeek optimizer. The provider receives only the prompt pack's
audited workspace assets and returns schema-validated JSON; it has no evaluator or benchmark filesystem
access. The pilot uses one train failure and one repo-disjoint development failure with an absolute cap of
four task-agent rollouts: development H0, train H0, train H1, and development H1 after train acceptance.

```bash
set -a
source ../../.env
set +a
PATH="/Users/chz/.local/share/uv/tools/openhands/bin:$PATH" \
  .venv/bin/python -m autosaddler_featureliftbench.runner \
  --config configs/causal_pilot_deepseek.yaml \
  --run-id <new-run-id>
```
