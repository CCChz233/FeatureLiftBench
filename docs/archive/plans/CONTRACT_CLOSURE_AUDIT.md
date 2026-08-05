# Contract-Closure Audit（当前第一步）

> **Documentation status: archived · Indexed: 2026-08-04**

**状态：** 进行中 · 暂停所有方法实验 · **先修门禁，再扩审，暂不逐题 revision**  
**更新时间：** 2026-07-31

## 为什么先审契约 / 先修门禁

TFL 等路径已证明：evaluator 不可推出要求会与“方法失败”混淆。  
抽查进一步证明：现有自动 constitution 门禁**并未**落实 TASK↔evaluator 双向 API 覆盖——
`returns` 曾被误标 `closed`，因门禁存在两个缺口（见下）。

**暂停：** 修 TFL、实现 Spec-Closure、抽 clean-6、**按 REVISION_QUEUE 逐题改并重跑 baseline**。  
**只做：** 修 audit gate → 修正标签 → 扩 opened-dev 审计 → 聚合问题族 → 再冻结批量修订政策。  
并行题层能力表：冻结并标注 [LIFT_TAXONOMY.md](../../reference/LIFT_TAXONOMY.md)
（Direct / Adapted / Composite）。

## 三维标签

```text
closure_status:   closed | underspecified | contradictory
oracle_relation:  direct_oracle | specified_adapter | inferred_adapter | no_upstream_oracle
lift_type:        Direct | Adapted | Composite
```

- `closure_status` × `oracle_relation`：契约是否闭合、证据从哪来。  
- `lift_type`：题的 feature-lifting 机制（定义见 [LIFT_TAXONOMY.md](../../reference/LIFT_TAXONOMY.md)）。  

三者正交。例：`lift_type=Direct` 且 `closure_status=underspecified`。  
`oracle_relation` 与 `lift_type` 的粗对齐见 lift taxonomy 文档；论文分布表以
`lift_type` 为准。

## 硬规则

1. **必须逐项审核全部 public/hidden 断言**（禁止 outcome-driven 修题）。
2. 测试只能使用**完整声明**的 API path（[TASK_DESIGN_RULES.md](../../TASK_DESIGN_RULES.md) §2.1）。
3. 修订保存旧 revision；整批冻结后再一次性 reference / validation / isolation / baseline。
4. 看过 evaluator 的题永久 `development`，`clean_eligible=false`。
5. `closure_status != closed` 不得用于判定方法成败。

## 审计事实源：`test_id → api_ids` manifest

路径：`benchmark/tasks/<id>/evaluation/test_api_usage.json`

```json
{
  "schema_version": "featureliftbench.test_api_usage.v1",
  "tests": [
    {
      "test_id": "public_tests/test_public_contract.py::test_success_map_and_bind",
      "api_ids": [
        "featurelifted.Success",
        "featurelifted.Success.map",
        "featurelifted.Success.bind",
        "featurelifted.Success.value"
      ]
    }
  ]
}
```

- **Manifest = 审核事实源**（人工/审计填写完整 path）。
- **AST = 交叉检查**：发现疑似遗漏；**不能**单独作为闭合证明（动态类型/返回值属性会有假阳性）。
- 门禁已改：类根声明**不再**覆盖未声明成员；链式 `.map().bind()` 会提取为 `Success.bind`。

实现：`harness/featureliftbench/constitution_validate.py`（`_validate_test_api_usage`）。

## 对 “150/150 spec-compliant” 的正确表述

> 150/150 通过了**现有/历史**自动门禁。

**不得**再宣称：

> 150/150 已证明 TASK–evaluator contract-closed。

## 执行顺序（锁定）

```text
修 audit gate
→ 修正 dev-6（closed 0/6）
→ 审完其余 opened-development hard tasks（只审计）
→ 聚合根因 / 冻结修订政策
→ 批量 revision wave
→ 批量 render/validate/reference/isolation/baseline
→ 再扩 hard50
→ 最后才恢复方法研究
```

## 产物

```text
reports/contract_closure_audit/
  DEV6_LABELS.jsonl
  DEV_OPENED_LABELS.md
  REVISION_QUEUE.md          # 政策草稿；暂不逐题执行
  OPENED_HARD_TASKS.txt
  OPENED_HARD_API_SCAN.jsonl # AST 表面扫描（非完整闭合审计）
  PROBLEM_FAMILIES.md
  OPENED_HARD_SUMMARY.md

reports/lift_taxonomy/
  LIFT_LABELS.jsonl          # 150 题 lift_type（seeded/unlabeled/reviewed）
  SUMMARY.md
```
