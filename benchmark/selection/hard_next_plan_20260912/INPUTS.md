# 执行前备齐什么

本目录是方案包，不能单独代替 FeatureLiftBench 仓库、历史结果、源码或 Docker 镜像。路径以下均相对仓库根目录；服务器根路径可以不同。

## 已有输入

| 输入 | 当前本地位置 | 用途 |
|---|---|---|
| 原三题服务器结果 | `experiments/workflow-hard-pilot-20260912-flash-main-r1-results.tar.gz` | 复核三题提交与旧运行条件 |
| 本轮历史分析 | `reports/workflow_hard3_review_20260912/ANALYSIS.md` | 判断依据与已知局限 |
| 证据索引/复算脚本 | 同目录 `evidence.json`、`build_evidence.py` | 追溯历史数据与输入 hash |
| Flash 历史运行 | `experiments/python/openhands/deepseek-v4-flash/python200-prime-v2-main-r1/` | 六例当时题面、submission、run/result、日志及 source workspace |
| Luna 历史运行 | `experiments/python/openhands/gpt-5.6-luna/python200-prime-v2-main-r1/` | 第二模型历史对照；不能冒充本轮新运行 |
| 旧三题创建资产 | `benchmark/selection/workflow_hard_pilot_20260912/` | P0 canary 物化与对照 |
| 旧三题来源注册 | `benchmark/sources/workflow_hard_pilot_registry.json` | 定位旧三题 pinned sources；新研究使用独立注册文件 |
| 原服务器私有 overlay | `exports/server-overlays/workflow-hard-pilot-20260912T102722Z.tar.gz` 与相邻输入锁/校验文件 | 已有可迁移的旧三题维护者资产；先校验再使用 |
| 当前仓库规范 | `.agents/skills/featureliftbench-{create,validate}-task/`、`featureliftbench-run-eval/`；`docs/TASK_DESIGN_RULES.md`、`docs/FULL_REPOSITORY_SOURCE_POLICY.md` | 按现行结构创建和审查研究任务 |

原三题结果包 SHA-256：`7fbba9fb3b107bcc46348d9854a3ba5fc2ff34a66cba25ce688c04d200172855`。

历史目录名不保证统一 freeze 或真实服务端模型版本。每个案例必须读取该次 run 的绑定信息；不要把当前 `benchmark/tasks/` 直接当作当年输入复制。
历史 `workspace/repo` 可用于代码取证，但不能自动当作满足 Main 完整来源政策的源码归档；P0/P2 仍须建立可验证 snapshot 绑定。

这些大文件有部分未纳入 Git；仅 checkout 当前提交不会自动带上它们。缺项先从原服务器/维护者归档找回并核对 hash。恢复不了的原版标记 missing，不用相近版本替代，不运行该对照。

## 在服务器新建的输出

建议使用独立 checkout，并把各阶段结果放在：

```text
experiments/calibration/hard_mechanism_study/
  environment.json
  P0/                         # canary、配置和上下文审计
  P1/<case_id>/case_card.json  # 六例证据卡、审查意见
  P2/                         # 版本差异、锁、逐次运行、判读
  P3/<candidate_id>/          # 来源、消费者、三类基线与审查
  P4/                         # 新题 Flash/第二模型结果
  decisions/                  # 每阶段阶段结论
```

研究题包只放 `benchmark/staging/<new_task_id>/`；source/reference 注册、无密钥 profile 的建议位置见执行手册。
模板应复制到上述结果目录再填写，保留原模板；计划矩阵在开始前复制为 execution matrix，填入实际输入锁、跳过原因和运行顺序并封存。

维护者材料包含 hidden、参考解和源码入口取证；这些文件不能放进 agent 可见 workspace 或提示词。只通过 harness 提供该实验臂允许的 TASK 和完整上游源码。

## 阶段如何交接

每阶段填写 `templates/stage_decision.md`，给出继续/停止/补充证据的明确结论。P0 与 P1 的只读证据审查可以并行推进；P2 模型实验必须等待二者完成。
若停止，已有失败尝试、排除理由和输入版本仍交付。方案上限不是必须跑满的配额。
