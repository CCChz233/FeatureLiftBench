# Task Schema

> **Documentation status: current · Last verified: 2026-08-31**

任务包是 maintainer/evaluator 资产，不等于 Agent workspace。公开契约和门禁
见 [TASK_DESIGN_RULES.md](../TASK_DESIGN_RULES.md)，source 规则见
[FULL_REPOSITORY_SOURCE_POLICY.md](../FULL_REPOSITORY_SOURCE_POLICY.md)。

## Python task package

```text
benchmark/tasks/<task_id>/
  metadata.json
  TASK.md
  requirements.lock
  repo/                    # historical task-local snapshot/provenance
  public_tests/
  hidden_tests/
  evaluation/
    forbidden_imports.txt
    oracle_manifest.json
```

部分 staging/pilot 还可以包含 `reference_solution/` 或
`evaluator_config.yaml`。Main reference 通常由
`benchmark/submissions/<task_id>/oracle/` 和 frozen reference registry 管理。

## Required metadata

核心字段：

| Field | Role |
| --- | --- |
| `task_id` | 全局唯一任务 ID |
| `language` | 当前 Main 为 `python` |
| `difficulty` | 设计标签；不是自动生成的经验等级 |
| `source` | display name、URL、revision、license |
| `feature` | maintainer-private feature provenance |
| `output` | canonical `featurelifted` output surface |
| `environment` | Python、network、timeout、dependency constraints |
| `tests` | evaluator test paths/command |
| `entanglement` | private analysis labels |
| `public_spec` | Agent-visible semantic contract 的唯一事实源 |
| `evaluation_spec` | private API/behavior→test mapping |
| `spec_status` | Main 必须 `compliant` |
| `spec_hash` | canonical `public_spec` digest |
| `generated_task_hash` | rendered `TASK.md` digest |
| `task_revision` | spec revision |

`metadata.json` 位于 benchmark private layer。Main workspace 只复制 redacted
metadata（若 runner 需要）并递归移除 entrypoints、source hints、难度、纠缠、
evaluation 和 reference 信息。

## `public_spec`

必须声明：

- title/summary；
- `required_api` 和 `optional_api`；
- observable behaviors；
- exclusions；
- forbidden/isolation requirements；
- public-vs-hidden note。

历史 metadata 中可能仍有 `public_spec.source_entrypoints` 或
`feature.source_entrypoints` 作为 maintainer provenance/ablation input。
它们不得渲染进 Main `TASK.md`，也不得进入 redacted metadata、prompt、
辅助状态或日志。

`TASK.md` 必须由 `public_spec` 生成；不允许手写第二份冲突规格。

## Evaluator assets

| Path | Visibility in Main | Role |
| --- | --- | --- |
| `public_tests/` | private | 基础 regression layer |
| `hidden_tests/` | private | 边界、组合和深层 behavior layer |
| `evaluation/` | private | forbidden、oracle、mapping、probes |
| reference/oracle | private | construction and compactness reference |

Public 和 hidden 都必须映射到已公开 API/behaviors；hidden 不得引入第二份
秘密规格。

## Canonical source registry

v3 Main source 不以 `<task>/repo/` 是否看起来完整来判断。事实源：

```text
benchmark/sources/registry.json
benchmark/sources/registry.schema.json
benchmark/sources/archives/<content-addressed>.tar.gz  # local/ignored
```

每个 task mapping 必须解析到：

- `source_repo_id`；
- `source_snapshot_id`；
- canonical URL/source kind；
- requested and resolved revision；
- `full_tracked_tree` 或受 policy 定义的 curated scope；
- archive SHA-256 和 source-tree SHA-256；
- license path；
- file/LOC/depth/byte statistics；
- `status=ready`。

同一 canonical source + revision 的任务共享同一 snapshot digest。

## Agent workspace

正式 Main：

```text
workspace/
  TASK.md                  # task-specific public_spec + 全局完整功能责任前提
  repo/                    # registry archive 物化的完整 source tree
  requirements.lock
  submission/
```

不复制：

```text
public_tests/
hidden_tests/
evaluation/
reference/oracle/
source entrypoints or hints
```

上游仓库自身的 tests/docs/examples/config/resources 属于完整 source tree，
仍可见。

`TASK.md` 的 task-specific 部分仍由 `metadata.public_spec` 单一生成；运行时
renderer 额外注入全局 `Complete Feature Responsibility` 协议段，要求 Agent
把目标视为完整 task-scoped module，并主动从完整仓库恢复实现位置、具体契约
语义和传递闭包。该全局段不由单题 metadata 维护，不改变 scope boundary，
也不能成为 Hidden 扩展未公开义务的依据。

## Submission

Python：

```text
submission/
  pyproject.toml           # 推荐
  featurelifted/
    __init__.py
    ...
```

Evaluator 从 submission 构建/导入，不把 source repo 加入 `PYTHONPATH`。
Tests import `featurelifted`，不 import `submission.featurelifted`。

Go calibration 使用：

```text
submission/
  go.mod
  featurelifted/
    ...
```

Go 尚不是 paper-ready Main。

## Lifecycle

新任务先进入本地 `benchmark/staging/` 或 `benchmark/batch3_pilot/`。通过
source、contract、reference、isolation、No-Hint、difficulty/calibration
和 freeze 门禁后，才可 promotion 到 `benchmark/tasks/`。

Main membership 以 split + current freeze 为准，不依赖旧 metadata 中是否有
`status=main`。完整流程见
[07_incremental_task_rules.md](07_incremental_task_rules.md)。
