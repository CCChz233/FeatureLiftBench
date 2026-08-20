# Python-200 跨模型 Main

> **Status: current · Last verified: 2026-08-18**
> 用途：组会 / 汇报直接投屏。
> 条件：Full-Repository / No-Hint Main，120 步，每题一次。
> 指标：evaluator `functional_gate`；`summary.passed` / `run.status` 只作运行诊断。
> **不是**当前 V1（Main+2M），也不是旧 Lite V1 checker/repair 协议。

## 主结果

| 模型 | Functional Pass | Pass Rate | Wilson 95% |
| --- | ---: | ---: | --- |
| DeepSeek V4 Flash 本地 | **145/200** | **72.5%** | 65.9%–78.2% |
| DeepSeek V4 Flash API | **144/200** | **72.0%** | 65.4%–77.8% |
| Qwen3.5 122B 本地 | **96/200** | **48.0%** | 41.2%–54.9% |
| Qwen3.6 35B 本地 | **95/200** | **47.5%** | 40.7%–54.4% |
| GPT-OSS 120B 本地 | **43/200** | **21.5%** | 16.4%–27.7% |

**一句话：DeepSeek 明显领先；两档 Qwen 几乎打平（区间重叠）；GPT-OSS 明显落后。**

## 150 / External-50 分解

| 模型 | Python-150 | External-50 | Python-200 |
| --- | ---: | ---: | ---: |
| DeepSeek API | 99/150 (66.0%) | 45/50 (90.0%) | **144/200** |
| DeepSeek 本地 | 98/150 (65.3%) | 47/50 (94.0%) | **145/200** |
| Qwen3.5 122B | 59/150 (39.3%) | 37/50 (74.0%) | **96/200** |
| Qwen3.6 35B | 59/150 (39.3%) | 36/50 (72.0%) | **95/200** |
| GPT-OSS 120B | 27/150 (18.0%) | 16/50 (32.0%) | **43/200** |

External-50 对所有模型都更容易，不能单独当能力结论。

## 失败阶段（互斥首败）

| 模型 | Pass | 未交付 | Build | Public | Hidden | Isolation |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| DeepSeek API | 144 | 5 | 2 | 27 | 22 | 0 |
| DeepSeek 本地 | 145 | 2 | 1 | 28 | 24 | 0 |
| Qwen3.5 122B | 96 | 0 | 0 | 70 | 33 | 1 |
| Qwen3.6 35B | 95 | 6 | 10 | 61 | 28 | 0 |
| GPT-OSS 120B | 43 | 5 | 18 | 88 | 46 | 0 |

Qwen / GPT-OSS 的主失败关是 Public，其次 Hidden。GPT-OSS 还有更多 Build 失败。
Qwen3.5 几乎总能交卷并过 build。

## 汇报时必须说清

- Qwen / GPT-OSS 是冻结 Python-150 + 2026-08-17 External-50 按题号合并，不是一次 200 连跑。
- Qwen3.6-35B External-50 的 `run.status` 几乎全失败，但 Functional 仍是 36/50。
- 通过题 RRES 中位数全贴 1.000，是 External-50 copy-heavy；跨模型不能比紧凑度。
- 不要把这张表和当前 V1、旧 Lite V1、Rescue+、V2、Core-12 混在一起。
- Qwen V1-200 已完成（55/200），解释在 [FINDINGS.md](FINDINGS.md)，不要写进本表。

证据：[STATUS.md](STATUS.md) ·
[`python200_cross_model_main_20260818.json`](../artifacts/research_analysis/current_results/python200_cross_model_main_20260818.json)。
DeepSeek 方法对比仍看 [汇报_实验结果表.md](汇报_实验结果表.md)。
