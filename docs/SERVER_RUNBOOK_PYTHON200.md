# Server Runbook: Python-200' Main

> **Status: current · Last verified: 2026-09-03**
> Paper suite: frozen Python-150 + Hard-50 (`python200_hard`). Full Flash table
> is **not** run. Condition: Full-Repository / No-Hint, benchmark tests hidden,
> one task attempt.
> Formal freeze: `6c20ff0307762503a73cbb9ff32e9992c6446e4b17483a68373027be58cbf419`
> (v2). Predecessor `474862c22165ac9cc8ab895f1e265dd0bb43da81f52e77561b29fde44798a8d8`
> keeps the 132/200 Flash audit headline.
> Launch Official Main or current V1 only. Rescue+ / Lite checker arms are
> discontinued. DeepSeek Harness / Codex is optional and is not Official Main;
> see [METHOD_AGENT_RUNTIME.md](METHOD_AGENT_RUNTIME.md).
>
> `./harness/scripts/archive/run_python200_paper.sh` still targets the **superseded**
> 150 + External-50 release. Do not use it to write the new main table. Replay
> commands for that suite are in §11.

## 1. Prerequisites

- Linux server with Docker and enough disk for source archives, images and task workspaces.
- Python 3.11+ for the harness (use 3.12 when the host default is 3.9).
- A configured `.env` and `harness/config/agents.toml` profile.
- Checkout or bundle containing `benchmark/python200_hard_tasks/`,
  `benchmark/sources/python200_hard_registry.json`, frozen private evaluator
  assets and wheels. Canonical source archives are rebuilt on the server.
- Explicitly pinned agent and evaluator images for paper runs.

Do not print `.env`, API keys, or the full private agent configuration into logs.

## 2. Upload freeze v2 (the only paper pack)

Copy the whole folder `exports/python200-prime-freeze-v2/` to the server.
Do not upload `exports/archive/` or anything under `server-overlays/`.
Instructions: `exports/python200-prime-freeze-v2/README.md`.

```bash
scp -r exports/python200-prime-freeze-v2 <server>:<transfer-directory>/
```

On the server:

```bash
cd <transfer-directory>/python200-prime-freeze-v2
shasum -a 256 -c SHA256SUMS
mkdir -p FeatureLiftBench
tar -xzf worktree.tar.gz -C FeatureLiftBench
python3.12 FeatureLiftBench/scripts/build_python200_server_overlay.py \
  --verify overlay-offline.tar.gz
tar -xzf overlay-offline.tar.gz -C FeatureLiftBench
docker load < images.tar.gz
```

Never put `.env` in the pack; configure credentials on the server.

After the overlay is applied:

```bash
cd FeatureLiftBench
python3.12 scripts/build_python200_prime_candidate_freeze.py --check
python3.12 scripts/build_python200_prime_final_freeze.py --check \
  --agent-image featureliftbench-agent:python200-prime-212930ea \
  --evaluator-image featureliftbench-eval:python200-prime-212930ea
python3.12 benchmark/selection/scripts/materialize_python200_hard_release.py --check
python3.12 scripts/check_task_lifecycle.py
```

`check_python200_baseline_freeze.py` pins the frozen Python-150 tree
(`0b106842…`) and does not admit Hard-50 into `benchmark/tasks/`. Freeze v2
repaired overlapping Python-150 packages, so that check now reports drift on
the live tree. Do not roll back those repairs to make the 150 check green.
Paper identity is Python-200′ freeze v2 `6c20ff03…`. Do not bypass catalog or
symlink checks for a formal run.

## 3. Build and Pin Images

Build the exact frozen Agent and evaluator images, then record their immutable
identities:

