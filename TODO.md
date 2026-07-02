# FeatureLiftBench TODO

Current objective: make OpenHands runs credible enough for fixed slices and then a full Python main-suite experiment.

## P0: Validate Current OpenHands Path

- [ ] Re-run `run_openhands_pilot5.sh` after the latest script fixes.
- [ ] Confirm `pilot5-summary.json.summary.total == 5`.
- [ ] Confirm no `agent_setup_failed`, `rate_limited`, `eval_infra_failed`, or `agent_step_limited`.
- [ ] Confirm `assistant_steps` is nonzero on real OpenHands events.
- [ ] Confirm token/context audit is verified for DeepSeek Flash.

## P1: Small Slice Before Full Run

- [ ] Define a fixed 5-10 task slice from `benchmark/tasks/`.
- [ ] Run OpenHands with `NUM_WORKERS=1`.
- [ ] Check `suite.json.summary.failure_classes`.
- [ ] Inspect token cost per task and max prompt tokens.
- [ ] Decide whether `FEATURELIFTBENCH_OPENHANDS_MAX_STEPS=120` is enough or should be raised.

## P2: Full Main-Suite Run

- [ ] Run `./run_openhands.sh benchmark/tasks "$OUT"` only after pilot and slice are infrastructure-clean.
- [ ] Keep agent/eval Docker enabled.
- [ ] Keep context audit enabled.
- [ ] Separate infrastructure failures from `model_failed` in all reporting.

## P3: Remaining Harness Improvements

- [ ] Add suite-level RPM/TPM throttling.
- [ ] Add post-run compact report for failure classes, token totals, max prompt, and step counts.
- [ ] Add resume validation for incomplete pilot directories.
- [ ] Consider tighter OpenHands tool restrictions if logs show harmful tool usage.
- [ ] Consider mini-swe-agent + context compression as a controlled ablation, not the mainline.

## Reference Backlogs

- OpenHands details: [docs/OPENHANDS_BENCHMARK_TODO.md](docs/OPENHANDS_BENCHMARK_TODO.md)
- Known limitations: [docs/limitations.md](docs/limitations.md)
- Task expansion workflow: [BATCH1_PLAYBOOK.md](BATCH1_PLAYBOOK.md)
- Go exploration: [GO_FEATURELIFTBENCH_DESIGN.md](GO_FEATURELIFTBENCH_DESIGN.md)
