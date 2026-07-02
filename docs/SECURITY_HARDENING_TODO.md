# FeatureLiftBench 安全与稳定性加固 TODO

> Status note: much of the original Docker/eval hardening has already landed.
> Current run safety is documented in [OPENHANDS_SERVER_RUNBOOK.md](OPENHANDS_SERVER_RUNBOOK.md)
> and current remaining work is tracked in [../TODO.md](../TODO.md).

最后更新：2026-06-29

本文档给出 FeatureLiftBench 的安全与稳定性落地计划。目标不是一开始做成公开多租户平台，而是先让正式实验的 eval 可复现、相对隔离、不会被异常 submission 打爆机器，同时给 agent 跑题建立清晰边界。

当前实现状态：A1 eval Docker 与 A2 agent Docker v0 已接入。正式实验推荐用 `FEATURELIFTBENCH_AGENT_DOCKER=1 FEATURELIFTBENCH_EVAL_DOCKER=1 ./run.sh`；local agent/local eval 只作为开发调试路径。

## 0. 设计结论

- **eval Docker 先做**：eval 会执行 submission 和 pytest，是最直接的不可信代码执行面；它不需要联网，边界简单，收益最高。
- **agent Docker 作为可选边界**：agent 需要模型 API，所以网络默认允许；文件系统边界通过只挂载 prepared workspace、agent output 和只读 harness 实现。维护者本地调试可继续用 local agent，长跑或外部 agent 应启用 `--agent-docker`。
- **不维护 100 套环境**：只维护 1 个 eval 镜像和 1 个 agent 镜像。每题/每次提交起短命容器，跑完删除。
- **Docker 是资源与文件系统边界，不是完整防作弊边界**：pytest 与 submission 在同一 Python 进程中执行，恶意 submission 理论上可能通过 Python introspection 观察测试上下文。当前目标是保护机器、提高复现性、限制资源和文件系统影响，不把 hidden tests 设计成对抗式秘密。

## 1. 威胁模型

| 等级 | 场景 | 当前目标 |
| --- | --- | --- |
| T0 | 维护者本地调试可信 oracle / agent 输出 | 允许非 Docker，本地快速迭代 |
| T1 | agent 生成的异常或恶意 submission | eval 必须有 timeout、内存、CPU、进程数、网络、文件系统边界 |
| T2 | agent 进程发疯，尝试改 workspace 外文件 | 使用 agent Docker 限制 host mount；local agent 仅用于维护者调试 |
| T3 | 外部用户提交任意代码，公开服务 | 暂不作为当前版本目标；需要 rootless Docker / gVisor / VM 等更强隔离 |

## 2. P0：正式 eval Docker 化

P0 是论文和正式 baseline 前必须完成的部分。

### P0.1 Harden `evaluate_submission_docker`

更新 `harness/featureliftbench/docker_eval.py`，让每次 eval 使用短命容器，并默认启用以下限制：

```text
docker run --rm
  --network none
  --memory 4g
  --memory-swap 4g
  --cpus 2
  --pids-limit 256
  --read-only
  --tmpfs /tmp:rw,nosuid,nodev,size=2g
  --cap-drop=ALL
  --security-opt no-new-privileges
  --ulimit nofile=1024:1024
  -v <harness>:/workspace/harness:ro
  -v <task>:/workspace/tasks/<task_id>:ro
  -v <submission>:/workspace/submission:ro
  -v <output>:/workspace/output:rw
```

注意点：

- `--read-only` 必须配 `--tmpfs /tmp`，因为 evaluator 会在 `/tmp/featureliftbench-eval-*` 建 venv。
- task 和 submission 必须只读；只有 output 可写。
- 不挂载 host home、`.env`、SSH key、pip cache 或整个仓库根目录。
- 默认值可通过环境变量覆盖，例如 `FEATURELIFTBENCH_DOCKER_MEMORY=4g`、`FEATURELIFTBENCH_DOCKER_CPUS=2`、`FEATURELIFTBENCH_DOCKER_PIDS=256`、`FEATURELIFTBENCH_DOCKER_TMPFS=/tmp:rw,nosuid,nodev,size=2g`。

