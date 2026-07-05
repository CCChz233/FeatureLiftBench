# Go Track 实验协议（与 Python 分离）

**最后更新：** 2026-07-05

Go v2 gold track 的 **agent 实验**与 Python v1.1 主榜**分开目录、分开 agent、分开报告**。decoupling 语义与打分公式与 Python 相同。

政策：[GO_EXPANSION.md](GO_EXPANSION.md) · 出题 gate：[GO_PILOT_PLAYBOOK.md](GO_PILOT_PLAYBOOK.md) · 验收：[go_pilot_acceptance_report.md](go_pilot_acceptance_report.md)

---

## 1. 与 Python 主榜对比

| 维度 | Python v1.1 | Go v2 hard gold |
| --- | --- | --- |
| 数据集 | `benchmark/tasks/`（100 hard） | `benchmark/go/tasks/`（目标 10 hard gold；calibration 单独列） |
| Agent | **mini-swe-agent** | **OpenHands** headless |
| 模型（当前） | `deepseek/deepseek-v4-flash` 等 | `deepseek/deepseek-v4-flash` |
| 步数上限 | `MSWEA_GLOBAL_CALL_LIMIT`（profile） | OpenHands `max_iterations` **≤120** |
| Submission | `submission/featurelifted/` | `submission/*.go` + `go.mod` |
| 开发测试 | `pytest public_tests/` | `go test ./public_tests/...` |
| Eval | Docker `featureliftbench-eval:latest` | 同镜像（含 Go 1.22） |
| Agent 实验输出 | `experiments/mini-swe-agent/` | `experiments/go-openhands/` |
| 出题 / oracle gate | `experiments/batch1/` | `experiments/go-pilot/` |
| 机械 baseline | oracle / naive / copy_all | 同概念，Go submissions |

**禁止：** 将 Go run 写入 `experiments/mini-swe-agent/`；论文中混表 Python 与 Go 主榜数字。

---

## 2. 固定实验卡（OpenHands）

| 项 | 值 |
| --- | --- |
| Agent | OpenHands `--headless --exit-without-confirmation --override-with-envs` |
| Model | `LLM_MODEL=deepseek/deepseek-v4-flash` |
| API | `.env` 或 `~/.openhands/settings.json` |
| Max steps | **120**（OpenHands settings） |
| Eval | `featureliftbench.cli run-agent ... --eval-docker` |
| Output | `experiments/go-openhands/<run_id>/` |
| 题目范围 | 仅 **gold-ready**（真 repo 切片；非 hello `Add()` 模板） |

### 单题命令（WSL）

```bash
cd /mnt/d/Workspace/FeatureLiftBench
source .venv/bin/activate
export PYTHONPATH=harness
export LLM_MODEL=deepseek/deepseek-v4-flash

bash harness/scripts/run_go_openhands.sh <task_id> [run_id]
```

### 跑前自检

```bash
bash harness/scripts/preflight_go_openhands.sh
# Windows（无 WSL）：python harness/scripts/preflight_go_openhands.py
```

**PIPELINE_SMOKE**（无 OpenHands 时验证 harness 闭环，非 LLM agent）：

```bash
PIPELINE_SMOKE=1 bash harness/scripts/run_go_openhands.sh semver__version_parse_core__001
```

Windows + Docker Desktop：可用 `PYTHONPATH=harness python -m featureliftbench.cli run-agent ... --eval-docker`（见 `go_copy_naive_agent.py` 代理脚本）。

---

## 3. 产物布局

```text
experiments/go-openhands/<run_id>/
  run.json              # 汇总：agent + submission + evaluation
  workspace/            # agent 可见工作区（repo、public_tests、TASK.md）
  submission/           # 收集的 Go 模块
  eval/result.json      # Docker 测评
  agent/                # OpenHands stdout/stderr
```

出题证据（与 agent 实验分离）：

```text
experiments/go-pilot/<task_id>/review/
  gate_report.json
  oracle/naive/copy_all/result.json
  flash/run.json        # OpenHands run 摘要（真跑或 PIPELINE_SMOKE；用 sync_go_openhands_flash.py 同步）
```

---

## 4. 验收标准

### 4.1 流程通

- `run.json` → `submission.exists == true`
- `eval/result.json` 存在，`build_pass` 有明确结果
- 无 harness 级错误（路径、Docker、metadata）

### 4.2 难度（Flash 分层）

| Tier | 条件 | 含义 |
| --- | --- | --- |
| **A** | public ✓、hidden ✗ | 理想 hard 信号：hidden 有判别力 |
| **B-hard** | hidden ✓，但 footprint compact、非 oracle、明显低于 copy_all | 可进 hard review，需披露 |
| **B-calibration** | hidden ✓ 且 oracle footprint，或 hidden ✓ 且接近 copy_all | 只计 calibration |
| **C** | 低 extraction、硬编码或流程失败 | redesign/drop |

对照：`naive` baseline 应为 public ✓、hidden ✗（见 `go-pilot` gate）。`PIPELINE_SMOKE=1` 只验证 harness，不计入 Flash tier。

---

## 5. 三类 baseline（Go 专用）

| Baseline | 命令 | LLM |
| --- | --- | --- |
| copy_all | `bash harness/scripts/run_go_baseline.sh copy_all` | 无 |
| OpenHands | `bash harness/scripts/run_go_openhands.sh <task_id>` | 是 |
| oracle / naive | `run_go_pilot_review.sh` | 无 |

---

## 6. 相关脚本

| 脚本 | 作用 |
| --- | --- |
| [run_go_openhands.sh](../harness/scripts/run_go_openhands.sh) | OpenHands + Docker eval |
| [run_go_pilot_review.sh](../harness/scripts/run_go_pilot_review.sh) | 出题 gate（oracle/naive/copy_all） |
| [run_go_baseline.sh](../harness/scripts/run_go_baseline.sh) | copy_all / mini（Go 上 mini 仅作对照，非主 agent） |
| [preflight_go_openhands.sh](../harness/scripts/preflight_go_openhands.sh) | 跑前自检（bash） |
| [preflight_go_openhands.py](../harness/scripts/preflight_go_openhands.py) | 跑前自检（Windows/cross-platform） |
| [go_copy_naive_agent.py](../harness/scripts/go_copy_naive_agent.py) | PIPELINE_SMOKE 代理（非 OpenHands） |
| [sync_go_openhands_flash.py](../harness/scripts/sync_go_openhands_flash.py) | OpenHands run → go-pilot flash 证据 |
