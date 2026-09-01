# Plan: Hard-50 进新 Python-200（论文对齐 + 宁难勿易）

> **Documentation status: current · Created: 2026-08-27 · Last verified: 2026-08-28**  
> 旧 External-50 实体与历史结果不动。Hard-50 与冻结 Python-150 组成新主套件。  
> 选题矩阵：[hard50_selection_matrix.md](hard50_selection_matrix.md) · ledger：`benchmark/selection/hard50_expansion_20260827.json`

**本阶段完成：** Pilot 10 Flash 功能 **4/10 = 40%**；余 40 Flash 功能 **25/40 = 62.5%**；Hard-50 合计功能 **29/50 = 58%**（目标带 40%–65% 内）。Phase 2 已 release。整套 200 主表 Flash 尚未跑。禁止事后加 Hidden。禁止宣称已进 Python-150 主表。

## 定稿组成

```text
保留（不改实体、不删结果）
  benchmark/external50/
  benchmark/python200_tasks/          # 旧 150+E50，标 superseded，可查询

新主套件（论文主表实体已物化，Flash 主表分未出）
  Python-200' = 冻结 Python-150 + Hard-50
  benchmark/tasks/                    # 150 不动（freeze 846b8147…）
  benchmark/hard50/                   # Hard-50 release 实体（50 题，无 oracle）
  benchmark/python200_hard_tasks/     # 150→tasks + 50→hard50 符号链接
```

- 主表只报 **150 + Hard-50**。
- External-50 仅作 easy / copy-heavy 旁路，分数不混进新主表。
- 不把 Hard-50 写入 `benchmark/tasks/`。
- 不复用 E50「只改合同不换题」路径。

## 论文主张 → 选题必须服务什么

论文定位（[paper/07_top_conference_readiness_plan.md](paper/07_top_conference_readiness_plan.md)、[paper/06_paper_outline.md](paper/06_paper_outline.md)）：

> 评测代码 Agent **从完整纠缠仓库**抽取 **行为完整、独立、尽量紧凑** 的功能包；
> 主瓶颈是行为闭合 / 不可见 Hidden / 无效自测尾部——不是绿场写码，也不是修 issue。

| 论文轴 | 选题必须提供的证据价值 |
| --- | --- |
| **RQ1 能力** | No-Hint 下定位 + 契约完成 + 解耦；浅 Direct 整包 copy 过不了关 |
| **RQ2 紧凑性** | 仓内有大片无关 decoy；copy-all 功能过但 RRES 明显劣于 reference |
| **RQ4 失败机制** | 至少压到一类：closure / registry / config / state / 边界行为 |
| **RQ5 任务因子** | lift、entanglement、footprint 可分层；禁止假 Composite |

**有意义：** 真实工程里会被抽成独立包；上游有 tests/docs；切片边界清晰。  
**无意义（拒）：** 玩具 OTP/semver、单文件 recipe、假 Composite、整框架 vendoring、无边界「抽半个 Django」。

每张 card 强制 `paper_fit` 与 `why_hard`。缺一项不进 selected。

## 难度：合理前提下宁难勿易

- 下限：Flash 不得再出现 E50 式 **>85%** trivial pass 或通过解 RRES≈1.0。
- 目标带：Hard-50 Flash Functional **≤ Python-150 同模型带宽**，优先 **~40%–65%**。
- 过难可留：题目合理、oracle 稳、合同公平时 **20%–40%** 可接受；禁止为抬分砍 Hidden。
- 假难不可接受：糊合同、未声明 API、过严 `match=`、无意义巨仓。

| 基线 | 期望 |
| --- | --- |
| Oracle | public+hidden 全过 |
| Naive/shallow | hidden 失败 |
| Copy-all | 功能可过，RRES 明显劣于 reference |
| Flash | >85% 或 RRES≈1.0 → 换题；40%–65% 优先留；20%–40% 且 paper_fit 强 → 留；<15% 且合同可疑 → 复查假难 |
| 压分 | **禁止**事后加 Hidden；只许换 slice/仓或补清公开义务 |

## 落地路径

