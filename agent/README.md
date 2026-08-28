# FeatureLiftBench agents

> **Status: current · Last verified: 2026-08-28**

`agent/` is the public catalog of coding runtimes that can run FeatureLiftBench.
The evaluator and Docker capsule stay in `harness/`. Adapter code stays in
`harness/featureliftbench/`. Do not copy those packages here.

Experiments are **benchmark × agent × method**. Changing `--agent` must keep the
same task root, information boundary, and evaluator. Official paper numbers use
**OpenHands** only. DeepSeek Harness and Codex are registered here so they share
the CLI, but their scores stay off the OpenHands table.

## Registry

| Id | CLI `--agent` | Paper table | Notes |
| --- | --- | --- | --- |
| `openhands` | `openhands-agent` | yes | Official Main runtime |
| `deepseek-harness` | `deepseek-harness` | no | Runtime ablation after `./setup.sh` |
| `codex` | `codex` | no | Runtime ablation after `./setup.sh` |
| `mini-swe-agent` | `mini-swe-agent` | no | Legacy / internal |
| `featurelift-agent` | `featurelift-agent` | no | Internal |
| `command` | `command` | no | Tests and custom binaries |

Source of truth: [registry.toml](registry.toml). List and resolve:

```bash
PYTHONPATH=harness python3.12 -B -m featureliftbench.cli catalog list --kind agents
```

Model/profile strings (`openhands_deepseek_v4_flash_main`, …) live in
`harness/config/agents.example.toml`. `--method` picks the profile for the
chosen agent.

## Add an agent

1. Implement or wrap an adapter under `harness/featureliftbench/` and add it to
   `SUPPORTED_AGENTS`.
2. Register the id, `cli_name`, aliases, and paper-table flag in
   `registry.toml`.
3. Add default profiles under `method/registry.toml` for the methods the new
   agent may run (`main` at minimum).
4. Document whether scores may enter the OpenHands paper table.
5. Run `PYTHONPATH=harness python3.12 -B -m featureliftbench.cli catalog check`.
