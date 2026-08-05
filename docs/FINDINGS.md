# 当前实验结果能说明什么

> **Status: current · Last verified: 2026-08-05**  
> 本文是冻结 Python-150 实验结果的解释结论，不是运行手册。  
> 规模、资格与 blocker 以 [STATUS.md](STATUS.md) 为准。  
> **最新完整多指标主表：**
> [`reports/paper_analysis/python150_with_deepseek150_20260805/RESULTS.md`](../reports/paper_analysis/python150_with_deepseek150_20260805/RESULTS.md)  
> （Functional + 漏斗 + 过程 + 成本 + 紧凑性 + 成对比较）  
> 旧 20260803 审计仍保留作 GPT-OSS/Qwen 原始归档对照。

## 1. 证据范围

本结论基于：

- 冻结 suite：Python-150 Full-Repository / No-Hint Main；
- 主指标：逐题 evaluator `functional_gate`（Functional Pass@1）；
- DeepSeek V4 Flash：**150/150**（归档 `FeatureLiftBench-deepseek-v4-flash-150-20260805.tar.gz`）；
- GPT-OSS 120B、Qwen3.5 122B、Qwen3.6 35B：各 150/150（归档 20260803）。

以下材料**不**作为结论依据：MANIFEST / suite summary 的 run-status 通过数、历史 mixed-snapshot 拼表、方法 pilot，以及尚未开始的 Python-200 External-50 模型 run。

## 2. 主结果（Functional Pass@1）

| 模型 | 覆盖 | Pass@1 | 通过率 | Wilson 95% CI | Context 违规 |
| --- | ---: | ---: | ---: | --- | ---: |
| DeepSeek V4 Flash | 150/150 | **99/150** | **66.0%** | 58.1%–73.1% | 8 |
| Qwen3.5 122B | 150/150 | **59/150** | **39.3%** | 31.9%–47.3% | 9 |
| Qwen3.6 35B | 150/150 | **59/150** | **39.3%** | 31.9%–47.3% | 31 |
| GPT-OSS 120B | 150/150 | **27/150** | **18.0%** | 12.7%–24.9% | 0 |

四模型现均可同覆盖比较。资格 caveat：evaluator image 与 freeze 登记仍不一致；Qwen/DeepSeek 的 context 违规需 sensitivity 或重跑。

正确性漏斗（绝对题数 / 150）：

| 模型 | Build | Public | Hidden | Isolation | Functional |
| --- | ---: | ---: | ---: | ---: | ---: |
| DeepSeek | 144 | 120 | 106 | 144 | **99** |
| Qwen3.5 | 150 | 90 | 69 | 148 | **59** |
| Qwen3.6 | 137 | 85 | 64 | 135 | **59** |
| GPT-OSS | 134 | 66 | 32 | 130 | **27** |

任务成对比较（McNemar exact）：

| 对比 | Both pass | Left only | Right only | Both fail | p | 解读 |
| --- | ---: | ---: | ---: | ---: | ---: | --- |
| GPT-OSS vs Qwen3.5 | 18 | 9 | 41 | 82 | 5.6e-06 | Qwen3.5 更强 |
| GPT-OSS vs Qwen3.6 | 17 | 10 | 42 | 81 | 9.1e-06 | Qwen3.6 更强 |
| GPT-OSS vs DeepSeek | 24 | 3 | 75 | 48 | 5.2e-19 | DeepSeek 更强 |
| Qwen3.5 vs Qwen3.6 | 39 | 20 | 20 | 71 | 1.0 | 打平 |
| Qwen3.5 vs DeepSeek | 53 | 6 | 46 | 45 | 1.0e-08 | DeepSeek 更强 |
| Qwen3.6 vs DeepSeek | 53 | 6 | 46 | 45 | 1.0e-08 | DeepSeek 更强 |

DeepSeek 补齐：旧 100 题与新归档 **无翻转**；新增 50 题通过 33；总通过率仍约 66%。

## 3. 可以得出的结论

### C1. Benchmark 对当前 coding agent 有区分度

同覆盖下 Pass@1 从 **18%**（GPT-OSS）到 **66%**（DeepSeek），成对检验显著。任务集能拉开被测 agent。

### C2. 任务整体偏难；Public 过不等于最终通过

漏斗显示大量失败在 public→hidden→functional。主难度不只是构建或“找到文件”。

### C3. Agent 完成状态不能替代 Functional Pass

必须以 evaluator `functional_gate` 为准。

### C4. 同覆盖排名：DeepSeek ≫ Qwen3.5 ≈ Qwen3.6 ≫ GPT-OSS

DeepSeek 相对两款 Qwen 各多过 46 题、少输 6 题（p≈1e-08）。两款 Qwen 打平。均显著强于 GPT-OSS。

### C5. DeepSeek 现已可进入完整 150 横向比较

补齐前只能作 partial；补齐后覆盖与其它模型一致，**可以**进入 Python-150 成对排名（仍受 image/context 资格约束）。

### C6. Context window 仍是真实实验因素

GPT-OSS 0；DeepSeek 8；Qwen3.5 9；Qwen3.6 31。报告 Qwen/DeepSeek 结论时须附带 context 说明。

### C7. 逐题证据可用于失败归因与过程分析

不足以完整复现 OpenHands 逐事件轨迹（归档缺 event trajectory）。

### C8. Python-200 扩展仍无模型结果

External-50 包就绪；agent 扩展 run 未齐。不能出最终 Python-200 leaderboard。

## 4. 尚不能得出的结论

1. 最终 Python-200 排名。  
2. 严格冻结 evaluator 环境下的精确分数（image mismatch）。  
3. 与 context 无关的 Qwen/DeepSeek 排名。  
4. 抄袭 / `copied_fraction` headline。  
5. 外推到未测语言、应用仓或未测 agent 条件。  
6. 历史方法 pilot 的 Main 结果地位。

## 5. 对论文叙述的直接含义

可写（在完成环境资格处理后）：

- 冻结 Python-150 有区分度；  
- 主指标 Functional Pass@1；  
- **DeepSeek 显著强于两款 Qwen，Qwen 显著强于 GPT-OSS；两款 Qwen 同档。**

应延后：Python-200 总榜；未附带 image/context 说明的精确百分比。

## 6. 一句话总结

**DeepSeek 已补齐为 99/150（66%），四模型现可同覆盖比较：DeepSeek ≫ Qwen ≈ 39% ≫ GPT-OSS 18%。Benchmark 有效且偏难；仍缺 eval-image/context 收尾与 Python-200 扩展实验结果。**
