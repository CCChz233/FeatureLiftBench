# FeatureLiftBench 实验清单与缺口

**最后更新：** 2026-07-23
**权威冻结口径：** [paper_runs_frozen.md](paper_runs_frozen.md)  
**怎么跑：** 根目录 [RUN.md](../RUN.md) §6.1  
**分析入口：** [paper_tables.md](paper_tables.md) · `reports/paper_analysis/executive_summary.md` · [research_analysis/TRAJECTORY_FINDINGS.md](research_analysis/TRAJECTORY_FINDINGS.md)

## 1. 现在能跑吗？

**能。** Python 主榜 **150 hard**、Oracle freeze `5f9012f6dc748c90`（150/150）、Docker agent/eval 均可用。

| 能力 | 状态 |
| --- | --- |
| Reference / Docker eval | ✅ |
| OpenHands agent 主榜 | ✅ |
| 完整四模型 Python-150 对比 | ⚠️ Flash 已冻结；Qwen 27B/35B candidate 已齐；Coder 缺 hard50 |
| ECSM Pilot（机制臂） | ❌ 0/70（待导出授权） |
| OpenHands RSG Pilot | ⛔ 2/12 付费采用门后停止；不进入正式效果统计 |

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

### 2.3 2026-07-20 导入的 candidate runs

两个 Qwen hard50 run 已导入、任务集与 Flash Python-150 对齐，并通过 registry 结构检查；尚未加入论文冻结集。

| Model | Hard50 | Hard50 avg | 合并 Python-150 | 合并 avg |
| --- | ---: | ---: | ---: | ---: |
| qwen3.6-27b-fp8 | 4/50 | 0.026916 | **58/150** | 0.224684 |
| qwen3.6-35b-a3b-fp8 | 3/50 | 0.024567 | **52/150** | 0.210023 |

原始 bundle 与校验和位于 `experiments/bundles/incoming/`；组合口径见 `experiments/registry/studies/python150-current.json`。

### 2.4 已有分析产物（基于冻结 runs）

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
| Qwen3-Coder-30B hard50 | 缺 50 题 | `./harness/scripts/run_python_hard50_paper.sh openhands_qwen3_coder_30b_paper --execute` |
| Qwen3.6-27B / 35B candidate | 校验协议与运行元数据后写入 freeze 文档 | 不需重跑；使用 registry 审核 |
| （可选）整榜重跑 150 | 更贵；Flash 一般不必 | `./harness/scripts/run_python150_paper.sh <profile> --execute` |

冻结 candidate 或补齐 Coder 后：更新本文件与 [paper_runs_frozen.md](paper_runs_frozen.md)，再跑：

```bash
PYTHONPATH=harness .venv/bin/python harness/scripts/generate_paper_analysis.py
```

## 4. 基建 / Oracle / Control（非 agent leaderboard）

| 实验 | 状态 |
| --- | --- |
| Oracle freeze `5f9012f6dc748c90` | ✅ 450/450，quarantine 0 |
| Historical infra re-eval | ✅ 62/62 |
| batch-1 gate evidence | ✅ `evidence/python/batch1/` |
| Control functional preflight | ✅ 功能门过；workload 工时未记 |
| ECSM Pilot Stage A–C | ❌ 0 cells |
| OpenHands RSG Pilot | 2/12；`paid_pair_rsg_adoption_gate_failed` |

### 4.1 OpenHands RSG Pilot 门控

冻结口径为 DeepSeek-V4-Flash、OpenHands 1.16 / SDK 1.21、Celery 与
Requests Cache 两题、P0/P3 各 3 次。2026-07-23 的干净实验
`rsg-pilot-v1-20260723-clean1` 只执行了预注册的第一对：

| Arm | Formal | Total tokens | Max prompt | Condensation | RSG adoption |
| --- | --- | ---: | ---: | ---: | --- |
| P0 | fail | 1,642,027 | 68,134 | 0 | n/a |
| P3 | fail | 3,405,659 | 93,944 | 0 | fail：缺 `task-closure` |

P3 的 `submission-check` 成功且 fresh，graph 初始化、泄漏、protocol 和
context violation 均为 0，但 `task_closure_queried=false`。控制器因此停止，
没有运行后续 10 cells。单对结果只用于机制采用诊断，不用于比较 pass 或
token 效果。恢复条件是 OpenHands 原生 RSG tool 注册和新的真实 mechanism
smoke 通过。

## 5. 服务器最短路径

```bash
git pull
./setup.sh   # 确保 agents.toml 来自 agents.example.toml
# 配置 .env 中对应 API key / base

./harness/scripts/run_python_hard50_paper.sh openhands_qwen3_6_27b_fp8_paper          # dry-run
./harness/scripts/run_python_hard50_paper.sh openhands_qwen3_6_27b_fp8_paper --execute
# 同理 35B / coder
```

细节与 Docker 默认值见 [RUN.md](../RUN.md)。项目状态见 [STATUS.md](STATUS.md)。
