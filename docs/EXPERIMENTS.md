# FeatureLiftBench 实验清单与缺口

**最后更新：** 2026-07-20  
**权威冻结口径：** [paper_runs_frozen.md](paper_runs_frozen.md)  
**怎么跑：** 根目录 [RUN.md](../RUN.md) §6.1  
**分析入口：** [paper_tables.md](paper_tables.md) · `reports/paper_analysis/executive_summary.md` · [research_analysis/TRAJECTORY_FINDINGS.md](research_analysis/TRAJECTORY_FINDINGS.md)

## 1. 现在能跑吗？

**能。** Python 主榜 **150 hard**、Oracle freeze `5f9012f6dc748c90`（150/150）、Docker agent/eval 均可用。

| 能力 | 状态 |
| --- | --- |
| Reference / Docker eval | ✅ |
| OpenHands agent 主榜 | ✅ |
| 完整四模型 Python-150 对比 | ⚠️ Flash 已齐；另三模型缺 hard50 |
| ECSM Pilot（机制臂） | ❌ 0/70（待导出授权） |

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

### 2.2 Hard-extension-50（仅 Flash）

合并三波后 **8/50** pass（16%），avg final **0.037**。  
与 core-100 拼合 → Flash 全 Python-150：**91/150（60.7%）**，avg **0.359**。

### 2.3 已有分析产物（基于上述 runs）

| 产物 | 位置 |
| --- | --- |
| Executive summary | `reports/paper_analysis/executive_summary.md` |
| 论文表草稿 | [paper_tables.md](paper_tables.md) |
| 轨迹统计 / 发现 | [TRAJECTORY_FINDINGS.md](research_analysis/TRAJECTORY_FINDINGS.md) · `artifacts/research_analysis/trajectory_statistics.md` |
| Case studies | `reports/paper_analysis/case_studies/` |
| 报告索引 | [REPORTS_INDEX.md](REPORTS_INDEX.md) |

## 3. 缺口（要做完整 150 对比还差什么）

| 缺口 | 说明 | 推荐命令 |
| --- | --- | --- |
| Qwen3.6-27B hard50 | 缺 50 题 | `./harness/scripts/run_python_hard50_paper.sh openhands_qwen3_6_27b_fp8_paper --execute` |
| Qwen3.6-35B hard50 | 缺 50 题 | `./harness/scripts/run_python_hard50_paper.sh openhands_qwen3_6_35b_a3b_fp8_paper --execute` |
| Qwen3-Coder-30B hard50 | 缺 50 题 | `./harness/scripts/run_python_hard50_paper.sh openhands_qwen3_coder_30b_paper --execute` |
| （可选）整榜重跑 150 | 更贵；Flash 一般不必 | `./harness/scripts/run_python150_paper.sh <profile> --execute` |

补齐后：更新本文件与 [paper_runs_frozen.md](paper_runs_frozen.md)，再跑：

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
