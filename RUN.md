conda activate bench
cd /home/chaihongzheng/workspace/FeatureLiftBench

## Memory guard（建议先开）

未加 harness 内置内存沙箱前，先给当前 shell 及其子进程加 32GB 虚拟内存上限，避免 agent 自测或 eval 中的 `pytest` 因错误 submission 吃爆宿主机内存。

```bash
ulimit -v $((32 * 1024 * 1024))
```

## Local vLLM (Qwen example)

AGENT_PROFILE=qwen3_coder_30b_vllm NUM_WORKERS=1 \
  RUN_ID=benchmark-50-hard-qwen3-coder-$(date +%Y%m%d-%H%M%S) \
  PYTHON="$(which python)" MINI_BIN="$(which mini)" ./run.sh

## SiliconFlow API（GLM-5.2 / Kimi-K2.7-Code / MiniMax-M2.5）

`.env` 需配置 `SILICONFLOW_API_KEY` 与 `SILICONFLOW_API_BASE=https://api.siliconflow.cn/v1`（**不要**带 `/chat/completions`）。

限流建议：`NUM_WORKERS=1`、`RETRY_RATE_LIMIT=5`；一次只跑一个模型。

内存建议：一次只跑一个 suite；不要让多个模型或多个 full run 重叠。若看到内核日志 `Killed process ... (pytest)`，说明 untrusted submission 在测试阶段失控，先降低并发并加 `ulimit`，后续改为 Docker/cgroup 或 harness 内置内存限制。

```bash
conda activate bench
cd /home/chaihongzheng/workspace/FeatureLiftBench
export PYTHONPATH="$PWD/harness"
export PYTHON="$(which python)"
export MINI_BIN="$(which mini)"

# 示例：GLM-5.2 第一轮
AGENT_PROFILE=glm_5_2 NUM_WORKERS=1 RETRY_RATE_LIMIT=5 \
  RUN_ID=benchmark-50-hard-glm-5.2-run1-$(date +%Y%m%d-%H%M%S) \
  ./run.sh

# Kimi-K2.7-Code
AGENT_PROFILE=kimi_k2_7_code NUM_WORKERS=1 RETRY_RATE_LIMIT=5 \
  RUN_ID=benchmark-50-hard-kimi-k2.7-run1-$(date +%Y%m%d-%H%M%S) \
  ./run.sh

# MiniMax-M2.5
AGENT_PROFILE=minimax_m2_5 NUM_WORKERS=1 RETRY_RATE_LIMIT=5 \
  RUN_ID=benchmark-50-hard-minimax-m2.5-run1-$(date +%Y%m%d-%H%M%S) \
  ./run.sh
```

Profile 名：`glm_5_2` | `kimi_k2_7_code` | `minimax_m2_5`