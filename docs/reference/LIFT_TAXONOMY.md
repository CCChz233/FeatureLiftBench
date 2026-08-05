# Feature-Lift 类型（Direct / Adapted / Composite）

> **Documentation status: current · Last verified: 2026-08-04**

**状态：** 定义已冻结；release 分布与标注完成度见 [STATUS.md](../STATUS.md) 和 balance audit
**最近复核：** 2026-08-04
**产物：** [`reports/lift_taxonomy/`](../../reports/lift_taxonomy/)

## 一句话

按「目标 `featurelifted` 功能与上游实现如何对应」分类，测量的是
**feature-lifting 机制**，不是仓库 domain / archetype。

论文能力主张取决于这三档在冻结 release 中的覆盖，以及
每题契约是否闭合（见 [CONTRACT_CLOSURE_AUDIT.md](../archive/plans/CONTRACT_CLOSURE_AUDIT.md)）。

## 标签定义

| 标签 | 定义 |
| --- | --- |
| **Direct** | 目标功能与某个上游 API 行为基本等价，主要是抽取与解耦 |
| **Adapted** | 以一个明确上游功能为主体，但需要参数、返回值、异常或接口转换 |
| **Composite** | 没有单一上游 API 可以直接对应，需要组合多个组件或重建流程 |

废弃口头名 `synthetic`：易被理解成“编造答案”。合成测试夹具（如
`FakeElement`）**本身不决定** lift 类型；以主体功能是否单一可对应为准。

## 判别流程

```text
是否存在可点名的单一上游主体功能？
  ├─ 否 → Composite
  └─ 是 → 目标调用是否与该主体基本同构（含合理裁剪）？
        ├─ 是 → Direct
        └─ 否，但转换可写进契约 → Adapted
```

补充规则：

1. **测试脚手架 ≠ Composite。** 夹具只服务单一上游主体时，仍标 Direct/Adapted。
2. **Adapted 的转换必须可声明。** 若转换靠猜（旧 `inferred_adapter`），先标
   Adapted 且 `label_status=seeded`，修订时应写成 TASK 明文，或改判 Composite。
3. **Composite 契约更严。** 组合边界、中间对象、重建流程的 I/O 必须在
   public_spec / Required API 中闭合，否则常为 `underspecified`。
4. **与 closure 正交。** `lift_type=Direct` 仍可能 `closure_status=underspecified`。

## 与 `oracle_relation` 的粗对齐

审计维 `oracle_relation`（证据从哪来）与 `lift_type`（题怎么建）相关但不等同：

| `oracle_relation` | 常见 `lift_type` |
| --- | --- |
| `direct_oracle` | Direct |
| `specified_adapter` | Adapted |
| `inferred_adapter` | 多为 Adapted（声明不全）；少数应改判 Composite |
| `no_upstream_oracle` | 多为 Composite |

种子标注只用上表做 provisional 映射；**reviewed** 必须以 TASK + upstream 复核。

## 字段 schema

每题一行 JSONL（[`reports/lift_taxonomy/LIFT_LABELS.jsonl`](../../reports/lift_taxonomy/LIFT_LABELS.jsonl)）：

```json
{
  "task_id": "glom__spec_eval_core__hard3_001",
  "lift_type": "Direct",
  "label_status": "seeded",
  "upstream_anchor": "glom.core.glom / Spec evaluation",
  "rationale": "Single upstream glom entry; target mostly extract/decouple.",
  "seed_from_oracle_relation": "direct_oracle",
  "reviewer": null,
  "reviewed_at": null
}
```

| 字段 | 含义 |
| --- | --- |
| `lift_type` | `Direct` \| `Adapted` \| `Composite` \| `null`（未标） |
| `label_status` | `unlabeled` \| `seeded` \| `reviewed` |
| `upstream_anchor` | 单一主体时填写上游符号/功能；Composite 可列多个或写流程名 |
| `seed_from_oracle_relation` | 若由审计种子映射而来则填写 |

## 与另外两张分布的关系

论文需要的三张题层分布：

1. **Lift 类型**（本文）— Direct / Adapted / Composite
2. **行为语义 × coupling** — taxonomy 已有事实源：
   [`artifacts/research_analysis/python150_task_taxonomy.csv`](../../artifacts/research_analysis/python150_task_taxonomy.csv)
3. **难度 / 规模 / 源码重叠** — inventory + compactness registry；经验难度等 v3 baseline

优先级：**先标满 lift_type**，再与 (2)(3) 交叉出表。不加仓。

## 标注执行

```text
冻结本定义
→ 用 oracle_relation 种子 opened-dev hard
→ 基于 TASK.md + source_entrypoints 全量标注 150（已做，ai_assisted_task_md_v1）
→ 抽检复核 → 可将 label_status 升为 reviewed
→ 与 taxonomy / footprint 交叉出论文表
```

当前分布见 [`reports/lift_taxonomy/SUMMARY.md`](../../reports/lift_taxonomy/SUMMARY.md)。
标签在报告层，**尚未**写入 `benchmark/tasks/*/metadata.json`。
