# experiments/

OpenHands **跑分结果**目录。顶层只有三个文件夹：

```text
experiments/
  smoke/                          # 烟囱 / pilot / 调试（乱七八糟）
  python/
    openhands/
      <model>/                    # 按模型分
        <run_id>/                 # 一次实验
  GO/
    openhands/
      <model>/
        <run_id>/
```

出题 gate 在 `evidence/`（不是实验结果）。

---

## 目录说明

| 路径 | 放什么 |
| --- | --- |
| `smoke/` | `--suite smoke`、pilot5、sanity、未完成 main 等调试 run |
| `python/openhands/<model>/` | Python **100 题正式榜**（`--suite main`） |
| `GO/openhands/<model>/` | Go track OpenHands run |

`<model>` 由模型名自动生成，例如：
- `deepseek/deepseek-v4-flash` → `deepseek-v4-flash`
- `openai/Qwen3.6-27B-FP8` → `qwen3.6-27b-fp8`

---

## 当前正式结果

### Python 100-hard（`python/openhands/`）

| 模型目录 | run_id | 成绩 |
| --- | --- | ---: |
| `deepseek-v4-flash/` | `main-flash-20260705-232429` | **83/100** |
| `qwen3.6-27b-fp8/` | `qwen36-27b-fp8-main-20260704-001328` | 54/100 |
| `qwen3.6-35b-a3b-fp8/` | `qwen36-35b-a3b-fp8-main-20260704-001313` | 49/100 |
| `qwen3-coder-30b-a3b-instruct/` | `main-20260702-212731` | 24/100 |

mini-swe-agent + Flash 满榜（66/100）在 `archive/mini-swe-agent/benchmark-main-flash-20260703-122657/`。

### Go（`GO/openhands/`）

| 模型目录 | run_id |
| --- | --- |
| `deepseek-v4-flash/` | `go-openhands-deepseek-v4-flash-20260705-001`（3 题 suite） |
| `deepseek-v4-pro/` | hard mapstructure 调试 run ×2 |

---

## 怎么跑

| 命令 | 输出路径 |
| --- | --- |
| `featureliftbench run --suite main` | `experiments/python/openhands/<model>/main-<时间>/` |
| `featureliftbench run --suite smoke` | `experiments/smoke/smoke-<时间>/` |
| `featureliftbench run --suite pilot5` | `experiments/smoke/pilot5-<时间>/` |
| `bash harness/scripts/run_go_openhands.sh <task>` | `experiments/GO/openhands/<model>/<run_id>/` |
