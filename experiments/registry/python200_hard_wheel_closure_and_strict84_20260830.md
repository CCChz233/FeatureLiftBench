# Python-200′ wheel closure and strict-84 replacement prep — 2026-08-30

> **Status: wheels closed; 84-task replacement stalled at 38/84 on local `latest` · Last verified: 2026-09-02**
>
> `132/200` remains an audit headline only. This note does not promote a leaderboard.

## What this pass did

Closed the remaining CPython 3.11 Linux wheel gaps (196/200 → **200/200**) without
editing any task contract, freeze, or the received 2026-08-29 suite. Prepared an
independent 84-task replacement directory. On 2026-08-30 the operator requested
launch despite missing paper-pinned images; the replacement suite is **running**
against local `latest` tags. Image identity is a declared deviation, not a paper pin.

## Frozen input (unchanged)

```bash
PYTHONPATH=harness python3.12 -B harness/scripts/materialize_python200_hard_frozen_input.py \
  --output experiments/validation/preflight/python200-hard-freeze846-input \
  --check
```

| Field | Value |
| --- | --- |
| freeze_id | `846b814726217623fa205cb7688bee61e6c21c43efda1ebd05e79b5ed8cb4fbd` |
| task_set_sha256 | `a28c301e83bf62b831c007b7c5ebc4fd0f6e4c012496d812fa90d233dfe81ad3` |
| materialized_tree sha256 | `98463b9d37757bb0ab4db4d4ff1389a3f3b6d50767eba43f89ea5eb273de1138` |
| file_count | 13075 |
| `--check` | exit 0, both before and after wheel fetch |

84/84 IDs in `strict_replacement_task_ids.txt` have `metadata.json` under
`experiments/validation/preflight/python200-hard-freeze846-input/tasks`.

## Wheel audit

```bash
python3.12 benchmark/selection/scripts/audit_python200_wheels.py \
  --suite benchmark/selection/python200_hard_suite.json \
  --python-version 311
```

Before this pass: **196/200**. After: **200/200**, exit 0.

The four remaining tasks needed **cp311 manylinux x86_64** wheels. The cache
already had matching versions as cp312 and/or aarch64, which the eval ABI
rejects.

| Task | Locked requirement |
| --- | --- |
| `pandera__dataframe_schema_core__001` | `numpy==2.2.6` |
| `spiffworkflow__bpmn_engine_core__001` | `lxml==6.1.2` |
| `taskiq__broker_task_core__001` | `aiohttp==3.12.15`, `frozenlist==1.8.0`, `multidict==6.7.1`, `propcache==0.5.2`, `yarl==1.24.5` |
| `zope_component__site_lookup_core__001` | `zope.interface==7.2`, `zope.hookable==8.3` |

Fetch log: `experiments/validation/preflight/wheel_fetch_cp311_linux_20260830.log`.
Checksums: `experiments/validation/preflight/cp311_linux_wheels_20260830.sha256`.

Command used (per package, `--only-binary :all: --no-deps --python-version 311 --implementation cp --abi cp311`):

- try `--platform manylinux_2_28_x86_64`
- else `--platform manylinux2014_x86_64`

No `requirements.lock` or task package was modified.

## Replacement suite (running; not a paper table)

Directory:
`experiments/python/openhands/deepseek-v4-flash/python200-hard-main-20260830-strict84-replacement/`

Started 2026-08-30T09:51:23Z. First task: `aiohttp__url_params_core__hard3_001`.
Log: `launch.log`. Do not overwrite
`experiments/python/openhands/deepseek-v4-flash/python200-hard-main-20260829/`.

Required identity (from received suite `suite.json`):

| Dimension | Value |
| --- | --- |
| profile | `openhands_deepseek_v4_flash_main` |
| model | `deepseek/deepseek-v4-flash` |
| ablation | `main`, `prompt_style=standard`, no public tests, no source hints |
| steps | 120 |
| context | 131072 / reserved 8192 / condenser `token` trigger 122880 target 61440 |
| attempts | 1 |
| agent image | `sha256:0843b6633d48da91832ce16c0e6ac42baf2f04d7b08cb66061720f176a8f2eea` |
| eval image | `sha256:d1ea357c125a6f4957e1246f770bd1deb4717448e46e779f62b0351213cad191` |
| tasks-root | `experiments/validation/preflight/python200-hard-freeze846-input/tasks` |
| source registry | `benchmark/sources/python200_hard_registry.json` |

Launched command (local `latest`, not received-suite digests):

```bash
./scripts/run_benchmark.sh \
  --agent openhands \
  --method main \
  --profile openhands_deepseek_v4_flash_main \
  --tasks-root experiments/validation/preflight/python200-hard-freeze846-input/tasks \
  --source-registry benchmark/sources/python200_hard_registry.json \
  --task-file experiments/python/openhands/deepseek-v4-flash/python200-hard-main-20260830-strict84-replacement/strict_replacement_task_ids.txt \
  --output experiments/python/openhands/deepseek-v4-flash/python200-hard-main-20260830-strict84-replacement \
  --docker \
  --agent-image featureliftbench-agent:latest \
  --eval-image featureliftbench-eval:latest \
  --workers 1 \
  --timeout 3600
```

After a complete 84-task suite, merge by task ID (replacement for the 84,
original for the other 116) then:

```bash
PYTHONPATH=harness python3.12 -B harness/scripts/analyze_python200_hard_main.py \
  <merged_suite_dir> \
  --output-dir reports/paper_analysis/python200_hard_main_20260830

python3.12 -B harness/scripts/audit_python200_hard_candidate.py \
  <merged_suite_dir> \
  --analysis-dir reports/paper_analysis/python200_hard_main_20260830
```

Do not analyze the empty 20260830 directory as if it were a suite.

## Remaining blockers (this run is not paper-mergeable until identity matches)

1. **Image identity deviation (declared).** This host does not have the received
   suite digests. The running replacement uses local `latest`:
   agent `sha256:cc6229204b71d871ebd3eea0a251c9947e8b5631aeb652a4159d8591d43033fe`
   and eval `sha256:cccf858c5f9b278de16bf9317aa032fd61c022dd1c257016ab08d5b68990f368`.
   Required paper pins remain `0843b663…` / `d1ea357c…`. Do not merge this 84-task
   outcome into the final table without stating the image mismatch, or re-run
   after loading the exact received digests.
2. **Hard context enforcement is still audit-only in the proxy.** This run keeps
   the received Main condenser settings (trigger 122880). A fail-closed prompt
   guard would be a protocol change and was not enabled.
3. **84-task replacement is incomplete (2026-09-02 check: 38/84 `run.json`).**
   Log stopped at `[39/84] started lark__parse_tree_core__001`; that workspace
   has no `run.json` and no live process. Resume, if needed, must write only
   into the 20260830 replacement directory. Do not merge and do not analyze
   that directory as a complete suite. Eligibility note:
   `reports/paper_analysis/python200_hard_main_20260829/strict84_replacement_audit_20260902.md`.

## What not to do

- Do not write `132/200` into the abstract or final leaderboard.
- Do not rerun on dirty `benchmark/tasks/` (freeze drift).
- Do not edit task behavior or locks to dodge missing wheels (wheels are now closed).
- Do not treat this host’s `latest` images as the paper eval/agent identity.
