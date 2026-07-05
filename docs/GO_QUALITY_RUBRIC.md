# Go Track 质量评审 Rubric

**最后更新：** 2026-07-05

Go staging 题进入 hard paper-ready 集合前的客观标准。机械 gate 以 [GO_PILOT_PLAYBOOK.md](GO_PILOT_PLAYBOOK.md) 为准；本文说明**为什么**以及**一票否决**项。

Python 对照：[BATCH1_QUALITY_RUBRIC.md](BATCH1_QUALITY_RUBRIC.md)

---

## 适用范围

- `benchmark/go/staging/<task_id>/`
- `benchmark/go/tasks/<task_id>/`（promote 后复核）

---

## Immediate Rejects

| Reject | 含义 |
| --- | --- |
| 弱源仓库 | 玩具 repo、无法 pin、license 不清、无可信 standalone slice |
| 仓库过密 | 同 repo 已有 2 题且无书面例外 |
| 无 design spike | 没有 `docs/go_task_designs/<task_id>.md`，或 Practical reuse 三问答不清 |
| 文件边界抽取 | oracle 只是复制一组完整 `.go` 文件并改 package name；agent 可通过文件选择直接等于 oracle |
| 隐性文件提示 | 文件名、注释、TASK 或 public tests 暗示哪些文件是 target / non-target |
| 无 oracle | submission 缺失或 eval 失败 |
| 无浅层判别 | naive 未 public pass + hidden fail |
| 无 copy 判别 | copy_all 失败或与 oracle extraction 拉不开 |
| 非确定性 | 网络、墙钟、随机、locale、本机路径 |
| Hidden 重复 public | hidden 仅重复 public 快乐路径 |
| 薄玩具题 | oracle 单文件 wrapper，无 hard 理由 |
| 范围失控 | oracle 需 vendor 大半源仓 |
| Forbidden import | submission 依赖原 module path |
| 弱 Flash | C 档、oracle-footprint hidden pass、或 copy_all-footprint hidden pass |
| 缺证据 | 无 `gate_report.json`、probe 日志或 result.json |
| cgo / 特权 | 需要 cgo 或 Docker 特权（Phase 0–2 禁止） |

---

## Hard Boundary Rule

Go hard 题的边界必须是 **symbol / behavior boundary**，不是文件边界。

必须满足：

- 至少两个源文件同时包含 target 和 non-target 代码。
- oracle 需要裁剪、重组或改写函数 / 方法 / 类型，而不是整文件复制。
- copy_all 可以 functional pass，但 extraction 必须明显高于 oracle。
- public tests 描述目标 API 和主路径，不暴露目标文件名或 hidden 组合点。
- hidden tests 迫使 agent 保留跨函数状态、顺序、错误类型、边界行为或反射/tag 语义。

如果一个强 agent 能通过“识别目标文件 + 改 package name”完成任务，该题只能是 calibration/easy-B。

---

## Mechanical Gates（G0–G8）

与 [GO_PILOT_PLAYBOOK.md](GO_PILOT_PLAYBOOK.md) 一致。G0–G4 失败且无登记 exception → 不得进入 hard 表；G8 失败 → 只能 `promote_calibration`，不得 `paper_ready_hard`。

---

## Repository Selection Rubric

| Repo check | Promote 期望 |
| --- | --- |
| 真实使用 | 生产级 Go 库或明确策展的 legacy；有下游 import 场景 |
| 抽取面 | 至少一个 feature 可独立为 `featurelifted` |
| 自然缠绕 | internal package、init、全局 registry、配置耦合等 |
| 稳定证据 | commit pin；离线确定性测试 |
| 体量适中 | 非单文件；oracle 有界 |
| 不重复 | 不与 Go/Python 现有题同源同 API |

进入 task 设计前必须一句话答清：

1. 解耦后 `featurelifted` 是什么现实可复用模块？
2. 谁会在什么场景单独 import 它？
3. 为什么 compact closure 比 vendor/copy-all 更合理？

**浓度限制（Go 10 hard gold）：**

| 范围 | 限制 |
| --- | --- |
| 10 hard gold 默认 | 1 task / repo |
| 例外 | 2 tasks / repo，需不同 API + 不同 entanglement |
| 硬顶 | 3 tasks / repo（书面例外） |
| 未来 100 | 5 tasks / repo |

---

## Quality Scorecard

机械 gate 通过后，用记分卡辅助（**80/100** 正常 promote；Flash B 档需 **85/100**）。

| 领域 | 分 | 客观检查 |
| --- | ---: | --- |
| Reuse 价值 | 15 | 谁 import、为何非 copy-all |
| 边界清晰 | 15 | included/excluded 具体；API 覆盖 public+hidden；不是文件边界 |
| 难度 | 15 | symbol-level oracle；target/non-target 混在源文件内；≥2 entanglement |
| 测试质量 | 20 | public 引导主路径；hidden 组合/错误/边界；确定性 |
| Baseline 分离 | 20 | oracle/naive/copy_all 清晰分层；probe 映射 hidden |
| Agent 校准 | 10 | Flash tier/readiness 记录；oracle/copy_all footprint pass 只能 calibration |
| 文档 | 5 | design note、backlog、catalog 一致 |

<60 分 → drop；60–79 → redesign。

---

## Flash Tiers

| Tier | 含义 | 默认决策 |
| --- | --- | --- |
| A | hidden 挡住 Flash，或 public pass hidden fail | 可进入 hard review |
| B-hard | hidden pass，但 footprint compact、非 oracle、明显低于 copy_all | 可进入 hard review，需披露 |
| B-calibration | hidden pass 且 oracle footprint，或 hidden pass 且接近 copy_all | `promote_calibration` |
| C | 低 extraction / 硬编码过 hidden | redesign/drop |

Go 验收报告须披露 A/B/C/readiness 分布。`promote_calibration` 只说明流程通过，不说明 hard paper-ready。

---

## Review Decision 模板

`experiments/go-pilot/<task_id>/review/decision.md`：

```markdown
# Review: <task_id>

Decision: promote_calibration | paper_ready_hard | redesign | drop
Flash tier: A | B | C | not_run
Readiness: calibration_pass | overextract_pass | paper_ready_hard | pending_flash | redesign

## Summary
...

## Gates
| Gate | Pass | Notes |
| G0 | yes/no | ... |

## Exceptions
- none | low_oracle_extraction_A_tier_exception | ...

## Scorecard (optional)
Total: /100

## Next action
...
```

---

## 10 Hard Gold 集层面检查

| 检查 | 期望 |
| --- | --- |
| 唯一 repo | ≥8 / 10 |
| Entanglement 多样性 | 至少 4 种 types 在 10 题中出现 |
| Extraction 分布 | 有 spread，非全部挤在 0.2–0.25 |
| Hard readiness | 10/10 `paper_ready_hard`；calibration/easy-B 单独列 |
| Flash A/B 分布 | 披露；不声称「Flash 普遍失败」若 calibration 为主 |
| Harness | 10 题同一 eval 版本可复现 |
