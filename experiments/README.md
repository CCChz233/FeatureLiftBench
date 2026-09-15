# FeatureLiftBench 原始实验记录

> **Status: reference · Last verified: 2026-09-14**

本目录保存实际恢复的原始结果和恢复台账。当前正文取数路径由
[paper_sources.json](../docs/paper/paper_sources.json) 登记，不按目录日期或名称挑选成绩。

| 目录 / 文件 | 当前内容 |
| --- | --- |
| `python/openhands/deepseek-v4-pro/python150-prime-v2-main-r1` | Pro 150 题原始记录 |
| `python/openhands/deepseek-v4-flash/python200-prime-v2-main-r1` | Flash 200 题；本文选其中 150 题 |
| `python/openhands/glm-5.3-flash/python200-prime-v2-main-r1` | 截断包恢复 12 题；其中 7 题属于论文集合 |
| [paper_results_20260913/](paper_results_20260913/README.md) | 压缩包和恢复范围说明 |
| `paper-results-full-20260913T154543Z.tar.gz` | 原始截断传输包，保留用于溯源 |
| [registry/](registry/README.md) | 历史实验身份与维护台账 |

Luna/Qwen/OSS 的当前主实验原始目录未恢复。论文有完整的 900 条派生逐题结果，
但本地主实验 profile 仅 307/900；二者不是同一完整性声明。

旧运行、校准与传输包已移动至
[archive/paper_unrelated_20260914/](../archive/paper_unrelated_20260914/README.md)。
历史运行保留原始身份，不改名冒充新实验。新实验仍通过 `scripts/run_benchmark.sh` 运行，
写入 `experiments/python/<runtime>/<model>/<run-id>/`，不在本轮执行。
