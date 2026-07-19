# experiments/

OpenHands **跑分结果**目录（默认 gitignore，不进仓库）。

```text
experiments/
  smoke/                          # 烟囱 / pilot / 调试
  python/
    openhands/
      <model>/                    # 按模型分
        <run_id>/                 # 一次实验
  GO/
    openhands/
      <model>/
        <run_id>/
  v1_1_* / batch3-* / ecsm_pilot/ # 基建、材料化、Pilot（非主榜 leaderboard）
```

出题 gate 在 `evidence/`（不是实验结果）。  
**正式实验清单与缺口：** [docs/EXPERIMENTS.md](../docs/EXPERIMENTS.md)  
**冻结 run ID：** [docs/paper_runs_frozen.md](../docs/paper_runs_frozen.md)  
**怎么跑：** [RUN.md](../RUN.md) §6.1

---

## 目录说明

| 路径 | 放什么 |
| --- | --- |
| `smoke/` | smoke / pilot / 调试 run |
| `python/openhands/<model>/` | Python 正式 OpenHands run（core-100、hard50、或 python150） |
| `GO/openhands/<model>/` | Go track OpenHands run |

`<model>` 示例：`deepseek-v4-flash`、`qwen3.6-27b-fp8`。

---

## 当前正式结果（摘要）

### Python core-100

| 模型目录 | run_id | 成绩 |
| --- | --- | ---: |
| `deepseek-v4-flash/` | `main-flash-20260705-232429` | **83/100** |
| `qwen3.6-27b-fp8/` | `qwen36-27b-fp8-main-20260704-001328` | 54/100 |
| `qwen3.6-35b-a3b-fp8/` | `qwen36-35b-a3b-fp8-main-20260704-001313` | 49/100 |
| `qwen3-coder-30b-a3b-instruct/` | `main-20260702-212731` | 24/100 |

### Python-150 / hard50

| 模型 | 状态 |
| --- | --- |
| Flash | ✅ 全 150（core-100 + hard50 合并）→ **91/150** |
| 另三模型 | ❌ 缺 hard50；用 `run_python_hard50_paper.sh` 补齐 |

### Go

| 模型目录 | 说明 |
| --- | --- |
| `deepseek-v4-flash/` 等 | pilot / calibration，非 paper main |

---

## 怎么跑（服务器）

| 目标 | 命令 |
| --- | --- |
| 补 hard50（推荐） | `./harness/scripts/run_python_hard50_paper.sh <paper-profile> --execute` |
| 整榜 150 | `./harness/scripts/run_python150_paper.sh <profile> --execute` |
| 分析 suite | `PYTHONPATH=harness python harness/scripts/analyze_benchmark_suite.py <suite_dir>` |
| 论文表重建 | `PYTHONPATH=harness python harness/scripts/generate_paper_analysis.py` |

Paper profiles 见 `harness/config/agents.example.toml`（`openhands_qwen3_*_paper`、`openhands_deepseek_v4_flash`）。