| 组件 | 路径 |
| --- | --- |
| 开发区 | `benchmark/hard50_pilot/` |
| Release | `benchmark/hard50/` |
| Cards | `benchmark/selection/hard50_design_cards/` |
| Ledger | `benchmark/selection/hard50_expansion_20260827.json` |
| Registry | `benchmark/sources/hard50_registry.json` |
| 合并 registry | `benchmark/sources/python200_hard_registry.json`（150 + Hard-50，**不含** E50） |
| Suite / symlink | `benchmark/selection/python200_hard_suite.json` / `benchmark/python200_hard_tasks/` |
| 物化 | `benchmark/selection/scripts/materialize_python200_hard_release.py` |

仓池不得与 Python-150 或 External-50 upstream 重叠。换题只用 ledger `backup`，尽量同 `planned_lift_type` 与机制族。

## 分阶段

### Phase 0 — 矩阵 + 卡片（当前）

1. 本文件 + 选题矩阵。
2. 按格找仓，不先开仓再硬套题。
3. 50 selected + ≥15 backup cards（`paper_fit` / `why_hard`）。
4. **不 pin、不写 tests/reference。**

### Phase 1 — Pilot 10（难度闸）

清单见 ledger `pilot_candidates`。每题：pin → `hard50_pilot/` materialize → validate/oracle/isolation → copy-all + naive + Flash。  
过易必换；过难且合理则留。未过闸 **不开** 后 40。

### Phase 2 — 扩满 50 + release

backup 换题；50/50 工程门；跑 `materialize_python200_hard_release.py`；`check_python200_baseline_freeze.py` 仍只保证 150 不变。  
STATUS：新 suite 行；旧 `python200-full-repository-no-hint-20260801-v1` 标 superseded；E50 旁路。

### Phase 3 — 主表重跑

对 `python200_hard_tasks/` 跑 Flash（及后续模型）。列 **150 / Hard-50 / Python-200'**。禁止混用旧 E50 90%–94%。

## 明确禁止

- 为凑 50 瞎选仓，或先选热门库再硬找 slice
- 无 `paper_fit` / `why_hard` 的卡片进 selected
- Direct 微库、假 Composite、合同模板句、事后 Hidden 压分
- 改 E50 实体或 150 freeze
- 用「一天升格合同」冒充 Hard-50
- 宣称 Hard-50 已出论文主表分（release 实体已齐，Flash 200 未跑）

## 进度

- [x] PLAN + 选题矩阵 + 目录骨架
- [x] 50 selected + 15 backup design cards（commit 均为 pending pin）
- [x] Pilot 10 pin + materialize + copy-all/naive（本地 eval 绿）
- [x] Pilot 10 Flash（原 10 题功能 5/10=50%）
- [x] 换 confuse→paste、injector→polyfactory、openapi_core→graphene；换题 Flash 功能并回 **4/10=40%**（带内下沿）
- [x] 余 40 本地闸齐（pyfakefs blocked→webob 已 pin 并过闸）
- [x] 扩满 50 + `python200_hard_tasks/` release（suite `python200-hard-full-repository-no-hint-unreleased`）
- [x] 余 40 Flash（功能 25/40=62.5%；Hard-50 合计 29/50=58%）
- [x] 6 道换题 Flash：功能 **6/6**（suite 5 passed / 1 failed=`pika` agent exit 86，但 `functional_gate=1.0`）；通过解 RRES 0.10–0.72。Hard-50 拼回 **29/50 = 58%**（带内）
- [x] 重建 `hard50/` + `python200_hard_tasks/` + `python200_hard_registry`（digest `6b1cac758212…`；suite 仍 `python200-hard-full-repository-no-hint-unreleased`）
- [x] 合并 150 taxonomy + Hard-50 ledger 为 Python-200' 分析层表（`python200_hard_v1`）
- [x] 结果包接收与离线审计：原始 headline 132/200；17 题未启动、16 题依赖失败、59 题 context violation
- [x] 冻结严格替换集合：三类问题按 task ID 去重为 84 题；固定子集 95/116
- [ ] 结果资格闭环：修复离线依赖与 freeze-spec mismatch，严格替换 84 题并按 task ID 合并
