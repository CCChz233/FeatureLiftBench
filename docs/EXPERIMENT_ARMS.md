# FeatureLiftBench 实验臂（Ablation Arms）

- **状态：** v1.1（2026-07-24，test-blind Main）
- **上位：** [BENCHMARK_DESIGN.md](BENCHMARK_DESIGN.md) · [TASK_DESIGN_RULES.md](TASK_DESIGN_RULES.md) §6
- **原则：** 臂之间只改变 Agent **反馈与文风**；**不改变**语义契约与 evaluator。

---

## 1. 共同不变量（所有臂）

不得在臂之间修改：

- `required_api` / `optional_api` / behaviors / exclusions  
- `source_entrypoints` / forbidden  
- 任务包内 `public_tests/`、`hidden_tests/` 内容  
- evaluator 门控与打分公式  
- pinned `repo/` commit  

否则不是 ablation，而是不同任务。

每条 run 必须记录：`ablation_arm`、`spec_hash`、`task_revision`。

---

## 2. Main（默认主榜：评分测试全盲）

| 项 | 设定 |
| --- | --- |
| Agent workspace | 不挂载任何 Benchmark evaluator tests |
| TASK | 由 `public_spec` 生成的标准文案 |
| 交卷后 eval | public + hidden + isolation + … |

`repo/` 中属于 pinned 上游快照的 tests/docs/examples 保持可见。Agent 可以
自己发现、改写或新建测试并运行，但不能获得 Benchmark 自建评分测试。

用途：正式能力报告；测“完整功能契约 + 仓库证据 → 自主剥离与自测”。

---

## 3. Public-feedback（显式给基础评分测试反馈）

### 3.1 目的

量化直接暴露基础评分测试对通过率、停止行为与 test-fitting 的影响。
它不是正式主榜默认。

### 3.2 怎么跑（已实现）

推荐用仓库根目录的相对路径入口（任意机器克隆后可直接跑）：

```bash
./run_experiment.sh --arm public_feedback \
  --tasks transitions__state_machine_core__hard3_001

# 三臂对照（同 tasks，顺序跑）
./run_experiment.sh --compare-arms main,public_feedback,short_prompt \
  --tasks iniconfig__parse_config__001,transitions__state_machine_core__hard3_001
```

等价手写 CLI：

```bash
# Profile
PYTHONPATH=harness python -m featureliftbench.cli run-agent benchmark/tasks \
  --agent openhands-agent \
  --agent-config harness/config/agents.example.toml \
  --agent-profile openhands_deepseek_v4_flash_public_feedback \
  --env-file .env \
  --agent-docker --agent-docker-image featureliftbench-agent:openhands-rsg-pilot-v1 \
  --eval-docker \
  --task-id transitions__state_machine_core__hard3_001 \
  --output experiments/ablation/public_feedback_demo

# 或 CLI 覆盖任意 profile
... --agent-profile openhands_deepseek_v4_flash_main --agent-public-tests
```

`run.json` 含 `"ablation": {"ablation_arm": "public_feedback", "mount_public_tests": true, ...}`。

### 3.3 Agent 侧

| 项 | 设定 |
| --- | --- |
| `public_tests/` | 显式复制进 workspace |
| Go `run_public_tests.sh` | 生成 |
| TASK / OpenHands 外层 | 允许运行基础 evaluator tests |
| 配置 | `mount_public_tests = true` 或 `--agent-public-tests` |

### 3.4 Evaluator 侧（不变）

交卷后仍跑相同的 public + hidden + isolation / forbidden / compactness。

### 3.5 实现落点

- `harness/featureliftbench/ablation.py`
- `prepare_agent_workspace(..., ablation=)`
- `build_task_prompt` / `_build_openhands_prompt`
- profile 字段 + CLI；`agent_config` summary / `run.json` 记录臂名

**Main 严谨表述：**

> 任务包中的 public/hidden 均保留为 evaluator 资产；默认 Main 在 Agent
> workspace 中不复制、不挂载、不可访问。`repo/` 内的上游 tests 不属于
> evaluator 资产，保持可见。交卷后 evaluator 运行同一组 public 和 hidden。

Validate 目标还包括：Main workspace 中不存在 evaluator tests；symlink、
环境变量、缓存和日志均不能间接访问；Main 与 Public-feedback 使用相同
`public_spec` 与 evaluator。

**历史兼容：** 旧 `no_public` 名称等价于新的 test-blind Main；旧 Main
结果实际上属于现在的 Public-feedback 条件，报告时必须重标，不能与新 Main
拼接。

### 3.6 对照解读

| 现象 | 可能含义 |
| --- | --- |
| Public-feedback 更高 | Agent 依赖 Benchmark 测试反馈完成契约 |
| 两臂都 basic✓ hidden✗ | 瓶颈仍在契约深度 |
| 两臂无差异 | Agent 已能从契约、源码和自建测试完成 |

---

## 4. Short-prompt

### 4.1 怎么跑（已实现）

```bash
./run_experiment.sh --arm short_prompt --tasks iniconfig__parse_config__001
```

等价手写 CLI：

```bash
PYTHONPATH=harness python -m featureliftbench.cli run-agent benchmark/tasks \
  --agent openhands-agent \
  --agent-config harness/config/agents.example.toml \
  --agent-profile openhands_deepseek_v4_flash_short_prompt \
  --env-file .env \
  --agent-docker --agent-docker-image featureliftbench-agent:openhands-rsg-pilot-v1 \
  --eval-docker \
  --task-id iniconfig__parse_config__001 \
  --output experiments/ablation/short_prompt_demo

# 或
... --prompt-style short
```

### 4.2 设定

| 项 | 设定 |
| --- | --- |
| 改变 | 删除 Closure Discipline / Entanglement；How-to 压缩 |
| 保留 | Source、Target Feature、Required Output API、Constraints、forbidden |
| public 挂载 | 不挂载（与 test-blind Main 相同） |
| 配置 | `prompt_style = "short"` |

可与 Public-feedback 组合：`--agent-public-tests --prompt-style short` →
`ablation_arm=public_feedback_short`。

---

## 5. 推荐对照矩阵

最小有信息量集合：

| 条件 | 目的 |
| --- | --- |
| Main | 基线 |
| Public-feedback | 增加 Benchmark 基础测试反馈 |
| Short-prompt | 去流程说教 |
| （可选）Oracle Closure 上界 | 验证「给对闭包信息」的天花板 |

同一模型、同一 task 子集、记录 token/steps/gates。

---

## 6. 与规格迁移的关系

Public-feedback / Short-prompt **不替代** `public_spec` 合规。

| 主榜口径 | 说明 |
| --- | --- |
| **historical legacy runs** | 历史双轨规格结果保留，但 headline 须标 legacy |
| **compliant（150 题）** | `public_spec` + 宪法 validate + Oracle 复验；当前主榜统一口径 |

优先：独立人工审核 + 新合规 core-100 rebaseline → 再解读全量臂效应。

操作：[CONSTITUTION_MIGRATION.md](CONSTITUTION_MIGRATION.md)