### P0.2 解决离线依赖

当前 evaluator 使用 `pip install --no-index --no-deps -r requirements.lock`，Docker 内如果没有预置 wheel，非空 lock 的任务会失败。

当前做法：

- 当前 eval image 预装已知非空 lock 需要的 `idna==3.7`、`multidict==6.0.4`、`propcache==0.4.1`。
- 扩题或改 lock 后，要重新扫描主榜 `requirements.lock`，把新增 allowed dependency 加进 eval image。
- Docker eval 默认断网后，100 题 oracle 仍能通过。
- 记录 image digest 和依赖清单，避免“本机 pip cache 可用才通过”。

### P0.3 给 stdout/stderr 和日志加上限

`run_captured_command()` 已改成 bounded stream 读取，避免恶意 submission 疯狂打印导致 harness 内存膨胀。

当前做法：

- 给每个命令的 stdout/stderr 设置字节上限，默认 `8 MiB`。
- 超限后终止当前命令，结果标记为 `log_limit_exceeded=true`。
- result.json 中记录 `stdout_truncated` / `stderr_truncated`。
- 分析脚本/论文表格应把 `log_limit_exceeded` 与普通 hidden failure 分开统计。

### P0.4 让 suite 正式结果使用 Docker eval

`run-agent` 已支持 Docker eval backend。正式实验可以二选一：

1. 跑 agent 时直接传 `--eval-docker` 或设置 `FEATURELIFTBENCH_EVAL_DOCKER=1`。
2. 对历史 suite，用 `harness/scripts/reeval_suite.py --docker` 全量重算，并以 re-eval 结果作为论文统计口径。

验收口径必须明确：论文表格引用的是 Docker eval 结果，而不是 macOS/宿主机 local eval 结果。

### P0.5 资源失败分类

当前做法：

- result.json 区分 `timed_out`、`resource_limited`、`log_limit_exceeded`、`docker_sandbox_error`。
- suite summary 中把 resource/sandbox failure 与 functional failure 分开。
- 论文分析中不要把明确的 resource/log/sandbox failure 混入普通模型功能失败。

## 3. P1：agent 跑题边界

P1 的目标是防止 agent 发疯时污染 benchmark 仓库或宿主机。它不阻塞 P0，但如果要跑外部 agent、多人共享机器或公开平台，就要提前。

### P1.1 Host-only 最小防护

维护者本地调试可信 agent 时，可使用低成本 host-only 保护；正式长跑优先用 agent Docker：

- 使用独立输出目录，不在 benchmark 仓库根目录写临时文件。
- agent workspace 继续使用当前的 redacted copy：`repo/`、`public_tests/`、`metadata.json`、`TASK.md`、`submission/`。
- agent 运行前后记录 `git status --short`；若非 `experiments/` 的 tracked 文件发生变化，标记 run 为 `workspace_escape_detected`。
- 在正式跑批机器上使用专用 OS 用户，该用户不持有 SSH key、云凭据或无关项目写权限。
- `.env` 只传给 agent 进程，不复制进 workspace；日志里不得记录 API key 原文。

### P1.2 Agent Docker 可用路径

当前新增 1 个 agent 镜像，不按题目维护镜像。每次 task run 起一个短命容器：

```text
agent container
  network: allowed for model API
  mounts:
    prepared workspace: rw
    agent output dir: rw
    benchmark root: not mounted
    host home: not mounted
  env:
    model API key only
    FEATURELIFTBENCH_WORKSPACE
    FEATURELIFTBENCH_TASK_FILE
    FEATURELIFTBENCH_SUBMISSION_DIR
  limits:
    memory, cpu, pids, timeout
  security:
    no privileged mode
    cap-drop=ALL where compatible
    no-new-privileges
```

关键设计：

