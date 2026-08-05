# Task Design: `<task_id>` (Go)

> **Documentation status: reference · Last verified: 2026-08-04**

> Package schema: [Task Schema](../06_task_schema.md). Human maintainer note for
> the Go calibration track; not Agent-visible.

Status: draft | design-approved | oracle-verified | agent-calibrated | calibration | paper_ready_hard | redesign | dropped

## Why This Task

为何属于 FeatureLiftBench Go track；functional vs decoupling 判别点是什么。

## Practical reuse（必填）

1. **Reuse module** — 解耦成功后 `featurelifted` 代表什么真实模块？（如 semver 比较、HTML sanitize policy）
2. **Who imports it** — 哪类下游会单独依赖此包？（CLI 工具、微服务、库）
3. **Why not copy-all** — 为何紧凑闭包比 vendor 整仓更现实？

如果三问无法用具体下游场景回答，本题应停止在 design spike，不进入 staging。

## Source

| Field | Value |
| --- | --- |
| Source repo | `<url>` |
| Commit | `<hash>` |
| License | `<SPDX>` |
| Language | **Go** |
| Difficulty | hard |
| Tags | multi-package, `<discriminator-tag>` |

## Entanglement

```json
{
  "level": "high",
  "types": ["internal_packages", "global_registry"],
  "description": "...",
  "signals": ["..."]
}
```

Go 常见 types：`internal_packages`, `init_side_effects`, `global_registry`, `build_tags`, `reflection_coupling`, `error_chain`.

## Target Feature

### Source entrypoints

- `repo/...`

### Output API

```go
import "example.com/featurelifted"

featurelifted.<Callable>(...)
```

### Module path

- Submission `go.mod` module: `example.com/featurelifted`（或题目约定）

## Included Behaviors

- ...

## Excluded Behaviors

- CLI / main
- 原仓库 `go test` 全集
- 网络、DB、cgo
- 原 module path runtime import

## Boundary Plan（hard 题必填）

Go hard 题必须是 **symbol / behavior boundary**，不是文件边界。这里必须说明 agent 为什么不能靠复制一组完整 `.go` 文件过关。

### Target symbols

列出需要进入 oracle 的函数、方法、类型、常量或接口：

- `...`

### Non-target symbols sharing source files

至少两个源文件应同时包含 target 和 non-target 代码：

| Source file | Target symbols | Non-target symbols in same file | 为什么 copy 整文件会过宽 |
| --- | --- | --- | --- |
| `repo/...go` | `...` | `...` | ... |

### Oracle transformation

说明 oracle 需要做什么重组，而不是整文件复制：

- 裁剪哪些 non-target symbols
- 合并/拆分哪些 helpers
- 改写哪些 package/module/import 依赖
- 保留哪些错误类型、状态或注册逻辑

### File-boundary rejection check

- [ ] oracle 不是从 `repo/` 复制一组完整 `.go` 文件得到的
- [ ] public contract / TASK 不透露目标文件名；Main 不向 Agent 暴露评分测试
- [ ] 文件名和注释不标记 `excluded` / `noise` / `non-target`
- [ ] copy_all 功能通过，但 reference-relative compactness 显著差于 reference

## Environment

```json
{
  "go": "1.22",
  "network": false,
  "timeout_seconds": 120,
  "cgo_enabled": false
}
```

## Test Plan

### Public

- 主路径 happy path
- 1–2 个常见错误

### Hidden

- 边界组合（不与 public 重复断言）
- 错误类型 / 顺序 / 空值
- 至少 3 个 module probe 映射点

### Determinism

- 无 `time.Now()` 断言；fixture 在 repo 内

## Baseline Expectations

| Variant | Public | Hidden | Reference-relative size |
| --- | --- | --- | --- |
| reference | pass | pass | 1.0 |
| naive | pass | **fail** | report |
| copy_all | pass | pass | clearly > 1.0 |

若 Flash 直接达到 reference 行为与体量，或仅靠 copy-all 过关，本题只能保留为
calibration，不能据此宣称高难度。

## Oracle Closure Estimate

- 约 N 个 target symbols，约 M LOC
- 主要抽取自：`repo/...`
- 涉及文件数可写，但不能把文件列表当作 oracle 边界

## Agent Calibration（promote 前填）

| Model | Public | Hidden | Compactness | Functional Pass | Tier |
| --- | --- | --- | --- | --- | --- |
| deepseek_v4_flash | | | | | A/B/C |

## Go/No-Go（入榜决策）

- [ ] Reuse 成立
- [ ] Boundary Plan 证明不是文件边界抽取
- [ ] G0–G4 证据就绪
- [ ] Flash tier 已记录
- [ ] Hard readiness 已记录

Decision: promote_calibration | paper_ready_hard | redesign | drop

## References

- [Go split docs](../go/README.md)
- [Go difficulty rubric](../go/03_go_difficulty_rubric.md)
