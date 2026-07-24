# FeatureLiftBench 下一周执行清单

**最后更新：** 2026-07-24 · 当前状态摘要：[../STATUS.md](../STATUS.md)

> **方向覆盖（2026-07-23）**  
> ECSM Pilot（下文 P0-4 / P0-5 / Stage A–C）**全部停止**。  
> 当前优先：按 [../CURRENT_RESEARCH.md](../CURRENT_RESEARCH.md) **重设计通用 RSG**；补齐 leaderboard 缺口；推进独立人工标注门禁。  
> 下文 2026-07-19 清单中与 ECSM 执行相关的条目仅作历史。

## 当前起点（2026-07-19 快照 + 2026-07-23 修订）

- Python150 当前 Oracle freeze **`7c042d5528b7d0fd`** 已完成 canary
  15/15 和 full 450/450：**150 题稳定通过，0 题 quarantine**。对应
  spec freeze 为 **`f7c616edb47ea533`**；旧 freeze
  `5f9012f6dc748c90` 只保留作历史证据。
- **P0-2（13 quarantine 修复）已完成** — 证据见 [ORACLE_REVALIDATION_REPORT.md](ORACLE_REVALIDATION_REPORT.md) 与 `experiments/v1_1_oracle_validation/5f9012f6dc748c90/`。
- 150/150 行为契约已映射 328 public + 643 hidden nodeids；状态仍为 `ai_assisted_reviewed`，**不能**写成独立人工 gold。
- Diagnostic-40 file scope 40/40 complete（AI-assisted）；**0/40** 独立人工 adjudication。
- Taxonomy v1：150 rows、121 sources；15 rows 仍待人工 adjudication。Representative-20 constraint audit：`exact_constraints`。
- Control functional preflight 已通过；**workload gate 未通过**（缺 prospective person-hours 记录）。
- 论文 release gate：**8/13**；engineering Pilot freeze revision 5（`c94764ed110992a6`）已通过；**0/14** Stage A cells 已执行。
- Pilot 执行仍等待扩大外部导出范围的明确授权。

## P0-1：完成独立人工标注与裁决

- **任务内容：** 两位标注者独立审核 behavior contract、Diagnostic-40 closure、15 个 taxonomy AI-assisted rows 和 8 个近重复簇；第三方裁决分歧。
- **优先顺序：** Pilot-10 + 六个 contract 疑点 → Diagnostic-40 → 剩余 Python150 behavior mappings。
- **输入：** `benchmark/tasks/*/TASK.md`、metadata、公开/隐藏测试、`evaluation/behavior_contract.json`、Diagnostic-40 `closure_gold.json`、taxonomy CSV 与 review queues。
- **输出：** 更新 review status、reviewer、disagreement、adjudicator 和 evidence；重建 audit JSON、release gate。
- **验收：** 150 behavior contracts 人工审核；40/40 closure 独立裁决；15 taxonomy + 8 近重复簇人工语义裁决；κ / Jaccard 达预注册阈值或有重标记录。
- **依赖：** 必须有真实两位人类标注者；AI 不能替代该门禁。
- **已完成（工程预备，2026-07-19）：** 专家 AI 审阅包 [expert_review/](expert_review/) — taxonomy 15/15 accept（2 reservation）、近重复 8/8 accept、Pilot-10 10/10 engineering accept（3 reservation）、Diagnostic-40 file-scope provisional。真人审阅应优先处理该包中的 reservation / spot-check 清单。**不可**据此将 gate 标为 human-reviewed。

## P0-2：修复并重验 quarantine 任务 — **已完成（2026-07-19）**

- **历史结果：** 13 题全部修复；freeze `5f9012f6dc748c90`
  450/450 全过；ledger `benchmark/quarantine/python_v1_1_revision_3.json`。
  当前 contract-hardened freeze 已更新为 `7c042d5528b7d0fd`。
- **报告：** [ORACLE_REVALIDATION_REPORT.md](ORACLE_REVALIDATION_REPORT.md)
- **主要改动：** `harness/scripts/build_oracle_submission.py`（relocation、vendor、grammar、babel/environs 等）

## P0-3：补 prospective workload 记录

- **任务内容：** 使用 boltons/pluggy control 模板，前瞻记录 acceptable alternative、copy-heavy、narrow 的实际人工时间、非环境返工轮数和 evaluator 次数。
- **输入：** `control_workload_prospective_log.csv`、control submissions 和 evaluator。
- **输出：** 完整 workload log 与 `control_workload_record.json`。
- **验收：** 两题总 person-hours、返工轮数、Pilot-10 人日投影均可审计。

## P0-4：授权后只运行 Stage A

- **任务内容：** Pilot-10 公共资产外发授权后，验证 revision-5 freeze，运行 boltons/schema 14 cells。
- **命令：** `python experiments/ecsm_pilot/pilot_freeze.py verify`；`python experiments/ecsm_pilot/run_pilot.py --stage A --execute`；`python experiments/ecsm_pilot/analyze_pilot.py`。
- **验收：** 14/14 artifact 完整；无 hidden leakage；condition hash 与 usage 可追溯。

## P0-5：Stage B 资源门禁与有条件 Stage C

- **任务内容：** Stage A 通过后四题 × 五 arms = 20 cells；分析器写 `stage_b_resource_decision.json`；门禁触发才补 Stage C 36 cells。
- **验收：** Stage B 阈值只用于资源分配；完整 70 cells 需结合 Diagnostic-40 与轨迹证据。

## P1：论文 release candidate

- **任务内容：** P0-1、P0-3 完成后重建 audit/release 文档，冻结 paper-ready revision。
- **验收：** release gate 13/13；paper-ready freeze 区别于 provisional engineering freeze。

## 本周明确不做

不运行 150×7；不扩 Go；不训练模型；不把 AI-assisted review 写成独立人工 gold；不把未运行 cell 填成失败或零分。
