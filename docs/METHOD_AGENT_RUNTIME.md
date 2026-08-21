# Agent Runtime Ablation (DeepSeek Harness / Codex)

> **Status: current · Last verified: 2026-08-21**
> 这是可选的 **agent runtime** 实验臂，不是 Official Main，也不是信息消融。
> 基础设施已落地，**尚无正式分数**。

## Decision

Official Main 仍是 **OpenHands + Docker evaluator + No-Hint Full-Repository**。
DeepSeek Harness 与 Codex 作为与 OpenHands 同级的 **coding runtime**：同一信息边界、
同一 evaluator、同一 `functional_gate` / RRES。它们的分数写进独立 runtime 表，
**不得并入** 现有 5-model OpenHands Python-200 主表。

钉版本，不跟 head：

| Runtime | Adapter | Pin |
| --- | --- | --- |
| DeepSeek Harness | `deepseek-harness` | tag `dsh-v0.1.0-rc.8` / `141eb6fef83422698aef7a981029e843e8161534` |
| OpenAI Codex CLI | `codex` | tag `rust-v0.149.0` / `758ef40f50c1a458425c7cfbf1eb12cbc07af0b0` |

Pins 在 [runtime_pins.json](../harness/config/runtime_pins.json)。DeepSeek Harness
当前仍是 developer preview（无 1.0）；Codex 钉的是非 alpha 的 `0.149.0`。

## Same / Different

| Dimension | Same as Official Main? |
| --- | --- |
| Task set (when comparing) | yes, start with Core-12 |
| Source context | full pinned `repo/` |
| Source hints | hidden |
| Benchmark tests | hidden |
| Prompt contract | `TASK.md` + required `submission/featurelifted/` |
| Attempts | one per task |
| Evaluator | isolated eval Docker, `functional_gate` + RRES |
| Agent runtime | **no** — this is the factor |
| Agent Docker image | OpenHands image does **not** contain `dsh`/`codex`; host PATH or a custom image |

先跑 **一个** runtime + Flash（或该 runtime 的默认模型），在 Core-12 上与
OpenHands+Flash Main 成对，不要一上来全量 Python-200。CLI adapter 名：
`--agent deepseek-harness` 或 `--agent codex`。

## Install Pins

```bash
./harness/scripts/pin_runtime_agents.sh
```

Checkout 落在 `third_party/runtimes/`（gitignore）。随后自行把二进制放到 PATH，
或设 `FEATURELIFTBENCH_DSH_BIN` / `FEATURELIFTBENCH_CODEX_BIN`：

- DeepSeek Harness：在 checkout 里 `pnpm install && pnpm run build`，使用 `dsh`
- Codex：用 release `0.149.0` 的平台 binary，或从 `codex-cli` 构建 `codex`

## Run

把 [agents.example.toml](../harness/config/agents.example.toml) 里的
`dsh_deepseek_v4_flash_main` / `codex_gpt_main` 拷进本地 `agents.toml`。

```bash
# plan only
./harness/scripts/run_runtime_ablation.sh deepseek-harness dsh_deepseek_v4_flash_main

# execute Core-12, host agent + eval Docker
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

尚无正式分数。STATUS / FINDINGS 只记基础设施就绪。数字不进 Python-200 主表，见
[EVALUATION.md](EVALUATION.md)、[STATUS.md](STATUS.md)、[FINDINGS.md](FINDINGS.md)。
