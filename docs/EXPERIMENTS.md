# FeatureLiftBench 实验清单与缺口

**最后更新：** 2026-07-24
**权威冻结口径：** [paper_runs_frozen.md](paper_runs_frozen.md)  
**怎么跑：** 根目录 [RUN.md](../RUN.md) §6.1  
**分析入口：** [paper_tables.md](paper_tables.md) · `reports/paper_analysis/executive_summary.md` · [research_analysis/TRAJECTORY_FINDINGS.md](research_analysis/TRAJECTORY_FINDINGS.md)

## 1. 现在能跑吗？

**能。** Python 主榜 **150 hard**、Oracle freeze `7c042d5528b7d0fd`
（450/450）、spec freeze `f7c616edb47ea533`、Docker agent/eval 与
test-blind Main runner 均可用。

| 能力 | 状态 |
| --- | --- |
| Reference / Docker eval | ✅ |
| OpenHands agent 主榜 | ✅ |
| 规格宪法 validate / migrate | ✅ Python-150（150 compliant / 0 legacy） |
| 完整四模型 Python-150 对比 | ⚠️ Flash 已冻结（**legacy 口径**）；Qwen candidate；Coder 缺 hard50 |
| ECSM Pilot | ⛔ **已废弃** |
| Compliant 子集 rebaseline | ✅ Flash hard-50：历史 Public-feedback **11/50**；test-blind Main **4/50** |

研究主线见 [CURRENT_RESEARCH.md](CURRENT_RESEARCH.md)：RSG 为可选工具，决策权在大模型。

## 2. 已完成的正式 Agent 实验

协议：OpenHands standard · 冻结于 `docs/paper_runs_frozen.md`。

### 2.1 Shared core-100（四模型）

| Model | Run ID | Pass | Avg final |
| --- | --- | ---: | ---: |
| deepseek-v4-flash | `main-flash-20260705-232429` | 83/100 | 0.520 |
| qwen3.6-27b-fp8 | `qwen36-27b-fp8-main-20260704-001328` | 54/100 | 0.324 |
| qwen3.6-35b-a3b-fp8 | `qwen36-35b-a3b-fp8-main-20260704-001313` | 49/100 | 0.303 |
| qwen3-coder-30b-a3b-instruct | `main-20260702-212731` | 24/100 | 0.173 |

路径：`experiments/python/openhands/<model>/<run_id>/`

### 2.2 Hard-extension-50（冻结集：Flash）

合并三波后 **8/50** pass（16%），avg final **0.037**。  
与 core-100 拼合 → Flash 全 Python-150：**91/150（60.7%）**，avg **0.359**。

### 2.3 Hard-50 compliant rebaseline（2026-07-24）

冻结同一 50 题、同一 DeepSeek V4 Flash、同一 standard prompt 与 Docker
agent/evaluator；唯一预期处理差异是 Agent workspace 是否挂载 Benchmark
基础 evaluator tests。

| 当前语义 | 历史运行标签 | Pass | Avg final | Infra failures | Total tokens |
| --- | --- | ---: | ---: | ---: | ---: |
| Public-feedback | Main | **11/50（22%）** | 0.120691 | 0 | 51,868,511 |
| Test-blind Main | No-public | **4/50（8%）** | 0.045947 | 0 | 55,018,550 |

配对结果：both-pass 4、Public-feedback-only 7、test-blind-Main-only 0、
both-fail 39；Public feedback 净增 14 percentage points，exact McNemar
`p=0.015625`。Legacy hard-50 为 8/50；与历史 public-feedback 条件的
compliant 结果差异为 +6 points，但 `p=0.375`，且迁移改变了规格/测试，
不能作稳定因果提分宣称。

> 这批结果生成时使用旧命名：`Main` 表示可见 public tests，`No-public`
> 表示不可见。v1.1 起默认 `Main` 即 test-blind；旧结果必须按上表映射，
> 不能静默当成新 Main。

原始 suite 与报告：
`experiments/ablation/hard50-compliant-deepseek-v4-flash-20260724/`。

### 2.4 2026-07-20 导入的 candidate runs

两个 Qwen hard50 run 已导入、任务集与 Flash Python-150 对齐，并通过 registry 结构检查；尚未加入论文冻结集。

| Model | Hard50 | Hard50 avg | 合并 Python-150 | 合并 avg |
| --- | ---: | ---: | ---: | ---: |
| qwen3.6-27b-fp8 | 4/50 | 0.026916 | **58/150** | 0.224684 |
| qwen3.6-35b-a3b-fp8 | 3/50 | 0.024567 | **52/150** | 0.210023 |

原始 bundle 与校验和位于 `experiments/bundles/incoming/`；组合口径见 `experiments/registry/studies/python150-current.json`。

### 2.5 已有分析产物（基于冻结 runs）

