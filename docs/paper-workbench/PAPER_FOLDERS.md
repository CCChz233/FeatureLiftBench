# 论文与 `benchmark/`、`experiments/` 对照

> **Status: current · Last verified: 2026-09-14**

2026-09-14 已把与当前论文无关的题包和旧运行移到
[`archive/paper_unrelated_20260914/`](../../archive/paper_unrelated_20260914/README.md)。
没有删除。论文数字仍以 [`paper_sources.json`](paper_sources.json) 和 `reports/paper_analysis/` 为准。

## 现在这两个目录里有什么

`benchmark/` 只留冻结题包：

| 路径 | 作用 |
| --- | --- |
| `benchmark/tasks/` | 正文 150 题的实体包（另有一道 sanity：`iniconfig__parse_config__001`） |
| `benchmark/hard50/` | freeze 里另外 50 题；正文不报这 50 题成绩 |
| `benchmark/python200_hard_tasks/` | 200 个符号链接：150 → `tasks/`，50 → `hard50/` |
| `benchmark/sources/` | 源仓库 registry 与快照记录 |
| `suites.toml` / `manifest.json` / `README.md` / `PAPER.md` | 套件名与说明 |

`experiments/` 已解出论文结果包中能恢复的部分：

| 路径 | 作用 |
| --- | --- |
| `experiments/python/openhands/deepseek-v4-pro/python150-prime-v2-main-r1` | Pro 原始运行，150/150 |
| `experiments/python/openhands/deepseek-v4-flash/python200-prime-v2-main-r1` | Flash 原始运行，200/200（正文用其中 150 题） |
| `experiments/python/openhands/glm-5.3-flash/python200-prime-v2-main-r1` | GLM，压缩包截断，共 12 题；其中 7 题属于论文 150 题 |
| `experiments/paper_results_20260913/` | 清单、恢复说明 |
| `experiments/paper-results-full-20260913T154543Z.tar.gz` | 原包；gzip 不完整，Luna/Qwen/OSS 不在里面 |
| `experiments/registry/` | 历史路径台账 |

正文表仍读 `reports/paper_analysis/`。缺的 Luna/Qwen/OSS 原始目录需要完整的 6.35 GB 包才能补。恢复细节见 [`experiments/paper_results_20260913/README.md`](../../experiments/paper_results_20260913/README.md)。

## 论文读数路径

```text
benchmark/python200_hard_tasks/<id>/   题面与契约（150 题链到 tasks/）
docs/paper/writing/python150_membership.json
artifacts/.../current_benchmark_freeze.json
        │
        ▼
reports/paper_analysis/python150_prime_v2_analysis_20260905/task_results.csv
reports/paper_analysis/source_ablation_40_20260913/
        │
        ▼
docs/paper/main.tex
```

Blinker 例题：`benchmark/python200_hard_tasks/blinker__signal_registry_core__001/`。

需要旧题包或旧运行时，到 `archive/paper_unrelated_20260914/`，不要从那里写正文数字。旧论文图文件名在 `archive/paper_workspace_20260914/`。

```bash
python -B scripts/paper.py check
```

本地可核验主实验 profile 合计 307/900。完整逐题结果矩阵有 900 条；`check` 核对当前可用证据，`audit` 要求原始 profile 全部齐备。新版正文来源见 [FSE 同步记录](FSE_SYNC_20260914.md)。
