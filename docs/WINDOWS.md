# Windows 上运行 FeatureLiftBench

本文档说明在 **Windows 10/11** 上跑实验的完整流程。项目 harness 面向 **Linux/bash**；Windows 上请通过 **WSL2 + Docker Desktop** 执行，**不要**在 PowerShell 里直接跑 `./run.sh` 或 `.venv\Scripts\python`。

相关：[SETUP.md](SETUP.md) · [RUN.md](../RUN.md) · [SERVER_DEPLOY.md](SERVER_DEPLOY.md)

最后更新：2026-07-03

---

## 1. 和 Linux 服务器差在哪？

| 方面 | Linux 服务器 | Windows（推荐做法） |
| --- | --- | --- |
| Shell | bash 直接跑 | **WSL Ubuntu** 里跑 bash |
| Python venv | `.venv/bin/python` | 同样在 WSL 里用 `.venv/bin/python` |
| Docker | `docker` 命令 | Docker Desktop + `wsl_docker_setup.sh` 包装 |
| 仓库路径 | `/path/to/FeatureLiftBench` | `/mnt/d/Workspace/FeatureLiftBench`（盘符对应 `/mnt/<盘符>/`） |
| 终端实时进度 | Rich 进度条（需 TTY） | 后台跑时**无**进度条；日志在 `experiments/` 目录 |
| 原生 PowerShell | — | **不支持**（见下文 §6） |

**结论**：在 WSL 里执行的命令，与 Linux 文档里写的**基本一致**；差别主要在「如何进入 WSL」和「Docker 路径适配」。

---

## 2. 前置条件

1. **WSL2**，已安装 **Ubuntu**（`wsl -l -v` 可看到 `Ubuntu`）。
2. **Docker Desktop**，开启 *Use the WSL 2 based engine*，并为 Ubuntu 分发启用集成。
3. 仓库克隆在 Windows 盘上即可（如 `D:\Workspace\FeatureLiftBench`），WSL 内路径为 `/mnt/d/Workspace/FeatureLiftBench`。

验证：

```powershell
# PowerShell
wsl -d Ubuntu -e bash -lc "docker info >/dev/null && echo docker_ok"
```

---

## 3. 一次性安装（在 WSL 里）

每次新开 WSL 终端，建议先进入仓库并加载 Docker 包装：

```bash
cd /mnt/d/Workspace/FeatureLiftBench   # 按你的盘符改

# 修复 Windows 检出带来的 CRLF（仅需一次或 git pull 后）
sed -i 's/\r$//' setup.sh run.sh run_smoke.sh start_run.sh harness/scripts/*.sh docker/*.sh 2>/dev/null || true

./setup.sh
nano .env    # 填入 API Key，见 .env.example

source harness/scripts/wsl_docker_setup.sh
docker/build_agent_image.sh featureliftbench-agent:latest
docker/build_eval_image.sh featureliftbench-eval:latest
```

开跑前检查：

```bash
export PYTHONPATH=harness
.venv/bin/python harness/scripts/preflight.py \
  --bootstrap \
  --agent-profile deepseek_v4_flash \
  --docker-suite \
  --mini-bin .venv/bin/mini
```

---

## 4. 常用命令（WSL 内）

与 [RUN.md](../RUN.md) 相同，但**每条命令前**建议：

```bash
cd /mnt/d/Workspace/FeatureLiftBench
source harness/scripts/wsl_docker_setup.sh
export PYTHONPATH=harness
```

### 4.0 首次打开 Ubuntu 终端：创建 Linux 用户

若终端停在 `Create a default Unix user account:`，说明 Ubuntu 正在**首次初始化**：

1. 在该终端输入**英文用户名**（如 `flbuser`，小写、无空格）
2. 设置密码并再输入一次（输入时不显示字符，属正常）
3. 完成后关闭该终端，**新建终端**再试

若不想创建用户，可用 root 登录（与项目此前后台跑法一致）：

```powershell
wsl -d Ubuntu -u root
```

Cursor 终端配置建议使用 `wsl.exe` 参数 `["-d", "Ubuntu", "-u", "root"]`，不要用 `bash.exe -d Ubuntu`（`-d` 是 wsl 的参数）。

### 4.1 单题 smoke

```bash
bash run_smoke.sh
```