| 产物 | 位置 |
| --- | --- |
| Executive summary | `reports/paper_analysis/executive_summary.md` |
| 论文表草稿 | [paper_tables.md](paper_tables.md) |
| 轨迹统计 / 发现 | [TRAJECTORY_FINDINGS.md](research_analysis/TRAJECTORY_FINDINGS.md) · `artifacts/research_analysis/trajectory_statistics.md` |
| Case studies | `reports/paper_analysis/case_studies/` |
| 报告索引 | [REPORTS_INDEX.md](REPORTS_INDEX.md) |

## 3. 缺口与待冻结项

| 缺口 | 说明 | 推荐命令 |
| --- | --- | --- |
| 最新 compliant Python-150 基线 | 当前规格下必须整榜重跑；历史 legacy core/hard 结果不能拼接 | `./harness/scripts/run_python150_paper.sh <profile> <run-id> --execute` |
| Qwen3-Coder-30B hard50（历史 legacy 表） | 仅用于补历史旧口径，不替代 compliant 全榜 | `./harness/scripts/run_python_hard50_paper.sh openhands_qwen3_coder_30b_paper --execute` |
| Qwen3.6-27B / 35B candidate（历史 legacy 表） | 校验旧协议与运行元数据后才能写入旧 freeze 文档 | 使用 registry 审核，不与 compliant 新跑混报 |

冻结 candidate 或补齐 Coder 后：更新本文件与 [paper_runs_frozen.md](paper_runs_frozen.md)，再跑：

```bash
PYTHONPATH=harness .venv/bin/python harness/scripts/generate_paper_analysis.py
```

## 4. 基建 / Oracle / Control（非 agent leaderboard）

| 实验 | 状态 |
| --- | --- |
| Oracle freeze `7c042d5528b7d0fd` | ✅ canary 15/15；full 450/450；quarantine 0 |
| Spec freeze `f7c616edb47ea533` | ✅ 150/150 experiment-ready；内容寻址清单已生成 |
| Historical infra re-eval | ✅ 62/62 |
| batch-1 gate evidence | ✅ `evidence/python/batch1/` |
| Control functional preflight | ✅ 功能门过；workload 工时未记 |
| ECSM Pilot Stage A–C | ⛔ 已废弃；目录 `experiments/ecsm_pilot/` 仅历史保留 |
| OpenHands × RSG（旧 Pilot） | 历史诊断 2/12；**不恢复**旧强制采用门协议 |

### 4.1 OpenHands × RSG 历史诊断

2026-07-23 的 `rsg-pilot-v1-20260723-clean1`（DeepSeek-V4-Flash、Celery 题、P0/P3）
只完成第一对后因旧「必调 task-closure + submission-check」采用门停止：

| Arm | Formal | Total tokens | Max prompt | 备注 |
| --- | --- | ---: | ---: | --- |
| P0 | fail | 1,642,027 | 68,134 | 无 RSG |
| P3 | fail | 3,405,659 | 93,944 | 仅调了 `submission-check` |

该结果只说明硬性工具合同 fragile，**不**支持 RSG 效果结论。  
按 [CURRENT_RESEARCH.md](CURRENT_RESEARCH.md)，后续应在**重设计后的可选通用 RSG**上另开实验，而不是继续旧 12-cell Pilot。

## 5. 规格合规与实验口径（2026-07-24）

| 口径 | 题数 | 说明 |
| --- | ---: | --- |
| `spec_status: legacy` | 0 | 历史 Flash 91/150 等仍是 **legacy run 数字**；不能与新跑拼接 |
| `spec_status: compliant` | 150 | schema / validator / contract / Oracle 已闭环；可跑正式实验 |

- 合规报表：`reports/constitution/spec_compliance_150_20260724.csv`
- 新协议内容审计：`reports/audits/new_protocol_readiness.md`
- 当前审计：engineering-ready 150/150、完整非模板化契约 150/150、
  experiment-ready 150/150；含可发现上游测试 48/150 为信息项。
  独立人工审核 0/150，因此 paper-ready 0/150，但不阻塞模型实验。
- 迁移手册：[CONSTITUTION_MIGRATION.md](CONSTITUTION_MIGRATION.md)
- Compliant 重跑示例见 [RUN.md](../RUN.md) §1.5 · [CONSTITUTION_MIGRATION.md](CONSTITUTION_MIGRATION.md) §6

## 6. 服务器最短路径

```bash
git pull
PYTHON=python3.12 SKIP_MINI=1 ./setup.sh
# 配置 .env 中对应 API key / base

./harness/scripts/run_python150_paper.sh \
  openhands_deepseek_v4_flash \
  compliant150-flash-main-001

./harness/scripts/run_python150_paper.sh \
  openhands_deepseek_v4_flash \
  compliant150-flash-main-001 \
  --workers 1 \
  --execute
```

完整流程见 [SERVER_RUNBOOK_COMPLIANT150.md](SERVER_RUNBOOK_COMPLIANT150.md)；Docker 默认值见 [RUN.md](../RUN.md)。项目状态见 [STATUS.md](STATUS.md)。