```bash
export FEATURELIFTBENCH_BENCHMARK_ID=212930ea5363f21824afd5454c4da125052ad7a7d7186886e3dddef145811254
export FEATURELIFTBENCH_DOCKER_PLATFORM=linux/amd64
FEATURELIFTBENCH_INSTALL_OPENHANDS=1 \
  ./docker/build_agent_image.sh featureliftbench-agent:python200-prime-212930ea
./docker/build_eval_image.sh featureliftbench-eval:python200-prime-212930ea

python3.12 scripts/build_python200_prime_final_freeze.py --check \
  --agent-image featureliftbench-agent:python200-prime-212930ea \
  --evaluator-image featureliftbench-eval:python200-prime-212930ea
```

Use those identities explicitly in every model run. If extending an existing baseline, use the
same agent/evaluator identities or re-evaluate the baseline submissions under the new evaluator.

## 4. Catalog Preflight (no model calls)

```bash
./harness/scripts/archive/run_python200_prime_paper.sh \
  openhands_deepseek_v4_flash \
  python200-prime-deepseek-v4-flash-main-r1 \
  --workers 4 --timeout 3600
```

This is plan-only: it performs all checkout, task, freeze and Docker checks but
does not call the model API.

Expected paper suite id is `python200_hard` (aliases include `python200-prime`).
Task root must be `benchmark/python200_hard_tasks` with source registry
`benchmark/sources/python200_hard_registry.json`.

## 4b. Current V1 cost arm (Main + 2M cap)

Canonical V1 is Main protocol plus a 2M total-token cap. It is **not** the
retired `contract_closure_gate_lite_v1*` checker/repair protocol. Spec:
[METHOD_V1.md](METHOD_V1.md). Existing Qwen **55/200** is on the superseded
150+External-50 suite; do not copy it onto Python-200'.

```bash
./scripts/run_benchmark.sh \
  --benchmark python200_hard \
  --agent openhands \
  --method v1 \
  --output experiments/python/openhands/<model>/<run-id> \
  --docker --workers 1 --timeout 3600
```

Omit `--execute`-style flags: `run_benchmark.sh` runs when invoked. Confirm the
resolved method is `v1` in suite metadata before a costly full pass.

## 4c. Optional runtime ablation (not Official Main)

DeepSeek Harness and Codex share the Main information boundary and evaluator,
but they are a different agent runtime. `./setup.sh` installs the pinned CLIs
at the same level as OpenHands. Do not write those scores into the OpenHands
table.

```bash
./setup.sh
./scripts/run_benchmark.sh \
  --benchmark python200_hard \
  --agent deepseek-harness \
  --method main \
  --output experiments/python/runtime/deepseek-harness/<model>/<run-id> \
  --docker --workers 1
```

Core-12 wrapper (historical helper; still not Official Main):

```bash
./harness/scripts/run_runtime_ablation.sh deepseek-harness dsh_deepseek_v4_flash_main
```

Default execution is host CLI + eval Docker. To bake `dsh`/`codex` into the
agent image the same way as OpenHands:

```bash
FEATURELIFTBENCH_INSTALL_RUNTIME_AGENTS=1 ./docker/build_agent_image.sh
```

Spec: [METHOD_AGENT_RUNTIME.md](METHOD_AGENT_RUNTIME.md).

Historical Frozen Lite V1 (45+10) and main-budget Lite V1 profiles remain in
`agents.toml` for replay only. Do not launch them as the current V1 method.

## 5. Smoke Before Full Cost

Run one representative task with the same profile and images using the standard CLI:

```bash
./scripts/run_benchmark.sh \
  --benchmark python200_hard \
  --agent openhands \
  --method main \
  --tasks <one-task-id> \
  --output experiments/smoke/<run-id> \
  --docker --workers 1
```

Confirm:

- agent container starts and receives no benchmark tests or source hints;
- source archive materializes;
- submission is saved outside the agent workspace;
- isolated evaluator completes with network disabled;
- `run.json`, `eval/result.json`, usage and image IDs are present.

Do not promote the smoke attempt into Pass@1 of the formal suite.

## 6. Launch Full Python-200'

```bash
./harness/scripts/archive/run_python200_prime_paper.sh \
  openhands_deepseek_v4_flash \
  python200-prime-deepseek-v4-flash-main-r1 \
  --workers 4 --timeout 3600 --execute
```

