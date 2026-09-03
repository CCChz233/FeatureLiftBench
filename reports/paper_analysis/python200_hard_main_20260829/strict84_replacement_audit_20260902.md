# Strict-84 replacement eligibility — 2026-09-02

> **Verdict: do not merge. Do not write a final main table.**
> This is an identity/progress check, not a leaderboard.

Directory:
`experiments/python/openhands/deepseek-v4-flash/python200-hard-main-20260830-strict84-replacement/`

ID list:
`reports/paper_analysis/python200_hard_main_20260829/strict_replacement_task_ids.txt`
(84 IDs; extra `run.json` directories: 0).

## Progress

| Item | Value |
| --- | --- |
| Wanted tasks | 84 |
| Directories with `run.json` | **38** |
| Missing | **46** (first: `lark__parse_tree_core__001`) |
| Incomplete workspace without `run.json` | `lark__parse_tree_core__001/` (started 2026-08-31, no live process) |
| `launch.log` last line | `[39/84] started lark__parse_tree_core__001` |
| `launch_identity.json` status | still `"running"` (stale; no matching process) |
| Run-level `status=passed` among 38 | 4 (`chameleon`, `graphene`, `humanize`, `isort`) |

The 20260829 received suite was **not** overwritten.

## Image identity (blocker)

From `launch_identity.json`, still true of local `latest` on 2026-09-02:

| Role | Required (paper / received suite) | Used (local `latest`) |
| --- | --- | --- |
| agent | `sha256:0843b6633d48da91832ce16c0e6ac42baf2f04d7b08cb66061720f176a8f2eea` | `sha256:cc6229204b71d871ebd3eea0a251c9947e8b5631aeb652a4159d8591d43033fe` |
| eval | `sha256:d1ea357c125a6f4957e1246f770bd1deb4717448e46e779f62b0351213cad191` | `sha256:cccf858c5f9b278de16bf9317aa032fd61c022dd1c257016ab08d5b68990f368` |

`image_identity`: `local_latest_not_received_suite_digest`.

Closing the main table requires the pinned images on the machine, a complete
84/84 `run.json` set, then merge **by task ID** with the untouched 116 from
20260829. Resume must write only into the 20260830 replacement directory.

Prep note:
[`experiments/registry/python200_hard_wheel_closure_and_strict84_20260830.md`](../../../experiments/registry/python200_hard_wheel_closure_and_strict84_20260830.md).
