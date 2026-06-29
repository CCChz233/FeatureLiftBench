# FeatureLiftBench 安全与稳定性验收标准

最后更新：2026-06-28

本文档定义安全加固完成后如何验收。验收重点是：eval 不打爆机器、正式结果可复现、agent 有明确边界、论文表述不夸大隔离能力。

## 1. 验收等级

| 等级 | 名称 | 用途 | 当前要求 |
| --- | --- | --- | --- |
| A0 | Local Dev | 维护者本地调试可信 oracle / 单题 | 允许非 Docker，不可作为论文正式结果 |
| A1 | Official Eval | 论文 baseline、模型对比、100 题正式统计 | **必须达到** |
| A2 | Bounded Agent Runs | 多模型长跑、共享机器、外部 agent 接入 | 建议达到；外部 agent 必须达到 |
| A3 | Hostile Public Service | 开放给任意用户提交代码 | 暂不要求，需单独安全设计 |

当前项目的最低目标：**A1 必须完成；A2 在引入外部 agent 或共享机器前完成；A3 不作为当前论文阻塞项。**

## 2. A1：Official Eval 验收

A1 通过后，才可以把结果称为 official eval / paper baseline。

### A1.1 Docker 边界

每次 submission eval 必须在短命 Docker container 中执行：

- 使用 `docker run --rm`，run 结束后容器删除。
- task mount 只读。
- submission mount 只读。
- harness mount 只读，或直接 baked into image。
- output mount 是唯一可写 host mount。
- 不挂载 host home、`.env`、SSH key、Docker socket、整个仓库根目录。
- eval container 默认 `--network none`。
- eval container 设置内存、CPU、进程数限制。
- eval container 使用 read-only root filesystem，并为 `/tmp` 提供有限 tmpfs。
- eval container 启用 `--cap-drop=ALL` 和 `--security-opt no-new-privileges`，除非有明确兼容性例外并记录。

推荐默认值：

```text
memory: 4g
memory-swap: 4g
cpus: 2
pids-limit: 256
tmpfs /tmp: 2g
nofile: 1024
network: none
```

### A1.2 离线依赖

- 在无 host pip cache、无网络的 Docker eval 中，100 题 oracle 全部通过。
- 非空 `requirements.lock` 的依赖来自镜像内预置 wheel 或已安装包。
- result 或 suite metadata 记录 eval image tag，最好记录 image digest。
- 官方实验说明中写明 Docker image 构建方式和依赖来源。

### A1.3 资源与日志保护

必须有专门的恶意/异常 fixture 验证以下情况：

| Fixture | 预期结果 |
| --- | --- |
| 无限循环 pytest | eval timeout，父进程继续运行 |
| 大内存分配 | container OOM 或 `resource_limited=true`，宿主机不 OOM |
| fork bomb / 多进程爆炸 | pids limit 生效，eval 失败但 suite 不崩 |
| stdout/stderr 大量输出 | 日志被截断或命令被终止，harness 内存不随输出无限增长 |
| 网络访问 | 在 eval container 内失败，不产生外网请求 |
| 写 task/repo/submission | 因只读 mount 失败 |
| 写 `/tmp` 大文件 | 受 tmpfs size 限制，不填满宿主磁盘 |
| 读取 host `.env` / home | 文件不存在或不可见 |

验收阈值：

- 所有 fixture 都必须返回结构化失败，不允许卡死整条 suite。
- fixture 运行后宿主机可继续执行下一条 eval。
- 结果中能区分 timeout、resource limit、log limit、sandbox error。

### A1.4 结果口径

正式模型结果必须满足以下任一条件：

- `run-agent` 直接使用 Docker eval backend。
- 或者 agent 只负责生成 submission，随后用 Docker re-eval 全量重算结果，论文统计只引用 re-eval。

不合格口径：

- 在 macOS 上用 local eval 直接作为 official baseline。
- 只设置 `EVAL_MEMORY_MB` 但没有 Docker/cgroup 边界。
- `featureliftbench eval --docker` 可用，但 suite 统计仍来自 local eval。

### A1.5 回归验收命令

验收时至少记录并保存以下命令输出：

```bash
docker build -t featureliftbench-eval:latest -f docker/Dockerfile.eval .
docker image inspect featureliftbench-eval:latest

PYTHONPATH=harness .venv/bin/python harness/scripts/verify_all_oracles.py benchmark/tasks
```

如果 `verify_all_oracles.py` 尚未接入 Docker eval，需要补一个 Docker oracle verification 命令或脚本。最终验收必须证明：

- 100/100 oracle pass under Docker eval。
- 0 unexpected dependency install failure。
- 0 undocumented resource/sandbox failure。
- local eval 与 Docker eval 的 functional status 一致；如有差异，必须有记录和解释。

## 3. A2：Bounded Agent Runs 验收

A2 目标是防止 agent 误改 benchmark 仓库或宿主机敏感文件。A2 可以通过 host-only 防护或 agent Docker 防护达成；外部 agent 接入时必须使用 Docker 或等价沙箱。

### A2.1 Host-only 最低验收

适用于维护者自己跑可信 agent 的过渡期。