Write under `experiments/python/openhands/<model>/<run-id>/` for OpenHands
leaderboard runs. Do not edit the method profile after preflight. If any
setting changes, use a new run id.

Lite Rescue、Rescue+ 和 Adaptive Budget V2 已停。不要再跑
`contract_closure_gate_lite_rescue*` profile，也不要把它们标成当前 V1。历史协议见
[archive/methods/](archive/methods/README.md)。当前 cost arm 规范见
[METHOD_V1.md](METHOD_V1.md)。

## 7. Monitor and Resume

Monitor task-level terminal `run.json` files and suite progress without editing results.

```bash
./harness/scripts/archive/run_python200_prime_paper.sh \
  openhands_deepseek_v4_flash \
  --workers 4 --timeout 3600 \
  --resume experiments/python/openhands/deepseek-v4-flash/python200-prime-deepseek-v4-flash-main-r1 \
  --execute
```

Resume may fill tasks without a terminal attempt; it must not retry completed
failures under Pass@1.

## 8. Acceptance and Export

```bash
PYTHONPATH=harness python3.12 harness/scripts/analyze_benchmark_suite.py <suite-dir>
PYTHONPATH=harness python3.12 harness/scripts/report_entanglement_coverage.py --suite-dir <suite-dir>
```

Before export, verify exact task coverage, attempt counts, image IDs, context violations, missing
submissions and Functional/completion mismatches. Create a tarball and SHA256 without deleting
the server copy. Paper metrics must be recomputable from per-task `run.json` and
`eval/result.json`. Report Python-150 and Hard-50 separately as well as the 200 union.

## 9. Failure Policy

- Infra failure before a valid agent attempt: record and rerun only under the declared exception policy.
- Missing submission after a valid attempt: Functional failure.
- Agent timeout/step limit with a valid submission: evaluate it; process status and Functional status remain separate.
- Context-window violation: retain the result, flag it, and run the predeclared sensitivity procedure.
- Evaluator image mismatch: do not silently merge; attest or re-evaluate saved submissions.

Current blockers and available evidence are listed in [STATUS.md](STATUS.md).

## 10. Do not use these as the paper entrypoint

| Command / path | Why |
| --- | --- |
| `./harness/scripts/archive/run_python200_paper.sh` | Still the 150+External-50 runner + 150 freeze gate |
| `./scripts/run_benchmark.sh --benchmark python200_hard` | Generic runner; it does not enforce the final Python-200′ freeze ID |
| `--suite main` | Legacy alias for **python150**, not Python-200' |
| `benchmark/python200_tasks/` | Superseded unified view |
| Root `run.sh`, `run_openhands.sh`, `run_easy.sh`, … | Removed 2026-09-02; use `./scripts/run_benchmark.sh` |
| `./logs/*.sh` | Removed ops wrappers; use `run_benchmark.sh` |

## 11. Replay: superseded 150 + External-50

Use only to reproduce historical tables. Selection checks below are the old
release gates, not Python-200'.

```bash
python3 benchmark/selection/scripts/materialize_python200_release.py --check
python3 benchmark/selection/scripts/finalize_python200_source_registry.py --check
python3 benchmark/selection/scripts/finalize_python200_dependencies.py --check
python3 benchmark/selection/scripts/audit_python200_balance.py --check
python3 benchmark/selection/scripts/audit_python200_wheels.py --python-version 311
python3 benchmark/selection/scripts/check_python200_baseline_freeze.py
./harness/scripts/archive/run_python200_paper.sh \
  <openhands-profile> \
  <run-id> \
  --workers <n> \
  --agent-image <agent-image-id> \
  --eval-image <eval-image-id> \
  --execute
```

`--external-only` still means the old External-50 extension, not Hard-50.
Lite V1 checker replay remains possible via frozen profiles in `agents.toml`;
those runs are not current V1.
