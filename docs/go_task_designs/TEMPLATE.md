# Task Design: `<task_id>` (Go)

> Machine-readable spec: [GO_TASK_FORMAT.md](../GO_TASK_FORMAT.md). Human design note for Go track.

Status: draft | oracle-verified | agent-calibrated

## Why This Task

为何属于 FeatureLiftBench Go track；functional vs decoupling 判别点是什么。

## Practical reuse（必填）

1. **Reuse module** — 解耦成功后 `featurelifted` 代表什么真实模块？（如 semver 比较、HTML sanitize policy）
2. **Who imports it** — 哪类下游会单独依赖此包？（CLI 工具、微服务、库）
3. **Why not copy-all** — 为何紧凑闭包比 vendor 整仓更现实？

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

| Variant | Public | Hidden | Extraction |
| --- | --- | --- | --- |
| oracle | pass | pass | 0.20–0.60 |
| naive | pass | **fail** | ≤0.10 |
| copy_all | pass | pass | ≥0.85, Δ≥0.25 vs oracle |

## Oracle Closure Estimate

- 约 N 个 `.go` 文件，约 M LOC
- 主要抽取自：`repo/...`

## Agent Calibration（promote 前填）

| Model | Public | Hidden | Extraction | Final | Tier |
| --- | --- | --- | --- | --- | --- |
| deepseek_v4_flash | | | | | A/B/C |

## Go/No-Go（入榜决策）

- [ ] Reuse 成立
- [ ] G0–G4 证据就绪
- [ ] Flash tier 已记录

Decision: promote | redesign | drop

## References

- [GO_PILOT_PLAYBOOK.md](../GO_PILOT_PLAYBOOK.md)
- [GO_QUALITY_RUBRIC.md](../GO_QUALITY_RUBRIC.md)
