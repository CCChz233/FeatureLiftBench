# Go Track 扩题政策（10 Hard Gold → 100）

**最后更新：** 2026-07-05

本文定义 **Go 语言 decoupling track** 的扩题策略，与 Python v1.1 主榜（100 hard）**分开规划、分开报告**。

| 资源 | 路径 |
| --- | --- |
| **执行 playbook** | [GO_PILOT_PLAYBOOK.md](GO_PILOT_PLAYBOOK.md) |
| 任务格式 | [GO_TASK_FORMAT.md](GO_TASK_FORMAT.md) |
| 质量 rubric | [GO_QUALITY_RUBRIC.md](GO_QUALITY_RUBRIC.md) |
| 仓库池 | [GO_REPO_SELECTION.md](GO_REPO_SELECTION.md) |
| 候选台账 | [go_candidate_backlog.md](go_candidate_backlog.md) |
| Harness 工程 | [GO_HARNESS_PLAN.md](GO_HARNESS_PLAN.md) |
| 设计笔记模板 | [go_task_designs/TEMPLATE.md](go_task_designs/TEMPLATE.md) |
| 论文/复现契约 | [BENCHMARK_SPEC.md](BENCHMARK_SPEC.md) §11 |
| Python 扩题（对照） | [EXPANSION.md](EXPANSION.md) |

---

## 1. 核心决策

> **先做好 10 个 hard paper-ready Go 样例，再扩到 100。**

| 阶段 | 目标 | 说明 |
| --- | ---: | --- |
| **Phase 0** | Harness | Go evaluator、`go test`、Docker 镜像、`validate-task` |
| **Phase 1** | **1 pilot** | 端到端打通一条题 |
| **Phase 2** | **10 hard gold** | 每题有完整 evidence packet 和 hard-readiness 证据；论文骨架可写 |
| **Phase 3** | 100 | 在 playbook 稳定后批量复制（体力活） |

**不做：** 在 harness 未就绪时并行堆 10+ 道空壳题；与 Python 主榜混目录、混报告。

---

## 2. 什么叫「Hard Gold」Go 题？

每道题必须同时满足以下六条（与 [GO_QUALITY_RUBRIC.md](GO_QUALITY_RUBRIC.md) 机械 gate 一致）：

| # | 要求 | 验收 |
| --- | --- | --- |
| 1 | **功能真实有用** | design note 能回答「谁会在什么场景 `import` 解耦后的包」；不是玩具 API |
| 2 | **原仓库有缠绕** | 至少 2 类 `entanglement`；边界是 symbol/behavior，不是整文件列表 |
| 3 | **可抽成独立包** | oracle 为独立 `go.mod` + package `featurelifted`；无原模块 runtime 依赖；需要裁剪/重组而非整文件复制 |
| 4 | **hidden 能判别** | naive：public 过、hidden 挂；copy_all：过但 extraction 远高于 oracle |
| 5 | **evaluator 稳定** | `go test` 离线、确定性；无网络/时钟/随机/本机路径依赖 |
| 6 | **人类可读** | `TASK.md` + design note 非专家也能理解任务目标与边界 |

**Hard gold 的机械定义：** G0–G8 全过 + `gate_report.json` + oracle/naive/copy_all 分层证据 + 至少 3 个 module probe + OpenHands/Flash hard-readiness。`promote_calibration` 不能计入 hard gold。

文件边界红线：如果 agent 能通过“复制一组 `.go` 文件并改 package name”得到 oracle footprint，该题只能是 calibration。

---

## 3. 与 Python 主榜的关系

| 维度 | Python v1.1 | Go track |
| --- | --- | --- |
| 状态 | **已实现**；`benchmark/tasks/` 100 hard | **规划中**；`benchmark/go/staging/` → `benchmark/go/tasks/` |
| 报告 | 主榜数字 | **单独分区**；不与 Python 混表 |
| Playbook | [BATCH1_PLAYBOOK.md](../BATCH1_PLAYBOOK.md) | [GO_PILOT_PLAYBOOK.md](GO_PILOT_PLAYBOOK.md) |
| 语义 | behavior-preserving feature decoupling | **相同**（见 BENCHMARK_SPEC v2 policy） |

Python batch-0 冻结、batch-1 已满 100——**Go 扩题不修改任何 Python 题**。

---

## 4. 目录约定

```text
benchmark/go/
  staging/<task_id>/          # 试选题（promote 前）
  tasks/<task_id>/            # 正式 Go 题；hard 与 calibration 必须分状态报告
  sanity/                     # 可选：1–3 道 smoke（未来）

benchmark/submissions/<task_id>/
  oracle/                     # 与 Python 共用 submissions 树
  naive/
  copy_all/

docs/go_task_designs/<task_id>.md
docs/go_candidate_backlog.md

experiments/go-pilot/<task_id>/review/
  gate_report.json
  decision.md
  oracle/result.json
  naive/result.json
  copy_all/result.json
```

`task_id` 命名与 Python 一致：`<source>__<feature_slug>__<serial>`，例如 `semver__version_parse_core__001`。

---

## 5. 进度表（手动更新）

| 指标 | Phase 1 目标 | Phase 2 目标 | 当前 |
| --- | ---: | ---: | ---: |
| Go harness MVP | 1 | 1 | **1** |
| calibration/easy-B | — | 单独列 | **4** |
| active hard candidate | 1 | — | **1** |
| **hard gold tasks** | — | **10** | **0** |
| 正式 `benchmark/go/tasks/` hard | — | 10 | **0** |
| 扩至 100 | — | — | 0 |

---

## 6. 论文骨架（10 hard gold 即可支撑）

在 10 道 hard gold 题就绪后，论文可包含：

1. **问题定义** — feature-level decoupling（与 Python 共用 CONCEPTS）
2. **任务契约** — Go task format + evaluator（GO_TASK_FORMAT + GO_HARNESS_PLAN）
3. **Gold 集深度分析** — 10 题：pass rate、extraction 分布、失败模式、probe 案例
4. **跨语言动机** — 同一语义下 Python vs Go 的工程差异（module、test、`go.mod`）
5. **规模实验（可选附录）** — Python 100 主榜结果单独报告

**不必等 Go 100** 才能写清方法与判别力；10 hard gold 的质量证据比 100 道糙题更有说服力。

---

## 7. 节奏建议

```text
Week 1–2   Phase 0：harness MVP + validate-task for Go
Week 2–3   Phase 1：1 pilot 题全流程
Week 3–8   Phase 2：每批 1–3 题，共 10 hard gold（每题 evidence packet + hard readiness）
Week 9+    Phase 3：按 playbook 扩量（目标 100，可并行 agent 生成 + 人工 gate）
```

**单题节奏：** 与 Python 相同——**当前 pilot 未 promote 前不并行开下一题**（Phase 1）；Phase 2 可放宽为每批 2–3 题，但每题必须有独立 `gate_report.json`。

---

## 8. 不在本计划内

- 修改 Python `benchmark/tasks/` 任意题目
- Go bug-fix / patch track（与 decoupling 语义不同）
- 与 Python 混合 leaderboard 排名

---

## 9. 相关文档

- [GO_PILOT_PLAYBOOK.md](GO_PILOT_PLAYBOOK.md) — 七步执行流程与命令
- [GO_HARNESS_PLAN.md](GO_HARNESS_PLAN.md) — 评测器实现清单
- [BENCHMARK_SPEC.md](BENCHMARK_SPEC.md) §11 — v2 规格草案
