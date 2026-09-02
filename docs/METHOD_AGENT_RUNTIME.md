# Agent Runtime Ablation (DeepSeek Harness / Codex)

> **Status: current · Last verified: 2026-09-02**
> DeepSeek Harness 与 Codex 和 OpenHands 同级：clone 后跑 `./setup.sh` 即可调用。
> 这不是 Official Main，也不是信息消融。**尚无正式分数**。

## Decision

Official Main 仍是 **OpenHands + Docker evaluator + No-Hint Full-Repository**。
DeepSeek Harness 与 Codex 作为与 OpenHands 同级的 **coding runtime**：同一信息边界、
同一 evaluator、同一 `functional_gate` / RRES。`--agent` 入口相同。分数写进独立
runtime 表，**不得并入** 现有 5-model OpenHands Python-200 主表。

Runtime 的稳定 id 在 [agent/registry.toml](../agent/registry.toml)；协议在
[method/registry.toml](../method/registry.toml)。换 agent 只改 `--agent`，不要改
`--benchmark` 或 evaluator。

钉版本，不跟 head：

| Runtime | Adapter | Pin |
| --- | --- | --- |
| OpenHands | `openhands` | `openhands==1.16.0`（`INSTALL_OPENHANDS=1`） |
| DeepSeek Harness | `deepseek-harness` | npm `@deepseek-ai/dsh@0.1.0-rc.8` / commit `141eb6fef83422698aef7a981029e843e8161534` |
| OpenAI Codex CLI | `codex` | GitHub `rust-v0.149.0` / `758ef40f50c1a458425c7cfbf1eb12cbc07af0b0` |

Pins 在 [runtime_pins.json](../harness/config/runtime_pins.json)。DeepSeek Harness
当前仍是 developer preview（无 1.0）；Codex 钉的是非 alpha 的 `0.149.0`。

## Bootstrap (same as OpenHands)

```bash
./setup.sh
# edit .env with API keys
```

`./setup.sh` 会：

1. 创建 `.venv` 并安装 harness
2. 从 `agents.example.toml` 写出 `agents.toml`（若缺失）
3. 安装 pinned `dsh` 和 `codex` 到 `third_party/runtimes/bin/`（gitignore），并链进 `.venv/bin`
4. 可选：`INSTALL_OPENHANDS=1` 安装 host OpenHands CLI

不需要再手写本机绝对路径。Adapter 解析顺序：绝对 `agent_bin` / 环境变量 → 仓库 pin → PATH。

跳过 runtime CLI：`SKIP_RUNTIME_AGENTS=1 ./setup.sh`。单独重装：

```bash
./harness/scripts/pin_runtime_agents.sh
```

DeepSeek Harness 需要 Node.js `^22.19.0 || >=24`。没有 Node 时 Codex 仍会安装。

## Run

换 runtime 只改 `--agent`，题根用论文主套件 `python200_hard`（不要默认走已
superseded 的 `benchmark/python200_tasks`）：

```bash
./scripts/run_benchmark.sh --benchmark python200_hard --agent openhands --method main
./scripts/run_benchmark.sh --benchmark python200_hard --agent deepseek-harness --method main
./scripts/run_benchmark.sh --benchmark python200_hard --agent codex --method main
```

等价的底层 `run-agent`（显式题根）：

```bash
PYTHONPATH=harness python -B -m featureliftbench.cli run-agent benchmark/python200_hard_tasks \
  --agent openhands --agent-profile openhands_deepseek_v4_flash --eval-docker ...

PYTHONPATH=harness python -B -m featureliftbench.cli run-agent benchmark/python200_hard_tasks \
  --agent deepseek-harness --agent-profile dsh_deepseek_v4_flash_main --eval-docker ...

PYTHONPATH=harness python -B -m featureliftbench.cli run-agent benchmark/python200_hard_tasks \
  --agent codex --agent-profile codex_gpt_main --eval-docker ...
```

Core-12 成对包装：

```bash
./harness/scripts/run_runtime_ablation.sh deepseek-harness dsh_deepseek_v4_flash_main
./harness/scripts/run_runtime_ablation.sh deepseek-harness dsh_deepseek_v4_flash_main \
  runtime-dsh-flash-core12 --execute
```

Adapter 会在 workspace 写入 `FEATURELIFT_AGENT_TASK.md`（Main 边界说明 + `TASK.md`），
然后：

- DeepSeek：`dsh --profile headless "<short prompt>"`
- Codex：`codex exec --approve-for-me --skip-git-repo-check --json`

评测仍只收集 `submission/`。输出写入：

```text
experiments/python/runtime/<adapter>/<model>/<run-id>/
```

默认 host CLI + eval Docker。若要把 dsh/codex 放进 agent 镜像（与 OpenHands 镜像同级）：

```bash
FEATURELIFTBENCH_INSTALL_RUNTIME_AGENTS=1 ./docker/build_agent_image.sh
```

尚无正式分数。STATUS / FINDINGS 只记基础设施就绪。数字不进 Python-200 主表，见
[EVALUATION.md](EVALUATION.md)、[STATUS.md](STATUS.md)、[FINDINGS.md](FINDINGS.md)。
