# Python-200 Main 跨模型结果

> **Status: current · Generated: 2026-08-17T23:57:42+00:00**
> 条件：Full-Repository / No-Hint Main，120 步，每题一次。
> 指标：evaluator `functional_gate`；`summary.passed` / `run.status` 只作运行诊断。
> 这不是 V1（Main+2M cap），也不是旧 Lite V1 checker/repair 协议。

Suite: `python200-full-repository-no-hint-20260801-v1`  
Task set: `cee22c263a3c190e8b13b0c3c70d9fabac5c6c767010e5c21220f2c8c61bfa74`

## Leaderboard

| 模型 | 端点 | Functional Pass | Pass Rate | Wilson 95% | RRES median [Q1, Q3] |
| --- | --- | ---: | ---: | --- | --- |
| DeepSeek V4 Flash local vLLM | local_vllm | **145/200** | **72.5%** | 65.9%–78.2% | 145/145, median 1.000 [0.858, 1.000] |
| DeepSeek V4 Flash API | api | **144/200** | **72.0%** | 65.4%–77.8% | 144/144, median 1.000 [0.930, 1.001] |
| Qwen3.5 122B local vLLM | local_vllm | **96/200** | **48.0%** | 41.2%–54.9% | 96/96, median 1.000 [0.587, 1.000] |
| Qwen3.6 35B local vLLM | local_vllm | **95/200** | **47.5%** | 40.7%–54.4% | 95/95, median 1.000 [0.650, 1.000] |
| GPT-OSS 120B local vLLM | local_vllm | **43/200** | **21.5%** | 16.4%–27.7% | 43/43, median 1.000 [0.451, 1.002] |

## 150 / External-50 / 200 分解

| 模型 | Python-150 | External-50 | Python-200 |
| --- | ---: | ---: | ---: |
| DeepSeek V4 Flash API | 99/150 (66.0%) | 45/50 (90.0%) | **144/200 (72.0%)** |
| DeepSeek V4 Flash local vLLM | 98/150 (65.3%) | 47/50 (94.0%) | **145/200 (72.5%)** |
| Qwen3.5 122B local vLLM | 59/150 (39.3%) | 37/50 (74.0%) | **96/200 (48.0%)** |
| Qwen3.6 35B local vLLM | 59/150 (39.3%) | 36/50 (72.0%) | **95/200 (47.5%)** |
| GPT-OSS 120B local vLLM | 27/150 (18.0%) | 16/50 (32.0%) | **43/200 (21.5%)** |

## 失败阶段（Python-200，互斥首败）

| 模型 | Pass | 未交付 | Build | Public | Hidden | Isolation | Infra | 缺证据 | Unknown |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| DeepSeek V4 Flash API | 144 | 5 | 2 | 27 | 22 | 0 | 0 | 0 | 0 |
| DeepSeek V4 Flash local vLLM | 145 | 2 | 1 | 28 | 24 | 0 | 0 | 0 | 0 |
| Qwen3.5 122B local vLLM | 96 | 0 | 0 | 70 | 33 | 1 | 0 | 0 | 0 |
| Qwen3.6 35B local vLLM | 95 | 6 | 10 | 61 | 28 | 0 | 0 | 0 | 0 |
| GPT-OSS 120B local vLLM | 43 | 5 | 18 | 88 | 46 | 0 | 0 | 0 | 0 |

## 口径与资格

- Qwen3.5 / GPT-OSS：冻结 Python-150 整包 + 2026-08-17 External-50。
- Qwen3.6-35B：冻结 Python-150 三片（p8008/p8020/p8021）并集 + 同日 External-50。
- DeepSeek API：既有 150 + External-50；DeepSeek 本地：一次跑满 200。
- Agent/evaluator image 均钉在 `sha256:f328e2ce…` / `sha256:a491d620…`。
- Qwen3.6-35B External-50 的 `run.status` 大量失败，但 evaluator Functional 仍按 `functional_gate` 计；不得用 `summary.passed`。
- 未与当前 V1（Main+2M）混表。
