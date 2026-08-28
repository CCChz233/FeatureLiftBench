# Hard-50 选题矩阵（冻结草稿）

> **Status: current · Last verified: 2026-08-28**  
> 权威机读副本：[`benchmark/selection/hard50_selection_matrix.json`](../benchmark/selection/hard50_selection_matrix.json)  
> 配额是目标，不是为贴标签而假 Composite。50 selected 已落地；`direct_tooling_copytrap` 是 RQ2 选题格，不是第 11 个 feature family。

对应论文轴见 [PLAN_HARD50_EXPANSION.md](PLAN_HARD50_EXPANSION.md) 与 [paper/02_research_questions.md](paper/02_research_questions.md)。

## 机制族 × 目标 n

| 机制族 | 目标 n | 占比 | 服务的论文轴 | 失败机制（RQ4） | 若删掉这格，论文少了什么 |
| --- | ---: | ---: | --- | --- | --- |
| registry_plugin_dispatch | 13 | 26% | RQ1, RQ4, RQ5 | implicit dependency / dynamic import / global registry | 无法证明 Agent 能恢复「未在 TASK 点名的注册表闭合」 |
| config_resolve_discover | 11 | 22% | RQ1, RQ4 | config/environment merge, file discovery | 无法测多源配置覆盖与发现链 |
| workflow_session_orchestration | 8 | 16% | RQ1, RQ4 | lifecycle / session / cancel / scheduling | 无法测状态机与生命周期 Hidden |
| validate_normalize_construct | 9 | 18% | RQ1, RQ4 | data-model invariants, error paths | 无法测边界保真（naive 过 public、挂 Hidden） |
| parse_tokenize_decode | 4 | 8% | RQ1, RQ5 | parser state, dialect/transform | 保留深状态解析，避免 E50 浅 parse 稀释 |
| direct_tooling_copytrap | 5 | 10% | RQ2, RQ5 | compactness / copy-all 诱饵 | 证明大仓小切片时 copy-all RRES 必须差 |

合计 50。Direct 工具格每题必须有 copy-all 诱饵（无关模块/测试/插件远大于目标闭包）。

## Lift × 机制族（selected 目标）

Lift 贴近 Python-150：**Adapted 25 / Composite 13 / Direct 12**（50% / 26% / 24%）。

实现以 ledger `targets.lift_types` 为准（看源码后允许改类，须写 `reclassification_reason`）。

## Entanglement（每题）

- `level`: **high**
- types: **≥2**，优先含 `implicit_dependency_coupling` 或 `framework_coupling`
- 分析字段默认不进 TASK（[TASK_DESIGN_RULES.md](TASK_DESIGN_RULES.md) §2.4）

## 仓规模

- 目标中位 `python_loc` ≥ 8k–11k（对齐 Python-150）
- 拒 <3k 单模块微库，除非 oracle 闭包 ≥5 文件且仓内 decoy 明确
- 不与 `benchmark/sources/registry.json` 或 `external50_registry.json` 的 upstream 重叠

## Pilot 10 占格（未 pin）

优先 registry / config / workflow，覆盖三种 lift：

| slot | 机制族 | 计划 lift |
| --- | --- | --- |
| P1 | registry | Composite |
| P2 | registry | Adapted |
| P3 | registry | Composite |
| P4 | registry | Composite |
| P5 | config | Adapted |
| P6 | config | Composite |
| P7 | config/registry | Composite |
| P8 | workflow | Composite |
| P9 | workflow | Composite |
| P10 | validate | Composite |

具体 `task_id` 见 ledger `pilot_candidates`。
