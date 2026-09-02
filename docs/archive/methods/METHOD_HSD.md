# Harness-Selected Differential（HSD）

> **Status: archived · 可行性探针否决，未写规格、未跑模型 · Last verified: 2026-09-01**
> 本文件记录 **HSD** 为何在可行性阶段被否决，避免重复提出。不要实现，不要跑。

## 原设想

Main 信封内唯一的**行为** oracle 是钉住的上游 `repo/`（可执行）。之前所有用过
differential 的臂（Lite V1、V3、Rescue+ v2.1/v2.2）都由 **Agent 选输入**、且只有
1–3 条，因此继承了 Agent 自己的盲点——这与 CGVL 的失效机制相同（pygments 的
B004 有专门格子摆在面前，Agent 仍把条款窄化，并自报 `oracle_source` 取自上游）。

未试过的版本是把输入选择权收归 harness：

- **输入**：harness 从 `required_api` 的声明签名做类型定向生成（property-based）
- **oracle**：Agent 指认的上游对应物的执行结果
- **覆盖**：出现差异时 Agent 必须引用一条授权该差异的 `Bxxx`，否则算缺陷

第三条正好处理契约覆盖上游的情形（pygments 的 stripall）。

## 否决理由（2026-09-01 可行性探针）

脚本 `harness/scripts/probe_upstream_differential.py`，报告
[`upstream_differential_probe.md`](../../../reports/paper_analysis/upstream_differential_probe/upstream_differential_probe.md)。
零模型成本。

预注册门槛为可行题占比 ≥ 70%。150 道 `repo/` 已物化的题（另 50 题为
source-archive 标记、运行时才物化，不计入分母）：

| 分类 | 题数 | 占比 |
| --- | ---: | ---: |
| `runs_here` | 85 | 56.7% |
| `needs_lockfile` | 14 | 9.3% |
| `unresolvable` | 42 | 28.0% |
| `blocked` | 9 | 6.0% |

乐观上界 **66.0%**，低于门槛。但真正致命的是覆盖与失败**不重合**：

| lift | 失败题 | differential 可行 | 不可行 |
| --- | ---: | ---: | ---: |
| Direct | 4 | 4 | 0 |
| Adapted | 12 | 3 | 9 |
| Composite | 9 | 0 | 9 |
| **合计** | **25** | **7** | **18** |

全套件可行 66.0%，**失败题里只有 7/25 = 28% 可行**。按 lift 类型看，可定位率
Direct 91%、Adapted 63%、Composite **0%**。

原因是结构性的，不是实现问题：**Adapted 与 Composite 抽取的 API 按设计就不是任何
单个上游符号的 1:1 对应物，differential oracle 在那里没有定义。** 而失败集中在这
两类。上游 differential 能用的地方，正是 Agent 本来就做得好的地方
（`TOKEN_UTILITY.md`：Direct 的 `T*/T` 中位 0.36，最早通过）。

## 与整体结论的关系

HSD 是"Main 信封内是否存在可用行为信号"这个问题的最后一个候选。它的否决把该
问题关闭了：

| 信号类别 | 状态 |
| --- | --- |
| 结构（`required_api` 表面） | 过早闭合，VCT 标定证明丢的 pass 全在 `T*` 前 |
| Agent 自撰 oracle | 继承自身盲点（CGVL、TFL、pre-submit audit） |
| 上游 `repo/` 行为 | 仅对 Direct 有定义，与失败不重合（本文件） |
| 轨迹统计 | Phase 3 组合 AUC 0.63–0.67 |

参见 [../../METHOD_VCT.md](METHOD_VCT.md) 的离线 Kill、
[../../TOKEN_UTILITY.md](../snapshots/TOKEN_UTILITY.md) 的 checkpoint oracle `0/51`、
以及 [clause_narrowing](../../../reports/paper_analysis/python200_hard_main_20260829/clause_narrowing/clause_narrowing.md)
的 8 道 Hidden 首败里 4 道义务不可从契约恢复。

## 限制

- 定位是按名解析，不做语义匹配，因此 66.0% 是**上界**：能导入不等于语义对应正确。
- 50 道 source-archive 题未探。它们若全部可行，全套件上界升至 74.5%，但失败题
  重合度不变——那 25 题里只有 2 题属于未探集合。
