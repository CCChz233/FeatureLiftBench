# Python Repository and Task Inventory

> **Documentation status: reference · Last verified: 2026-08-04**

> This document describes the frozen Python baseline inventory. It is not the unified
> Python-200 release status; see [STATUS.md](../../STATUS.md) for the current suite.

**Snapshot date:** 2026-07-27

机器事实源：

- [`benchmark/sources/registry.json`](../../../benchmark/sources/registry.json)
- [`benchmark/tasks/`](../../../benchmark/tasks/)
- [`v3_main_readiness.json`](../../../reports/audits/v3_main_readiness.json)
- [`python150_task_taxonomy.csv`](../../../artifacts/research_analysis/python150_task_taxonomy.csv)

本文只给可读汇总，不再手工复制 150 行任务表。

## 总量

| 项 | 数量 |
| --- | ---: |
| Python Main tasks | 150 |
| Canonical external OSS repositories | 126 |
| Local curated sources in Main | 0 |
| Immutable source snapshots | 132 |
| Ready snapshots | 132 |
| v3-ready tasks | 150 |
| Separate Curated tasks | 7 |

按 task instances：

- external OSS：150/150（100%）；
- curated：0/150（0%）。

按 repositories：

- external OSS：126/126（100%）；
- curated：0/126（0%）。

`metadata.source.name` 的 127 个名称包含别名；唯一仓库数必须使用
`source_repo_id`，不能直接按 display name 计数。

## 仓库集中度

| 每仓任务数 | 仓库数 |
| ---: | ---: |
| 1 | 116 |
| 2 | 3 |
| 3 | 3 |
| 4 | 1 |
| 5 | 3 |

任务最多的来源：

| Source | Tasks |
| --- | ---: |
| coverage.py | 5 |
| Jinja2 | 5 |
| pytest | 5 |
| sqlparse | 4 |
| python-dateutil | 3 |
| Lark | 3 |
| pluggy | 3 |

116/126 repositories 只贡献 1 题，单个来源最多 5/150（3.3%），因此主结果
不会由一个仓库主导。7 道 `vibe_app` 题属于独立 Curated split，不计入本表。

## 完整 source snapshot 规模

132 个 immutable snapshots：

| 指标 | Min | P25 | Median | P75 | Max |
| --- | ---: | ---: | ---: | ---: | ---: |
| Python LOC | 513 | 3,580 | 8,961 | 20,685 | 497,313 |
| Python files | 3 | 21 | 39 | 108 | 795 |
| Tracked files | 12 | 57 | 120 | 318 | 2,306 |
| Max path depth | 2 | 3 | 4 | 6 | 10 |
| Total bytes | 32,436 | 320,837 | 940,568 | 2,709,211 | 42,618,336 |

为分析定义的规模带：

| Python LOC band | Snapshots |
| --- | ---: |
| small：<5k | 45 |
| medium：5k–20k | 53 |
| large：>20k | 34 |

这些统计来自完整 tracked tree，不是旧 task-local source slices。

## Repository archetype

按 task instances：

| Archetype | Tasks | Share |
| --- | ---: | ---: |
| Library | 102 | 68.0% |
| Developer tooling | 29 | 19.3% |
| Framework/plugin | 17 | 11.3% |
| Application/service | 2 | 1.3% |

因此当前结论主要适用于 Python libraries/tooling。2 个 application/service
tasks 只提供少量应用级覆盖，不足以外推到任意大型业务系统。

## Repository domain

| Domain | Tasks |
| --- | ---: |
| Parsing | 41 |
| General utility | 38 |
| Configuration | 15 |
| Data modeling | 13 |
| Networking | 12 |
| Packaging | 11 |
| Testing | 11 |
| Application | 9 |

## Entanglement

| Primary type | Tasks |
| --- | ---: |
| Parser state | 44 |
| Data model | 43 |
| Framework | 28 |
| Config/environment | 16 |
| Resource | 15 |
| Third-party dependency | 3 |

领域与纠缠不是完全均衡。Parsing 明显以 parser-state 为主，application
明显以 framework 为主。论文应报告交叉分布，避免把“仓库名多”
误写为机制完全多样。

| Domain | Parser | Data model | Framework | Config | Resource | Third party |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| Parsing | 32 | 4 | 4 | 0 | 1 | 0 |
| General utility | 4 | 17 | 8 | 0 | 8 | 1 |
| Application | 0 | 1 | 8 | 0 | 0 | 0 |
| Configuration | 1 | 1 | 2 | 10 | 1 | 0 |
| Data modeling | 0 | 12 | 1 | 0 | 0 | 0 |
| Networking | 6 | 2 | 2 | 1 | 0 | 1 |
| Packaging | 1 | 6 | 0 | 1 | 3 | 0 |
| Testing | 1 | 0 | 3 | 4 | 2 | 1 |

## Task footprint

active compactness registry 对 150/150 题提供 reference-file/LOC 统计：

| 指标 | Coverage | Min | P25 | Median | P75 | Max |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| Reference files | 150 | 1 | 2 | 5 | 14 | 81 |
| Reference LOC | 150 | 17 | 86 | 881 | 2,936 | 23,018 |
| Reference symbols | 49 | 1 | 2 | 3 | 4 | 13 |

Reference file/LOC 已覆盖全部 150 题；symbol-level closure 仍只覆盖 49
题，因此论文可以报告前两者，不应把 symbol 指标外推到全量。

## Difficulty

- metadata：150/150 `hard`；
- 历史构造切片：Core-100 + mechanism-challenging Hard-50；
- v3 Main：统一 150 题；
- 当前 `hard` 是设计标签，不是 v3 经验难度等级。

首轮 frozen v3 baseline 后，应按 empirical pass、failure stage、task
footprint 和 source size 重新校准 easy/medium/hard 分层。不能为了满足预设
比例修改 task contract 或 hidden tests。

## 选择与复现边界

当前 registry 已提供 URL、resolved commit、license、archive SHA-256、
source-tree digest、文件/LOC 统计和 task mapping。7 个 External Main
replacement 的 21-repository 固定候选队列、哈希排序和淘汰理由记录在
`benchmark/selection/external150_replacement_20260727.json`。原有 143 题的
历史选择协议仍需在论文中如实说明；不能从当前 registry 反向推断。

完整 source policy 见
[FULL_REPOSITORY_SOURCE_POLICY.md](../../FULL_REPOSITORY_SOURCE_POLICY.md)。