或手动：

```bash
.venv/bin/python -B -m featureliftbench.cli run-agent \
  benchmark/sanity/iniconfig__parse_config__001 \
  --agent mini-swe-agent \
  --agent-config harness/config/agents.toml \
  --agent-profile deepseek_v4_flash \
  --env-file .env \
  --yolo \
  --agent-docker \
  --eval-docker \
  --output "experiments/mini-swe-agent/smoke-$(date +%Y%m%d-%H%M%S)"
```

### 4.2 全量 100 题（主榜）

**前台**（可看 Rich 进度条，需保持终端不关）：

```bash
FEATURELIFTBENCH_AGENT_DOCKER=1 \
FEATURELIFTBENCH_EVAL_DOCKER=1 \
AGENT_PROFILE=deepseek_v4_flash \
NUM_WORKERS=1 \
RETRY_RATE_LIMIT=5 \
RUN_ID=benchmark-main-flash-$(date +%Y%m%d-%H%M%S) \
./run.sh
```

**后台**（推荐长跑；生成总日志文件）：

```bash
bash start_run.sh
# 默认：Flash + Docker + NUM_WORKERS=1 + RETRY_RATE_LIMIT=5
# 输出：experiments/mini-swe-agent/<RUN_ID>.log
```

自定义 profile / RUN_ID：

```bash
AGENT_PROFILE=deepseek_v4_pro RUN_ID=my-run-001 bash start_run.sh
```

### 4.3 续跑（中断后接上）

与 [RUN.md](../RUN.md) §4 相同：**必须用同一 `RUN_ID` 目录**，`passed` 题跳过，失败/无提交/未评测题重跑。

**WSL 内前台续跑：**

```bash
RESUME_DIR=experiments/mini-swe-agent/<RUN_ID> \
FEATURELIFTBENCH_AGENT_DOCKER=1 \
FEATURELIFTBENCH_EVAL_DOCKER=1 \
AGENT_PROFILE=deepseek_v4_flash \
./run.sh
```

**推荐：后台续跑（关 Cursor 也不停）**

项目根目录有 `resume_run.sh` 模板——把 `RESUME_DIR` 改成你的 run 目录后：

```bash
# 编辑 resume_run.sh 里的 RESUME_DIR，然后：
nohup bash resume_run.sh &
```

或 PowerShell 一行：

```powershell
wsl -d Ubuntu -u root bash -c "cd /mnt/d/Workspace/FeatureLiftBench && sed -i 's/\r$//' resume_run.sh run.sh && nohup bash resume_run.sh </dev/null >/dev/null 2>&1 &"
```

续跑日志默认追加到 `experiments/mini-swe-agent/<RUN_ID>-resume.log`。

**续跑前：**

```powershell
wsl -d Ubuntu -u root bash -c "cd /mnt/d/Workspace/FeatureLiftBench && bash harness/scripts/check_run_health.sh experiments/mini-swe-agent/<RUN_ID>"
```

若 `.run.lock` 残留且无进程：`rmdir experiments/mini-swe-agent/<RUN_ID>/.run.lock`（在 WSL 里执行）。

**勿用** `bash run.sh | head` 或会提前关闭管道的命令——会误杀长跑进程（见 [RUN.md](../RUN.md) §3.1）。

---

## 5. 日志在哪里？怎么查看？

日志**文件结构**与 Linux **完全相同**；差别是 Windows 后台跑时**终端里看不到** Rich 实时进度条。

### 5.1 目录结构

```text
experiments/mini-swe-agent/<RUN_ID>/
  suite.json              # 总进度（长跑中会带 checkpoint: true）
  <task_id>/
    run.json              # 单题摘要
    agent/stdout.log      # agent 标准输出（mini 步进、token 等）
    agent/stderr.log
    agent/trajectory.json # 完整对话轨迹
    submission/
    eval/result.json
    eval/logs/            # pytest 等评测日志
```

用 **资源管理器** 打开（与 WSL 路径等价）：

```text
D:\Workspace\FeatureLiftBench\experiments\mini-swe-agent\<RUN_ID>\
```

在 Cursor / VS Code 中直接打开上述文件即可查看。

### 5.2 后台跑时的总日志

若用 `start_run.sh` 启动，另有汇总日志：

