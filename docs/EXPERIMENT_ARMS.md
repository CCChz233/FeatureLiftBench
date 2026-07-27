# FeatureLiftBench 实验臂

状态：2026-07-27，适用于 Python External-150 v3。

上位规则：[BENCHMARK_DESIGN.md](BENCHMARK_DESIGN.md) ·
[TASK_DESIGN_RULES.md](TASK_DESIGN_RULES.md)

## 共同不变量

所有正式对照必须使用相同的：

- task revision、完整功能契约和输出 API；
- canonical upstream revision 与 evaluator freeze；
- public、hidden、isolation、forbidden 和 compactness evaluator；
- 模型、上下文预算、最大步数、Docker 环境和每题一次尝试。

每条 run 必须记录 `ablation_arm`、`spec_hash`、`task_revision`、
`source_repo_id`、`source_digest`、`snapshot_scope`、测试与定位提示可见性、
模型/profile、镜像 ID 和 benchmark freeze。一次只改变一个预注册变量。

## Main：正式主榜

| 项 | 设定 |
| --- | --- |
| Source context | 完整 pinned upstream tracked tree |
| TASK | 从 `public_spec` 生成的完整功能契约 |
| Source hints | 不提供 entrypoints、文件路径、符号或目标闭包 |
| Benchmark tests | public 和 hidden 均不进入 Agent workspace |
| Submission evaluation | public + hidden + isolation + forbidden + compactness |

上游仓库自身的 tests、docs 和 examples 属于完整源码的一部分，保持可见。
Agent 需要自行定位实现、发现或编写验证用例、完成剥离并提交独立包。

```bash
./run_experiment.sh --arm main \
  --tasks transitions__state_machine_core__hard3_001
```

正式 Python-150 运行使用
[SERVER_RUNBOOK_PYTHON150.md](SERVER_RUNBOOK_PYTHON150.md)。

## Entrypoint-Hint：定位消融

唯一变化：向 Agent 明确提供预先冻结的 source entrypoints。其余 source、
契约、测试盲性、环境与 evaluator 均与 Main 相同。

用途：分离源码定位难度与理解、闭包恢复、重构和验证难度。

```bash
./run_experiment.sh --arm entrypoint_hint \
  --tasks transitions__state_machine_core__hard3_001
```

该臂必须记录 `expose_source_hints=true`，不能混入 Main。

## Public-feedback：测试反馈消融

唯一变化：把 benchmark public tests 复制进 Agent workspace，并允许 Agent
在提交前运行。hidden tests 始终不可见。

用途：测量显式评分测试反馈带来的收益，以及 test-fitting 和停止行为变化。
它不是正式主榜。

```bash
./run_experiment.sh --arm public_feedback \
  --tasks transitions__state_machine_core__hard3_001
```

该臂必须记录 `mount_public_tests=true`。交卷后仍运行与 Main 完全相同的
evaluator。

## Short-prompt：提示文风消融

唯一变化：压缩流程性说明；保留完整功能契约、输出 API、约束、forbidden、
完整仓库、No-Hint 和测试盲性。

```bash
./run_experiment.sh --arm short_prompt \
  --tasks iniconfig__parse_config__001
```

该臂必须记录 `prompt_style=short`。

## Pruned-Context：源码范围消融

唯一变化：将完整仓库替换为预先冻结的目标相关裁剪 snapshot。是否提供定位
提示必须另行固定，不能同时变化。

用途：测量完整仓库搜索负担。Pruned-Context 不是 v3 Main，也不能与 Main
汇总为同一 headline。

该臂从独立冻结的
[`benchmark/sources/pruned_registry.json`](../benchmark/sources/pruned_registry.json)
物化源码，仍保持 No-Hint、test-blind、相同契约和相同 evaluator。当前已
导入的旧 Python-150 模型结果属于 `mixed_snapshot_v1`，还混有
Agent-visible entrypoint metadata；它们只能作为历史证据，不能冒充纯
Pruned-Context 或 v3 Main。

## 推荐最小矩阵

| Arm | 研究问题 |
| --- | --- |
| Main | 完整仓库、无提示、测试盲条件下的端到端能力 |
| Entrypoint-Hint | localization 提示的收益 |
| Public-feedback | benchmark 测试反馈的收益 |
| Short-prompt | 流程提示文风的影响 |
| Pruned-Context | 仓库搜索范围的影响 |

先完成 active v3 freeze 上的全量 Main baseline，再在预注册子集上做消融。
同一比较必须报告 Functional Pass@1、各 evaluator gate、steps、tokens、时长
和失败类型。

## 结果版本边界

| 结果 | 可使用的表述 |
| --- | --- |
| historical legacy | 旧双轨规格或旧 evaluator；只作历史结果 |
| `mixed_snapshot_v1` | 150 题规格合规，但源码范围混合且暴露 entrypoints |
| v3 Main | Full-Repository + No-Hint + test-blind + active v3 freeze |

旧 `no_public` 只证明评分测试未挂载，不自动证明完整仓库或 No-Hint。任何
结果必须按实际 source context、entrypoint visibility、test visibility 和
freeze 分报。