- agent workspace 是 per-task copy，不包含 hidden tests 和 `evaluation/`。
- agent 进程 cwd 是 workspace，不是仓库根目录。
- agent 输出只从 `workspace/submission/` 收集。
- run 前记录仓库 clean baseline；run 后检查非 output 目录没有被修改。
- `.env` 没有被复制进 workspace。
- agent stdout/stderr/trajectory 不包含 API key 原文。
- timeout 后 agent process group 被终止。

验收 fixture：

- 用一个 dummy agent 尝试写 `../outside_workspace.txt`、仓库根目录 canary 文件、`benchmark/tasks` canary 文件。
- run 结束后，系统应检测到 workspace escape，或在 OS 权限层阻止写入。
- dummy agent 尝试读取 hidden tests，workspace 中应不存在 hidden tests。

Host-only A2 只能称为 **bounded maintainer run**，不能称为 hostile sandbox。

### A2.2 Agent Docker 验收

agent Docker 通过后，可以称为 container-bounded agent run。

每次 task run：

- 使用短命 agent container。
- prepared workspace 是主要可写 mount。
- agent output dir 可写。
- 不挂载 benchmark root。
- 不挂载 host home。
- 不挂载 Docker socket。
- Docker command 只包含 env key，不包含 API key value。
- stdout/stderr log 与 `run.json` 不包含 API key 原文。
- hidden tests 和 `evaluation/` 不在 container 内。
- 网络只用于模型 API；eval 仍在独立 eval container 里禁网执行。
- 设置 memory、CPU、pids、timeout。
- 容器退出后删除。

验收 fixture：

| Fixture | 预期结果 |
| --- | --- |
| agent 写 workspace 外路径 | 写不到 host benchmark，或只能写到容器内临时 FS |
| agent 读取 hidden tests | 路径不存在 |
| agent 打印 env | 日志不包含 API key 原文，或 runner 做 redaction |
| agent 死循环 | timeout 后容器删除，suite 可继续 |
| agent fork bomb | pids/memory limit 生效，宿主机稳定 |

最小验收命令：

```bash
docker/build_agent_image.sh featureliftbench-agent:latest
docker/build_eval_image.sh featureliftbench-eval:latest

PYTHONPATH=harness python3 -B -m featureliftbench.cli run-agent \
  benchmark/tasks/<task_id> \
  --agent command \
  --agent-command "<command that writes {submission_dir}>" \
  --agent-docker \
  --eval-docker \
  --output /tmp/flb-agent-docker-smoke
```

验收结果中必须同时出现 `agent_backend=docker` 与 `eval_backend=docker`。

### A2.3 agent 与 eval 分离

无论 agent 是否 Docker 化，hidden eval 都不能在 agent workspace 里执行。验收要求：

- agent container 不包含 hidden tests。
- agent container 不直接运行 official hidden eval。
- collected submission 复制出来后，由 eval container 独立评分。

## 4. A3：Hostile Public Service 验收

A3 暂不作为当前版本目标。进入 A3 前必须重新评审：

- rootless Docker 或 VM 级隔离。
- 无任何 host secret。
- 作业队列和并发限流。
- 磁盘 quota 和日志 quota。
- 网络 egress 策略。
- 运行后清理和审计。
- hidden test 防作弊策略。

特别说明：pytest in-process hidden tests 不能防止主动恶意 submission 通过 Python introspection 观察测试上下文。A3 若要求对抗式防作弊，需要单独设计测试执行模型，不能只靠 Docker。

## 5. 文档与论文表述验收

正式写论文或 README 时，允许的表述：

- "Official evaluation runs submissions in short-lived Docker containers with read-only mounts and resource limits."
- "FeatureLiftBench reports functional pass and extraction quality."
- "Agent runs are workspace-bounded; Docker-bounded agent execution is optional unless running untrusted agents."

不允许的表述：

- "Docker makes hidden tests impossible to inspect by malicious submissions."
- "Local macOS eval is resource isolated."
- "Agent cannot modify host files" unless agent Docker 或 OS 权限验收已通过。
- "100 tasks use 100 environments"。正确说法是 1 个 eval image，按次起短命容器。

## 6. Definition of Done

### A1 Done

- [ ] Hardened Docker eval flags 已实现。
- [ ] Docker eval 默认禁网。
- [ ] Docker eval 只有 output 是 host 可写 mount。
- [ ] Eval image 可离线跑 100 题 oracle。
- [ ] stdout/stderr 有上限，不会无限进内存。
- [ ] resource/log/sandbox failure 有结构化状态。
- [ ] `run-agent` 结果可直接 Docker eval，或有全量 Docker re-eval 流程。
- [ ] 100/100 oracle pass under Docker eval。
- [ ] 恶意 fixture 全部通过验收。
- [ ] 文档写明 Docker 保护范围和不保护范围。

### A2 Done

- [ ] agent workspace 不包含 hidden tests / `evaluation/`。
- [ ] agent run 前后有 workspace escape 检测，或 agent Docker 已实现。
- [ ] API key 不落入 workspace 或日志。
- [ ] agent timeout 能清理子进程或删除容器。
- [ ] 外部 agent 只能在 agent Docker 或等价沙箱中运行。
- [ ] agent 产物仍由独立 eval container 评分。

### A3 Done

- [ ] 单独 threat model 已完成。
- [ ] rootless/container sandbox/VM 方案已选型。
- [ ] secrets、network、quota、queue、audit、cleanup 全部有验收 fixture。
- [ ] hidden-test 防作弊边界已重新设计或明确声明非目标。