```text
experiments/mini-swe-agent/<RUN_ID>.log
```

跟踪：

```bash
tail -f experiments/mini-swe-agent/<RUN_ID>.log
```

若直接用 `./run.sh` 前台跑，输出在终端；若从 PowerShell 包一层 `wsl bash -c "..."` 且未重定向，**可能没有**顶层 `.log` 文件——此时以各题 `agent/stdout.log` 和 `suite.json` 为准。

### 5.3 进度与健康检查

```bash
bash harness/scripts/check_run_health.sh \
  experiments/mini-swe-agent/<RUN_ID>
```

输出包括：已完成题数、`suite.json` checkpoint、`.run.lock` 持有者、活跃 `run-agent` 进程、`flb-*` 容器。

### 5.4 为什么终端「和 Linux 不一样」？

| 现象 | 原因 |
| --- | --- |
| 没有进度条 | Rich Live 需要交互式 TTY；`nohup` / `wsl bash -c` 后台无 TTY |
| PowerShell 里 `tail` 不好用 | 用 WSL 的 `tail -f`，或在 IDE 里打开日志文件 |
| 看不到 API 调用 | 看 `agent/trajectory.json` 或 `run.json` 里的 `agent.usage` |

---

## 6. 不支持原生 Windows 的原因

在 **PowerShell + 本机 Python** 下运行会失败，例如：

```text
ModuleNotFoundError: No module named 'resource'
```

`harness/featureliftbench/resource_limits.py` 依赖 Unix 的 `resource` 模块；且 `.venv` 由 WSL 创建时为 Linux 布局（`bin/python`），无 `Scripts\python.exe`。

**请勿**在 PowerShell 中执行：

```powershell
.\run.sh                          # 无法运行 bash 脚本
.\.venv\Scripts\python.exe ...    # venv 通常不存在此路径
python -m featureliftbench.cli    # 缺 resource 模块
```

从 PowerShell **仅用于进入 WSL**：

```powershell
wsl -d Ubuntu
```

---

## 7. `wsl_docker_setup.sh` 做什么？

WSL 内默认的 `docker` 可能连不上 Docker Desktop daemon，或把 `/mnt/d/...` 路径传给 `docker.exe` 时格式不对。该脚本会：

1. 在 `~/.flb-docker-bin/docker` 生成包装脚本，调用 Windows 的 `docker.exe`；
2. 将 `/mnt/<盘符>/...` 转为 `/<盘符>/...` 供卷挂载使用；
3. 清理 Windows 侧可能污染的 `PYTHONPATH` 环境变量。

`run.sh` 在检测到 WSL（`/proc/version` 含 Microsoft）时会**自动 source** 此脚本；手动跑 CLI 时仍需自行 `source`。

---

## 8. 故障排查

| 症状 | 处理 |
| --- | --- |
| `pipefail: invalid option` | 脚本为 CRLF：`sed -i 's/\r$//' <script>.sh` |
| `docker info` 失败 | 启动 Docker Desktop；WSL 内 `source harness/scripts/wsl_docker_setup.sh` |
| `another suite run holds .run.lock` | 确认无残留进程；若已崩溃：`rmdir experiments/.../<RUN_ID>/.run.lock` |
| eval/agent 挂载路径错误 | 确保在 WSL 内从 `/mnt/...` 路径运行，并已 source docker 包装 |
| `nohup` 后立刻退出 | 在 WSL **内部**执行 `bash start_run.sh`，不要仅用 `wsl -e ...` 且父 shell 立即结束 |
| API 未调用 | 确认用了 `run-agent` / `run_smoke.sh`，不是仅 `eval`；检查 `.env` 与 `--agent-profile` |

环境一键检查（可选）：

```bash
bash check_env.sh
```

---

## 9. 与 Linux 文档的对照

| 文档 | Windows 用户 |
| --- | --- |
| [SETUP.md](SETUP.md) | 安装项相同，在 WSL 内执行 `./setup.sh` |
| [RUN.md](../RUN.md) | 命令相同，加 §3 的前置 `source` |
| [SERVER_DEPLOY.md](SERVER_DEPLOY.md) | 服务器专用；Windows 本地跑可忽略 tmux 部分 |
| 本文 | **Windows 必读** |