- agent container 只看到已经准备好的 workspace，不看到 `benchmark/tasks/<task_id>/hidden_tests` 或 `evaluation/`。
- agent 产物只从 `workspace/submission/` 收集。
- eval 仍由 eval container 单独执行，不在 agent container 里跑 hidden tests。
- agent container 允许网络，因为要访问模型 API；eval container 默认禁网。
- Docker command 只记录 env key，不记录 secret value；stdout/stderr 和 run payload 需要对已知 API key 做 redaction。
- agent Docker 日志也有输出上限，避免 agent 输出打爆 harness 内存。

可用命令：

```bash
docker/build_agent_image.sh featureliftbench-agent:latest

PYTHONPATH=harness python3 -B -m featureliftbench.cli run-agent \
  benchmark/tasks/<task_id> \
  --agent mini-swe-agent \
  --agent-config harness/config/agents.toml \
  --agent-profile deepseek_v4_flash \
  --env-file .env \
  --yolo \
  --agent-docker \
  --eval-docker \
  --output experiments/mini-swe-agent/<run_id>
```

镜像默认使用 `python:3.11-slim`，可通过 `FEATURELIFTBENCH_AGENT_PYTHON_BASE` 覆盖。agent 镜像 pin `mini-swe-agent==1.17.3`，因为当前 `mini_live_runner.py` 依赖该系列 API；不要在正式实验镜像里使用未 pin 的 latest。

### P1.3 agent timeout 和子进程清理

当前 agent adapter 已有 timeout 和 process group kill。P1 需要补充：

- 超时后确认子进程树被清理。
- agent container 超时后整容器删除。
- 中断 suite 时终止所有 active agent process，并写出可恢复的 run 状态。

## 4. P2：公开 hostile submission 服务

暂不作为当前论文实验的必要工作。若未来开放给外部用户提交任意代码，需要额外设计：

- rootless Docker 或 gVisor/Kata/Firecracker/独立 VM。
- 每个 run 使用无权限 UID/GID。
- 无 host secrets、无 home mount、无 Docker socket mount。
- eval 禁网；agent 网络按模型 API 做 egress allowlist。
- 磁盘 quota、日志 quota、总运行时 quota。
- 作业队列、并发上限、自动清理、审计日志。
- 明确 hidden test 防作弊不是 pytest in-process 能完全解决的问题。

## 5. 推荐实施顺序

1. **已完成**：`docker_eval.py` hardened Docker flags。
2. **已完成**：eval image 预置当前非空 lock 依赖；扩题后继续维护依赖闭包。
3. **已完成**：command stdout/stderr 上限，防日志打爆内存。
4. **已完成**：`run-agent --eval-docker` 与 `reeval_suite.py --docker`。
5. **已完成**：agent Docker v0；长跑/外部 agent 用 `--agent-docker`。
6. **当前**：用 Docker eval 跑完整主榜 oracle 验收。
7. **当前**：用 agent Docker + eval Docker 跑 Flash / Pro 正式 suite。
8. **P2**：只有公开服务化时进入。

## 6. 当前版本可以怎么跑

本地调试：

```bash
PYTHONPATH=harness .venv/bin/python -m featureliftbench.cli eval \
  benchmark/tasks/<task_id> \
  benchmark/submissions/<task_id>/oracle \
  --output /tmp/flb-eval
```

正式单题 eval：

```bash
docker/build_eval_image.sh featureliftbench-eval:latest

FEATURELIFTBENCH_EVAL_DOCKER=1 \
PYTHONPATH=harness .venv/bin/python -m featureliftbench.cli eval \
  benchmark/tasks/<task_id> \
  experiments/<run_id>/<task_id>/submission \
  --output experiments/<run_id>/<task_id>/eval-docker
```

正式 agent suite：

```bash
docker/build_agent_image.sh featureliftbench-agent:latest
docker/build_eval_image.sh featureliftbench-eval:latest

NUM_WORKERS=1 \
FEATURELIFTBENCH_AGENT_DOCKER=1 \
FEATURELIFTBENCH_EVAL_DOCKER=1 \
./run.sh
```
