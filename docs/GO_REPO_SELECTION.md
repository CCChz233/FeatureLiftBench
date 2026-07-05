# Go Track Repository Selection

**Purpose:** Go repo 池与浓度规划，与单题实现状态分离。Repo gate 必须先于 task 实现；弱 repo 或只能文件级切片的 repo 不占 hard 名额。

```text
select strong Go repos
  -> choose one reusable symbol/behavior-level feature slice per repo
  -> build benchmark/go/staging/<task_id>
  -> review with GO_QUALITY_RUBRIC
```

| 文件 | 职责 |
| --- | --- |
| `benchmark/go/tasks/*/metadata.json` | 已接受正式 Go 题 |
| **本文** | repo 是否值得占用名额、浓度上限 |
| [go_candidate_backlog.md](go_candidate_backlog.md) | 具体 task 想法与 shortlist 队列 |

---

## Target Counts

| 阶段 | 目标 |
| --- | ---: |
| Phase 2 hard gold | **10** tasks |
| Phase 2 unique repos | **8–10** preferred |
| Phase 3 full board | **100** tasks |
| Full-board unique sources | **75+** preferred |

**候选池规模：** 为 10 hard gold 准备 **15–20** repo 候选（约 50% spare，应对 oracle/gate 失败）。

为 100 题准备 **60+** repo 候选（与 Python batch-1 相同 spare 率）。

---

## Concentration Limits

| 范围 | 限制 |
| --- | --- |
| 10 hard gold 默认 | 1 task / repo |
| 10 hard gold 例外 | 2 tasks / repo，不同 reusable slice |
| 10 hard gold 硬顶 | 3 tasks / repo + 书面例外 |
| Go 100 板 | 5 tasks / real OSS repo |

同 repo 例外须满足：

- 不同 output API；
- 不同 behavior family / entanglement；
- oracle runtime LOC 重叠 <30–40%；
- 不同 hidden tests 与 probes。

---

## Repo Gate（进 shortlist 前）

| 维度 | 要求 |
| --- | --- |
| License | SPDX 明确；可 redistribution |
| Pin | `commit` 可固定；`go.mod` 可 build |
| 生态 | 有真实下游（非仅 demo） |
| Reuse slice | 能一句话说明 standalone package、下游 importer、为什么非 copy-all |
| Symbol boundary | feature 边界能落在函数/类型/方法/行为上，不是完整文件列表 |
| Mixed source files | 至少两个源文件可同时包含 target 和 non-target 代码 |
| 测试友好 | 可无外部服务写 table tests；hidden 能覆盖组合/错误/边界 |
| 无 cgo（Phase 0–2） | 或明确排除 |
| 规模 | module 内多 package或多文件耦合优先；非单文件 utility |

### 立项前三问

一个 repo 进入 `go_candidate_backlog.md` 前，必须能回答：

1. 解耦成功后，`featurelifted` 代表什么现实可复用模块？
2. 谁会单独 import 它，在哪个生产或工具场景使用？
3. 为什么 compact closure 比 vendor/copy-all 更合理？

答不清则不进入 shortlist。

### 文件边界风险

以下 repo/slice 不适合作为 hard task：

- 目标 feature 天然完整落在少数独立 `.go` 文件中。
- non-target 代码都在明显命名的 `cache.go`、`registry.go`、`*_excluded.go` 等文件里。
- upstream 目录结构已经把 target package 单独隔离，agent 可直接复制该 package。
- public API 与内部文件名一一对应，缺少 symbol-level 重组需求。

这类题可以做 calibration，但不能计入 hard paper-ready。

---

## 已接受 Repo（Go）

| Repo | Tasks | Notes |
| --- | ---: | --- |
| — | 0 | Phase 2 尚未 promote |

*随 `benchmark/go/tasks/` 增长更新此表。*

---

## 拒绝模式（历史）

| 模式 | 处理 |
| --- | --- |
| 仅 CLI，无可 import API | drop |
| 生成器/ORM 全栈 | 范围过大，换 slice |
| 强依赖 `testing` 外网 | drop |
| 与 Python 题同源同 slice | drop 或换 entanglement |
| 只能文件级抽取 | calibration 或 drop；不进 hard |

---

## 与 Python 主榜

Python 已占用的 repo **可以**在 Go 做不同 slice，但须在 design note 说明差异，且 hidden/probe 不重复 Python 判别故事。

同一 **feature API** 跨语言重复 → 禁止。

---

## 相关

- [go_candidate_backlog.md](go_candidate_backlog.md) — 候选队列
- [GO_PILOT_PLAYBOOK.md](GO_PILOT_PLAYBOOK.md) — Step 0
