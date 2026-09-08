# 第二章写作与证据索引

2026-09-08。已直接扩写 `../main.tex` 的 §2.2–2.4，并补充附录 A。
保留 §2.1 的任务形式化和 Blinker 示例；不新增实验，不编译、渲染或生成图像。

## 章节如何讲

1. **§2.1 定义任务：** 完整源仓库和公开契约作为输入，独立包作为输出；Blinker 说明主流程之外仍需保留的行为。
2. **§2.2 说明构造：** 候选功能与源版本 → 可观察契约 → 受保护测试及 reference → 候选与最终冻结。解释每一步产生什么，以及如何支持复用任务的边界。
3. **§2.3 说明可信度：** 源身份与题包一致性、reference 可执行性与重复性、契约复核及覆盖限制。
4. **§2.4 说明组成：** 200/150/两个 50 的关系，仓库与快照数量，功能覆盖，三类 lift 的实例及标签性质。
5. **附录 A：** 提供完整任务索引的路径、字段和证据范围。

## 事实对应材料

| 内容 | 项目中的依据 | 采用方式 |
| --- | --- | --- |
| 候选功能范围与离线约束 | `docs/reference/python/01_python_repo_selection_criteria.md`；`docs/TASK_DESIGN_RULES.md` | 作为选择指导，不推断全部候选曾统一评分 |
| 扩展集 50 selected + 20 backup | `benchmark/selection/hard50_expansion_20260827.json` | 限定为这一轮的记录，不能当成全项目候选池 |
| 完整仓库、固定 commit、双 digest | `docs/FULL_REPOSITORY_SOURCE_POLICY.md`；当前 candidate/final freeze | 说明 source policy 与身份记录；182 archive 检查是历史记录 |
| 公开契约、映射与生成视图 | `docs/TASK_DESIGN_RULES.md`；`harness/featureliftbench/task_spec.py`、`task_render.py`、`constitution_validate.py` | 区分设计规则与检查实现；Main 中两组测试均不提供 |
| 候选冻结与最终冻结 | `scripts/build_python200_prime_candidate_freeze.py`、`build_python200_prime_final_freeze.py` | 读取实现与现存产物；未运行构建或验证流水线 |
| 200 任务 / 176 仓库 / 182 快照 | `artifacts/research_analysis/python200_prime/current_benchmark_freeze.json` | 按冻结的 canonical repository / snapshot ID 计数 |
| Python-150：126 仓库 / 132 快照；扩展：50 / 50 | 同上 | 数据集表新增快照列 |
| 600 次 reference 执行、200 个稳定结果 | `reports/audits/python200_prime_oracle_revalidation/summary.json` | 作为保存的运行证据，不表示本轮重跑或所有 agent 运行环境相同 |
| 38 题 LLM repair review | `current_repair_semantic_review_v2_closed.json` | 独立人工与 gold 均为 false |
| 其中 6 题 maintainer-proxy adjudication | `current_repair_maintainer_adjudication_v2.json` | reviewer 为 coding-agent-maintainer-proxy；修正文中“38 题均 maintainer-adjudicated”的宽泛说法 |
| 十个功能组与 lift 标签 | `artifacts/research_analysis/python200_hard_task_taxonomy.csv`；`docs/reference/LIFT_TAXONOMY.md` | 历史标签按 task ID 关联；150 labeled、50 planned_ledger；不升级为独立人工标注 |
| 三类实例 | Blinker、build、zope.interface 对应任务的当前 `metadata.public_spec` | 只使用公开要求、排除项和已有标签，不披露隐藏测试 |

以上 repair 文件位于 `artifacts/research_analysis/python200_prime/`。

## 随文任务索引

- `chapter2_task_inventory.json`：完整 200 条，包含当前冻结来源、reference 和历史分类字段。
- `chapter2_evidence.json`：聚合统计、输入文件 SHA-256、核对范围和限制。
- `chapter2_evidence.py`：仅从本地已存记录生成上述材料；不执行模型、oracle 或源归档下载。

本轮核对了全部 200 题的公开 specification 与 TASK 文本 hash，均匹配冻结；reference registry 的 200 条记录也与冻结 reference digest 相符。这并不等于重新核验所有 reference 实体或完整题包目录。

历史 taxonomy 有 **44 条 source commit 与当前冻结不同**，因此保留两种版本身份和匹配标志；功能类别仅用于概述覆盖面。扩展集的三类 lift 计数没有混入主集的已标注统计。

## 仍不可从现有材料补成事实的内容

- 全部任务共同的原始候选池、统一筛选漏斗、每轮排除数量。
- 全部任务的人工作者人数、标注耗时、独立人工一致性指标。
- 全量 adversarial、naive/copy-all 校准均已完成。
- 每条隐藏断言均完成独立语义公平性复核。

这些限制不阻止第二章形成完整初稿。后续应先补案例分析与讨论，再按 FSE 篇幅压缩；不要为了扩写补造构建历史。
