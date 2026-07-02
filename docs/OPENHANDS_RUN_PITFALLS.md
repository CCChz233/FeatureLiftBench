# OpenHands 排错速查

运行命令以 [RUN.md](../RUN.md) 为准。本文记录常见故障与已修复项。

## 配置与 CLI

| 现象 | 原因 | 处理 |
|------|------|------|
| `featureliftbench: command not found` | 未 `pip install -e .` | 在项目根 `pip install -e .` |
| `local config not found` | 无 `flb.local.toml` | `cp flb.local.toml.example flb.local.toml` |
| 进度条变成 `started ...` 一行 | `2>&1 \| tee` 破坏 stderr TTY | 只用 `\| tee`（不重定向 stderr） |
| main 先显示 `0/1` | 旧版内嵌 smoke | 已分离：先 `featureliftbench smoke`，再 `run --suite main` |
| 本地 vLLM preflight 404 | health probe 模型名 | 已自动 strip `openai/` 前缀；无需 `SKIP_LLM_HEALTH_CHECK` |
| Docker 内连不上 vLLM | bridge 访问不了 127.0.0.1 | CLI 自动 `AGENT_DOCKER_NETWORK=host` |

## 运行结果

| 现象 | 可能原因 | 处理 |
|------|----------|------|
| `api_calls == 0` | key/模型/profile 错误 | `featureliftbench setup`；查 `agent/stderr.log` |
| `docker_sandbox_error=true` | eval 容器 OOM/权限 | 查 `eval/result.json`；非模型能力问题 |
| `missing_submission` + 有 api_calls | Agent 未写出 submission | 模型/步数问题；可提高 `max_steps` |
| `agent_step_limited` | 步数上限 | main 建议 `--max-steps 180` |
| `rate_limited` | API TPM/RPM | `workers=1`，`task_cooldown_seconds=15`，`retry_rate_limit=5` |
| `usage_unverified=true` | 提供商未返回 usage | 仅作 pilot 参考 |

## Pilot5

- 必须同时有 `sanity3/` 与 `batch2/` 才完整 5 题。
- 基础设施干净：`total==5`、`docker_sandbox_failures==0`、无 `eval_infra_failed`。
- `model_failed` 可接受（属于 benchmark 结果）。

## 已在代码中修复（摘要）

- Eval Docker：`eval/`、`logs/` 预创建 + eval 容器 `--user`（避免 `docker_sandbox_error`）
- OpenHands 日志分流：`openhands_events.jsonl` vs stdout
- Suite `failure_class` 区分 infra / model
- Resume 前 `validate_suite_resume.py`
- `summarize_suite_infra.py` → `infra_clean`

## 资源起点（main）

在 `flb.local.toml` 或环境中：

```toml
[agent]
max_steps = 180

[run]
task_cooldown_seconds = 15
retry_rate_limit = 5
workers = 1
```

完整架构见 [ARCHITECTURE.md](ARCHITECTURE.md)。
